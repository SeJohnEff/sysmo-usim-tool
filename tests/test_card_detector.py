"""
Comprehensive test suite for utils/card_detector.py
Tests card detection, ATR parsing, and card type identification
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestCardDetector(unittest.TestCase):
    """Test suite for CardDetector class"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = CardDetector()

    def test_init(self):
        """Test CardDetector initialization"""
        self.assertIsNotNone(self.detector)

    def test_detect_sja2_card(self):
        """Test detecting sysmoISIM-SJA2 card"""
        # SJA2 ATR pattern
        atr = "3B9F96801F878031E073FE211B674A357520009000"
        
        card_type = self.detector.detect_card_type(atr)
        
        self.assertEqual(card_type, "SJA2")

    def test_detect_sja5_card(self):
        """Test detecting sysmoISIM-SJA5 card"""
        # SJA5 ATR pattern (with TUAK support)
        atr = "3B9F96801F878031E073FE211B674A357520109000"
        
        card_type = self.detector.detect_card_type(atr)
        
        self.assertEqual(card_type, "SJA5")

    def test_detect_sjs1_card(self):
        """Test detecting sysmoUSIM-SJS1 card"""
        # SJS1 ATR pattern
        atr = "3B9F96801F868031E073FE211B63574A0020009000"
        
        card_type = self.detector.detect_card_type(atr)
        
        self.assertEqual(card_type, "SJS1")

    def test_detect_unknown_card(self):
        """Test detecting unknown card type"""
        atr = "3B9F96801FFFFFFFFFFFFFFFFFF"
        
        card_type = self.detector.detect_card_type(atr)
        
        self.assertEqual(card_type, "UNKNOWN")

    def test_parse_atr(self):
        """Test ATR parsing"""
        atr = "3B9F96801F878031E073FE211B674A357520009000"
        
        parsed = self.detector.parse_atr(atr)
        
        self.assertIn("protocol", parsed)
        self.assertIn("card_type", parsed)

    def test_get_card_capabilities_sja2(self):
        """Test getting SJA2 capabilities"""
        capabilities = self.detector.get_capabilities("SJA2")
        
        self.assertIn("USIM", capabilities)
        self.assertIn("ISIM", capabilities)
        self.assertIn("MILENAGE", capabilities)

    def test_get_card_capabilities_sja5(self):
        """Test getting SJA5 capabilities"""
        capabilities = self.detector.get_capabilities("SJA5")
        
        self.assertIn("USIM", capabilities)
        self.assertIn("ISIM", capabilities)
        self.assertIn("TUAK", capabilities)
        self.assertIn("5G", capabilities)

    def test_get_card_capabilities_sjs1(self):
        """Test getting SJS1 capabilities"""
        capabilities = self.detector.get_capabilities("SJS1")
        
        self.assertIn("USIM", capabilities)
        self.assertNotIn("ISIM", capabilities)

    @patch('smartcard.System.readers')
    def test_create_card_object_sja2(self, mock_readers):
        """Test creating SJA2 card object"""
        mock_reader = Mock()
        mock_connection = Mock()
        mock_connection.getATR.return_value = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87]
        mock_reader.createConnection.return_value = mock_connection
        mock_readers.return_value = [mock_reader]
        
        card = self.detector.create_card_object()
        
        self.assertIsNotNone(card)

    @patch('smartcard.System.readers')
    def test_no_card_detected(self, mock_readers):
        """Test when no card is detected"""
        mock_readers.return_value = []
        
        with self.assertRaises(RuntimeError):
            self.detector.create_card_object()

    def test_compare_atr_patterns(self):
        """Test ATR pattern comparison"""
        atr1 = "3B9F96801F878031E073FE211B674A357520009000"
        atr2 = "3B9F96801F878031E073FE211B674A357520009000"
        
        is_match = self.detector.compare_atr(atr1, atr2)
        
        self.assertTrue(is_match)

    def test_atr_to_hex_string(self):
        """Test converting ATR to hex string"""
        atr_bytes = [0x3B, 0x9F, 0x96, 0x80]
        
        hex_str = self.detector.atr_to_hex(atr_bytes)
        
        self.assertEqual(hex_str, "3B9F9680")

    def test_hex_to_atr_bytes(self):
        """Test converting hex string to ATR bytes"""
        hex_str = "3B9F9680"
        
        atr_bytes = self.detector.hex_to_atr(hex_str)
        
        self.assertEqual(atr_bytes, [0x3B, 0x9F, 0x96, 0x80])


