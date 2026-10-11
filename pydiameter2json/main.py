import json
import struct
from datetime import datetime, timezone

from diameter.message.avp import AvpAddress, AvpTime
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
    if isinstance(value, (bytes, bytearray)):
        return bytes_to_text_or_hex(bytes(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _time_to_iso(avp: AvpTime) -> str:
    """RFC 6733 Time as an ISO 8601 UTC string.

    The library returns a naive datetime in the local time zone, so the output
    would depend on the machine's TZ. Decode the NTP seconds directly instead.
    """
    (seconds,) = struct.unpack("!I", avp.payload)  # struct.error on bad length
    if seconds < AvpTime.overflow_detection_cutoff:  # era 1: 2036 to 2104
        unix = seconds + AvpTime.overflow_timestamp
    else:  # era 0: 1968 to 2036
        unix = seconds - AvpTime.seconds_since_1900
    return datetime.fromtimestamp(unix, tz=timezone.utc).isoformat()


def avp_to_json(avp):
    """Convert an Avp (recursively for grouped AVPs) to a JSON-ready dict."""
    try:
        if isinstance(avp, AvpTime):
            value = _time_to_iso(avp)
        elif isinstance(avp, AvpAddress):
            # The library returns (address family, text); keep only the address.
            value = avp.value[1]
        else:
            value = _serialize_value(avp.value)
    except (UnicodeDecodeError, ValueError, struct.error, AvpDecodeError):
        # Library could not decode the value: show the raw payload instead.
        value = bytes_to_text_or_hex(avp.payload)
    raw = avp.as_bytes()
    # Avp.length (and so as_bytes) reports 0 for an empty payload; fix the header.
    length = (12 if avp.flags & 0x80 else 8) + len(avp.payload)
    if not avp.payload:
        raw = raw[:5] + length.to_bytes(3, "big") + raw[8:]
    return {
        "avp_hex": raw.hex(),
        "code": avp.code,
        "length": length,
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
            lines.extend(json_to_tree(item, prefix, i == len(json_obj) - 1))
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
