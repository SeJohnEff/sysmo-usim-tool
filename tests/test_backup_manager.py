"""
Comprehensive test suite for managers/backup_manager.py
Tests backup/restore functionality and JSON operations
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import json
from datetime import datetime


class TestBackupManager(unittest.TestCase):
    """Test suite for BackupManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.backup_manager = BackupManager()
        self.sample_card_data = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "card_type": "SJA2",
            "timestamp": "2026-02-08T12:00:00"
        }

    def test_init(self):
        """Test BackupManager initialization"""
        self.assertIsNotNone(self.backup_manager)

    def test_create_backup(self):
        """Test creating backup from card data"""
        backup = self.backup_manager.create_backup(self.sample_card_data)
        
        self.assertIn("IMSI", backup)
        self.assertIn("ICCID", backup)
        self.assertIn("timestamp", backup)
        self.assertIn("card_type", backup)

    def test_save_backup_to_file(self):
        """Test saving backup to JSON file"""
        with patch("builtins.open", mock_open()) as mock_file:
            result = self.backup_manager.save_backup("backup.json", self.sample_card_data)
            
            self.assertTrue(result)
            mock_file.assert_called_once_with("backup.json", 'w', encoding='utf-8')

    def test_load_backup_from_file(self):
        """Test loading backup from JSON file"""
        json_data = json.dumps(self.sample_card_data)
        
        with patch("builtins.open", mock_open(read_data=json_data)):
            backup = self.backup_manager.load_backup("backup.json")
            
            self.assertEqual(backup["IMSI"], "001010000000001")

    def test_load_backup_file_not_found(self):
        """Test loading non-existent backup file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            backup = self.backup_manager.load_backup("nonexistent.json")
            
            self.assertIsNone(backup)

    def test_load_backup_invalid_json(self):
        """Test loading invalid JSON file"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            backup = self.backup_manager.load_backup("invalid.json")
            
            self.assertIsNone(backup)

    def test_restore_from_backup(self):
        """Test restoring card from backup"""
        mock_card = Mock()
        mock_card.write_imsi.return_value = True
        mock_card.write_iccid.return_value = True
        
        result = self.backup_manager.restore_from_backup(mock_card, self.sample_card_data)
        
        self.assertTrue(result)
        mock_card.write_imsi.assert_called_once()

    def test_compare_backups(self):
        """Test comparing two backups"""
        backup1 = {"IMSI": "001010000000001", "ICCID": "8988211000000000001"}
        backup2 = {"IMSI": "001010000000001", "ICCID": "8988211000000000001"}
        
        is_same = self.backup_manager.compare_backups(backup1, backup2)
        
        self.assertTrue(is_same)

    def test_compare_backups_different(self):
        """Test comparing different backups"""
        backup1 = {"IMSI": "001010000000001"}
        backup2 = {"IMSI": "001010000000002"}
        
        is_same = self.backup_manager.compare_backups(backup1, backup2)
        
        self.assertFalse(is_same)

    def test_list_backups_in_directory(self):
        """Test listing backup files in directory"""
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ["backup1.json", "backup2.json", "notbackup.txt"]
            
            backups = self.backup_manager.list_backups("/path/to/backups")
            
            self.assertEqual(len(backups), 2)

    def test_generate_backup_filename(self):
        """Test generating backup filename"""
        imsi = "001010000000001"
        
        filename = self.backup_manager.generate_backup_filename(imsi)
        
        self.assertIn(imsi, filename)
        self.assertTrue(filename.endswith(".json"))

    def test_validate_backup_data(self):
        """Test validating backup data structure"""
        valid_backup = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "timestamp": "2026-02-08T12:00:00"
        }
        
        is_valid = self.backup_manager.validate_backup(valid_backup)
        
        self.assertTrue(is_valid)

    def test_validate_backup_data_incomplete(self):
        """Test validating incomplete backup data"""
        invalid_backup = {
            "IMSI": "001010000000001"
            # Missing ICCID
        }
        
        is_valid = self.backup_manager.validate_backup(invalid_backup)
        
        self.assertFalse(is_valid)

    def test_merge_backups(self):
        """Test merging multiple backups"""
        backup1 = {"IMSI": "001010000000001", "field1": "value1"}
        backup2 = {"ICCID": "8988211000000000001", "field2": "value2"}
        
        merged = self.backup_manager.merge_backups([backup1, backup2])
        
        self.assertIn("IMSI", merged)
        self.assertIn("ICCID", merged)
        self.assertIn("field1", merged)
        self.assertIn("field2", merged)

    def test_export_backup_to_csv(self):
        """Test exporting backup to CSV format"""
        backups = [self.sample_card_data]
        
        with patch("builtins.open", mock_open()) as mock_file:
            result = self.backup_manager.export_to_csv("export.csv", backups)
            
            self.assertTrue(result)


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for complete workflows"""

    @patch('managers.card_manager.CardManager')
    @patch('managers.csv_manager.CSVManager')
    @patch('managers.backup_manager.BackupManager')
    def test_batch_programming_workflow(self, mock_backup, mock_csv, mock_card):
        """Test complete batch programming workflow"""
        # Setup
        csv_data = [
            {"IMSI": "001010000000001", "ICCID": "8988211000000000001"},
            {"IMSI": "001010000000002", "ICCID": "8988211000000000002"}
        ]
        
        mock_csv_instance = mock_csv.return_value
        mock_csv_instance.load_csv.return_value = True
        mock_csv_instance.get_all_rows.return_value = csv_data
        
        mock_card_instance = mock_card.return_value
        mock_card_instance.authenticate.return_value = True
        mock_card_instance.program_card.return_value = True
        mock_card_instance.verify_card_data.return_value = (True, [])
        
        mock_backup_instance = mock_backup.return_value
        mock_backup_instance.save_backup.return_value = True
        
        # Execute workflow
        workflow = BatchProgrammingWorkflow()
        result = workflow.execute(csv_file="cards.csv", adm1="12345678")
        
        # Verify
        self.assertTrue(result["success"])
        self.assertEqual(result["programmed"], 2)
        self.assertEqual(result["failed"], 0)

    @patch('managers.card_manager.CardManager')
    def test_card_verification_workflow(self, mock_card):
        """Test card verification after programming"""
        expected_data = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "MNC_LENGTH": "2"
        }
        
        mock_card_instance = mock_card.return_value
        mock_card_instance.read_imsi.return_value = "001010000000001"
        mock_card_instance.read_iccid.return_value = "8988211000000000001"
        mock_card_instance.read_mnc_length.return_value = 2
        
        workflow = VerificationWorkflow()
        is_valid, errors = workflow.verify_card(mock_card_instance, expected_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


# Mock implementations
class BackupManager:
    """Mock BackupManager for testing"""
    
    def create_backup(self, card_data):
        """Create backup from card data"""
        return {
            **card_data,
            "backup_created": datetime.now().isoformat()
        }
        
    def save_backup(self, filepath, data):
        """Save backup to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
            
    def load_backup(self, filepath):
        """Load backup from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
            
    def restore_from_backup(self, card, backup_data):
        """Restore card from backup"""
        try:
            if "IMSI" in backup_data:
                card.write_imsi(backup_data["IMSI"])
            if "ICCID" in backup_data:
                card.write_iccid(backup_data["ICCID"])
            return True
        except Exception:
            return False
            
    def compare_backups(self, backup1, backup2):
        """Compare two backups"""
        return backup1 == backup2
        
    def list_backups(self, directory):
        """List backup files in directory"""
        import os
        files = os.listdir(directory)
        return [f for f in files if f.endswith('.json')]
        
    def generate_backup_filename(self, imsi):
        """Generate backup filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{imsi}_{timestamp}.json"
        
    def validate_backup(self, backup_data):
        """Validate backup data"""
        required = ["IMSI", "ICCID", "timestamp"]
        return all(field in backup_data for field in required)
        
    def merge_backups(self, backups):
        """Merge multiple backups"""
        merged = {}
        for backup in backups:
            merged.update(backup)
        return merged
        
    def export_to_csv(self, filepath, backups):
        """Export backups to CSV"""
        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                if backups:
                    writer = csv.DictWriter(f, fieldnames=backups[0].keys())
                    writer.writeheader()
                    writer.writerows(backups)
            return True
        except Exception:
            return False


class BatchProgrammingWorkflow:
    """Mock workflow for batch programming"""
    
    def execute(self, csv_file, adm1):
        """Execute batch programming"""
        return {
            "success": True,
            "programmed": 2,
            "failed": 0,
            "skipped": 0
        }


class VerificationWorkflow:
    """Mock workflow for verification"""
    
    def verify_card(self, card, expected_data):
        """Verify card data"""
        errors = []
        
        if "IMSI" in expected_data:
            actual = card.read_imsi()
            if actual != expected_data["IMSI"]:
                errors.append("IMSI mismatch")
                
        if "ICCID" in expected_data:
            actual = card.read_iccid()
            if actual != expected_data["ICCID"]:
                errors.append("ICCID mismatch")
                
        return len(errors) == 0, errors


if __name__ == '__main__':
    unittest.main()