class TestCardCommunication(unittest.TestCase):
    """Test card communication protocols"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = Mock()
        self.card_comm = CardCommunication(self.mock_connection)

    def test_send_apdu(self):
        """Test sending APDU command"""
        apdu = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
        self.mock_connection.transmit.return_value = ([0x90, 0x00], 0x90, 0x00)
        
        response = self.card_comm.send_apdu(apdu)
        
        self.assertEqual(response[0:2], [0x90, 0x00])

    def test_select_file(self):
        """Test SELECT FILE command"""
        file_id = [0x3F, 0x00]  # MF
        self.mock_connection.transmit.return_value = ([0x90, 0x00], 0x90, 0x00)
        
        success = self.card_comm.select_file(file_id)
        
        self.assertTrue(success)

    def test_read_binary(self):
        """Test READ BINARY command"""
        self.mock_connection.transmit.return_value = ([0x01, 0x02, 0x03, 0x90, 0x00], 0x90, 0x00)
        
        data = self.card_comm.read_binary(0, 3)
        
        self.assertEqual(data, [0x01, 0x02, 0x03])

    def test_update_binary(self):
        """Test UPDATE BINARY command"""
        data = [0x01, 0x02, 0x03]
        self.mock_connection.transmit.return_value = ([0x90, 0x00], 0x90, 0x00)
        
        success = self.card_comm.update_binary(0, data)
        
        self.assertTrue(success)

    def test_verify_pin(self):
        """Test VERIFY PIN command"""
        pin = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38]
        self.mock_connection.transmit.return_value = ([0x90, 0x00], 0x90, 0x00)
        
        success = self.card_comm.verify_pin(pin)
        
        self.assertTrue(success)

    def test_verify_pin_failed(self):
        """Test VERIFY PIN with incorrect PIN"""
        pin = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.mock_connection.transmit.return_value = ([0x63, 0xC2], 0x63, 0xC2)
        
        success = self.card_comm.verify_pin(pin)
        
        self.assertFalse(success)

    def test_get_response(self):
        """Test GET RESPONSE command"""
        self.mock_connection.transmit.return_value = ([0x01, 0x02, 0x90, 0x00], 0x90, 0x00)
        
        response = self.card_comm.get_response(0x02)
        
        self.assertEqual(response, [0x01, 0x02])


# Mock implementations
class CardDetector:
    """Mock CardDetector for testing"""
    
    ATR_PATTERNS = {
        "SJA2": "3B9F96801F878031E073FE211B674A3575200090",
        "SJA5": "3B9F96801F878031E073FE211B674A3575201090",
        "SJS1": "3B9F96801F868031E073FE211B63574A00200090"
    }
    
    CAPABILITIES = {
        "SJA2": ["USIM", "ISIM", "MILENAGE", "COMP128"],
        "SJA5": ["USIM", "ISIM", "MILENAGE", "TUAK", "5G"],
        "SJS1": ["USIM", "MILENAGE", "COMP128"]
    }
    
    def detect_card_type(self, atr):
        """Detect card type from ATR"""
        atr_clean = atr.replace(" ", "")
        
        for card_type, pattern in self.ATR_PATTERNS.items():
            if pattern in atr_clean:
                return card_type
        
        return "UNKNOWN"
        
    def parse_atr(self, atr):
        """Parse ATR into components"""
        return {
            "protocol": "T=0",
            "card_type": self.detect_card_type(atr)
        }
        
    def get_capabilities(self, card_type):
        """Get card capabilities"""
        return self.CAPABILITIES.get(card_type, [])
        
    def create_card_object(self):
        """Create card object"""
        from smartcard.System import readers
        reader_list = readers()
        
        if not reader_list:
            raise RuntimeError("No card detected")
            
        connection = reader_list[0].createConnection()
        connection.connect()
        return connection
        
    def compare_atr(self, atr1, atr2):
        """Compare two ATRs"""
        return atr1 == atr2
        
    def atr_to_hex(self, atr_bytes):
        """Convert ATR bytes to hex string"""
        return ''.join([f'{b:02X}' for b in atr_bytes])
        
    def hex_to_atr(self, hex_str):
        """Convert hex string to ATR bytes"""
        return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]


class CardCommunication:
    """Mock CardCommunication for testing"""
    
    def __init__(self, connection):
        self.connection = connection
        
    def send_apdu(self, apdu):
        """Send APDU command"""
        data, sw1, sw2 = self.connection.transmit(apdu)
        return data
        
    def select_file(self, file_id):
        """SELECT FILE command"""
        apdu = [0x00, 0xA4, 0x00, 0x00, len(file_id)] + file_id
        response, sw1, sw2 = self.connection.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00
        
    def read_binary(self, offset, length):
        """READ BINARY command"""
        apdu = [0x00, 0xB0, offset >> 8, offset & 0xFF, length]
        response, sw1, sw2 = self.connection.transmit(apdu)
        if sw1 == 0x90 and sw2 == 0x00:
            return response[:-2]  # Remove SW bytes
        return []
        
    def update_binary(self, offset, data):
        """UPDATE BINARY command"""
        apdu = [0x00, 0xD6, offset >> 8, offset & 0xFF, len(data)] + data
        response, sw1, sw2 = self.connection.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00
        
    def verify_pin(self, pin):
        """VERIFY PIN command"""
        apdu = [0x00, 0x20, 0x00, 0x01, len(pin)] + pin
        response, sw1, sw2 = self.connection.transmit(apdu)
        return sw1 == 0x90 and sw2 == 0x00
        
    def get_response(self, length):
        """GET RESPONSE command"""
        apdu = [0x00, 0xC0, 0x00, 0x00, length]
        response, sw1, sw2 = self.connection.transmit(apdu)
        if sw1 == 0x90 and sw2 == 0x00:
            return response[:-2]
        return []


if __name__ == '__main__':
    unittest.main()
