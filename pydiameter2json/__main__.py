from .main import avp_to_json, message_to_json, print_json_tree
from diameter.message import Message, Avp
import json
if __name__ == "__main__":
    import sys
    import typer

    app = typer.Typer()

    # convert avp hex to json
    @app.command()
    def avp2json(avp_hex: str):
        """
        Convert a Diameter AVP in hex format to JSON format.
        
        Args:
            avp_hex (str): The Diameter AVP in hex format.
        
        Returns:
            str: The Diameter AVP in JSON format.
        """
        if avp_hex.startswith("0x"):
            avp_hex = avp_hex[2:]

        # Decode the hex string to bytes
        avp_bytes = bytes.fromhex(avp_hex)
        
        # Create an AVP object from the bytes
        avp = Avp.from_bytes(avp_bytes)
        
        # Convert the AVP to JSON
        json_result = avp_to_json(avp)
        print_json_tree(json_result)
        print('\r\n'*2)
        json_result = json.dumps(json_result, indent=4)
        print(json_result)



    # convert diameter hex to json
    @app.command()
    def message2json(diameter_hex: str):
        """
        Convert a Diameter message in hex format to JSON format.
        
        Args:
            diameter_hex (str): The Diameter message in hex format.
        
        Returns:
            str: The Diameter message in JSON format.
        """
        if diameter_hex.startswith("0x"):
            diameter_hex = diameter_hex[2:]

        # Decode the hex string to bytes
        diameter_bytes = bytes.fromhex(diameter_hex)
        
        # Create a Diameter message from the bytes
        message = Message.from_bytes(diameter_bytes)
        
        # Convert the message to JSON
        json_result = message_to_json(message)
        print_json_tree(json_result)
        json_result = json.dumps(json_result, indent=4)
        print(json_result)


    app()
