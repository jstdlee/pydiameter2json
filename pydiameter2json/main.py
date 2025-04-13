from diameter.message import Avp
from diameter.message.avp import AvpAddress, AvpAddressSolo
from diameter.message.avp.errors import AvpDecodeError, AvpEncodeError
from diameter.message.constants import *
from diameter.message import Message
from datetime import datetime
import json

def avp_to_json(avp):
    # Handle different AVP types and ensure JSON serializability
    def serialize_value(value):
        if isinstance(value, datetime):
            return value.isoformat()  # Convert datetime to ISO 8601 string
        elif isinstance(value, list):  # Handle lists of AVPs (e.g., grouped AVPs)
            return [avp_to_json(sub_avp) for sub_avp in value]
        elif isinstance(value, AvpAddress) or isinstance(value, AvpAddressSolo):  # Handle AvpAddress type
            # Convert AvpAddress to a readable IP address
            return str(value)
        elif isinstance(value, bytes):  # Handle raw bytes
            try:
                return value.decode('utf-8')  # Attempt to decode as UTF-8
            except UnicodeDecodeError or AvpDecodeError:
                return value.hex()  # Fallback to hex representation
        elif hasattr(value, '__dict__'):  # Handle custom objects like AvpInteger32
            return {key: serialize_value(val) for key, val in value.__dict__.items()}
        else:
            return value
    


    result = {
        "avp_hex": avp.payload.hex(),
        "code": avp.code,
        "length": avp.length,
        "name": avp.name,
        "value": serialize_value(avp.value),
        "value_hex": serialize_value(avp.value),
        

    }
    if hasattr(avp, 'sub_avps') and avp.sub_avps:  # Handle nested AVPs
        result['sub_avps'] = [avp_to_json(sub_avp) for sub_avp in avp.sub_avps]
    return result

def message_to_json(message):
    result = [avp_to_json(avp) for avp in message.avps]  # Process all AVPs
    return result



def json_to_tree(json_obj, prefix="", is_last=True):
    """
    Convert a JSON object to a tree-like plain text structure.
    - Each row is formatted as (code, length), name, value.
    - Nested structures are displayed recursively with indentation.

    Args:
        json_obj: The JSON object (list or dict) to convert.
        prefix: Prefix string for indentation (used for nested structures).
        is_last: Boolean indicating if the current item is the last in its parent.

    Returns:
        A list of strings representing the tree structure.
    """
    lines = []
    connector = "└── " if is_last else "├── "
    next_prefix = prefix + ("    " if is_last else "│   ")

    if isinstance(json_obj, list):
        # Iterate over elements in the list
        for i, item in enumerate(json_obj):
            is_last_item = i == len(json_obj) - 1
            lines.extend(json_to_tree(item, next_prefix, is_last_item))
    elif isinstance(json_obj, dict):
        # Extract code, length, name, and value
        code = json_obj.get("code", "")
        length = json_obj.get("length", "")
        name = json_obj.get("name", "")
        value = json_obj.get("value", "")
        value_hex = json_obj.get("value_hex", "")
        avp_hex = json_obj.get("avp_hex", "")

        # Format the current row
        if isinstance(value, list):
            # If the value is nested, display the current row and process the nested values
            lines.append(f"{prefix}{connector}({code}, {length}), {name}")
            for i, sub_value in enumerate(value):
                is_last_sub_item = i == len(value) - 1
                lines.extend(json_to_tree(sub_value, next_prefix, is_last_sub_item))
        else:
            # If the value is not nested, display it on the same row
            lines.append(f"{prefix}{connector}({code}, {length}), {name}, {value}, {value_hex}")

    return lines


def print_json_tree(json_data):
    """
    Print a JSON object as a tree-like structure.

    Args:
        json_data: JSON object (can be a string or parsed dict/list).
    """
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        json_obj = json.loads(json_data)
    else:
        json_obj = json_data

    # Convert to tree and print
    tree_lines = json_to_tree(json_obj)
    for line in tree_lines:
        print(line)


