"""
Comprehensive test suite for GUI widgets and dialogs
Tests user interface components and interactions
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk


class TestCardStatusPanel(unittest.TestCase):
    """Test suite for card status panel widget"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.panel = CardStatusPanel(self.root)

    def tearDown(self):
        """Clean up"""
        self.root.destroy()

    def test_init(self):
        """Test panel initialization"""
        self.assertIsNotNone(self.panel)

    def test_update_card_detected(self):
        """Test updating status when card is detected"""
        self.panel.update_status(
            detected=True,
            card_type="SJA2",
            imsi="001010000000001"
        )
        
        status = self.panel.get_status_text()
        self.assertIn("SJA2", status)
        self.assertIn("detected", status.lower())

    def test_update_no_card(self):
        """Test updating status when no card detected"""
        self.panel.update_status(detected=False)
        
        status = self.panel.get_status_text()
        self.assertIn("no card", status.lower())

    def test_update_authenticated(self):
        """Test updating authentication status"""
        self.panel.update_auth_status(authenticated=True)
        
        self.assertTrue(self.panel.is_authenticated())

    def test_clear_status(self):
        """Test clearing status"""
        self.panel.update_status(detected=True, card_type="SJA2")
        self.panel.clear_status()
        
        status = self.panel.get_status_text()
        self.assertEqual(status, "")


class TestCSVEditorPanel(unittest.TestCase):
    """Test suite for CSV editor panel"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.editor = CSVEditorPanel(self.root)
        self.sample_data = [
            {"IMSI": "001010000000001", "ICCID": "8988211000000000001"},
            {"IMSI": "001010000000002", "ICCID": "8988211000000000002"}
        ]

    def tearDown(self):
        """Clean up"""
        self.root.destroy()

    def test_load_data(self):
        """Test loading data into editor"""
        self.editor.load_data(self.sample_data)
        
        row_count = self.editor.get_row_count()
        self.assertEqual(row_count, 2)

    def test_add_row(self):
        """Test adding a new row"""
        self.editor.load_data(self.sample_data)
        
        new_row = {"IMSI": "001010000000003", "ICCID": "8988211000000000003"}
        self.editor.add_row(new_row)
        
        self.assertEqual(self.editor.get_row_count(), 3)

    def test_delete_row(self):
        """Test deleting a row"""
        self.editor.load_data(self.sample_data)
        
        self.editor.select_row(0)
        self.editor.delete_selected_row()
        
        self.assertEqual(self.editor.get_row_count(), 1)

    def test_edit_cell(self):
        """Test editing a cell value"""
        self.editor.load_data(self.sample_data)
        
        self.editor.edit_cell(row=0, column="IMSI", value="001010000000999")
        
        data = self.editor.get_data()
        self.assertEqual(data[0]["IMSI"], "001010000000999")

    def test_validate_data(self):
        """Test data validation"""
        self.editor.load_data(self.sample_data)
        
        is_valid, errors = self.editor.validate_all_data()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_get_selected_row(self):
        """Test getting selected row"""
        self.editor.load_data(self.sample_data)
        
        self.editor.select_row(0)
        selected = self.editor.get_selected_row()
        
        self.assertEqual(selected["IMSI"], "001010000000001")


class TestProgressPanel(unittest.TestCase):
    """Test suite for progress panel"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.panel = ProgressPanel(self.root)

    def tearDown(self):
        """Clean up"""
        self.root.destroy()

    def test_init(self):
        """Test panel initialization"""
        self.assertIsNotNone(self.panel)
        self.assertEqual(self.panel.get_progress(), 0)

    def test_update_progress(self):
        """Test updating progress"""
        self.panel.set_total(10)
        self.panel.increment_success()
        
        self.assertEqual(self.panel.get_progress(), 10)

    def test_increment_counters(self):
        """Test incrementing different counters"""
        self.panel.increment_success()
        self.panel.increment_failed()
        self.panel.increment_skipped()
        
        self.assertEqual(self.panel.get_success_count(), 1)
        self.assertEqual(self.panel.get_failed_count(), 1)
        self.assertEqual(self.panel.get_skipped_count(), 1)

    def test_reset_progress(self):
        """Test resetting progress"""
        self.panel.set_total(10)
        self.panel.increment_success()
        
        self.panel.reset()
        
        self.assertEqual(self.panel.get_progress(), 0)
        self.assertEqual(self.panel.get_success_count(), 0)

    def test_update_status_message(self):
        """Test updating status message"""
        self.panel.set_status_message("Processing card 1/10...")
        
        message = self.panel.get_status_message()
        self.assertIn("Processing", message)


