import json
import re
import sys
from enum import Enum
from pathlib import Path

import typer
from diameter.message import Avp, Message

from .main import avp_to_json, json_to_tree, message_to_json

app = typer.Typer(help="Convert Diameter messages and AVPs from hex to JSON or a tree view.")


class OutputFormat(str, Enum):
    tree = "tree"
    json = "json"


def parse_hex(text: str) -> bytes:
    """Accept an optional 0x prefix and any whitespace; raise ValueError on bad hex."""
    cleaned = re.sub(r"\s+", "", text)
    if cleaned[:2].lower() == "0x":
        cleaned = cleaned[2:]
    if not cleaned:
        raise ValueError("empty hex input")
    return bytes.fromhex(cleaned)


def _parse_avp(data: bytes):
    """Parse one AVP and reject input whose length field does not match the bytes."""
    avp = Avp.from_bytes(data)
    declared = int.from_bytes(data[5:8], "big")
    header_len = 12 if data[4] & 0x80 else 8
    if declared < header_len:
        raise ValueError(f"AVP length field {declared} is smaller than its header ({header_len})")
    padded = (declared + 3) // 4 * 4
    if padded != len(data):
        raise ValueError(
            f"AVP length field says {declared} bytes ({padded} with padding), got {len(data)}"
        )
    return avp


def _parse_message(data: bytes):
    """Parse without the library's typed command classes.

    The typed classes reorder AVPs and add defaults (e.g. Auth-Application-Id)
    that are not on the wire. plain_msg=True keeps the AVPs exactly as received.
    """
    if len(data) >= 4:
        if data[0] != 1:
            raise ValueError(f"unsupported Diameter version {data[0]} (expected 1)")
        declared = int.from_bytes(data[1:4], "big")
        if declared != len(data):
            raise ValueError(f"header length field says {declared} bytes, got {len(data)}")
    return Message.from_bytes(data, plain_msg=True)


def _fail(message: str):
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


def read_input(arg: str) -> str:
    """Return the hex text for the argument.

    "-" reads standard input. An existing file path reads that file.
    Anything else is the hex text itself.
    """
    if arg == "-":
        return sys.stdin.read()
    try:
        path = Path(arg)
        is_file = path.is_file()
    except (OSError, ValueError):  # for example a name that is too long: it is hex
        return arg
    if is_file:
        try:
            return path.read_text()
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"cannot read file {arg!r} ({exc})") from exc
    return arg


def _convert(hex_text: str, parser, to_json, fmt: OutputFormat, what: str):
    try:
        data = parse_hex(read_input(hex_text))
    except ValueError as exc:
        _fail(f"invalid hex input ({exc})")
    try:
        result = to_json(parser(data))
    except Exception as exc:  # library raises several error types on bad input
        _fail(f"cannot decode {what}: {exc}")
    if fmt == OutputFormat.json:
        typer.echo(json.dumps(result, indent=4))
    else:
        typer.echo("\n".join(json_to_tree(result)))


@app.command()
def avp2json(
    avp_hex: str = typer.Argument(..., help="AVP as hex (0x prefix and spaces allowed), a file path, or - for stdin."),
    fmt: OutputFormat = typer.Option(OutputFormat.tree, "--format", "-f", help="Output format."),
):
    """Convert a Diameter AVP in hex format."""
    _convert(avp_hex, _parse_avp, avp_to_json, fmt, "AVP")


@app.command()
def message2json(
    diameter_hex: str = typer.Argument(..., help="Message as hex (0x prefix and spaces allowed), a file path, or - for stdin."),
    fmt: OutputFormat = typer.Option(OutputFormat.tree, "--format", "-f", help="Output format."),
):
    """Convert a Diameter message in hex format."""
    _convert(diameter_hex, _parse_message, message_to_json, fmt, "message")


if __name__ == "__main__":
    app()
