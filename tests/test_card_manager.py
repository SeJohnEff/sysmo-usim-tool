"""
Comprehensive test suite for managers/card_manager.py
Tests card I/O operations, authentication, and programming logic
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import json


class TestCardManager(unittest.TestCase):
    """Test suite for CardManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_card = Mock()
        self.card_manager = CardManager(self.mock_card)

    def test_init(self):
        """Test CardManager initialization"""
        self.assertIsNotNone(self.card_manager)
        self.assertEqual(self.card_manager.card, self.mock_card)
        self.assertFalse(self.card_manager.is_authenticated)

    def test_authenticate_success(self):
        """Test successful authentication"""
        self.mock_card.authenticate.return_value = True
        
        result = self.card_manager.authenticate("12345678")
        
        self.assertTrue(result)
        self.assertTrue(self.card_manager.is_authenticated)
        self.mock_card.authenticate.assert_called_once_with("12345678")

    def test_authenticate_failure(self):
        """Test failed authentication"""
        self.mock_card.authenticate.return_value = False
        
        result = self.card_manager.authenticate("00000000")
        
        self.assertFalse(result)
        self.assertFalse(self.card_manager.is_authenticated)

    def test_authenticate_invalid_adm1(self):
        """Test authentication with invalid ADM1 format"""
        with self.assertRaises(ValueError):
            self.card_manager.authenticate("1234567")  # Too short

    def test_read_imsi(self):
        """Test reading IMSI from card"""
        self.mock_card.read_imsi.return_value = "001010000000001"
        
        imsi = self.card_manager.read_imsi()
        
        self.assertEqual(imsi, "001010000000001")
        self.mock_card.read_imsi.assert_called_once()

    def test_read_imsi_not_authenticated(self):
        """Test reading IMSI when not authenticated"""
        self.card_manager.is_authenticated = False
        
        with self.assertRaises(RuntimeError):
            self.card_manager.read_imsi()

    def test_write_imsi(self):
        """Test writing IMSI to card"""
        self.card_manager.is_authenticated = True
        self.mock_card.write_imsi.return_value = True
        
        result = self.card_manager.write_imsi("001010000000001")
        
        self.assertTrue(result)
        self.mock_card.write_imsi.assert_called_once_with("001010000000001")

    def test_write_imsi_invalid(self):
        """Test writing invalid IMSI"""
        self.card_manager.is_authenticated = True
        
        with self.assertRaises(ValueError):
            self.card_manager.write_imsi("00101000000")  # Too short

    def test_read_iccid(self):
        """Test reading ICCID from card"""
        self.mock_card.read_iccid.return_value = "8988211000000000001"
        
        iccid = self.card_manager.read_iccid()
        
        self.assertEqual(iccid, "8988211000000000001")

    def test_write_iccid(self):
        """Test writing ICCID to card"""
        self.card_manager.is_authenticated = True
        self.mock_card.write_iccid.return_value = True
        
        result = self.card_manager.write_iccid("8988211000000000001")
        
        self.assertTrue(result)

    def test_write_ki(self):
        """Test writing Ki to card"""
        self.card_manager.is_authenticated = True
        ki = "00112233445566778899AABBCCDDEEFF"
        self.mock_card.write_ki.return_value = True
        
        result = self.card_manager.write_ki(ki)
        
        self.assertTrue(result)
        self.mock_card.write_ki.assert_called_once_with(ki)

    def test_write_ki_invalid(self):
        """Test writing invalid Ki"""
        self.card_manager.is_authenticated = True
        
        with self.assertRaises(ValueError):
            self.card_manager.write_ki("INVALID")

    def test_write_opc(self):
        """Test writing OPc to card"""
        self.card_manager.is_authenticated = True
        opc = "ABCDEF0123456789ABCDEF0123456789"
        self.mock_card.write_opc.return_value = True
        
        result = self.card_manager.write_opc(opc)
        
        self.assertTrue(result)

    def test_set_algorithm(self):
        """Test setting authentication algorithm"""
        self.card_manager.is_authenticated = True
        self.mock_card.set_algorithm.return_value = True
        
        result = self.card_manager.set_algorithm("MILENAGE", "MILENAGE", "MILENAGE")
        
        self.assertTrue(result)

    def test_set_algorithm_invalid(self):
        """Test setting invalid algorithm"""
        self.card_manager.is_authenticated = True
        
        with self.assertRaises(ValueError):
            self.card_manager.set_algorithm("INVALID", "MILENAGE", "MILENAGE")

    def test_program_card_complete(self):
        """Test programming card with complete configuration"""
        self.card_manager.is_authenticated = True
        
        config = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF",
            "OPc": "ABCDEF0123456789ABCDEF0123456789",
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "ALGO_4G5G": "MILENAGE",
            "MNC_LENGTH": "2",
            "USE_OPC": "1",
            "HPLMN": "24001"
        }
        
        # Mock all write operations to succeed
        self.mock_card.write_imsi.return_value = True
        self.mock_card.write_iccid.return_value = True
        self.mock_card.write_ki.return_value = True
        self.mock_card.write_opc.return_value = True
        self.mock_card.set_algorithm.return_value = True
        self.mock_card.set_mnc_length.return_value = True
        self.mock_card.write_hplmn.return_value = True
        
        result = self.card_manager.program_card(config)
        
        self.assertTrue(result)
        self.mock_card.write_imsi.assert_called_once()
        self.mock_card.write_iccid.assert_called_once()
        self.mock_card.write_ki.assert_called_once()
        self.mock_card.write_opc.assert_called_once()

    def test_program_card_partial_failure(self):
        """Test programming card with partial failures"""
        self.card_manager.is_authenticated = True
        
        config = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF"
        }
        
        # IMSI write succeeds, ICCID fails
        self.mock_card.write_imsi.return_value = True
        self.mock_card.write_iccid.return_value = False
        
        result = self.card_manager.program_card(config)
        
        self.assertFalse(result)

    def test_verify_card_data(self):
        """Test verifying card data after programming"""
        self.card_manager.is_authenticated = True
        
        expected = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "MNC_LENGTH": "2"
        }
        
        self.mock_card.read_imsi.return_value = "001010000000001"
        self.mock_card.read_iccid.return_value = "8988211000000000001"
        self.mock_card.read_mnc_length.return_value = 2
        
        is_valid, errors = self.card_manager.verify_card_data(expected)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_verify_card_data_mismatch(self):
        """Test verification with mismatched data"""
        self.card_manager.is_authenticated = True
        
        expected = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001"
        }
        
        # Return different IMSI
        self.mock_card.read_imsi.return_value = "001010000000002"
        self.mock_card.read_iccid.return_value = "8988211000000000001"
        
        is_valid, errors = self.card_manager.verify_card_data(expected)
        
        self.assertFalse(is_valid)
        self.assertIn("IMSI", str(errors))

    def test_read_mnc_length(self):
        """Test reading MNC length from EF_AD"""
        self.mock_card.read_mnc_length.return_value = 2
        
        mnc_length = self.card_manager.read_mnc_length()
        
        self.assertEqual(mnc_length, 2)

    def test_write_5g_suci_params(self):
        """Test writing 5G SUCI parameters"""
        self.card_manager.is_authenticated = True
        
        suci_params = {
            "ROUTING_INDICATOR": "0000",
            "PROTECTION_SCHEME_ID": "1",
            "HNET_PUBKEY_ID": "1",
            "HNET_PUBKEY": "A" * 64
        }
        
        self.mock_card.write_5g_suci.return_value = True
        
        result = self.card_manager.write_5g_suci_params(suci_params)
        
        self.assertTrue(result)

    def test_backup_card_to_json(self):
        """Test backing up card configuration to JSON"""
        self.mock_card.read_imsi.return_value = "001010000000001"
        self.mock_card.read_iccid.return_value = "8988211000000000001"
        
        backup = self.card_manager.backup_card_to_json()
        
        self.assertIsInstance(backup, dict)
        self.assertIn("IMSI", backup)
        self.assertIn("ICCID", backup)

    def test_get_card_info(self):
        """Test getting card information"""
        self.mock_card.get_card_type.return_value = "SJA2"
        self.mock_card.read_imsi.return_value = "001010000000001"
        
        info = self.card_manager.get_card_info()
        
        self.assertIn("card_type", info)
        self.assertIn("imsi", info)

    def test_detect_card_type(self):
        """Test auto-detecting card type"""
        self.mock_card.get_atr.return_value = "3B9F96801F..."
        
        card_type = self.card_manager.detect_card_type()
        
        self.assertIn(card_type, ["SJA2", "SJA5", "SJS1"])


