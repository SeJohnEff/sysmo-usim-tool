"""
Tests for managers/backup_manager.py - the REAL BackupManager class.
"""

import unittest
import tempfile
import os
import sys
import json
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.backup_manager import BackupManager


class TestBackupManagerInit(unittest.TestCase):

    def test_init_default_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                mgr = BackupManager()
                self.assertEqual(mgr.backup_dir, "backups")
                self.assertTrue(os.path.isdir(os.path.join(tmpdir, "backups")))
            finally:
                os.chdir(orig_cwd)

    def test_init_custom_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom = os.path.join(tmpdir, "my_backups")
            mgr = BackupManager(backup_dir=custom)
            self.assertEqual(mgr.backup_dir, custom)
            self.assertTrue(os.path.isdir(custom))

    def test_backup_version(self):
        self.assertEqual(BackupManager.BACKUP_VERSION, "1.0")


class TestBackupManagerCreateBackup(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_create_backup(self):
        mock_cm = Mock()
        mock_cm.card_type.name = "SJA5"
        mock_cm.atr = [0x3B, 0x9F]
        mock_cm.read_card_data.return_value = {
            'imsi': '001010000000001',
            'iccid': '8988211000000000001',
            'mnc_length': 2,
        }

        card_data = {
            'IMSI': '001010000000001',
            'ICCID': '8988211000000000001',
            'Ki': 'A' * 32,
            'OPc': 'B' * 32,
            'ALGO_2G': 'MILENAGE',
            'ALGO_3G': 'MILENAGE',
            'ALGO_4G5G': 'MILENAGE',
            'USE_OPC': '1',
            'MNC_LENGTH': '2',
        }

        filepath = self.mgr.create_backup(card_data, mock_cm)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath) as f:
            backup = json.load(f)

        self.assertEqual(backup['backup_version'], '1.0')
        self.assertEqual(backup['card_type'], 'SJA5')
        self.assertIn('timestamp', backup)
        self.assertEqual(backup['card_data']['imsi'], '001010000000001')
        self.assertTrue(backup['can_restore'])

    def test_create_backup_without_card_read(self):
        mock_cm = Mock()
        mock_cm.card_type.name = "SJA5"
        mock_cm.atr = None
        mock_cm.read_card_data.return_value = None

        card_data = {'IMSI': '001010000000001', 'ICCID': '8988211000000000001'}
        filepath = self.mgr.create_backup(card_data, mock_cm)
        self.assertIsNotNone(filepath)


