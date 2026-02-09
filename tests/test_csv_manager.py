"""
Tests for managers/csv_manager.py - the REAL CSVManager class.
"""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.csv_manager import CSVManager


class TestCSVManagerInit(unittest.TestCase):

    def test_init(self):
        mgr = CSVManager()
        self.assertEqual(mgr.get_card_count(), 0)
        self.assertFalse(mgr.has_errors())

    def test_columns_defined(self):
        self.assertIn("IMSI", CSVManager.BASIC_COLUMNS)
        self.assertIn("ICCID", CSVManager.BASIC_COLUMNS)
        self.assertIn("Ki", CSVManager.BASIC_COLUMNS)
        self.assertIn("USE_OPC", CSVManager.ADVANCED_COLUMNS)


class TestCSVManagerLoadSave(unittest.TestCase):

    def setUp(self):
        self.mgr = CSVManager()
        self.tmpdir = tempfile.mkdtemp()

    def _write_csv(self, filename, content):
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_load_valid_csv(self):
        path = self._write_csv("test.csv",
            "IMSI,ICCID,Ki,OPc,ALGO_2G,ALGO_3G,ALGO_4G5G,MNC_LENGTH\n"
            "001010000000001,8988211000000000001,00112233445566778899AABBCCDDEEFF,"
            "ABCDEF0123456789ABCDEF0123456789,MILENAGE,MILENAGE,MILENAGE,2\n"
        )

        result = self.mgr.load_csv(path)

        self.assertTrue(result)
        self.assertEqual(self.mgr.get_card_count(), 1)
        card = self.mgr.get_card(0)
        self.assertEqual(card["IMSI"], "001010000000001")

    def test_load_csv_fills_defaults(self):
        path = self._write_csv("test.csv",
            "IMSI,ICCID,Ki,OPc,ALGO_2G,ALGO_3G,ALGO_4G5G,MNC_LENGTH\n"
            "001010000000001,8988211000000000001,00112233445566778899AABBCCDDEEFF,"
            "ABCDEF0123456789ABCDEF0123456789,MILENAGE,MILENAGE,MILENAGE,2\n"
        )
        self.mgr.load_csv(path)
        card = self.mgr.get_card(0)
        self.assertEqual(card["USE_OPC"], "1")  # default

    def test_load_csv_missing_columns(self):
        path = self._write_csv("bad.csv", "IMSI,ICCID\n001,899\n")
        result = self.mgr.load_csv(path)
        self.assertFalse(result)

    def test_load_nonexistent_file(self):
        result = self.mgr.load_csv("/nonexistent/path.csv")
        self.assertFalse(result)

    def test_save_csv(self):
        self.mgr.add_card({
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF",
        })

        path = os.path.join(self.tmpdir, "output.csv")
        result = self.mgr.save_csv(path, include_advanced=False)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

        # Verify we can reload it
        mgr2 = CSVManager()
        result2 = mgr2.load_csv(path)
        self.assertTrue(result2)
        self.assertEqual(mgr2.get_card_count(), 1)

    def test_save_csv_with_advanced(self):
        self.mgr.add_card({"IMSI": "001010000000001", "ICCID": "8988211000000000001",
                           "Ki": "A" * 32})
        path = os.path.join(self.tmpdir, "adv.csv")
        result = self.mgr.save_csv(path, include_advanced=True)
        self.assertTrue(result)

        with open(path) as f:
            header = f.readline()
        self.assertIn("USE_OPC", header)

    def test_load_card_parameters_txt(self):
        path = self._write_csv("params.txt",
            "Card #1:\n"
            "  ICCID: 8988211000000000001\n"
            "  IMSI: 001010000000001\n"
            "  Ki: 00112233445566778899AABBCCDDEEFF\n"
            "  OPc: ABCDEF0123456789ABCDEF0123456789\n"
            "  ADM1: 12345678\n"
            "\n"
            "Card #2:\n"
            "  ICCID: 8988211000000000002\n"
            "  IMSI: 001010000000002\n"
            "  Ki: 11223344556677889900AABBCCDDEEFF\n"
        )

        result = self.mgr.load_card_parameters_file(path)

        self.assertTrue(result)
        self.assertEqual(self.mgr.get_card_count(), 2)
        self.assertEqual(self.mgr.get_card(0)["IMSI"], "001010000000001")
        self.assertEqual(self.mgr.get_card(1)["IMSI"], "001010000000002")


class TestCSVManagerCardOperations(unittest.TestCase):

    def setUp(self):
        self.mgr = CSVManager()

    def test_add_card(self):
        self.mgr.add_card({"IMSI": "001010000000001"})
        self.assertEqual(self.mgr.get_card_count(), 1)

    def test_add_card_fills_defaults(self):
        self.mgr.add_card({"IMSI": "001010000000001"})
        card = self.mgr.get_card(0)
        self.assertEqual(card["ALGO_2G"], "MILENAGE")

    def test_remove_card(self):
        self.mgr.add_card({"IMSI": "001"})
        self.mgr.add_card({"IMSI": "002"})
        self.mgr.remove_card(0)
        self.assertEqual(self.mgr.get_card_count(), 1)

    def test_remove_card_invalid_index(self):
        self.mgr.remove_card(99)  # Should not crash
        self.assertEqual(self.mgr.get_card_count(), 0)

    def test_get_card_invalid_index(self):
        self.assertIsNone(self.mgr.get_card(0))
        self.assertIsNone(self.mgr.get_card(-1))

    def test_update_card(self):
        self.mgr.add_card({"IMSI": "001"})
        self.mgr.update_card(0, {"IMSI": "002"})
        self.assertEqual(self.mgr.get_card(0)["IMSI"], "002")

    def test_update_card_invalid_index(self):
        self.mgr.update_card(99, {"IMSI": "001"})  # Should not crash


class TestCSVManagerValidation(unittest.TestCase):

    def setUp(self):
        self.mgr = CSVManager()

    def test_validate_valid_cards(self):
        self.mgr.add_card({
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF",
            "OPc": "ABCDEF0123456789ABCDEF0123456789",
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "MNC_LENGTH": "2",
        })
        errors = self.mgr.validate_all()
        self.assertEqual(len(errors), 0)
        self.assertFalse(self.mgr.has_errors())

    def test_validate_invalid_imsi(self):
        self.mgr.add_card({"IMSI": "bad", "ICCID": "8988211000000000001", "Ki": "A" * 32,
                           "ALGO_2G": "MILENAGE", "ALGO_3G": "MILENAGE", "MNC_LENGTH": "2"})
        errors = self.mgr.validate_all()
        self.assertGreater(len(errors), 0)
        self.assertTrue(self.mgr.has_errors())

    def test_get_errors_for_row(self):
        self.mgr.add_card({"IMSI": "bad", "ICCID": "8988211000000000001", "Ki": "A" * 32,
                           "ALGO_2G": "MILENAGE", "ALGO_3G": "MILENAGE", "MNC_LENGTH": "2"})
        self.mgr.validate_all()
        row_errors = self.mgr.get_errors_for_row(0)
        self.assertGreater(len(row_errors), 0)


if __name__ == '__main__':
    unittest.main()