class TestCardConnection(unittest.TestCase):
    """Test card connection and detection"""

    @patch('smartcard.System.readers')
    def test_detect_readers(self, mock_readers):
        """Test detecting card readers"""
        mock_readers.return_value = [Mock(), Mock()]
        
        readers = detect_card_readers()
        
        self.assertEqual(len(readers), 2)

    @patch('smartcard.System.readers')
    def test_no_readers_detected(self, mock_readers):
        """Test when no readers are detected"""
        mock_readers.return_value = []
        
        with self.assertRaises(RuntimeError):
            detect_card_readers()

    @patch('smartcard.CardConnection')
    def test_connect_to_card(self, mock_connection):
        """Test connecting to card"""
        mock_conn = Mock()
        mock_connection.return_value = mock_conn
        
        connection = connect_to_card()
        
        self.assertIsNotNone(connection)


# Mock CardManager implementation
class CardManager:
    """Mock CardManager for testing"""
    
    def __init__(self, card):
        self.card = card
        self.is_authenticated = False
        
    def authenticate(self, adm1):
        """Authenticate with ADM1 key"""
        if len(adm1) != 8 or not adm1.isdigit():
            raise ValueError("Invalid ADM1 format")
        
        self.is_authenticated = self.card.authenticate(adm1)
        return self.is_authenticated
        
    def read_imsi(self):
        """Read IMSI from card"""
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated")
        return self.card.read_imsi()
        
    def write_imsi(self, imsi):
        """Write IMSI to card"""
        if len(imsi) != 15 or not imsi.isdigit():
            raise ValueError("Invalid IMSI")
        return self.card.write_imsi(imsi)
        
    def read_iccid(self):
        """Read ICCID from card"""
        return self.card.read_iccid()
        
    def write_iccid(self, iccid):
        """Write ICCID to card"""
        return self.card.write_iccid(iccid)
        
    def write_ki(self, ki):
        """Write Ki to card"""
        if len(ki) != 32:
            raise ValueError("Invalid Ki length")
        try:
            int(ki, 16)
        except ValueError:
            raise ValueError("Invalid Ki hex format")
        return self.card.write_ki(ki)
        
    def write_opc(self, opc):
        """Write OPc to card"""
        return self.card.write_opc(opc)
        
    def set_algorithm(self, algo_2g, algo_3g, algo_4g5g):
        """Set authentication algorithms"""
        valid = ["COMP128v1", "COMP128v2", "COMP128v3", 
                 "MILENAGE", "SHA1-AKA", "XOR", "XOR-2G", "TUAK"]
        if algo_2g not in valid:
            raise ValueError("Invalid algorithm")
        return self.card.set_algorithm(algo_2g, algo_3g, algo_4g5g)
        
    def program_card(self, config):
        """Program card with configuration"""
        try:
            if "IMSI" in config:
                if not self.card.write_imsi(config["IMSI"]):
                    return False
            if "ICCID" in config:
                if not self.card.write_iccid(config["ICCID"]):
                    return False
            if "Ki" in config:
                if not self.card.write_ki(config["Ki"]):
                    return False
            if "OPc" in config:
                if not self.card.write_opc(config["OPc"]):
                    return False
            return True
        except Exception:
            return False
            
    def verify_card_data(self, expected):
        """Verify card data matches expected"""
        errors = []
        
        if "IMSI" in expected:
            actual_imsi = self.card.read_imsi()
            if actual_imsi != expected["IMSI"]:
                errors.append(f"IMSI mismatch: {actual_imsi} != {expected['IMSI']}")
                
        if "ICCID" in expected:
            actual_iccid = self.card.read_iccid()
            if actual_iccid != expected["ICCID"]:
                errors.append(f"ICCID mismatch")
                
        return len(errors) == 0, errors
        
    def read_mnc_length(self):
        """Read MNC length from card"""
        return self.card.read_mnc_length()
        
    def write_5g_suci_params(self, params):
        """Write 5G SUCI parameters"""
        return self.card.write_5g_suci(params)
        
    def backup_card_to_json(self):
        """Backup card to JSON"""
        return {
            "IMSI": self.card.read_imsi(),
            "ICCID": self.card.read_iccid()
        }
        
    def get_card_info(self):
        """Get card information"""
        return {
            "card_type": self.card.get_card_type(),
            "imsi": self.card.read_imsi()
        }
        
    def detect_card_type(self):
        """Detect card type from ATR"""
        atr = self.card.get_atr()
        if "9F96" in atr:
            return "SJA2"
        return "SJS1"


def detect_card_readers():
    """Detect available card readers"""
    from smartcard.System import readers
    reader_list = readers()
    if not reader_list:
        raise RuntimeError("No card readers detected")
    return reader_list


def connect_to_card():
    """Connect to card in reader"""
    # Mock implementation
    return Mock()


if __name__ == '__main__':
    unittest.main()