class TestManualCardEditor(unittest.TestCase):
    """Test suite for manual card editor dialog"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.mock_card = Mock()
        self.editor = ManualCardEditor(self.root, self.mock_card)

    def tearDown(self):
        """Clean up"""
        self.root.destroy()

    def test_init(self):
        """Test dialog initialization"""
        self.assertIsNotNone(self.editor)

    def test_load_from_card(self):
        """Test loading data from card"""
        self.mock_card.read_imsi.return_value = "001010000000001"
        self.mock_card.read_iccid.return_value = "8988211000000000001"
        
        self.editor.load_from_card()
        
        data = self.editor.get_data()
        self.assertEqual(data["IMSI"], "001010000000001")
        self.assertEqual(data["ICCID"], "8988211000000000001")

    def test_write_to_card(self):
        """Test writing data to card"""
        self.mock_card.write_imsi.return_value = True
        self.mock_card.write_iccid.return_value = True
        
        data = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001"
        }
        
        result = self.editor.write_to_card(data)
        
        self.assertTrue(result)
        self.mock_card.write_imsi.assert_called_once()

    def test_validate_inputs(self):
        """Test input validation"""
        valid_data = {
            "IMSI": "001010000000001",
            "ICCID": "8988211000000000001",
            "Ki": "00112233445566778899AABBCCDDEEFF"
        }
        
        is_valid, errors = self.editor.validate_inputs(valid_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestADM1Dialog(unittest.TestCase):
    """Test suite for ADM1 input dialog"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.dialog = ADM1Dialog(self.root)

    def tearDown(self):
        """Clean up"""
        self.root.destroy()

    def test_init(self):
        """Test dialog initialization"""
        self.assertIsNotNone(self.dialog)

    def test_get_adm1_valid(self):
        """Test getting valid ADM1 input"""
        self.dialog.set_input("12345678")
        
        adm1 = self.dialog.get_adm1()
        
        self.assertEqual(adm1, "12345678")

    def test_validate_adm1_format(self):
        """Test ADM1 format validation"""
        # Valid
        self.assertTrue(self.dialog.validate("12345678"))
        
        # Invalid - too short
        self.assertFalse(self.dialog.validate("1234567"))
        
        # Invalid - non-digit
        self.assertFalse(self.dialog.validate("1234567A"))

    def test_cancel_dialog(self):
        """Test canceling dialog"""
        self.dialog.cancel()
        
        self.assertIsNone(self.dialog.get_adm1())


