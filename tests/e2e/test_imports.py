"""
E2E tests - verify the full import graph and module wiring
using subprocess.run to catch import errors and missing dependencies.
"""

import unittest
import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestModuleImports(unittest.TestCase):
    """Test that all modules can be imported without errors."""

    def _run_import(self, module_name, extra_path=None):
        """Run a Python import in a subprocess and return (returncode, stderr)."""
        path = extra_path or PROJECT_ROOT
        result = subprocess.run(
            [sys.executable, '-c', f'import sys; sys.path.insert(0, "{path}"); import {module_name}'],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode, result.stderr

    def test_import_managers_card_manager(self):
        rc, err = self._run_import('managers.card_manager')
        self.assertEqual(rc, 0, f"Failed to import managers.card_manager: {err}")

    def test_import_managers_csv_manager(self):
        rc, err = self._run_import('managers.csv_manager')
        self.assertEqual(rc, 0, f"Failed to import managers.csv_manager: {err}")

    def test_import_managers_backup_manager(self):
        rc, err = self._run_import('managers.backup_manager')
        self.assertEqual(rc, 0, f"Failed to import managers.backup_manager: {err}")

    def test_import_utils_validators(self):
        rc, err = self._run_import('utils.validators')
        self.assertEqual(rc, 0, f"Failed to import utils.validators: {err}")

    def test_import_utils_card_detector(self):
        rc, err = self._run_import('utils.card_detector')
        self.assertEqual(rc, 0, f"Failed to import utils.card_detector: {err}")

    def test_import_sysmo_usim(self):
        rc, err = self._run_import('sysmo_usim')
        self.assertEqual(rc, 0, f"Failed to import sysmo_usim: {err}")

    def test_import_sysmo_isim_sja2(self):
        rc, err = self._run_import('sysmo_isim_sja2')
        self.assertEqual(rc, 0, f"Failed to import sysmo_isim_sja2: {err}")

    def test_import_sysmo_usim_sjs1(self):
        rc, err = self._run_import('sysmo_usim_sjs1')
        self.assertEqual(rc, 0, f"Failed to import sysmo_usim_sjs1: {err}")

    def test_import_simcard(self):
        rc, err = self._run_import('simcard')
        self.assertEqual(rc, 0, f"Failed to import simcard: {err}")

    def test_import_utils_module(self):
        rc, err = self._run_import('utils')
        self.assertEqual(rc, 0, f"Failed to import utils: {err}")

    def test_import_theme(self):
        rc, err = self._run_import('theme')
        self.assertEqual(rc, 0, f"Failed to import theme: {err}")

    def test_import_pytlv(self):
        """pytlv is required at runtime for USIM TLV parsing in simcard.py."""
        rc, err = self._run_import('pytlv.TLV')
        self.assertEqual(rc, 0, f"Failed to import pytlv.TLV (install with: pip install pytlv): {err}")


class TestCardManagerEndToEnd(unittest.TestCase):
    """Test CardManager construction and method availability via subprocess."""

    def test_card_manager_init(self):
        code = """
import sys
sys.path.insert(0, "{root}")
from managers.card_manager import CardManager
cm = CardManager()
assert cm.card is None
assert cm.authenticated == False
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"CardManager init failed: {result.stderr}")
        self.assertIn("OK", result.stdout)

    def test_card_manager_has_program_card(self):
        code = """
import sys
sys.path.insert(0, "{root}")
from managers.card_manager import CardManager
cm = CardManager()
assert hasattr(cm, 'program_card')
assert hasattr(cm, 'detect_card')
assert hasattr(cm, 'authenticate')
assert hasattr(cm, 'verify_card')
assert hasattr(cm, 'read_card_data')
assert hasattr(cm, 'disconnect')
assert hasattr(cm, '_encode_imsi')
assert hasattr(cm, '_decode_imsi')
assert hasattr(cm, '_encode_iccid')
assert hasattr(cm, '_decode_iccid')
assert hasattr(cm, '_encode_plmn')
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Method check failed: {result.stderr}")

    def test_csv_manager_roundtrip(self):
        code = """
import sys, tempfile, os
sys.path.insert(0, "{root}")
from managers.csv_manager import CSVManager

mgr = CSVManager()
mgr.add_card({{
    "IMSI": "001010000000001",
    "ICCID": "8988211000000000001",
    "Ki": "FD4241E9C53B40E6E14107F19DF7C93E",
}})

tmpdir = tempfile.mkdtemp()
path = os.path.join(tmpdir, "test.csv")
assert mgr.save_csv(path, include_advanced=False)

mgr2 = CSVManager()
assert mgr2.load_csv(path)
assert mgr2.get_card_count() == 1
card = mgr2.get_card(0)
assert card["IMSI"] == "001010000000001"
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"CSV roundtrip failed: {result.stderr}")

    def test_validators_validate_row(self):
        code = """
import sys
sys.path.insert(0, "{root}")
from utils.validators import Validators

row = {{
    "IMSI": "001010000000001",
    "ICCID": "8988211000000000001",
    "Ki": "FD4241E9C53B40E6E14107F19DF7C93E",
    "OPc": "BC435ACD7123201B19A2D065B65EB5DA",
    "ALGO_2G": "MILENAGE",
    "ALGO_3G": "MILENAGE",
    "MNC_LENGTH": "2",
}}
errors = Validators.validate_row(row, 0, "SJA5")
assert len(errors) == 0, f"Unexpected errors: {{errors}}"
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Validation failed: {result.stderr}")

    def test_card_detector_detect(self):
        code = """
import sys
sys.path.insert(0, "{root}")
from utils.card_detector import CardDetector, CardType

# SJA5 9FV ATR
atr = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
       0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x35, 0x02, 0x59, 0xC4]
result = CardDetector.detect_card_type(atr)
assert result == CardType.SJA5, f"Expected SJA5, got {{result}}"
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Detection failed: {result.stderr}")

    def test_backup_manager_roundtrip(self):
        code = """
import sys, tempfile, os, json
sys.path.insert(0, "{root}")
from managers.backup_manager import BackupManager

tmpdir = tempfile.mkdtemp()
mgr = BackupManager(backup_dir=tmpdir)

# Write a backup manually
data = {{"backup_version": "1.0", "card_data": {{"imsi": "001"}}, "timestamp": "2026-01-01T00:00:00"}}
path = os.path.join(tmpdir, "test.json")
with open(path, 'w') as f:
    json.dump(data, f)

# Load it back
loaded = mgr.load_backup(path)
assert loaded is not None
assert loaded["card_data"]["imsi"] == "001"

# List backups
backups = mgr.list_backups()
assert len(backups) == 1

# Delete
assert mgr.delete_backup(path)
assert not os.path.exists(path)
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Backup roundtrip failed: {result.stderr}")


class TestWriteImsiNotOnSimcard(unittest.TestCase):
    """Regression test: write_imsi must be on the card object, NOT on card.sim."""

    def test_write_imsi_is_not_on_simcard(self):
        """The bug that caused 'Simcard has no attribute write_imsi'."""
        code = """
import sys
sys.path.insert(0, "{root}")
from simcard import Simcard
assert not hasattr(Simcard, 'write_imsi'), "write_imsi should NOT be on Simcard"
assert not hasattr(Simcard, 'write_iccid'), "write_iccid should NOT be on Simcard"

from sysmo_usim import Sysmo_usim
assert hasattr(Sysmo_usim, 'write_imsi'), "write_imsi MUST be on Sysmo_usim"
assert hasattr(Sysmo_usim, 'write_iccid'), "write_iccid MUST be on Sysmo_usim"
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Regression check failed: {result.stderr}")

    def test_card_manager_calls_write_imsi_on_card_not_sim(self):
        """Verify card_manager.py calls self.card.write_imsi, not self.card.sim.write_imsi."""
        code = """
import sys
sys.path.insert(0, "{root}")

with open("{root}/managers/card_manager.py") as f:
    source = f.read()

# The bug was: self.card.sim.write_imsi
assert "self.card.sim.write_imsi" not in source, "BUG: card_manager still calls self.card.sim.write_imsi!"
assert "self.card.sim.write_iccid" not in source, "BUG: card_manager still calls self.card.sim.write_iccid!"

# The correct call should be present
assert "self.card.write_imsi" in source, "card_manager should call self.card.write_imsi"
assert "self.card.write_iccid" in source, "card_manager should call self.card.write_iccid"
print("OK")
""".format(root=PROJECT_ROOT)
        result = subprocess.run(
            [sys.executable, '-c', code],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"Source check failed: {result.stderr}")


if __name__ == '__main__':
    unittest.main()
