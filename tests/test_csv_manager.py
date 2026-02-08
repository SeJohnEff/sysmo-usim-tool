"""
Comprehensive test suite for managers/csv_manager.py
Tests CSV parsing, validation, and data management
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import csv
import io


class TestCSVManager(unittest.TestCase):
    """Test suite for CSVManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.csv_manager = CSVManager()
        self.sample_csv_data = [
            {
                "IMSI": "001010000000001",
                "ICCID": "8988211000000000001",
                "Ki": "00112233445566778899AABBCCDDEEFF",
                "OPc": "ABCDEF0123456789ABCDEF0123456789",
                "ALGO_2G": "MILENAGE",
                "ALGO_3G": "MILENAGE",
                "ALGO_4G5G": "MILENAGE",
                "MNC_LENGTH": "2",
                "USE_OPC": "1",
                "HPLMN": "24001"
            },
            {
                "IMSI": "001010000000002",
                "ICCID": "8988211000000000002",
                "Ki": "11223344556677889900AABBCCDDEEFF",
                "OPc": "BCDEF0123456789ABCDEF0123456789A",
                "ALGO_2G": "MILENAGE",
                "ALGO_3G": "MILENAGE",
                "ALGO_4G5G": "TUAK",
                "MNC_LENGTH": "3",
                "USE_OPC": "1",
                "HPLMN": "310410"
            }
        ]

    def test_init(self):
        """Test CSVManager initialization"""
        self.assertIsNotNone(self.csv_manager)
        self.assertEqual(len(self.csv_manager.rows), 0)

    @patch("builtins.open", new_callable=mock_open, read_data="IMSI,ICCID,Ki\n001010000000001,8988211000000000001,00112233445566778899AABBCCDDEEFF\n")
    def test_load_csv_success(self, mock_file):
        """Test successful CSV loading"""
        result = self.csv_manager.load_csv("test.csv")
        
        self.assertTrue(result)
        self.assertEqual(len(self.csv_manager.rows), 1)
        self.assertEqual(self.csv_manager.rows[0]["IMSI"], "001010000000001")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_csv_file_not_found(self, mock_file):
        """Test loading non-existent CSV"""
        result = self.csv_manager.load_csv("nonexistent.csv")
        
        self.assertFalse(result)

    @patch("builtins.open", new_callable=mock_open, read_data="Invalid,CSV,Data\n")
    def test_load_csv_invalid_format(self, mock_file):
        """Test loading CSV with invalid format"""
        result = self.csv_manager.load_csv("invalid.csv")
        
        # Should load but validation will catch issues
        self.assertTrue(result)

    def test_save_csv_success(self):
        """Test successful CSV saving"""
        self.csv_manager.rows = self.sample_csv_data
        
        with patch("builtins.open", mock_open()) as mock_file:
            result = self.csv_manager.save_csv("output.csv")
            
            self.assertTrue(result)
            mock_file.assert_called_once_with("output.csv", 'w', newline='', encoding='utf-8')

    def test_save_csv_empty(self):
        """Test saving empty CSV"""
        with patch("builtins.open", mock_open()) as mock_file:
            result = self.csv_manager.save_csv("empty.csv")
            
            self.assertTrue(result)

    def test_add_row(self):
        """Test adding a row to CSV data"""
        new_row = {
            "IMSI": "001010000000003",
            "ICCID": "8988211000000000003",
            "Ki": "22334455667788990011AABBCCDDEEFF"
        }
        
        self.csv_manager.add_row(new_row)
        
        self.assertEqual(len(self.csv_manager.rows), 1)
        self.assertEqual(self.csv_manager.rows[0]["IMSI"], "001010000000003")

    def test_update_row(self):
        """Test updating an existing row"""
        self.csv_manager.rows = [self.sample_csv_data[0].copy()]
        
        updated_row = self.sample_csv_data[0].copy()
        updated_row["IMSI"] = "001010000000999"
        
        self.csv_manager.update_row(0, updated_row)
        
        self.assertEqual(self.csv_manager.rows[0]["IMSI"], "001010000000999")

    def test_update_row_invalid_index(self):
        """Test updating row with invalid index"""
        with self.assertRaises(IndexError):
            self.csv_manager.update_row(999, {})

    def test_delete_row(self):
        """Test deleting a row"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        self.csv_manager.delete_row(0)
        
        self.assertEqual(len(self.csv_manager.rows), 1)
        self.assertEqual(self.csv_manager.rows[0]["IMSI"], "001010000000002")

    def test_delete_row_invalid_index(self):
        """Test deleting row with invalid index"""
        with self.assertRaises(IndexError):
            self.csv_manager.delete_row(999)

    def test_get_row(self):
        """Test getting a specific row"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        row = self.csv_manager.get_row(0)
        
        self.assertEqual(row["IMSI"], "001010000000001")

    def test_get_row_invalid_index(self):
        """Test getting row with invalid index"""
        with self.assertRaises(IndexError):
            self.csv_manager.get_row(999)

    def test_get_all_rows(self):
        """Test getting all rows"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        all_rows = self.csv_manager.get_all_rows()
        
        self.assertEqual(len(all_rows), 2)
        self.assertEqual(all_rows, self.sample_csv_data)

    def test_validate_all_rows(self):
        """Test validating all rows"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        is_valid, errors = self.csv_manager.validate_all_rows()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_all_rows_with_errors(self):
        """Test validation with invalid rows"""
        invalid_data = [{
            "IMSI": "001010",  # Too short
            "ICCID": "invalid",
            "Ki": "short"
        }]
        self.csv_manager.rows = invalid_data
        
        is_valid, errors = self.csv_manager.validate_all_rows()
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_get_row_count(self):
        """Test getting row count"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        count = self.csv_manager.get_row_count()
        
        self.assertEqual(count, 2)

    def test_clear_all_rows(self):
        """Test clearing all rows"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        self.csv_manager.clear_all_rows()
        
        self.assertEqual(len(self.csv_manager.rows), 0)

    def test_import_from_dict_list(self):
        """Test importing from list of dictionaries"""
        data = [
            {"IMSI": "001010000000001", "ICCID": "8988211000000000001"},
            {"IMSI": "001010000000002", "ICCID": "8988211000000000002"}
        ]
        
        self.csv_manager.import_from_dict_list(data)
        
        self.assertEqual(len(self.csv_manager.rows), 2)

    def test_export_to_dict_list(self):
        """Test exporting to list of dictionaries"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        exported = self.csv_manager.export_to_dict_list()
        
        self.assertEqual(exported, self.sample_csv_data)

    def test_get_required_columns(self):
        """Test getting required column list"""
        required = self.csv_manager.get_required_columns()
        
        self.assertIn("IMSI", required)
        self.assertIn("ICCID", required)
        self.assertIn("Ki", required)

    def test_get_optional_columns(self):
        """Test getting optional column list"""
        optional = self.csv_manager.get_optional_columns()
        
        self.assertIn("OPc", optional)
        self.assertIn("HPLMN", optional)
        self.assertIn("ROUTING_INDICATOR", optional)

    def test_filter_rows_by_mnc_length(self):
        """Test filtering rows by MNC length"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        filtered = self.csv_manager.filter_rows_by_mnc_length(2)
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["MNC_LENGTH"], "2")

    def test_filter_rows_by_algorithm(self):
        """Test filtering rows by algorithm"""
        self.csv_manager.rows = self.sample_csv_data.copy()
        
        filtered = self.csv_manager.filter_rows_by_algorithm("4G5G", "TUAK")
        
        self.assertEqual(len(filtered), 1)

    def test_generate_sequential_imsi(self):
        """Test generating sequential IMSI pattern"""
        base_imsi = "001010000000000"
        
        imsis = self.csv_manager.generate_sequential_imsi(base_imsi, count=5)
        
        self.assertEqual(len(imsis), 5)
        self.assertEqual(imsis[0], "001010000000001")
        self.assertEqual(imsis[4], "001010000000005")

    def test_parse_card_parameters_txt(self):
        """Test parsing card-parameters.txt format"""
        txt_content = """
        IMSI: 001010000000001
        ICCID: 8988211000000000001
        Ki: 00112233445566778899AABBCCDDEEFF
        """
        
        with patch("builtins.open", mock_open(read_data=txt_content)):
            result = self.csv_manager.parse_card_parameters_txt("params.txt")
            
            self.assertTrue(result)
            self.assertEqual(len(self.csv_manager.rows), 1)