class TestBackupManagerLoadBackup(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def _write_backup(self, filename, data):
        path = os.path.join(self.tmpdir, filename)
        with open(path, 'w') as f:
            json.dump(data, f)
        return path

    def test_load_valid_backup(self):
        data = {
            'backup_version': '1.0',
            'timestamp': '2026-02-08T12:00:00',
            'card_type': 'SJA5',
            'card_data': {'imsi': '001010000000001'},
        }
        path = self._write_backup("test.json", data)
        result = self.mgr.load_backup(path)

        self.assertIsNotNone(result)
        self.assertEqual(result['card_type'], 'SJA5')

    def test_load_nonexistent_file(self):
        result = self.mgr.load_backup("/nonexistent/backup.json")
        self.assertIsNone(result)

    def test_load_invalid_json(self):
        path = os.path.join(self.tmpdir, "bad.json")
        with open(path, 'w') as f:
            f.write("not valid json{{{")
        result = self.mgr.load_backup(path)
        self.assertIsNone(result)

    def test_load_version_mismatch_still_loads(self):
        data = {'backup_version': '99.0', 'card_data': {}}
        path = self._write_backup("old.json", data)
        result = self.mgr.load_backup(path)
        self.assertIsNotNone(result)


class TestBackupManagerRestoreBackup(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_restore_backup(self):
        backup_data = {
            'backup_version': '1.0',
            'can_restore': True,
            'card_data': {
                'imsi': '001010000000001',
                'iccid': '8988211000000000001',
                'mnc_length': '2',
                'authentication': {
                    'ki': 'A' * 32, 'opc': 'B' * 32,
                    'use_opc': True, 'algo_2g': 'MILENAGE',
                    'algo_3g': 'MILENAGE', 'algo_4g5g': 'MILENAGE',
                },
                'milenage_params': {},
                'tuak_params': {},
            },
        }

        path = os.path.join(self.tmpdir, "restore.json")
        with open(path, 'w') as f:
            json.dump(backup_data, f)

        mock_cm = Mock()
        mock_cm.program_card.return_value = (True, "OK")

        success, msg = self.mgr.restore_backup(path, mock_cm)

        self.assertTrue(success)
        mock_cm.program_card.assert_called_once()
        call_data = mock_cm.program_card.call_args[0][0]
        self.assertEqual(call_data['IMSI'], '001010000000001')

    def test_restore_nonexistent_file(self):
        mock_cm = Mock()
        success, msg = self.mgr.restore_backup("/nonexistent.json", mock_cm)
        self.assertFalse(success)

    def test_restore_non_restorable(self):
        backup_data = {'backup_version': '1.0', 'can_restore': False, 'card_data': {}}
        path = os.path.join(self.tmpdir, "norestore.json")
        with open(path, 'w') as f:
            json.dump(backup_data, f)

        mock_cm = Mock()
        success, msg = self.mgr.restore_backup(path, mock_cm)
        self.assertFalse(success)
        self.assertIn("non-restorable", msg)


class TestBackupManagerListBackups(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_list_empty(self):
        self.assertEqual(len(self.mgr.list_backups()), 0)

    def test_list_backups(self):
        for i in range(3):
            data = {
                'backup_version': '1.0',
                'timestamp': f'2026-02-0{i+1}T12:00:00',
                'card_type': 'SJA5',
                'card_data': {'imsi': f'00101000000000{i}', 'iccid': f'899{i}'},
            }
            path = os.path.join(self.tmpdir, f"backup_{i}.json")
            with open(path, 'w') as f:
                json.dump(data, f)

        backups = self.mgr.list_backups()
        self.assertEqual(len(backups), 3)
        self.assertGreater(backups[0]['timestamp'], backups[2]['timestamp'])

    def test_list_with_iccid_filter(self):
        for i, iccid in enumerate(["AAA", "BBB", "AAA"]):
            data = {
                'backup_version': '1.0',
                'timestamp': f'2026-02-0{i+1}T12:00:00',
                'card_data': {'iccid': iccid},
            }
            path = os.path.join(self.tmpdir, f"backup_{i}.json")
            with open(path, 'w') as f:
                json.dump(data, f)

        backups = self.mgr.list_backups(iccid_filter="AAA")
        self.assertEqual(len(backups), 2)

    def test_list_ignores_non_json(self):
        with open(os.path.join(self.tmpdir, "readme.txt"), 'w') as f:
            f.write("not a backup")
        self.assertEqual(len(self.mgr.list_backups()), 0)


class TestBackupManagerDeleteBackup(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_delete_backup(self):
        path = os.path.join(self.tmpdir, "todelete.json")
        with open(path, 'w') as f:
            json.dump({}, f)
        self.assertTrue(self.mgr.delete_backup(path))
        self.assertFalse(os.path.exists(path))

    def test_delete_nonexistent(self):
        self.assertFalse(self.mgr.delete_backup("/nonexistent.json"))


class TestBackupManagerExportToCsvRow(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_export_to_csv_row(self):
        backup_data = {
            'backup_version': '1.0',
            'card_data': {
                'imsi': '001010000000001',
                'iccid': '8988211000000000001',
                'mnc_length': '2',
                'authentication': {
                    'ki': 'A' * 32, 'opc': 'B' * 32,
                    'use_opc': True, 'algo_2g': 'MILENAGE',
                    'algo_3g': 'MILENAGE', 'algo_4g5g': 'MILENAGE',
                },
                'milenage_params': {},
                'tuak_params': {},
            },
        }
        path = os.path.join(self.tmpdir, "export.json")
        with open(path, 'w') as f:
            json.dump(backup_data, f)

        row = self.mgr.export_to_csv_row(path)
        self.assertIsNotNone(row)
        self.assertEqual(row['IMSI'], '001010000000001')
        self.assertEqual(row['USE_OPC'], '1')

    def test_export_nonexistent(self):
        self.assertIsNone(self.mgr.export_to_csv_row("/nonexistent.json"))


class TestBackupToCardData(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_full_conversion(self):
        backup = {
            'card_data': {
                'imsi': '001010000000001',
                'iccid': '8988211000000000001',
                'mnc_length': '2',
                'authentication': {
                    'ki': 'AABBCCDD' * 4, 'opc': '11223344' * 4,
                    'use_opc': True, 'algo_2g': 'MILENAGE',
                    'algo_3g': 'MILENAGE', 'algo_4g5g': 'TUAK',
                },
                'milenage_params': {'r1': '40', 'r2': '00', 'r3': '20', 'r4': '40', 'r5': '60'},
                'tuak_params': {'res_size': '128', 'mac_size': '128', 'ckik_size': '256'},
            },
        }
        result = self.mgr._backup_to_card_data(backup)
        self.assertEqual(result['IMSI'], '001010000000001')
        self.assertEqual(result['ALGO_4G5G'], 'TUAK')
        self.assertEqual(result['MILENAGE_R1'], '40')
        self.assertEqual(result['TUAK_RES_SIZE'], '128')

    def test_empty_backup(self):
        result = self.mgr._backup_to_card_data({})
        self.assertEqual(result['IMSI'], '')
        self.assertEqual(result['ALGO_2G'], 'MILENAGE')

    def test_use_op_false(self):
        backup = {
            'card_data': {
                'authentication': {'use_opc': False},
                'milenage_params': {},
                'tuak_params': {},
            },
        }
        result = self.mgr._backup_to_card_data(backup)
        self.assertEqual(result['USE_OPC'], '0')


class TestAtrToHexString(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = BackupManager(backup_dir=self.tmpdir)

    def test_atr_to_hex(self):
        self.assertEqual(self.mgr._atr_to_hex_string([0x3B, 0x9F, 0x96]), "3B 9F 96")

    def test_empty_atr(self):
        self.assertEqual(self.mgr._atr_to_hex_string([]), "")

    def test_none_atr(self):
        self.assertEqual(self.mgr._atr_to_hex_string(None), "")


if __name__ == '__main__':
    unittest.main()
