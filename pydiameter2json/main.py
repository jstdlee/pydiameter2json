import json
from datetime import datetime

from diameter.message.avp import AvpAddress
from diameter.message.avp.errors import AvpDecodeError


def bytes_to_text_or_hex(value: bytes) -> str:
    """Return text if the bytes are valid, printable UTF-8; otherwise hex."""
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError:
        return value.hex()
    return text if text.isprintable() else value.hex()


def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):  # grouped AVP: list of Avp objects
        return [avp_to_json(sub) for sub in value]
    if isinstance(value, tuple):
        return [_serialize_value(v) for v in value]
    if isinstance(value, AvpAddress):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return bytes_to_text_or_hex(bytes(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def avp_to_json(avp):
    """Convert an Avp (recursively for grouped AVPs) to a JSON-ready dict."""
    try:
        value = _serialize_value(avp.value)
    except (UnicodeDecodeError, ValueError, AvpDecodeError):
        # Library could not decode the value: show the raw payload instead.
        value = bytes_to_text_or_hex(avp.payload)
    return {
        "avp_hex": avp.as_bytes().hex(),
        "code": avp.code,
        "length": avp.length,
        "name": avp.name,
        "value": value,
        "value_hex": avp.payload.hex(),
    }


def message_to_json(message):
    return [avp_to_json(avp) for avp in message.avps]


def json_to_tree(json_obj, prefix="", is_last=True):
    """Render AVP dicts as tree lines: (code, length), name, value."""
    lines = []
    connector = "└── " if is_last else "├── "
    next_prefix = prefix + ("    " if is_last else "│   ")

    if isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            lines.extend(json_to_tree(item, next_prefix, i == len(json_obj) - 1))
    elif isinstance(json_obj, dict):
        code = json_obj.get("code", "")
        length = json_obj.get("length", "")
        name = json_obj.get("name", "")
        value = json_obj.get("value", "")
        value_hex = json_obj.get("value_hex", "")
        if isinstance(value, list):
            lines.append(f"{prefix}{connector}({code}, {length}), {name}")
            for i, sub in enumerate(value):
                lines.extend(json_to_tree(sub, next_prefix, i == len(value) - 1))
        else:
            lines.append(f"{prefix}{connector}({code}, {length}), {name}, {value}, {value_hex}")
    return lines


def print_json_tree(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    for line in json_to_tree(json_data):
        print(line)