if __name__ == "__main__":
    hexs = [
        '010002ecc000011001000016efebb99493c4269e000001074000002c63302d3137322d32352d33372d332d6767736e3937313b313339373130373030343b3735000001026000000c01000016000001084000001e63302d3137322d32352d33372d332d6767736e393731000000000128400000126f63732e6f63612e677000000000011b60000015753163636e312e6f63612e6770000000000001a06000000c000000010000019f6000000c000000000000042480000010000000c10001000100000017c000000e000028af69000000000001166000000c00000002000001bb60000028000001c26000000c00000000000001bc60000014353936363936333130333634000001bb6000002c000001c26000000c00000001000001bc6000001733343030313937303237343735303800000003fcc000000d000028af35000000000003fdc0000010000028af00000001000000086000000cac1aa10d00000403c0000010000028af0000000000000015e000000d000028af010000000000040880000010000028af000003e8000001ca6000002c000001cb2000000c00000000000001cc2000001833353832343030333232343337333438000003f8c0000058000028af00000404c0000010000028af0000000600000203c0000010000028af0083d60000000204c0000010000028af003d86000000040ac000001c000028af0000041680000010000028af0000000100000406c0000010000028af0000000100000012e0000011000028af333430303100000000000006e0000010000028afc1fba4a10000001e600000116f637370726f646770000000000003e8c0000010000028af00000000000001f5c0000012000028af0001c1fba4830000000003fec0000020000028af000001f7c0000014000028af34363438373132300000038dc0000017000028af3334303031666666656666000000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000003',
        '01000328c000011000000004efebb99393c4269d000001074000002c63302d3137322d32352d33372d332d6767736e3937313b313339373130373030343b3734000001084000001e63302d3137322d32352d33372d332d6767736e393731000000000128400000126f63732e6f63612e677000000000011b40000015753163636e312e6f63612e6770000000000001254000000e753163636e310000000001024000000c00000004000001a04000000c000000030000019f4000000c00000002000001cd40000018382e333232353140336770702e6f7267000000374000000cd6f7d59d000001164000000c00000002000001274000000c00000001000001bb40000028000001c24000000c00000000000001bc40000014353936363936333130333634000001bb4000002c000001c24000000c00000001000001bc4000001733343030313937303237343735303800000001c840000068000001be40000038000001a54000001000000000000072270000019c400000100000000000000a650000019e4000001000000000000067c2000001b74000000c000000c7000001b04000000c000000c700000368c0000010000028af00000002000001ca40000024000001cb4000000c00000000000001cc40000010532804302234378400000369c000014c000028af0000036ac0000140000028af00000002c0000010000028af02c5528000000003c0000010000028af00000000000004cbc0000012000028af0001ac1aa10c000000000005c0000025000028af39392d30623931316637333936623666653734383134303538000000000004ccc0000012000028af0001c1fba4a100000000034fc0000012000028af0001c1fba483000000000008c0000012000028af33343030313900000000000ac000000d000028af350000000000000bc000000d000028afff0000000000000cc000000d000028af300000000000000dc0000010000028af3030303000000012c0000011000028af333430303100000000000017c000000e000028af6900000000000016c0000014000028af0043f010ffffffff00000015c000000d000028af010000000000001e400000116f637370726f646770000000',
        '010000c44000011000000004efebb99393c4269d000001074000002c63302d3137322d32352d33372d332d6767736e3937313b313339373130373030343b37340000010c4000000c000007d1000001084000000e753163636e3100000000012840000015753163636e312e6f63612e6770000000000001024000000c00000004000001a04000000c000000030000019f4000000c00000002000001c84000002c0000010c4000000c000007d1000001b04000000c000000c7000001b74000000c000000c7',
        '0100020040000110010000163000006a93c426a60000010c4000000c000007d10000010840000016753173647031622e6f63612e6770000000000128400000157531736470312e6f63612e6770000000000001074000002c63302d3137322d32352d33372d332d6767736e3937313b313339373130373030343b3738000001026000000c01000016000001a06000000c000000010000019f6000000c0000000000000412c0000010000028afd6f92620000003e9c0000030000028af000003edc0000012000028af3130303032300000000003fcc000000d000028af35000000000003f8c0000068000028af00000404c0000010000028af000000060000040a8000001c000028af0000041680000010000028af00000001000003fcc000000d000028af3500000000000204c0000010000028af003d860000000203c0000010000028af0083d6000000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000001000003ffc0000010000028af00000000000003eec0000010000028af00000000000003eec0000010000028af00000002000003eec0000010000028af00000004000003eec0000010000028af0000000d000003eec0000010000028af00000019000003eec0000010000028af00000011000003eec0000010000028af00000001',
    ]
    print('----------------------')
    print('pydiameter2json')
    for hex in hexs:
        if hex.startswith("0x"):
            hex = hex[2:]

        # Decode the hex string to bytes
        diameter_bytes = bytes.fromhex(hex)
        
        # Create a Diameter message from the bytes
        message = Message.from_bytes(diameter_bytes)
        
        # Convert the message to JSON
        json_result = message_to_json(message)
        print('----------------------')
        print('Message to tree view:')
        print_json_tree(json_result)
        print('\r\n'*2)

        print('----------------------')
        print('Message to json view:')
        json_result = json.dumps(json_result, indent=4)
        print(json_result)

    avp_hex = '00000369c000014c000028af0000036ac0000140000028af00000002c0000010000028af02c5528000000003c0000010000028af00000000000004cbc0000012000028af0001ac1aa10c000000000005c0000025000028af39392d30623931316637333936623666653734383134303538000000000004ccc0000012000028af0001c1fba4a100000000034fc0000012000028af0001c1fba483000000000008c0000012000028af33343030313900000000000ac000000d000028af350000000000000bc000000d000028afff0000000000000cc000000d000028af300000000000000dc0000010000028af3030303000000012c0000011000028af333430303100000000000017c000000e000028af6900000000000016c0000014000028af0043f010ffffffff00000015c000000d000028af010000000000001e400000116f637370726f646770000000'
    if avp_hex.startswith("0x"):
        avp_hex = avp_hex[2:]
    # Decode the hex string to bytes
    avp_bytes = bytes.fromhex(avp_hex)
    # Create an AVP object from the bytes
    avp = Avp.from_bytes(avp_bytes)
    # Convert the AVP to JSON
    json_result = avp_to_json(avp)
    print('----------------------')
    print('AVP to tree view:')
    print_json_tree(json_result)
    print('\r\n'*2)
    print('----------------------')
    print('AVP to json view:')
    json_result = json.dumps(json_result, indent=4)
    print(json_result)