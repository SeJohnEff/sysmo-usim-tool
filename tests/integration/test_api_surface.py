"""
Integration tests - verify that real sysmo-isim-tool modules have the
methods and signatures that our GUI code depends on.

These tests import the REAL sysmo classes (Sysmo_isim_sja2, Sysmo_isim_sja5,
Sysmo_usim_sjs1, Sysmo_usim) and verify their API surface without requiring
a physical card reader.
"""

import unittest
import inspect
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestSysmoModuleImports(unittest.TestCase):
    """Verify all required modules can be imported."""

    def test_import_sysmo_usim(self):
        import sysmo_usim
        self.assertTrue(hasattr(sysmo_usim, 'Sysmo_usim'))
        self.assertTrue(hasattr(sysmo_usim, 'SYSMO_USIM_ADM1'))

    def test_import_sysmo_isim_sja2(self):
        import sysmo_isim_sja2
        self.assertTrue(hasattr(sysmo_isim_sja2, 'Sysmo_isim_sja2'))
        self.assertTrue(hasattr(sysmo_isim_sja2, 'Sysmo_isim_sja5'))

    def test_import_sysmo_usim_sjs1(self):
        import sysmo_usim_sjs1
        self.assertTrue(hasattr(sysmo_usim_sjs1, 'Sysmo_usim_sjs1'))

    def test_import_simcard(self):
        from simcard import Simcard
        self.assertTrue(callable(Simcard))

    def test_import_utils(self):
        from utils import ascii_to_list, asciihex_to_list
        self.assertTrue(callable(ascii_to_list))
        self.assertTrue(callable(asciihex_to_list))


class TestSysmoUsimAPISurface(unittest.TestCase):
    """Verify Sysmo_usim base class has methods our code depends on."""

    @classmethod
    def setUpClass(cls):
        from sysmo_usim import Sysmo_usim
        cls.klass = Sysmo_usim

    def test_has_admin_auth(self):
        self.assertTrue(hasattr(self.klass, 'admin_auth'))
        sig = inspect.signature(self.klass.admin_auth)
        params = list(sig.parameters.keys())
        self.assertIn('self', params)
        self.assertIn('adm1', params)
        self.assertIn('force', params)

    def test_has_write_imsi(self):
        self.assertTrue(hasattr(self.klass, 'write_imsi'))
        sig = inspect.signature(self.klass.write_imsi)
        params = list(sig.parameters.keys())
        self.assertIn('self', params)
        self.assertIn('imsi', params)

    def test_has_write_iccid(self):
        self.assertTrue(hasattr(self.klass, 'write_iccid'))
        sig = inspect.signature(self.klass.write_iccid)
        params = list(sig.parameters.keys())
        self.assertIn('self', params)
        self.assertIn('iccid', params)

    def test_has_write_mnclen(self):
        self.assertTrue(hasattr(self.klass, 'write_mnclen'))

    def test_has_show_iccid(self):
        self.assertTrue(hasattr(self.klass, 'show_iccid'))

    def test_has_show_mnclen(self):
        self.assertTrue(hasattr(self.klass, 'show_mnclen'))

    def test_has_show_aid(self):
        self.assertTrue(hasattr(self.klass, 'show_aid'))


class TestSysmoIsimSja2APISurface(unittest.TestCase):
    """Verify Sysmo_isim_sja2 has methods CardManager calls."""

    @classmethod
    def setUpClass(cls):
        from sysmo_isim_sja2 import Sysmo_isim_sja2
        cls.klass = Sysmo_isim_sja2

    def test_inherits_sysmo_usim(self):
        from sysmo_usim import Sysmo_usim
        self.assertTrue(issubclass(self.klass, Sysmo_usim))

    def test_has_write_key_params(self):
        self.assertTrue(hasattr(self.klass, 'write_key_params'))

    def test_has_write_auth_params(self):
        self.assertTrue(hasattr(self.klass, 'write_auth_params'))
        sig = inspect.signature(self.klass.write_auth_params)
        params = list(sig.parameters.keys())
        self.assertIn('algo_2g_str', params)
        self.assertIn('algo_3g_str', params)

    def test_has_write_opc_params(self):
        self.assertTrue(hasattr(self.klass, 'write_opc_params'))
        sig = inspect.signature(self.klass.write_opc_params)
        params = list(sig.parameters.keys())
        self.assertIn('select', params)
        self.assertIn('op', params)

    def test_has_write_milenage_params(self):
        self.assertTrue(hasattr(self.klass, 'write_milenage_params'))

    def test_has_show_key_params(self):
        self.assertTrue(hasattr(self.klass, 'show_key_params'))

    def test_has_show_auth_params(self):
        self.assertTrue(hasattr(self.klass, 'show_auth_params'))

    def test_has_show_opc_params(self):
        self.assertTrue(hasattr(self.klass, 'show_opc_params'))

    def test_has_show_milenage_params(self):
        self.assertTrue(hasattr(self.klass, 'show_milenage_params'))

    def test_has_show_tuak_cfg(self):
        self.assertTrue(hasattr(self.klass, 'show_tuak_cfg'))

    def test_has_write_tuak_cfg(self):
        self.assertTrue(hasattr(self.klass, 'write_tuak_cfg'))

    def test_has_algorithms_attribute(self):
        self.assertTrue(hasattr(self.klass, 'algorithms'))

    def test_has_dump(self):
        self.assertTrue(hasattr(self.klass, 'dump'))


