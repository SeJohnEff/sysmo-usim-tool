#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Manager for loading, validating, and exporting SIM card configurations

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import csv
import re
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validators, ValidationError, DEFAULT_VALUES


class CSVManager:
    """Manage CSV files with SIM card configurations"""

    # Basic columns (always visible in UI)
    BASIC_COLUMNS = [
        'IMSI', 'ICCID', 'Ki', 'OPc', 'ALGO_2G', 'ALGO_3G', 'ALGO_4G5G', 'MNC_LENGTH'
    ]

    # Advanced columns (hidden by default)
    ADVANCED_COLUMNS = [
        'USE_OPC',
        'MILENAGE_R1', 'MILENAGE_R2', 'MILENAGE_R3', 'MILENAGE_R4', 'MILENAGE_R5',
        'MILENAGE_C1', 'MILENAGE_C2', 'MILENAGE_C3', 'MILENAGE_C4', 'MILENAGE_C5',
        'SQN_IND_SIZE_BITS', 'SQN_CHECK_ENABLED', 'SQN_AGE_LIMIT_ENABLED',
        'SQN_MAX_DELTA_ENABLED', 'SQN_CHECK_SKIP_FIRST',
        'TUAK_RES_SIZE', 'TUAK_MAC_SIZE', 'TUAK_CKIK_SIZE', 'TUAK_NUM_KECCAK'
    ]

    ALL_COLUMNS = BASIC_COLUMNS + ADVANCED_COLUMNS

    def __init__(self):
        self.cards: List[Dict[str, str]] = []
        self.validation_errors: List[ValidationError] = []

    def load_csv(self, filename: str, card_type: str = 'SJA5') -> bool:
        """
        Load cards from CSV file

        Args:
            filename: Path to CSV file
            card_type: Card type for validation (SJA2, SJA5, SJS1)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.cards = []
            self.validation_errors = []

            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Check required columns
                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers")

                missing_required = set(self.BASIC_COLUMNS) - set(reader.fieldnames)
                if missing_required:
                    raise ValueError(f"Missing required columns: {', '.join(missing_required)}")

                # Load and validate rows
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    # Fill in default values for missing optional fields
                    for col in self.ALL_COLUMNS:
                        if col not in row or not row[col]:
                            row[col] = DEFAULT_VALUES.get(col, '')

                    # Validate row
                    errors = Validators.validate_row(row, row_num, card_type)
                    self.validation_errors.extend(errors)

                    self.cards.append(row)

            return True

        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False

    def save_csv(self, filename: str, include_advanced: bool = True) -> bool:
        """
        Save cards to CSV file

        Args:
            filename: Path to CSV file
            include_advanced: Include advanced columns

        Returns:
            True if successful, False otherwise
        """
        try:
            columns = self.BASIC_COLUMNS if not include_advanced else self.ALL_COLUMNS

            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()

                for card in self.cards:
                    # Only write specified columns
                    row = {col: card.get(col, '') for col in columns}
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False

    def load_card_parameters_file(self, filename: str) -> bool:
        """
        Load card-parameters.txt file format

        Format:
        Card #1:
        ICCID: 8988211000000000001
        IMSI: 001010000000001
        Ki: 00112233445566778899AABBCCDDEEFF
        OPc: ABCDEF0123456789ABCDEF0123456789
        ADM1: 12345678

        Args:
            filename: Path to card-parameters.txt file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.cards = []
            self.validation_errors = []

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split by "Card #" sections
            card_sections = re.split(r'Card\s+#\d+:', content)

            for section in card_sections[1:]:  # Skip first empty element
                card = {}

                # Extract fields using regex
                imsi_match = re.search(r'IMSI:\s*(\d+)', section)
                if imsi_match:
                    card['IMSI'] = imsi_match.group(1)

                iccid_match = re.search(r'ICCID:\s*(\d+)', section)
                if iccid_match:
                    card['ICCID'] = iccid_match.group(1)

                ki_match = re.search(r'Ki:\s*([0-9A-Fa-f]+)', section)
                if ki_match:
                    card['Ki'] = ki_match.group(1).upper()

                opc_match = re.search(r'OP[cC]?:\s*([0-9A-Fa-f]+)', section)
                if opc_match:
                    card['OPc'] = opc_match.group(1).upper()

                adm1_match = re.search(r'ADM1:\s*(\d{8})', section)
                if adm1_match:
                    card['ADM1'] = adm1_match.group(1)

                # Fill in defaults
                for col in self.ALL_COLUMNS:
                    if col not in card:
                        card[col] = DEFAULT_VALUES.get(col, '')

                if card.get('IMSI'):  # Only add if we have at least IMSI
                    self.cards.append(card)

            return len(self.cards) > 0

        except Exception as e:
            print(f"Error loading card-parameters file: {e}")
            return False

    def add_card(self, card_data: Dict[str, str]):
        """Add a new card configuration"""
        # Fill in defaults
        for col in self.ALL_COLUMNS:
            if col not in card_data:
                card_data[col] = DEFAULT_VALUES.get(col, '')
        self.cards.append(card_data)

    def remove_card(self, index: int):
        """Remove card at index"""
        if 0 <= index < len(self.cards):
            del self.cards[index]

    def get_card(self, index: int) -> Optional[Dict[str, str]]:
        """Get card at index"""
        if 0 <= index < len(self.cards):
            return self.cards[index]
        return None

    def update_card(self, index: int, card_data: Dict[str, str]):
        """Update card at index"""
        if 0 <= index < len(self.cards):
            self.cards[index] = card_data

    def get_card_count(self) -> int:
        """Get number of cards"""
        return len(self.cards)

    def validate_all(self, card_type: str = 'SJA5') -> List[ValidationError]:
        """
        Validate all cards

        Args:
            card_type: Card type for validation

        Returns:
            List of validation errors
        """
        self.validation_errors = []
        for i, card in enumerate(self.cards):
            errors = Validators.validate_row(card, i + 2, card_type)  # +2 for header row
            self.validation_errors.extend(errors)
        return self.validation_errors

    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.validation_errors) > 0

    def get_errors_for_row(self, row_index: int) -> List[ValidationError]:
        """Get validation errors for specific row"""
        return [e for e in self.validation_errors if e.row == row_index + 2]


# Example usage
if __name__ == "__main__":
    manager = CSVManager()

    # Test loading CSV
    if manager.load_csv("test_cards.csv"):
        print(f"Loaded {manager.get_card_count()} cards")
        if manager.has_errors():
            print("Validation errors:")
            for error in manager.validation_errors:
                print(f"  {error}")
        else:
            print("All cards valid!")

    # Test adding a card
    manager.add_card({
        'IMSI': '001010000000001',
        'ICCID': '8988211000000000001',
        'Ki': '00112233445566778899AABBCCDDEEFF',
        'OPc': 'ABCDEF0123456789ABCDEF0123456789',
    })

    # Save to new file
    manager.save_csv("output_cards.csv")