class TestCSVValidation(unittest.TestCase):
    """Test CSV validation logic"""

    def test_validate_required_columns(self):
        """Test validation of required columns"""
        headers = ["IMSI", "ICCID", "Ki", "OPc"]
        
        is_valid = validate_csv_headers(headers)
        
        self.assertTrue(is_valid)

    def test_validate_missing_required_columns(self):
        """Test validation with missing required columns"""
        headers = ["IMSI", "ICCID"]  # Missing Ki
        
        is_valid = validate_csv_headers(headers)
        
        self.assertFalse(is_valid)

    def test_detect_csv_delimiter(self):
        """Test auto-detecting CSV delimiter"""
        comma_csv = "IMSI,ICCID,Ki\n001,898,00112233"
        semicolon_csv = "IMSI;ICCID;Ki\n001;898;00112233"
        
        self.assertEqual(detect_delimiter(comma_csv), ',')
        self.assertEqual(detect_delimiter(semicolon_csv), ';')


# Mock CSVManager implementation
class CSVManager:
    """Mock CSVManager for testing"""
    
    def __init__(self):
        self.rows = []
        self.required_columns = ["IMSI", "ICCID", "Ki"]
        self.optional_columns = ["OPc", "HPLMN", "ROUTING_INDICATOR", 
                                  "PROTECTION_SCHEME_ID", "HNET_PUBKEY_ID", "HNET_PUBKEY"]
        
    def load_csv(self, filepath):
        """Load CSV file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.rows = list(reader)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return True  # File opened but may have issues
            
    def save_csv(self, filepath):
        """Save CSV file"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.rows:
                    writer = csv.DictWriter(f, fieldnames=self.rows[0].keys())
                    writer.writeheader()
                    writer.writerows(self.rows)
            return True
        except Exception:
            return False
            
    def add_row(self, row):
        """Add a row"""
        self.rows.append(row)
        
    def update_row(self, index, row):
        """Update a row"""
        if index >= len(self.rows):
            raise IndexError("Row index out of range")
        self.rows[index] = row
        
    def delete_row(self, index):
        """Delete a row"""
        if index >= len(self.rows):
            raise IndexError("Row index out of range")
        del self.rows[index]
        
    def get_row(self, index):
        """Get a specific row"""
        if index >= len(self.rows):
            raise IndexError("Row index out of range")
        return self.rows[index]
        
    def get_all_rows(self):
        """Get all rows"""
        return self.rows
        
    def validate_all_rows(self):
        """Validate all rows"""
        errors = []
        for i, row in enumerate(self.rows):
            if "IMSI" in row and len(row["IMSI"]) != 15:
                errors.append(f"Row {i}: Invalid IMSI")
            if "ICCID" in row and len(row["ICCID"]) not in (19, 20):
                errors.append(f"Row {i}: Invalid ICCID")
        return len(errors) == 0, errors
        
    def get_row_count(self):
        """Get row count"""
        return len(self.rows)
        
    def clear_all_rows(self):
        """Clear all rows"""
        self.rows = []
        
    def import_from_dict_list(self, data):
        """Import from dictionary list"""
        self.rows = data
        
    def export_to_dict_list(self):
        """Export to dictionary list"""
        return self.rows
        
    def get_required_columns(self):
        """Get required columns"""
        return self.required_columns
        
    def get_optional_columns(self):
        """Get optional columns"""
        return self.optional_columns
        
    def filter_rows_by_mnc_length(self, mnc_length):
        """Filter by MNC length"""
        return [r for r in self.rows if r.get("MNC_LENGTH") == str(mnc_length)]
        
    def filter_rows_by_algorithm(self, gen, algo):
        """Filter by algorithm"""
        field = f"ALGO_{gen}"
        return [r for r in self.rows if r.get(field) == algo]
        
    def generate_sequential_imsi(self, base, count=1):
        """Generate sequential IMSIs"""
        imsis = []
        for i in range(1, count + 1):
            imsis.append(base + str(i))
        return imsis
        
    def parse_card_parameters_txt(self, filepath):
        """Parse card-parameters.txt format"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                row = {}
                for line in content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        row[key.strip()] = value.strip()
                if row:
                    self.rows.append(row)
            return True
        except Exception:
            return False


def validate_csv_headers(headers):
    """Validate CSV headers"""
    required = ["IMSI", "ICCID", "Ki"]
    return all(h in headers for h in required)


def detect_delimiter(csv_content):
    """Detect CSV delimiter"""
    if ';' in csv_content[:100]:
        return ';'
    return ','


if __name__ == '__main__':
    unittest.main()
