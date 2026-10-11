import json
from pathlib import Path

import pytest
from diameter.message import Avp, Message
from typer.testing import CliRunner

from pydiameter2json.__main__ import app, parse_hex
from pydiameter2json.main import avp_to_json, bytes_to_text_or_hex, json_to_tree, message_to_json

DATA = Path(__file__).parent
CCR_HEX = (DATA / "gx.ccr.grouped.txt").read_text().strip()
ORIGIN_HOST_HEX = (DATA / "gx.origin.host.txt").read_text().strip()
runner = CliRunner()
split_runner = CliRunner(mix_stderr=False)


def find(avps, code):
    return next(a for a in avps if a["code"] == code)


def test_grouped_avp_is_recursive():
    result = message_to_json(Message.from_bytes(bytes.fromhex(CCR_HEX)))
    sub_id = find(result, 443)  # Subscription-Id
    assert isinstance(sub_id["value"], list)
    assert {s["code"] for s in sub_id["value"]} == {450, 444}
    data = find(sub_id["value"], 444)
    assert data["value"] == "596696310364"
    # nested two levels: QoS-Information contains plain AVPs
    qos = find(result, 1016)
    assert find(qos["value"], 1028)["value"] == 6


def test_grouped_tree_view_shows_children():
    result = message_to_json(Message.from_bytes(bytes.fromhex(CCR_HEX)))
    tree = "\n".join(json_to_tree(result))
    assert "Subscription-Id-Data, 596696310364" in tree
    assert "│   ├── (450, 12), Subscription-Id-Type" in tree


def test_avp_hex_is_full_avp_and_value_hex_is_payload():
    avp = Avp.from_bytes(bytes.fromhex(ORIGIN_HOST_HEX))
    result = avp_to_json(avp)
    assert result["avp_hex"] == ORIGIN_HOST_HEX
    assert result["value_hex"] == avp.payload.hex()
    assert result["value_hex"] != result["avp_hex"]


def test_grouped_value_hex_contains_children_bytes():
    result = message_to_json(Message.from_bytes(bytes.fromhex(CCR_HEX)))
    sub_id = find(result, 443)
    children = "".join(c["avp_hex"] for c in sub_id["value"])
    assert sub_id["value_hex"] == children


@pytest.mark.parametrize(
    "raw,expected",
    [
        (b"hello", "hello"),
        (b"\xff\xfe", "fffe"),  # invalid UTF-8
        (b"\x00\x01", "0001"),  # valid UTF-8 but not printable
        (b"a\nb", "610a62"),
    ],
)
def test_bytes_to_text_or_hex(raw, expected):
    assert bytes_to_text_or_hex(raw) == expected


def test_parse_hex_accepts_prefix_and_whitespace():
    assert parse_hex("0x01 02\n03") == b"\x01\x02\x03"
    assert parse_hex("0X0a0B") == b"\x0a\x0b"
    with pytest.raises(ValueError):
        parse_hex("zz")
    with pytest.raises(ValueError):
        parse_hex("  ")


def test_cli_message_json():
    r = runner.invoke(app, ["message2json", CCR_HEX, "--format", "json"])
    assert r.exit_code == 0
    data = json.loads(r.stdout)
    assert find(data, 443)["value"][0]["code"] == 450


def test_cli_message_tree_default():
    r = runner.invoke(app, ["message2json", "0x" + CCR_HEX])
    assert r.exit_code == 0
    assert "Subscription-Id-Data" in r.stdout


def test_cli_avp_with_spaces():
    spaced = " ".join(ORIGIN_HOST_HEX[i : i + 8] for i in range(0, len(ORIGIN_HOST_HEX), 8))
    r = runner.invoke(app, ["avp2json", spaced, "-f", "json"])
    assert r.exit_code == 0
    assert json.loads(r.stdout)["name"] == "Origin-Host"


@pytest.mark.parametrize("cmd", ["avp2json", "message2json"])
def test_cli_bad_hex(cmd):
    r = runner.invoke(app, [cmd, "not-hex"])
    assert r.exit_code == 1
    assert "invalid hex" in r.output
    assert "Traceback" not in r.output


@pytest.mark.parametrize("cmd", ["avp2json", "message2json"])
def test_cli_decode_failure(cmd):
    r = runner.invoke(app, [cmd, "0000"])
    assert r.exit_code == 1
    assert "cannot decode" in r.output


@pytest.mark.parametrize("cmd,hex_text", [("avp2json", ORIGIN_HOST_HEX), ("message2json", CCR_HEX)])
def test_cli_reads_stdin(cmd, hex_text):
    r = runner.invoke(app, [cmd, "-", "-f", "json"], input=hex_text + "\n")
    assert r.exit_code == 0
    json.loads(r.stdout)


def test_cli_reads_file(tmp_path):
    path = tmp_path / "msg.txt"
    path.write_text(CCR_HEX + "\n")
    r = runner.invoke(app, ["message2json", str(path), "-f", "json"])
    assert r.exit_code == 0
    assert find(json.loads(r.stdout), 443)["value"][0]["code"] == 450


def test_cli_missing_file_is_treated_as_hex(tmp_path):
    r = split_runner.invoke(app, ["avp2json", str(tmp_path / "nope.txt")])
    assert r.exit_code == 1
    assert "invalid hex" in r.stderr


def test_cli_empty_stdin():
    r = split_runner.invoke(app, ["message2json", "-"], input="")
    assert r.exit_code == 1
    assert "empty hex" in r.stderr


@pytest.mark.parametrize("cmd", ["avp2json", "message2json"])
def test_cli_errors_use_stderr_only(cmd):
    r = split_runner.invoke(app, [cmd, "0000"])
    assert r.exit_code == 1
    assert r.stdout == ""
    assert r.stderr.startswith("Error: ")
