#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backup Manager - Create and restore JSON backups of card data

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path


class BackupManager:
    """Manage JSON backups of SIM card configurations"""

    BACKUP_VERSION = "1.0"
    DEFAULT_BACKUP_DIR = "backups"

    def __init__(self, backup_dir: str = None):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory for backups (default: ./backups)
        """
        self.backup_dir = backup_dir or self.DEFAULT_BACKUP_DIR
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)

    def create_backup(self, card_data: Dict, card_manager) -> Optional[str]:
        """
        Create JSON backup of card data

        Args:
            card_data: Card configuration dictionary
            card_manager: CardManager instance for reading current card state

        Returns:
            Backup filename or None on error
        """
        try:
            # Read current card state
            current_state = card_manager.read_card_data()

            # Build backup structure
            backup = {
                "backup_version": self.BACKUP_VERSION,
                "timestamp": datetime.now().isoformat(),
                "card_type": card_manager.card_type.name if card_manager.card_type else "UNKNOWN",
                "card_atr": self._atr_to_hex_string(card_manager.atr) if card_manager.atr else None,
                "card_data": {
                    "imsi": current_state.get('imsi') if current_state else card_data.get('IMSI'),
                    "iccid": current_state.get('iccid') if current_state else card_data.get('ICCID'),
                    "mnc_length": current_state.get('mnc_length') if current_state else card_data.get('MNC_LENGTH'),
                    "authentication": {
                        "algo_2g": card_data.get('ALGO_2G'),
                        "algo_3g": card_data.get('ALGO_3G'),
                        "algo_4g5g": card_data.get('ALGO_4G5G'),
                        "ki": card_data.get('Ki'),
                        "opc": card_data.get('OPc'),
                        "use_opc": card_data.get('USE_OPC', '1') == '1',
                    },
                    "milenage_params": {
                        "r1": card_data.get('MILENAGE_R1'),
                        "r2": card_data.get('MILENAGE_R2'),
                        "r3": card_data.get('MILENAGE_R3'),
                        "r4": card_data.get('MILENAGE_R4'),
                        "r5": card_data.get('MILENAGE_R5'),
                        "c1": card_data.get('MILENAGE_C1'),
                        "c2": card_data.get('MILENAGE_C2'),
                        "c3": card_data.get('MILENAGE_C3'),
                        "c4": card_data.get('MILENAGE_C4'),
                        "c5": card_data.get('MILENAGE_C5'),
                    },
                    "tuak_params": {
                        "res_size": card_data.get('TUAK_RES_SIZE'),
                        "mac_size": card_data.get('TUAK_MAC_SIZE'),
                        "ckik_size": card_data.get('TUAK_CKIK_SIZE'),
                        "num_keccak": card_data.get('TUAK_NUM_KECCAK'),
                    },
                },
                "can_restore": True,
                "notes": "Backup created by sysmo-usim-tool GUI"
            }

            # Generate filename
            iccid = current_state.get('iccid') if current_state else card_data.get('ICCID', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{iccid}_{timestamp}.json"
            filepath = os.path.join(self.backup_dir, filename)

            # Write backup file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup, f, indent=2)

            return filepath

        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def load_backup(self, filepath: str) -> Optional[Dict]:
        """
        Load backup from JSON file

        Args:
            filepath: Path to backup file

        Returns:
            Backup dictionary or None on error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                backup = json.load(f)

            # Validate backup version
            if backup.get('backup_version') != self.BACKUP_VERSION:
                print(f"Warning: Backup version mismatch. Expected {self.BACKUP_VERSION}, got {backup.get('backup_version')}")

            return backup

        except Exception as e:
            print(f"Error loading backup: {e}")
            return None

    def restore_backup(self, filepath: str, card_manager) -> tuple[bool, str]:
        """
        Restore card from backup file

        Args:
            filepath: Path to backup file
            card_manager: CardManager instance

        Returns:
            Tuple of (success, message)
        """
        try:
            # Load backup
            backup = self.load_backup(filepath)
            if not backup:
                return False, "Could not load backup file"

            if not backup.get('can_restore', False):
                return False, "This backup is marked as non-restorable"

            # Convert backup format to card_data format
            card_data = self._backup_to_card_data(backup)

            # Program card
            success, message = card_manager.program_card(card_data)

            return success, message

        except Exception as e:
            return False, f"Restore error: {str(e)}"

    def list_backups(self, iccid_filter: str = None) -> list[Dict]:
        """
        List available backups

        Args:
            iccid_filter: Optional ICCID to filter by

        Returns:
            List of backup info dictionaries
        """
        backups = []

        try:
            for filename in os.listdir(self.backup_dir):
                if not filename.endswith('.json'):
                    continue

                filepath = os.path.join(self.backup_dir, filename)

                # Load backup metadata
                try:
                    backup = self.load_backup(filepath)
                    if not backup:
                        continue

                    iccid = backup.get('card_data', {}).get('iccid')

                    # Apply filter
                    if iccid_filter and iccid != iccid_filter:
                        continue

                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'timestamp': backup.get('timestamp'),
                        'card_type': backup.get('card_type'),
                        'iccid': iccid,
                        'imsi': backup.get('card_data', {}).get('imsi'),
                    })

                except:
                    continue

            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            print(f"Error listing backups: {e}")

        return backups

    def delete_backup(self, filepath: str) -> bool:
        """
        Delete backup file

        Args:
            filepath: Path to backup file

        Returns:
            True if successful
        """
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False

    def export_to_csv_row(self, filepath: str) -> Optional[Dict[str, str]]:
        """
        Convert backup to CSV row format

        Args:
            filepath: Path to backup file

        Returns:
            Dictionary with CSV column values or None
        """
        try:
            backup = self.load_backup(filepath)
            if not backup:
                return None

            card_data = self._backup_to_card_data(backup)
            return card_data

        except Exception as e:
            print(f"Error exporting backup: {e}")
            return None

    def _backup_to_card_data(self, backup: Dict) -> Dict[str, str]:
        """Convert backup format to card_data format"""
        card_data = backup.get('card_data', {})
        auth = card_data.get('authentication', {})
        milenage = card_data.get('milenage_params', {})
        tuak = card_data.get('tuak_params', {})

        return {
            'IMSI': str(card_data.get('imsi', '')),
            'ICCID': str(card_data.get('iccid', '')),
            'MNC_LENGTH': str(card_data.get('mnc_length', '2')),
            'Ki': auth.get('ki', ''),
            'OPc': auth.get('opc', ''),
            'USE_OPC': '1' if auth.get('use_opc', True) else '0',
            'ALGO_2G': auth.get('algo_2g', 'MILENAGE'),
            'ALGO_3G': auth.get('algo_3g', 'MILENAGE'),
            'ALGO_4G5G': auth.get('algo_4g5g', 'MILENAGE'),
            'MILENAGE_R1': milenage.get('r1', ''),
            'MILENAGE_R2': milenage.get('r2', ''),
            'MILENAGE_R3': milenage.get('r3', ''),
            'MILENAGE_R4': milenage.get('r4', ''),
            'MILENAGE_R5': milenage.get('r5', ''),
            'MILENAGE_C1': milenage.get('c1', ''),
            'MILENAGE_C2': milenage.get('c2', ''),
            'MILENAGE_C3': milenage.get('c3', ''),
            'MILENAGE_C4': milenage.get('c4', ''),
            'MILENAGE_C5': milenage.get('c5', ''),
            'TUAK_RES_SIZE': tuak.get('res_size', ''),
            'TUAK_MAC_SIZE': tuak.get('mac_size', ''),
            'TUAK_CKIK_SIZE': tuak.get('ckik_size', ''),
            'TUAK_NUM_KECCAK': tuak.get('num_keccak', ''),
        }

    def _atr_to_hex_string(self, atr: list) -> str:
        """Convert ATR list to hex string"""
        if not atr:
            return ""
        return ' '.join(f'{b:02X}' for b in atr)


# Example usage
if __name__ == "__main__":
    manager = BackupManager()

    # List all backups
    backups = manager.list_backups()
    print(f"Found {len(backups)} backups:")
    for backup in backups:
        print(f"  {backup['filename']}: ICCID={backup['iccid']}, IMSI={backup['imsi']}")