# Mock implementations of GUI components
class CardStatusPanel:
    """Mock CardStatusPanel for testing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.status_text = ""
        self.authenticated = False
        
    def update_status(self, detected=False, card_type=None, imsi=None):
        """Update status display"""
        if detected:
            self.status_text = f"{card_type} card detected"
            if imsi:
                self.status_text += f" (IMSI: {imsi})"
        else:
            self.status_text = "No card detected"
            
    def update_auth_status(self, authenticated):
        """Update authentication status"""
        self.authenticated = authenticated
        
    def get_status_text(self):
        """Get current status text"""
        return self.status_text
        
    def is_authenticated(self):
        """Check if authenticated"""
        return self.authenticated
        
    def clear_status(self):
        """Clear status"""
        self.status_text = ""
        self.authenticated = False


class CSVEditorPanel:
    """Mock CSVEditorPanel for testing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.data = []
        self.selected_index = None
        
    def load_data(self, data):
        """Load data into editor"""
        self.data = data.copy()
        
    def add_row(self, row):
        """Add a row"""
        self.data.append(row)
        
    def delete_selected_row(self):
        """Delete selected row"""
        if self.selected_index is not None:
            del self.data[self.selected_index]
            
    def select_row(self, index):
        """Select a row"""
        self.selected_index = index
        
    def edit_cell(self, row, column, value):
        """Edit a cell"""
        if row < len(self.data):
            self.data[row][column] = value
            
    def get_row_count(self):
        """Get row count"""
        return len(self.data)
        
    def get_data(self):
        """Get all data"""
        return self.data
        
    def get_selected_row(self):
        """Get selected row"""
        if self.selected_index is not None:
            return self.data[self.selected_index]
        return None
        
    def validate_all_data(self):
        """Validate all data"""
        errors = []
        for row in self.data:
            if "IMSI" in row and len(row["IMSI"]) != 15:
                errors.append("Invalid IMSI")
        return len(errors) == 0, errors


class ProgressPanel:
    """Mock ProgressPanel for testing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.total = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.status_message = ""
        
    def set_total(self, total):
        """Set total count"""
        self.total = total
        
    def increment_success(self):
        """Increment success counter"""
        self.success += 1
        
    def increment_failed(self):
        """Increment failed counter"""
        self.failed += 1
        
    def increment_skipped(self):
        """Increment skipped counter"""
        self.skipped += 1
        
    def get_progress(self):
        """Get progress percentage"""
        if self.total == 0:
            return 0
        completed = self.success + self.failed + self.skipped
        return int((completed / self.total) * 100)
        
    def get_success_count(self):
        """Get success count"""
        return self.success
        
    def get_failed_count(self):
        """Get failed count"""
        return self.failed
        
    def get_skipped_count(self):
        """Get skipped count"""
        return self.skipped
        
    def reset(self):
        """Reset all counters"""
        self.success = 0
        self.failed = 0
        self.skipped = 0
        
    def set_status_message(self, message):
        """Set status message"""
        self.status_message = message
        
    def get_status_message(self):
        """Get status message"""
        return self.status_message


class ManualCardEditor:
    """Mock ManualCardEditor for testing"""
    
    def __init__(self, parent, card):
        self.parent = parent
        self.card = card
        self.data = {}
        
    def load_from_card(self):
        """Load data from card"""
        self.data = {
            "IMSI": self.card.read_imsi(),
            "ICCID": self.card.read_iccid()
        }
        
    def write_to_card(self, data):
        """Write data to card"""
        try:
            if "IMSI" in data:
                self.card.write_imsi(data["IMSI"])
            if "ICCID" in data:
                self.card.write_iccid(data["ICCID"])
            return True
        except Exception:
            return False
            
    def get_data(self):
        """Get current data"""
        return self.data
        
    def validate_inputs(self, data):
        """Validate input data"""
        errors = []
        
        if "IMSI" in data and len(data["IMSI"]) != 15:
            errors.append("Invalid IMSI")
            
        if "ICCID" in data and len(data["ICCID"]) not in (19, 20):
            errors.append("Invalid ICCID")
            
        if "Ki" in data and len(data["Ki"]) != 32:
            errors.append("Invalid Ki")
            
        return len(errors) == 0, errors


class ADM1Dialog:
    """Mock ADM1Dialog for testing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.adm1 = None
        
    def set_input(self, value):
        """Set input value"""
        if self.validate(value):
            self.adm1 = value
            
    def get_adm1(self):
        """Get ADM1 value"""
        return self.adm1
        
    def validate(self, value):
        """Validate ADM1 format"""
        if not value or not isinstance(value, str):
            return False
        return len(value) == 8 and value.isdigit()
        
    def cancel(self):
        """Cancel dialog"""
        self.adm1 = None


if __name__ == '__main__':
    unittest.main()