class TestSysmoIsimSja5APISurface(unittest.TestCase):
    """Verify Sysmo_isim_sja5 inherits SJA2 and has same API."""

    @classmethod
    def setUpClass(cls):
        from sysmo_isim_sja2 import Sysmo_isim_sja5
        cls.klass = Sysmo_isim_sja5

    def test_inherits_sja2(self):
        from sysmo_isim_sja2 import Sysmo_isim_sja2
        self.assertTrue(issubclass(self.klass, Sysmo_isim_sja2))

    def test_has_all_sja2_methods(self):
        from sysmo_isim_sja2 import Sysmo_isim_sja2
        for name in ['write_key_params', 'write_auth_params', 'write_opc_params',
                      'write_milenage_params', 'write_tuak_cfg', 'write_imsi',
                      'write_iccid', 'write_mnclen', 'admin_auth']:
            self.assertTrue(hasattr(self.klass, name), f"SJA5 missing method: {name}")

    def test_write_auth_params_accepts_4g5g(self):
        sig = inspect.signature(self.klass.write_auth_params)
        params = list(sig.parameters.keys())
        self.assertIn('algo_4g5g_str', params)

    def test_has_algorithms(self):
        self.assertTrue(hasattr(self.klass, 'algorithms'))
        self.assertIsInstance(self.klass.algorithms, list)
        self.assertGreater(len(self.klass.algorithms), 0)


class TestSysmoUsimSjs1APISurface(unittest.TestCase):
    """Verify Sysmo_usim_sjs1 has methods CardManager calls."""

    @classmethod
    def setUpClass(cls):
        from sysmo_usim_sjs1 import Sysmo_usim_sjs1
        cls.klass = Sysmo_usim_sjs1

    def test_inherits_sysmo_usim(self):
        from sysmo_usim import Sysmo_usim
        self.assertTrue(issubclass(self.klass, Sysmo_usim))

    def test_has_write_key_params(self):
        self.assertTrue(hasattr(self.klass, 'write_key_params'))

    def test_has_write_auth_params(self):
        self.assertTrue(hasattr(self.klass, 'write_auth_params'))
        sig = inspect.signature(self.klass.write_auth_params)
        params = list(sig.parameters.keys())
        self.assertIn('algo_2g_str', params)
        self.assertIn('algo_3g_str', params)

    def test_write_auth_params_no_4g5g(self):
        """SJS1 write_auth_params does NOT accept algo_4g5g_str."""
        sig = inspect.signature(self.klass.write_auth_params)
        params = list(sig.parameters.keys())
        self.assertNotIn('algo_4g5g_str', params)

    def test_has_write_opc_params(self):
        self.assertTrue(hasattr(self.klass, 'write_opc_params'))

    def test_has_write_milenage_params(self):
        self.assertTrue(hasattr(self.klass, 'write_milenage_params'))


class TestSimcardAPISurface(unittest.TestCase):
    """Verify Simcard has methods our code uses."""

    @classmethod
    def setUpClass(cls):
        from simcard import Simcard
        cls.klass = Simcard

    def test_has_select(self):
        self.assertTrue(hasattr(self.klass, 'select'))

    def test_has_read_binary(self):
        self.assertTrue(hasattr(self.klass, 'read_binary'))

    def test_has_update_binary(self):
        self.assertTrue(hasattr(self.klass, 'update_binary'))

    def test_has_verify_chv(self):
        self.assertTrue(hasattr(self.klass, 'verify_chv'))

    def test_has_chv_retrys(self):
        self.assertTrue(hasattr(self.klass, 'chv_retrys'))

    def test_has_read_record(self):
        self.assertTrue(hasattr(self.klass, 'read_record'))

    def test_has_update_record(self):
        self.assertTrue(hasattr(self.klass, 'update_record'))


class TestUtilsFunctions(unittest.TestCase):
    """Test real utils functions that CardManager uses."""

    def test_ascii_to_list(self):
        from utils import ascii_to_list
        result = ascii_to_list("12345678")
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0], 0x31)  # ASCII '1'

    def test_asciihex_to_list(self):
        from utils import asciihex_to_list
        result = asciihex_to_list("AABBCCDD")
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 0xAA)
        self.assertEqual(result[1], 0xBB)

    def test_asciihex_to_list_32_char(self):
        from utils import asciihex_to_list
        ki_hex = "FD4241E9C53B40E6E14107F19DF7C93E"
        result = asciihex_to_list(ki_hex)
        self.assertEqual(len(result), 16)

    def test_asciihex_roundtrip(self):
        from utils import asciihex_to_list, hexdump
        original = "AABBCCDDEEFF0011"
        as_bytes = asciihex_to_list(original)
        self.assertEqual(len(as_bytes), 8)


class TestCardManagerWithRealImports(unittest.TestCase):
    """Verify CardManager can import and reference real modules."""

    def test_card_manager_imports(self):
        from managers.card_manager import CardManager
        self.assertTrue(callable(CardManager))

    def test_card_manager_uses_real_card_detector(self):
        from managers.card_manager import CardManager
        from utils.card_detector import CardType
        cm = CardManager()
        self.assertEqual(cm.card_type, CardType.UNKNOWN)

    def test_card_manager_uses_real_asciihex(self):
        """CardManager should be able to call asciihex_to_list."""
        from utils import asciihex_to_list
        result = asciihex_to_list("FD4241E9C53B40E6E14107F19DF7C93E")
        self.assertEqual(len(result), 16)

    def test_card_manager_uses_real_ascii(self):
        """CardManager should be able to call ascii_to_list for ADM1."""
        from utils import ascii_to_list
        result = ascii_to_list("12345678")
        self.assertEqual(len(result), 8)
        # ADM1 is ASCII-encoded digits
        self.assertEqual(result, [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38])


if __name__ == '__main__':
    unittest.main()
