import json
import re
from enum import Enum

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


def _fail(message: str):
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


def _convert(hex_text: str, parser, to_json, fmt: OutputFormat, what: str):
    try:
        data = parse_hex(hex_text)
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
    avp_hex: str = typer.Argument(..., help="AVP as hex (0x prefix and spaces allowed)."),
    fmt: OutputFormat = typer.Option(OutputFormat.tree, "--format", "-f", help="Output format."),
):
    """Convert a Diameter AVP in hex format."""
    _convert(avp_hex, Avp.from_bytes, avp_to_json, fmt, "AVP")


@app.command()
def message2json(
    diameter_hex: str = typer.Argument(..., help="Message as hex (0x prefix and spaces allowed)."),
    fmt: OutputFormat = typer.Option(OutputFormat.tree, "--format", "-f", help="Output format."),
):
    """Convert a Diameter message in hex format."""
    _convert(diameter_hex, Message.from_bytes, message_to_json, fmt, "message")


if __name__ == "__main__":
    app()
