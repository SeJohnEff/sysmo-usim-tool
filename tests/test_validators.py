"""
Tests for utils/validators.py - the REAL Validators class and DEFAULT_VALUES.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validators, ValidationError, DEFAULT_VALUES


class TestValidateIMSI(unittest.TestCase):

    def test_valid_15_digits(self):
        ok, err = Validators.validate_imsi("001010000000001")
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_valid_swedish_imsi(self):
        ok, _ = Validators.validate_imsi("240010000167270")
        self.assertTrue(ok)

    def test_empty(self):
        ok, err = Validators.validate_imsi("")
        self.assertFalse(ok)

    def test_none_string(self):
        ok, err = Validators.validate_imsi(None)
        self.assertFalse(ok)

    def test_too_short(self):
        ok, err = Validators.validate_imsi("24001000016727")
        self.assertFalse(ok)

    def test_too_long(self):
        ok, err = Validators.validate_imsi("2400100001672700")
        self.assertFalse(ok)

    def test_non_digit(self):
        ok, err = Validators.validate_imsi("24001000016727A")
        self.assertFalse(ok)


class TestValidateICCID(unittest.TestCase):

    def test_valid_19_digits(self):
        ok, _ = Validators.validate_iccid("8949440000001672706")
        self.assertTrue(ok)

    def test_valid_20_digits(self):
        ok, _ = Validators.validate_iccid("89494400000016727060")
        self.assertTrue(ok)

    def test_empty(self):
        ok, _ = Validators.validate_iccid("")
        self.assertFalse(ok)

    def test_too_short(self):
        ok, _ = Validators.validate_iccid("894944000000167270")
        self.assertFalse(ok)

    def test_non_digit(self):
        ok, _ = Validators.validate_iccid("8949440000001672A06")
        self.assertFalse(ok)


class TestValidateKi(unittest.TestCase):

    def test_valid_128bit(self):
        ok, _ = Validators.validate_ki("FD4241E9C53B40E6E14107F19DF7C93E")
        self.assertTrue(ok)

    def test_valid_256bit(self):
        ok, _ = Validators.validate_ki("A" * 64)
        self.assertTrue(ok)

    def test_empty(self):
        ok, _ = Validators.validate_ki("")
        self.assertFalse(ok)

    def test_wrong_length(self):
        ok, _ = Validators.validate_ki("ABCD")
        self.assertFalse(ok)

    def test_invalid_hex(self):
        ok, _ = Validators.validate_ki("G" * 32)
        self.assertFalse(ok)


class TestValidateOPc(unittest.TestCase):

    def test_valid_milenage(self):
        ok, _ = Validators.validate_opc("BC435ACD7123201B19A2D065B65EB5DA", "MILENAGE")
        self.assertTrue(ok)

    def test_valid_tuak(self):
        ok, _ = Validators.validate_opc("A" * 64, "TUAK")
        self.assertTrue(ok)

    def test_not_required_for_xor(self):
        ok, _ = Validators.validate_opc("", "XOR")
        self.assertTrue(ok)

    def test_required_for_milenage(self):
        ok, err = Validators.validate_opc("", "MILENAGE")
        self.assertFalse(ok)
        self.assertIn("required", err)

    def test_required_for_sha1aka(self):
        ok, _ = Validators.validate_opc("", "SHA1-AKA")
        self.assertFalse(ok)


class TestValidateAlgorithm(unittest.TestCase):

    def test_all_sja5_algorithms(self):
        for algo in Validators.ALGORITHMS_SJA5:
            ok, _ = Validators.validate_algorithm(algo, "SJA5")
            self.assertTrue(ok, f"Algorithm {algo} should be valid for SJA5")

    def test_tuak_not_valid_for_sja2(self):
        ok, _ = Validators.validate_algorithm("TUAK", "SJA2")
        self.assertFalse(ok)

    def test_empty(self):
        ok, _ = Validators.validate_algorithm("")
        self.assertFalse(ok)

    def test_invalid_name(self):
        ok, _ = Validators.validate_algorithm("INVALID")
        self.assertFalse(ok)

    def test_sjs1_algorithms(self):
        for algo in Validators.ALGORITHMS_SJS1:
            ok, _ = Validators.validate_algorithm(algo, "SJS1")
            self.assertTrue(ok)


class TestValidateMNCLength(unittest.TestCase):

    def test_valid_values(self):
        for v in ["1", "2", "3"]:
            ok, _ = Validators.validate_mnc_length(v)
            self.assertTrue(ok)

    def test_invalid_value(self):
        ok, _ = Validators.validate_mnc_length("4")
        self.assertFalse(ok)

    def test_empty(self):
        ok, _ = Validators.validate_mnc_length("")
        self.assertFalse(ok)

    def test_non_numeric(self):
        ok, _ = Validators.validate_mnc_length("abc")
        self.assertFalse(ok)


class TestValidateBoolean(unittest.TestCase):

    def test_valid_values(self):
        for v in ["0", "1", "true", "false", "yes", "no"]:
            ok, _ = Validators.validate_boolean(v, "test")
            self.assertTrue(ok, f"'{v}' should be valid")

    def test_empty_is_optional(self):
        ok, _ = Validators.validate_boolean("", "test")
        self.assertTrue(ok)

    def test_invalid(self):
        ok, _ = Validators.validate_boolean("maybe", "test")
        self.assertFalse(ok)


class TestValidateIntegerRange(unittest.TestCase):

    def test_in_range(self):
        ok, _ = Validators.validate_integer_range("5", "test", 1, 10)
        self.assertTrue(ok)

    def test_out_of_range(self):
        ok, _ = Validators.validate_integer_range("15", "test", 1, 10)
        self.assertFalse(ok)

    def test_empty_is_optional(self):
        ok, _ = Validators.validate_integer_range("", "test", 1, 10)
        self.assertTrue(ok)

    def test_non_numeric(self):
        ok, _ = Validators.validate_integer_range("abc", "test", 1, 10)
        self.assertFalse(ok)


class TestValidateMilenageParams(unittest.TestCase):

    def test_valid_r_param(self):
        ok, _ = Validators.validate_milenage_r("40", "R1")
        self.assertTrue(ok)

    def test_empty_r_is_optional(self):
        ok, _ = Validators.validate_milenage_r("", "R1")
        self.assertTrue(ok)

    def test_invalid_r_hex(self):
        ok, _ = Validators.validate_milenage_r("GG", "R1")
        self.assertFalse(ok)

    def test_valid_c_param(self):
        ok, _ = Validators.validate_milenage_c("0" * 32, "C1")
        self.assertTrue(ok)

    def test_empty_c_is_optional(self):
        ok, _ = Validators.validate_milenage_c("", "C1")
        self.assertTrue(ok)


class TestValidatePLMN(unittest.TestCase):

    def test_valid_5_digit(self):
        ok, _ = Validators.validate_plmn("24001")
        self.assertTrue(ok)

    def test_valid_6_digit(self):
        ok, _ = Validators.validate_plmn("310410")
        self.assertTrue(ok)

    def test_empty_is_optional(self):
        ok, _ = Validators.validate_plmn("")
        self.assertTrue(ok)

    def test_too_short(self):
        ok, _ = Validators.validate_plmn("2400")
        self.assertFalse(ok)

    def test_too_long(self):
        ok, _ = Validators.validate_plmn("2400100")
        self.assertFalse(ok)

    def test_non_digit(self):
        ok, _ = Validators.validate_plmn("24A01")
        self.assertFalse(ok)


class TestValidate5GParams(unittest.TestCase):

    def test_valid_routing_indicator(self):
        ok, _ = Validators.validate_routing_indicator("0000")
        self.assertTrue(ok)

    def test_valid_routing_hex(self):
        ok, _ = Validators.validate_routing_indicator("ABCD")
        self.assertTrue(ok)

    def test_invalid_routing_length(self):
        ok, _ = Validators.validate_routing_indicator("000")
        self.assertFalse(ok)

    def test_empty_routing_optional(self):
        ok, _ = Validators.validate_routing_indicator("")
        self.assertTrue(ok)

    def test_valid_hnet_pubkey(self):
        ok, _ = Validators.validate_hnet_pubkey("0e6e6e15b5d20b0aa382ef1b5277a780bfd061cd9b94cf7ee1200faaea5da53f")
        self.assertTrue(ok)

    def test_empty_hnet_optional(self):
        ok, _ = Validators.validate_hnet_pubkey("")
        self.assertTrue(ok)

    def test_invalid_hnet_length(self):
        ok, _ = Validators.validate_hnet_pubkey("ABCD")
        self.assertFalse(ok)

    def test_valid_protection_scheme(self):
        for v in ["0", "1", "2"]:
            ok, _ = Validators.validate_protection_scheme(v)
            self.assertTrue(ok)

    def test_invalid_protection_scheme(self):
        ok, _ = Validators.validate_protection_scheme("3")
        self.assertFalse(ok)


class TestValidateTUAKParams(unittest.TestCase):

    def test_valid_res_sizes(self):
        for v in ["32", "64", "128", "256"]:
            ok, _ = Validators.validate_tuak_res_size(v)
            self.assertTrue(ok)

    def test_invalid_res_size(self):
        ok, _ = Validators.validate_tuak_res_size("100")
        self.assertFalse(ok)

    def test_valid_mac_sizes(self):
        for v in ["64", "128", "256"]:
            ok, _ = Validators.validate_tuak_mac_size(v)
            self.assertTrue(ok)

    def test_valid_ckik_sizes(self):
        for v in ["128", "256"]:
            ok, _ = Validators.validate_tuak_ckik_size(v)
            self.assertTrue(ok)

    def test_invalid_ckik_size(self):
        ok, _ = Validators.validate_tuak_ckik_size("64")
        self.assertFalse(ok)


class TestValidateRow(unittest.TestCase):
    """Test full row validation."""

    def test_valid_complete_row(self):
        row = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF",
            "OPc": "ABCDEF0123456789ABCDEF0123456789",
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "MNC_LENGTH": "2",
        }
        errors = Validators.validate_row(row, 2, "SJA5")
        self.assertEqual(len(errors), 0)

    def test_invalid_row_multiple_errors(self):
        row = {
            "IMSI": "001010",
            "ICCID": "invalid",
            "Ki": "short",
            "ALGO_2G": "INVALID",
            "ALGO_3G": "MILENAGE",
            "MNC_LENGTH": "5",
        }
        errors = Validators.validate_row(row, 2, "SJA5")
        self.assertGreater(len(errors), 3)

    def test_validation_error_attributes(self):
        row = {"IMSI": "bad", "ICCID": "8988211000000000001", "Ki": "A" * 32,
               "ALGO_2G": "MILENAGE", "ALGO_3G": "MILENAGE", "MNC_LENGTH": "2"}
        errors = Validators.validate_row(row, 5, "SJA5")
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].row, 5)
        self.assertEqual(errors[0].column, "IMSI")

    def test_tuak_params_validated_for_sja5(self):
        row = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "A" * 32,
            "ALGO_2G": "MILENAGE",
            "ALGO_3G": "MILENAGE",
            "MNC_LENGTH": "2",
            "TUAK_RES_SIZE": "999",  # Invalid
        }
        errors = Validators.validate_row(row, 2, "SJA5")
        tuak_errors = [e for e in errors if "TUAK" in e.column]
        self.assertGreater(len(tuak_errors), 0)


class TestValidationError(unittest.TestCase):

    def test_attributes(self):
        err = ValidationError(5, "IMSI", "too short")
        self.assertEqual(err.row, 5)
        self.assertEqual(err.column, "IMSI")
        self.assertEqual(err.message, "too short")
        self.assertIn("Row 5", str(err))
        self.assertIn("IMSI", str(err))

    def test_is_exception(self):
        with self.assertRaises(ValidationError):
            raise ValidationError(1, "Ki", "invalid")


class TestDefaultValues(unittest.TestCase):

    def test_required_defaults_present(self):
        for key in ["USE_OPC", "ALGO_2G", "ALGO_3G", "ALGO_4G5G", "MNC_LENGTH"]:
            self.assertIn(key, DEFAULT_VALUES)

    def test_milenage_defaults(self):
        for i in range(1, 6):
            self.assertIn(f"MILENAGE_R{i}", DEFAULT_VALUES)
            self.assertIn(f"MILENAGE_C{i}", DEFAULT_VALUES)

    def test_5g_defaults(self):
        self.assertIn("ROUTING_INDICATOR", DEFAULT_VALUES)
        self.assertIn("PROTECTION_SCHEME_ID", DEFAULT_VALUES)
        self.assertIn("HNET_PUBKEY_ID", DEFAULT_VALUES)
        self.assertIn("HNET_PUBKEY", DEFAULT_VALUES)

    def test_default_algo_is_milenage(self):
        self.assertEqual(DEFAULT_VALUES["ALGO_2G"], "MILENAGE")
        self.assertEqual(DEFAULT_VALUES["ALGO_3G"], "MILENAGE")


if __name__ == '__main__':
    unittest.main()
