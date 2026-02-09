"""
Tests for managers/card_manager.py - the REAL CardManager class.
Mocks only the hardware (Simcard/pySim) layer.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.card_manager import (
    CardManager, CardError, CardNotPresentError,
    CardAuthenticationError, CardLockError,
)
from utils.card_detector import CardType


class TestCardManagerInit(unittest.TestCase):
    """Test CardManager initialization and state management."""

    def test_init_defaults(self):
        cm = CardManager()
        self.assertIsNone(cm.card)
        self.assertEqual(cm.card_type, CardType.UNKNOWN)
        self.assertFalse(cm.authenticated)
        self.assertIsNone(cm.atr)

    def test_disconnect(self):
        cm = CardManager()
        cm.card = Mock()
        cm.card_type = CardType.SJA5
        cm.authenticated = True
        cm.atr = [0x3B]

        cm.disconnect()

        self.assertIsNone(cm.card)
        self.assertEqual(cm.card_type, CardType.UNKNOWN)
        self.assertFalse(cm.authenticated)
        self.assertIsNone(cm.atr)


class TestCardManagerDetect(unittest.TestCase):
    """Test card detection."""

    @patch('managers.card_manager.CardDetector')
    def test_detect_card_success(self, mock_detector_cls):
        mock_card = Mock()
        mock_card.sim.card.get_ATR.return_value = [0x3B, 0x9F]
        mock_detector_cls.create_card_object.return_value = (CardType.SJA5, mock_card)
        mock_detector_cls.get_card_type_name.return_value = "sysmoISIM-SJA5"

        cm = CardManager()
        success, msg = cm.detect_card()

        self.assertTrue(success)
        self.assertIn("sysmoISIM-SJA5", msg)
        self.assertEqual(cm.card, mock_card)
        self.assertEqual(cm.card_type, CardType.SJA5)

    @patch('managers.card_manager.CardDetector')
    def test_detect_card_unknown(self, mock_detector_cls):
        mock_detector_cls.create_card_object.return_value = (CardType.UNKNOWN, None)

        cm = CardManager()
        success, msg = cm.detect_card()

        self.assertFalse(success)
        self.assertIn("unknown", msg.lower())

    @patch('managers.card_manager.CardDetector')
    def test_detect_card_exception(self, mock_detector_cls):
        mock_detector_cls.create_card_object.side_effect = Exception("No reader")

        cm = CardManager()
        success, msg = cm.detect_card()

        self.assertFalse(success)
        self.assertIn("No reader", msg)

    @patch('managers.card_manager.CardDetector')
    def test_detect_card_clears_previous_state(self, mock_detector_cls):
        mock_detector_cls.create_card_object.return_value = (CardType.UNKNOWN, None)

        cm = CardManager()
        cm.card = Mock()
        cm.authenticated = True

        cm.detect_card()

        self.assertFalse(cm.authenticated)


class TestCardManagerAuthenticate(unittest.TestCase):
    """Test ADM1 authentication."""

    def _make_cm(self):
        cm = CardManager()
        cm.card = Mock()
        cm.card_type = CardType.SJA5
        return cm

    def test_authenticate_success(self):
        cm = self._make_cm()
        cm.card.admin_auth.return_value = True

        success, msg = cm.authenticate("12345678")

        self.assertTrue(success)
        self.assertTrue(cm.authenticated)
        cm.card.admin_auth.assert_called_once()

    def test_authenticate_no_card(self):
        cm = CardManager()

        success, msg = cm.authenticate("12345678")

        self.assertFalse(success)
        self.assertIn("No card", msg)

    def test_authenticate_failure(self):
        cm = self._make_cm()
        cm.card.admin_auth.return_value = False
        cm.card.sim.chv_retrys.return_value = 2

        success, msg = cm.authenticate("00000000")

        self.assertFalse(success)
        self.assertFalse(cm.authenticated)

    def test_authenticate_card_locked(self):
        cm = self._make_cm()
        cm.card.admin_auth.return_value = False
        cm.card.sim.chv_retrys.return_value = 0

        success, msg = cm.authenticate("00000000")

        self.assertFalse(success)
        self.assertIn("locked", msg.lower())


class TestCardManagerProgramCard(unittest.TestCase):
    """Test card programming with real CardManager.program_card()."""

    def _make_authenticated_cm(self, card_type=CardType.SJA5):
        cm = CardManager()
        cm.card = Mock()
        cm.card_type = card_type
        cm.authenticated = True
        return cm

    def test_program_card_not_authenticated(self):
        cm = CardManager()
        success, msg = cm.program_card({"IMSI": "001010000000001"})
        self.assertFalse(success)
        self.assertIn("Not authenticated", msg)

    def test_program_imsi(self):
        cm = self._make_authenticated_cm()
        card_data = {"IMSI": "001010000000001"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_imsi.assert_called_once()
        # Verify the encoded IMSI was passed
        args = cm.card.write_imsi.call_args[0][0]
        self.assertIsInstance(args, list)
        self.assertEqual(args[0], 15)  # Length byte

    def test_program_iccid(self):
        cm = self._make_authenticated_cm()
        card_data = {"ICCID": "8949440000001672706"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_iccid.assert_called_once()

    def test_program_iccid_failure_ignored(self):
        """ICCID write failure should be silently ignored."""
        cm = self._make_authenticated_cm()
        cm.card.write_iccid.side_effect = Exception("Not supported")
        card_data = {"ICCID": "8949440000001672706"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)

    def test_program_ki(self):
        cm = self._make_authenticated_cm()
        card_data = {"Ki": "FD4241E9C53B40E6E14107F19DF7C93E"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_key_params.assert_called_once()
        args = cm.card.write_key_params.call_args[0][0]
        self.assertEqual(len(args), 16)  # 16 bytes

    def test_program_opc(self):
        cm = self._make_authenticated_cm()
        card_data = {"OPc": "BC435ACD7123201B19A2D065B65EB5DA", "USE_OPC": "1"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_opc_params.assert_called_once()
        args = cm.card.write_opc_params.call_args
        self.assertEqual(args[0][0], 1)  # use_opc = True

    def test_program_opc_use_op(self):
        cm = self._make_authenticated_cm()
        card_data = {"OPc": "BC435ACD7123201B19A2D065B65EB5DA", "USE_OPC": "0"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        args = cm.card.write_opc_params.call_args
        self.assertEqual(args[0][0], 0)  # use_opc = False

    def test_program_algorithms_sja5(self):
        cm = self._make_authenticated_cm()
        card_data = {
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "ALGO_4G5G": "MILENAGE",
        }

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_auth_params.assert_called_once_with("MILENAGE", "MILENAGE", "MILENAGE")

    def test_program_algorithms_no_4g5g(self):
        cm = self._make_authenticated_cm(CardType.SJS1)
        card_data = {"ALGO_2G": "MILENAGE", "ALGO_3G": "MILENAGE"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_auth_params.assert_called_once_with("MILENAGE", "MILENAGE")

    def test_program_mnc_length(self):
        cm = self._make_authenticated_cm()
        card_data = {"MNC_LENGTH": "2"}

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_mnclen.assert_called_once_with([2])

    def test_program_complete_card(self):
        """Test programming a complete card configuration."""
        cm = self._make_authenticated_cm()
        card_data = {
            "IMSI": "240010000167270",
            "ICCID": "8949440000001672706",
            "Ki": "FD4241E9C53B40E6E14107F19DF7C93E",
            "OPc": "BC435ACD7123201B19A2D065B65EB5DA",
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "ALGO_4G5G": "MILENAGE",
            "MNC_LENGTH": "2",
            "USE_OPC": "1",
            "HPLMN": "24001",
        }

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_imsi.assert_called_once()
        cm.card.write_iccid.assert_called_once()
        cm.card.write_key_params.assert_called_once()
        cm.card.write_opc_params.assert_called_once()
        cm.card.write_auth_params.assert_called_once()
        cm.card.write_mnclen.assert_called_once()
        # PLMN is also programmed via sim.select/update_binary
        self.assertTrue(cm.card.sim.select.called)

    def test_program_card_exception_returns_error(self):
        cm = self._make_authenticated_cm()
        cm.card.write_imsi.side_effect = Exception("Card error")
        card_data = {"IMSI": "001010000000001"}

        success, msg = cm.program_card(card_data)

        self.assertFalse(success)
        self.assertIn("Card error", msg)

    def test_program_5g_suci_sja5_only(self):
        """5G SUCI should only be programmed for SJA5 cards."""
        cm = self._make_authenticated_cm(CardType.SJA2)
        card_data = {
            "ROUTING_INDICATOR": "0000",
            "HNET_PUBKEY": "0e6e6e15b5d20b0aa382ef1b5277a780bfd061cd9b94cf7ee1200faaea5da53f",
        }

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        # For SJA2, 5G SUCI should NOT be written
        # The sim.select should not be called for DF.5GS
        select_calls = [str(c) for c in cm.card.sim.select.call_args_list]
        for call_str in select_calls:
            self.assertNotIn("[95, 192]", call_str)  # 0x5FC0 = DF.5GS

    def test_program_5g_suci_sja5(self):
        """5G SUCI should be programmed for SJA5 cards with HNET_PUBKEY."""
        cm = self._make_authenticated_cm(CardType.SJA5)
        card_data = {
            "ROUTING_INDICATOR": "0000",
            "PROTECTION_SCHEME_ID": "1",
            "HNET_PUBKEY_ID": "1",
            "HNET_PUBKEY": "0e6e6e15b5d20b0aa382ef1b5277a780bfd061cd9b94cf7ee1200faaea5da53f",
        }
        # Mock read_binary for UST
        mock_ust = Mock()
        mock_ust.apdu = [0x00] * 16
        cm.card.sim.read_binary.return_value = mock_ust

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        # Verify sim.select was called for DF.5GS files
        self.assertTrue(cm.card.sim.update_binary.called)

    def test_program_tuak_params(self):
        cm = self._make_authenticated_cm(CardType.SJA5)
        card_data = {
            "TUAK_RES_SIZE": "128",
            "TUAK_MAC_SIZE": "128",
            "TUAK_CKIK_SIZE": "128",
            "TUAK_NUM_KECCAK": "12",
        }

        success, msg = cm.program_card(card_data)

        self.assertTrue(success)
        cm.card.write_tuak_cfg.assert_called_once_with("128", "128", "128", "12")


class TestEncodeDecodeFunctions(unittest.TestCase):
    """Test IMSI/ICCID/PLMN encoding and decoding."""

    def setUp(self):
        self.cm = CardManager()

    def test_encode_imsi_15_digits(self):
        result = self.cm._encode_imsi("240010000167270")
        self.assertEqual(result[0], 15)  # length
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 9)  # 1 length byte + ceil(15/2) = 8 BCD bytes

    def test_encode_imsi_roundtrip(self):
        original = "240010000167270"
        encoded = self.cm._encode_imsi(original)
        decoded = self.cm._decode_imsi(encoded)
        self.assertEqual(decoded, original)

    def test_encode_imsi_all_zeros(self):
        original = "000000000000000"
        encoded = self.cm._encode_imsi(original)
        decoded = self.cm._decode_imsi(encoded)
        self.assertEqual(decoded, original)

    def test_decode_imsi_invalid(self):
        self.assertIsNone(self.cm._decode_imsi([]))
        self.assertIsNone(self.cm._decode_imsi([0]))

    def test_encode_iccid(self):
        result = self.cm._encode_iccid("8949440000001672706")
        self.assertIsInstance(result, list)
        # 19 digits -> 10 bytes (last nibble padded with F)
        self.assertEqual(len(result), 10)

    def test_encode_iccid_roundtrip(self):
        original = "89494400000016727060"  # 20-digit ICCID
        encoded = self.cm._encode_iccid(original)
        decoded = self.cm._decode_iccid(encoded)
        self.assertEqual(decoded, original)

    def test_decode_iccid_empty(self):
        self.assertIsNone(self.cm._decode_iccid([]))

    def test_encode_plmn_2digit_mnc(self):
        """Test PLMN encoding: "24001" (MCC=240, MNC=01)."""
        result = self.cm._encode_plmn("24001")
        self.assertEqual(result, [0x42, 0xF0, 0x10])

    def test_encode_plmn_3digit_mnc(self):
        """Test PLMN encoding: "310410" (MCC=310, MNC=410)."""
        result = self.cm._encode_plmn("310410")
        self.assertEqual(result, [0x13, 0x00, 0x14])

    def test_encode_plmn_invalid_length(self):
        with self.assertRaises(ValueError):
            self.cm._encode_plmn("240")

    def test_get_access_technology_flags_all(self):
        card_data = {"ALGO_2G": "MILENAGE", "ALGO_3G": "MILENAGE", "ALGO_4G5G": "TUAK"}
        flags = self.cm._get_access_technology_flags(card_data)
        self.assertEqual(len(flags), 2)
        flag_val = (flags[0] << 8) | flags[1]
        self.assertTrue(flag_val & 0x0080)  # GSM
        self.assertTrue(flag_val & 0x8000)  # UTRAN
        self.assertTrue(flag_val & 0x4000)  # E-UTRAN
        self.assertTrue(flag_val & 0x2000)  # NR (5G via TUAK)

    def test_get_access_technology_flags_2g_only(self):
        card_data = {"ALGO_2G": "COMP128v1"}
        flags = self.cm._get_access_technology_flags(card_data)
        flag_val = (flags[0] << 8) | flags[1]
        self.assertTrue(flag_val & 0x0080)  # GSM
        self.assertFalse(flag_val & 0x8000)  # No UTRAN
        self.assertFalse(flag_val & 0x4000)  # No E-UTRAN

    def test_get_access_technology_flags_empty(self):
        card_data = {}
        flags = self.cm._get_access_technology_flags(card_data)
        flag_val = (flags[0] << 8) | flags[1]
        self.assertEqual(flag_val, 0)


class TestCardManagerVerify(unittest.TestCase):
    """Test card verification."""

    def test_verify_not_authenticated(self):
        cm = CardManager()
        ok, mismatches = cm.verify_card({"IMSI": "001010000000001"})
        self.assertFalse(ok)

    def test_verify_matching(self):
        cm = CardManager()
        cm.authenticated = True
        cm.card = Mock()
        cm.card.sim.card.get_imsi.return_value = "001010000000001"
        cm.card.sim.card.get_ICCID.return_value = "8988211000000000001"
        cm.card_type = CardType.SJA5

        # Mock the EF_AD read
        mock_ad = Mock()
        mock_ad.apdu = [0x00, 0x00, 0x00, 0x02]
        cm.card.sim.read_binary.return_value = mock_ad

        ok, mismatches = cm.verify_card({
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
        })
        self.assertTrue(ok)
        self.assertEqual(len(mismatches), 0)

    def test_verify_imsi_mismatch(self):
        cm = CardManager()
        cm.authenticated = True
        cm.card = Mock()
        cm.card.sim.card.get_imsi.return_value = "001010000000002"
        cm.card.sim.card.get_ICCID.return_value = "8988211000000000001"
        cm.card_type = CardType.SJA5
        mock_ad = Mock()
        mock_ad.apdu = [0x00, 0x00, 0x00, 0x02]
        cm.card.sim.read_binary.return_value = mock_ad

        ok, mismatches = cm.verify_card({"IMSI": "001010000000001"})
        self.assertFalse(ok)
        self.assertIn("IMSI", mismatches[0])


class TestCardManagerReadData(unittest.TestCase):
    """Test reading card data."""

    def test_read_not_authenticated(self):
        cm = CardManager()
        self.assertIsNone(cm.read_card_data())

    def test_read_card_data_success(self):
        cm = CardManager()
        cm.authenticated = True
        cm.card = Mock()
        cm.card_type = CardType.SJA5
        cm.card.sim.card.get_imsi.return_value = "240010000167270"
        cm.card.sim.card.get_ICCID.return_value = "8949440000001672706"

        mock_ad = Mock()
        mock_ad.apdu = [0x00, 0x00, 0x00, 0x02]
        cm.card.sim.read_binary.return_value = mock_ad

        data = cm.read_card_data()

        self.assertIsNotNone(data)
        self.assertEqual(data['imsi'], "240010000167270")
        self.assertEqual(data['iccid'], "8949440000001672706")
        self.assertEqual(data['mnc_length'], 2)
        self.assertEqual(data['card_type'], 'SJA5')

    def test_read_card_data_partial_failure(self):
        cm = CardManager()
        cm.authenticated = True
        cm.card = Mock()
        cm.card_type = CardType.SJA5
        cm.card.sim.card.get_imsi.side_effect = Exception("Read error")
        cm.card.sim.card.get_ICCID.return_value = "8949440000001672706"
        cm.card.sim.read_binary.side_effect = Exception("EF_AD error")

        data = cm.read_card_data()

        self.assertIsNotNone(data)
        self.assertIsNone(data['imsi'])
        self.assertEqual(data['iccid'], "8949440000001672706")


class TestCardManagerGetRemainingAttempts(unittest.TestCase):

    def test_no_card(self):
        cm = CardManager()
        self.assertIsNone(cm.get_remaining_attempts())

    def test_with_card(self):
        cm = CardManager()
        cm.card = Mock()
        cm.card.sim.chv_retrys.return_value = 3

        result = cm.get_remaining_attempts()
        self.assertEqual(result, 3)


class TestCardExceptions(unittest.TestCase):
    """Test custom exception classes."""

    def test_card_error(self):
        with self.assertRaises(CardError):
            raise CardError("test")

    def test_card_not_present(self):
        with self.assertRaises(CardNotPresentError):
            raise CardNotPresentError("no card")

    def test_card_auth_error(self):
        err = CardAuthenticationError(2)
        self.assertEqual(err.remaining_attempts, 2)
        self.assertIn("2", str(err))

    def test_card_lock_error(self):
        with self.assertRaises(CardLockError):
            raise CardLockError("locked")


if __name__ == '__main__':
    unittest.main()
