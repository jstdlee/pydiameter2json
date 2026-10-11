"""Regression tests for bugs found in code review (wire fidelity, Address, Time, lengths)."""
import json
import socket
import struct
import time

import pytest
from diameter.message import Avp
from typer.testing import CliRunner

from pydiameter2json.__main__ import app
from pydiameter2json.main import avp_to_json, json_to_tree

runner = CliRunner()


def pad(b):
    return b + b"\0" * (-len(b) % 4)


def avp(code, data, flags=0x40, vendor=None):
    if vendor is not None:
        flags |= 0x80
    length = 8 + (4 if vendor is not None else 0) + len(data)
    out = struct.pack(">I", code) + bytes([flags]) + length.to_bytes(3, "big")
    if vendor is not None:
        out += struct.pack(">I", vendor)
    return pad(out + data)


def msg(cmd, request, avps, app_id=0):
    body = b"".join(avps)
    flags = 0xC0 if request else 0x40
    return (
        b"\x01" + (20 + len(body)).to_bytes(3, "big") + bytes([flags]) + cmd.to_bytes(3, "big")
        + struct.pack(">III", app_id, 1, 2) + body
    )


def cli(*args):
    return runner.invoke(app, list(args))


def test_message_keeps_wire_order_and_adds_no_avps():
    # CCA on the wire without Auth-Application-Id; ordering is not the library's.
    data = msg(272, False, [
        avp(1, b"user"), avp(263, b"s;1"), avp(268, struct.pack(">I", 2001)),
        avp(55, struct.pack(">I", 3_900_000_000)), avp(416, struct.pack(">I", 1)),
    ])
    out = json.loads(cli("message2json", data.hex(), "-f", "json").stdout)
    assert [a["code"] for a in out] == [1, 263, 268, 55, 416]


@pytest.mark.parametrize(
    "ip,family",
    [("2001:db8::1", socket.AF_INET6), ("192.0.2.9", socket.AF_INET)],
)
def test_address_avp_is_plain_string_and_visible_in_tree(ip, family):
    fam = 1 if family == socket.AF_INET else 2
    raw = avp(257, struct.pack(">H", fam) + socket.inet_pton(family, ip))
    result = avp_to_json(Avp.from_bytes(raw))
    assert result["value"] == ip
    assert f"Host-IP-Address, {ip}," in "\n".join(json_to_tree(result))


def test_time_avp_is_utc_and_independent_of_local_timezone(monkeypatch):
    ntp = 1_700_000_000 + 2_208_988_800  # 2023-11-14T22:13:20Z
    raw = avp(55, struct.pack(">I", ntp))
    results = set()
    for tz in ("UTC", "Asia/Singapore", "America/New_York"):
        monkeypatch.setenv("TZ", tz)
        time.tzset()
        results.add(avp_to_json(Avp.from_bytes(raw))["value"])
    monkeypatch.delenv("TZ")
    time.tzset()
    assert results == {"2023-11-14T22:13:20+00:00"}


def test_empty_avp_reports_real_length_and_hex():
    result = avp_to_json(Avp.from_bytes(avp(99997, b"")))
    assert result["length"] == 8
    assert result["avp_hex"] == "0001869d40000008"


def test_tree_top_level_has_no_indent():
    lines = json_to_tree([avp_to_json(Avp.from_bytes(avp(268, struct.pack(">I", 2001))))])
    assert lines == ["└── (268, 12), Result-Code, 2001, 000007d1"]


@pytest.mark.parametrize(
    "hex_in,fragment",
    [
        ("00000108400000040000" + "0000", "smaller than its header"),
        (avp(264, b"abcd").hex() + "00", "length field says"),
    ],
)
def test_avp2json_rejects_inconsistent_length(hex_in, fragment):
    result = cli("avp2json", hex_in)
    assert result.exit_code == 1
    assert fragment in result.output


def test_message2json_rejects_bad_header_length_and_version():
    good = msg(272, True, [avp(263, b"s")])
    assert cli("message2json", good.hex()).exit_code == 0
    too_long = good + b"\0\0\0\0"
    r = cli("message2json", too_long.hex())
    assert r.exit_code == 1 and "header length field" in r.output
    r = cli("message2json", ("02" + good.hex()[2:]))
    assert r.exit_code == 1 and "version" in r.output
