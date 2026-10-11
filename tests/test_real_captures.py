"""Regression tests on Diameter messages taken from public captures (see data/SOURCES.md).

The expected structure comes from a small independent AVP walker, not from the
library. The same fields were also compared with tshark when the samples were chosen.
"""
import json
import struct
from pathlib import Path

import pytest

from pydiameter2json.__main__ import _parse_message
from pydiameter2json.main import message_to_json

SAMPLES = json.loads((Path(__file__).parent / "data" / "real_captures.json").read_text())["samples"]
BY_ID = {s["id"]: s for s in SAMPLES}


def walk(data: bytes):
    """Yield (code, vendor, length, padded raw bytes, payload) per AVP."""
    pos = 0
    while pos < len(data):
        code, flags_len = struct.unpack("!II", data[pos : pos + 8])
        flags, length = flags_len >> 24, flags_len & 0xFFFFFF
        header = 8
        vendor = 0
        if flags & 0x80:
            (vendor,) = struct.unpack("!I", data[pos + 8 : pos + 12])
            header = 12
        raw = data[pos : pos + (length + 3) // 4 * 4]  # avp_hex keeps the padding
        yield code, vendor, length, raw, raw[header:length]
        pos += (length + 3) // 4 * 4


def check(expected_bytes: bytes, got: list):
    walked = list(walk(expected_bytes))
    assert len(walked) == len(got)
    for (code, _vendor, length, raw, payload), avp in zip(walked, got):
        assert avp["code"] == code
        assert avp["length"] == length
        assert avp["avp_hex"] == raw.hex()
        assert avp["value_hex"] == payload.hex()
        if isinstance(avp["value"], list):  # grouped AVP
            check(payload, avp["value"])


def convert(sample_id: str):
    data = bytes.fromhex(BY_ID[sample_id]["hex"])
    return data, message_to_json(_parse_message(data))


@pytest.mark.parametrize("sample", SAMPLES, ids=[s["id"] for s in SAMPLES])
def test_structure_matches_wire(sample):
    data, result = convert(sample["id"])
    check(data[20:], result)


def find_all(avps, code):
    for avp in avps:
        if avp["code"] == code:
            yield avp
        if isinstance(avp["value"], list):
            yield from find_all(avp["value"], code)


def test_framed_ip_is_dotted():
    _, result = convert("magma-gx-gy-05-frame121")
    (framed,) = find_all(result, 8)
    assert framed["value"] == "172.17.241.255"
    assert framed["value_hex"] == "ac11f1ff"


def test_3gpp_sgsn_and_ggsn_addresses_are_dotted():
    _, result = convert("magma-gx-gy-05-frame32")
    assert [a["value"] for a in find_all(result, 6)] == ["172.16.10.101"]
    assert [a["value"] for a in find_all(result, 7)] == ["172.16.10.101"]
    assert next(find_all(result, 8))["value"] == "172.17.241.255"


def test_s6a_sample_values():
    _, result = convert("magma-gx-gy-05-frame17")
    assert next(find_all(result, 268))["value"] == 2001
    assert next(find_all(result, 264))["value"] == "tvm-vhss.magma.com"
