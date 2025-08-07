"""
Test suite for Diameter message parsing functionality.
"""
import pytest
import json
from pathlib import Path
from diameter.message import Message, Avp
from diameter.message import Message
from pydiameter2json.main import message_to_json, avp_to_json, json_to_tree


class TestDiameterMessageParsing:
    """Test cases for Diameter message parsing."""
    
    @pytest.fixture
    def sample_message_path(self):
        """Fixture for the sample Diameter message file."""
        return Path(__file__).parent / "gx.diameter.message.txt"
    
    @pytest.fixture
    def sample_avp_path(self):
        """Fixture for the sample AVP file."""
        return Path(__file__).parent / "gx.origin.host.txt"
    
    @pytest.fixture
    def sample_message_hex(self, sample_message_path):
        """Fixture providing the sample message as hex string."""
        return sample_message_path.read_text().strip()
    
    @pytest.fixture
    def sample_avp_hex(self, sample_avp_path):
        """Fixture providing the sample AVP as hex string."""
        return sample_avp_path.read_text().strip()
    
    def test_message_parsing_structure(self, sample_message_hex):
        """Test that message parsing returns valid JSON structure."""
        message_bytes = bytes.fromhex(sample_message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        assert isinstance(result, list)
        assert len(result) >= 3  # Should have at least 3 AVPs
        
        # Check required AVPs are present
        avp_codes = [avp["code"] for avp in result]
        assert 264 in avp_codes  # Origin-Host
        assert 296 in avp_codes  # Origin-Realm
        assert 278 in avp_codes  # Origin-State-Id
    
    def test_origin_host_avp(self, sample_message_hex):
        """Test Origin-Host AVP parsing."""
        message_bytes = bytes.fromhex(sample_message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        origin_host = next(avp for avp in result if avp["code"] == 264)
        assert origin_host["name"] == "Origin-Host"
        assert "ptsd-6.module-2.TPEPTS01.taiwanmobile.com" in str(origin_host["value"])
        assert origin_host["length"] == 49
    
    def test_origin_realm_avp(self, sample_message_hex):
        """Test Origin-Realm AVP parsing."""
        message_bytes = bytes.fromhex(sample_message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        origin_realm = next(avp for avp in result if avp["code"] == 296)
        assert origin_realm["name"] == "Origin-Realm"
        assert "taiwanmobile.com" in str(origin_realm["value"])
        assert origin_realm["length"] == 24
    
    def test_origin_state_id_avp(self, sample_message_hex):
        """Test Origin-State-Id AVP parsing."""
        message_bytes = bytes.fromhex(sample_message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        origin_state_id = next(avp for avp in result if avp["code"] == 278)
        assert origin_state_id["name"] == "Origin-State-Id"
        assert str(origin_state_id["value"]) == "1410781750"
        assert origin_state_id["length"] == 12
    
    def test_avp_parsing(self, sample_avp_hex):
        """Test individual AVP parsing."""
        avp_bytes = bytes.fromhex(sample_avp_hex)
        avp = Avp.from_bytes(avp_bytes)
        result = avp_to_json(avp)
        
        assert result["code"] == 264
        assert result["name"] == "Origin-Host"
        assert result["length"] == 49
        assert "ptsd-6.module-2.TPEPTS01.taiwanmobile.com" in str(result["value"])
    
    def test_message_command_code(self, sample_message_hex):
        """Test that message contains correct command code."""
        # First 4 bytes: 0100006c -> version 1, length 108
        # Next 4 bytes: 80000118 -> flags 0x80, command code 280 (Device-Watchdog-Request)
        assert sample_message_hex.startswith("0100006c80000118")
    
    def test_message_bytes_conversion(self, sample_message_hex):
        """Test that message can be converted from hex to bytes and parsed."""
        message_bytes = bytes.fromhex(sample_message_hex)
        message = Message.from_bytes(message_bytes)
        assert message is not None
        assert len(message.avps) >= 3

    def test_gx_avp_2_decoding(self):
        """Test decoding of gx.avp.2.txt - verify successful decoding without detail checks."""
        with open("tests/gx.avp.2.txt", "r") as f:
            avp_hex = f.read().strip()
        
        avp_bytes = bytes.fromhex(avp_hex)
        avp = Avp.from_bytes(avp_bytes)
        
        assert avp is not None
        assert avp.code is not None
        assert avp.length is not None

    def test_gx_message_2_decoding(self):
        """Test decoding of gx.message.2.txt - verify successful decoding without detail checks."""
        with open("tests/gx.message.2.txt", "r") as f:
            message_hex = f.read().strip()
        
        message_bytes = bytes.fromhex(message_hex)
        message = Message.from_bytes(message_bytes)
        
        assert message is not None
        assert hasattr(message, 'avps')
        assert len(message.avps) > 0


class TestGxSpecificParsing:
    """Test cases specific to Gx interface messages."""
    
    def test_gx_message_structure(self):
        """Test Gx message specific structure validation."""
        message_hex = "0100006c8000011800000000a3734495a375f3e40000010840000031707473642d362e6d6f64756c652d322e54504550545330312e74616977616e6d6f62696c652e636f6d000000000001284000001874616977616e6d6f62696c652e636f6d000001164000000c5416d236"
        
        message_bytes = bytes.fromhex(message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        # Verify all expected AVPs are present
        expected_avps = {264, 296, 278}  # Origin-Host, Origin-Realm, Origin-State-Id
        actual_avps = {avp["code"] for avp in result}
        assert expected_avps.issubset(actual_avps)
    
    def test_gx_avp_format(self):
        """Test Gx AVP format compliance."""
        message_hex = "0100006c8000011800000000a3734495a375f3e40000010840000031707473642d362e6d6f64756c652d322e54504550545330312e74616977616e6d6f62696c652e636f6d000000000001284000001874616977616e6d6f62696c652e636f6d000001164000000c5416d236"
        
        message_bytes = bytes.fromhex(message_hex)
        message = Message.from_bytes(message_bytes)
        result = message_to_json(message)
        
        for avp in result:
            assert "code" in avp
            assert "name" in avp
            assert "length" in avp
            assert "value" in avp
            assert "value_hex" in avp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])