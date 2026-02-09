"""
Tests for utils/card_detector.py - the REAL CardDetector and CardType.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.card_detector import CardDetector, CardType


class TestCardType(unittest.TestCase):

    def test_enum_values(self):
        self.assertEqual(CardType.UNKNOWN.value, 0)
        self.assertEqual(CardType.SJA2.value, 1)
        self.assertEqual(CardType.SJA5.value, 2)
        self.assertEqual(CardType.SJS1.value, 3)

    def test_enum_names(self):
        self.assertEqual(CardType.SJA5.name, "SJA5")
        self.assertEqual(CardType.SJS1.name, "SJS1")


class TestCardDetectorDetectType(unittest.TestCase):

    # Real ATR patterns from card_detector module
    SJA2_ATR = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x4C, 0x75, 0x30, 0x34, 0x05, 0x4B, 0xA9]

    SJA5_ATR_9FV = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                    0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x35, 0x02, 0x59, 0xC4]

    SJA5_ATR_SLM17 = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                      0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x34, 0x02, 0x51, 0xC4]

    SJA5_ATR_3FJ = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0xC7, 0x80, 0x31, 0xE0, 0x73,
                    0xFE, 0x21, 0x1B, 0x64, 0x10, 0x38, 0x0A, 0x00, 0x74, 0x02, 0x59, 0xC4]

    SJS1_ATR = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x31, 0x02, 0x65, 0xF8]

    def test_detect_sja2(self):
        self.assertEqual(CardDetector.detect_card_type(self.SJA2_ATR), CardType.SJA2)

    def test_detect_sja5_9fv(self):
        self.assertEqual(CardDetector.detect_card_type(self.SJA5_ATR_9FV), CardType.SJA5)

    def test_detect_sja5_slm17(self):
        self.assertEqual(CardDetector.detect_card_type(self.SJA5_ATR_SLM17), CardType.SJA5)

    def test_detect_sja5_3fj(self):
        self.assertEqual(CardDetector.detect_card_type(self.SJA5_ATR_3FJ), CardType.SJA5)

    def test_detect_sjs1(self):
        self.assertEqual(CardDetector.detect_card_type(self.SJS1_ATR), CardType.SJS1)

    def test_detect_unknown(self):
        self.assertEqual(CardDetector.detect_card_type([0xFF] * 20), CardType.UNKNOWN)

    def test_detect_empty(self):
        self.assertEqual(CardDetector.detect_card_type([]), CardType.UNKNOWN)

    def test_detect_none(self):
        self.assertEqual(CardDetector.detect_card_type(None), CardType.UNKNOWN)

    def test_detect_too_short(self):
        self.assertEqual(CardDetector.detect_card_type([0x3B, 0x9F]), CardType.UNKNOWN)


class TestAtrMatches(unittest.TestCase):

    def test_match_full(self):
        pattern = [0x3B, 0x9F, 0x96]
        atr = [0x3B, 0x9F, 0x96, 0x80]
        self.assertTrue(CardDetector._atr_matches(atr, pattern))

    def test_no_match(self):
        pattern = [0x3B, 0x9F, 0x96]
        atr = [0x3B, 0x9F, 0x00, 0x80]
        self.assertFalse(CardDetector._atr_matches(atr, pattern))

    def test_atr_too_short(self):
        pattern = [0x3B, 0x9F, 0x96, 0x80, 0x1F]
        atr = [0x3B, 0x9F]
        self.assertFalse(CardDetector._atr_matches(atr, pattern))

    def test_match_with_explicit_length(self):
        pattern = [0x3B, 0x9F, 0x96, 0x80]
        atr = [0x3B, 0x9F, 0x96, 0x80, 0xFF]
        self.assertTrue(CardDetector._atr_matches(atr, pattern, 3))

    def test_exact_length_match(self):
        pattern = [0x3B, 0x9F]
        atr = [0x3B, 0x9F]
        self.assertTrue(CardDetector._atr_matches(atr, pattern))


class TestGetCardTypeName(unittest.TestCase):

    def test_sja2_name(self):
        self.assertEqual(CardDetector.get_card_type_name(CardType.SJA2), "sysmoISIM-SJA2")

    def test_sja5_name(self):
        self.assertEqual(CardDetector.get_card_type_name(CardType.SJA5), "sysmoISIM-SJA5")

    def test_sjs1_name(self):
        self.assertEqual(CardDetector.get_card_type_name(CardType.SJS1), "sysmoUSIM-SJS1")

    def test_unknown_name(self):
        self.assertEqual(CardDetector.get_card_type_name(CardType.UNKNOWN), "Unknown")


class TestAtrToString(unittest.TestCase):

    def test_normal_atr(self):
        self.assertEqual(CardDetector.atr_to_string([0x3B, 0x9F, 0x96, 0x80]), "3B 9F 96 80")

    def test_empty_atr(self):
        self.assertEqual(CardDetector.atr_to_string([]), "No ATR")

    def test_none_atr(self):
        self.assertEqual(CardDetector.atr_to_string(None), "No ATR")

    def test_single_byte(self):
        self.assertEqual(CardDetector.atr_to_string([0x00]), "00")


class TestCreateCardObject(unittest.TestCase):

    @patch('utils.card_detector.Sysmo_isim_sja5')
    def test_create_sja5_auto(self, mock_sja5_cls):
        mock_card = Mock()
        mock_sja5_cls.return_value = mock_card

        card_type, card = CardDetector.create_card_object(atr=None)
        self.assertEqual(card_type, CardType.SJA5)
        self.assertEqual(card, mock_card)

    @patch('utils.card_detector.Sysmo_isim_sja5', side_effect=Exception("fail"))
    @patch('utils.card_detector.Sysmo_isim_sja2')
    def test_create_sja2_fallback(self, mock_sja2_cls, mock_sja5_cls):
        mock_card = Mock()
        mock_sja2_cls.return_value = mock_card

        card_type, card = CardDetector.create_card_object(atr=None)
        self.assertEqual(card_type, CardType.SJA2)
        self.assertEqual(card, mock_card)

    @patch('utils.card_detector.Sysmo_isim_sja5', side_effect=Exception("fail"))
    @patch('utils.card_detector.Sysmo_isim_sja2', side_effect=Exception("fail"))
    @patch('utils.card_detector.Sysmo_usim_sjs1')
    def test_create_sjs1_fallback(self, mock_sjs1_cls, mock_sja2_cls, mock_sja5_cls):
        mock_card = Mock()
        mock_sjs1_cls.return_value = mock_card

        card_type, card = CardDetector.create_card_object(atr=None)
        self.assertEqual(card_type, CardType.SJS1)
        self.assertEqual(card, mock_card)

    @patch('utils.card_detector.Sysmo_isim_sja5', side_effect=Exception("fail"))
    @patch('utils.card_detector.Sysmo_isim_sja2', side_effect=Exception("fail"))
    @patch('utils.card_detector.Sysmo_usim_sjs1', side_effect=Exception("fail"))
    def test_create_no_card(self, mock_sjs1, mock_sja2, mock_sja5):
        card_type, card = CardDetector.create_card_object(atr=None)
        self.assertEqual(card_type, CardType.UNKNOWN)
        self.assertIsNone(card)

    @patch('utils.card_detector.Sysmo_isim_sja5')
    def test_create_with_sja5_atr(self, mock_sja5_cls):
        mock_card = Mock()
        mock_sja5_cls.return_value = mock_card

        atr = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
               0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x35, 0x02, 0x59, 0xC4]

        card_type, card = CardDetector.create_card_object(atr=atr)
        self.assertEqual(card_type, CardType.SJA5)

    def test_create_with_unknown_atr(self):
        atr = [0xFF] * 20
        card_type, card = CardDetector.create_card_object(atr=atr)
        self.assertEqual(card_type, CardType.UNKNOWN)
        self.assertIsNone(card)


class TestCardDetectorClassAttributes(unittest.TestCase):

    def test_sja2_atr_prefix_length(self):
        self.assertEqual(len(CardDetector.SJA2_ATR_PREFIX), 16)

    def test_sja5_atr_9fv_length(self):
        self.assertEqual(len(CardDetector.SJA5_ATR_9FV), 19)

    def test_sjs1_atr_length(self):
        self.assertEqual(len(CardDetector.SJS1_ATR), 19)

    def test_sja5_variants_differ(self):
        self.assertNotEqual(CardDetector.SJA5_ATR_9FV, CardDetector.SJA5_ATR_SLM17)
        self.assertNotEqual(CardDetector.SJA5_ATR_9FV, CardDetector.SJA5_ATR_3FJ)


if __name__ == '__main__':
    unittest.main()
