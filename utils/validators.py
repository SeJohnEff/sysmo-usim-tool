#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation rules for SIM card parameters

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import re
from typing import Dict, List, Tuple, Optional


class ValidationError(Exception):
    """Validation error with row, column, and message"""
    def __init__(self, row: int, column: str, message: str):
        self.row = row
        self.column = column
        self.message = message
        super().__init__(f"Row {row}, Column '{column}': {message}")


class Validators:
    """Validation rules for SIM card parameters"""

    # Supported algorithms by card type
    ALGORITHMS_SJA2 = ['COMP128v1', 'COMP128v2', 'COMP128v3', 'MILENAGE', 'SHA1-AKA', 'XOR']
    ALGORITHMS_SJA5 = ALGORITHMS_SJA2 + ['XOR-2G', 'TUAK']
    ALGORITHMS_SJS1 = ALGORITHMS_SJA2  # Same as SJA2

    # Algorithms requiring OPc
    ALGORITHMS_NEEDING_OPC = ['MILENAGE', 'SHA1-AKA', 'TUAK']

    @staticmethod
    def validate_imsi(value: str) -> Tuple[bool, Optional[str]]:
        """Validate IMSI - 15 digits"""
        if not value or len(value) == 0:
            return False, "IMSI is required"
        if not re.match(r'^\d{15}$', value):
            return False, "IMSI must be exactly 15 digits"
        return True, None

    @staticmethod
    def validate_iccid(value: str) -> Tuple[bool, Optional[str]]:
        """Validate ICCID - 19-20 digits"""
        if not value or len(value) == 0:
            return False, "ICCID is required"
        if not re.match(r'^\d{19,20}$', value):
            return False, "ICCID must be 19-20 digits"
        return True, None

    @staticmethod
    def validate_hex_string(value: str, expected_length: int, name: str) -> Tuple[bool, Optional[str]]:
        """Validate hex string of specific length"""
        if not value or len(value) == 0:
            return False, f"{name} is required"
        if not re.match(r'^[0-9A-Fa-f]+$', value):
            return False, f"{name} must contain only hexadecimal characters (0-9, A-F)"
        if len(value) != expected_length:
            return False, f"{name} must be exactly {expected_length} characters ({expected_length // 2} bytes)"
        return True, None

    @staticmethod
    def validate_ki(value: str) -> Tuple[bool, Optional[str]]:
        """Validate Ki - 32 hex characters (16 bytes) or 64 for TUAK"""
        if not value or len(value) == 0:
            return False, "Ki is required"
        if len(value) == 32:
            return Validators.validate_hex_string(value, 32, "Ki")
        elif len(value) == 64:
            return Validators.validate_hex_string(value, 64, "Ki (256-bit)")
        else:
            return False, "Ki must be 32 characters (128-bit) or 64 characters (256-bit)"

    @staticmethod
    def validate_opc(value: str, algo: str = 'MILENAGE') -> Tuple[bool, Optional[str]]:
        """Validate OPc - 32 hex characters for Milenage, 64 for TUAK"""
        if algo not in Validators.ALGORITHMS_NEEDING_OPC:
            return True, None  # Not required for this algorithm

        if not value or len(value) == 0:
            return False, f"OPc is required for {algo} algorithm"

        if algo == 'TUAK':
            return Validators.validate_hex_string(value, 64, "OPc/TOPc")
        else:
            return Validators.validate_hex_string(value, 32, "OPc")

    @staticmethod
    def validate_algorithm(value: str, card_type: str = 'SJA5') -> Tuple[bool, Optional[str]]:
        """Validate algorithm name"""
        if not value or len(value) == 0:
            return False, "Algorithm is required"

        if card_type == 'SJA2':
            valid_algos = Validators.ALGORITHMS_SJA2
        elif card_type == 'SJA5':
            valid_algos = Validators.ALGORITHMS_SJA5
        elif card_type == 'SJS1':
            valid_algos = Validators.ALGORITHMS_SJS1
        else:
            valid_algos = Validators.ALGORITHMS_SJA5  # Default to most permissive

        if value not in valid_algos:
            return False, f"Algorithm must be one of: {', '.join(valid_algos)}"
        return True, None

    @staticmethod
    def validate_mnc_length(value: str) -> Tuple[bool, Optional[str]]:
        """Validate MNC length - 1 or 2"""
        if not value or len(value) == 0:
            return False, "MNC length is required"
        try:
            mnc_len = int(value)
            if mnc_len not in [1, 2, 3]:
                return False, "MNC length must be 1, 2, or 3"
            return True, None
        except ValueError:
            return False, "MNC length must be a number"

    @staticmethod
    def validate_boolean(value: str, name: str) -> Tuple[bool, Optional[str]]:
        """Validate boolean value - 0, 1, true, false"""
        if not value or len(value) == 0:
            return True, None  # Optional, defaults to 0
        if value.lower() in ['0', '1', 'true', 'false', 'yes', 'no']:
            return True, None
        return False, f"{name} must be 0/1 or true/false"

    @staticmethod
    def validate_integer_range(value: str, name: str, min_val: int, max_val: int) -> Tuple[bool, Optional[str]]:
        """Validate integer within range"""
        if not value or len(value) == 0:
            return True, None  # Optional
        try:
            int_val = int(value)
            if int_val < min_val or int_val > max_val:
                return False, f"{name} must be between {min_val} and {max_val}"
            return True, None
        except ValueError:
            return False, f"{name} must be a number"

    @staticmethod
    def validate_milenage_r(value: str, name: str) -> Tuple[bool, Optional[str]]:
        """Validate Milenage R parameter - 2 hex characters (1 byte)"""
        if not value or len(value) == 0:
            return True, None  # Optional, has defaults
        return Validators.validate_hex_string(value, 2, name)

    @staticmethod
    def validate_plmn(value: str) -> Tuple[bool, Optional[str]]:
        """Validate PLMN - 5 or 6 digits (MCC + MNC)"""
        if not value or len(value) == 0:
            return True, None  # Optional
        if not re.match(r'^\d{5,6}$', value):
            return False, "PLMN must be 5-6 digits (MCC + MNC)"
        return True, None

    @staticmethod
    def validate_routing_indicator(value: str) -> Tuple[bool, Optional[str]]:
        """Validate Routing Indicator - 4 hex digits"""
        if not value or len(value) == 0:
            return True, None  # Optional, defaults to 0000
        if not re.match(r'^[0-9A-Fa-f]{4}$', value):
            return False, "Routing Indicator must be 4 hexadecimal digits"
        return True, None

    @staticmethod
    def validate_hnet_pubkey(value: str) -> Tuple[bool, Optional[str]]:
        """Validate Home Network Public Key - 64 hex characters (32 bytes) for ECIES Profile A"""
        if not value or len(value) == 0:
            return True, None  # Optional for non-5G cards
        if not re.match(r'^[0-9A-Fa-f]{64}$', value):
            return False, "Home Network Public Key must be 64 hexadecimal characters (32 bytes)"
        return True, None

    @staticmethod
    def validate_protection_scheme(value: str) -> Tuple[bool, Optional[str]]:
        """Validate Protection Scheme ID - 0 (Null), 1 (ProfileA/ECIES), 2 (ProfileB)"""
        if not value or len(value) == 0:
            return True, None  # Optional, defaults to 1
        try:
            scheme = int(value)
            if scheme not in [0, 1, 2]:
                return False, "Protection Scheme ID must be 0 (Null), 1 (ProfileA), or 2 (ProfileB)"
            return True, None
        except ValueError:
            return False, "Protection Scheme ID must be a number"

    @staticmethod
    def validate_milenage_c(value: str, name: str) -> Tuple[bool, Optional[str]]:
        """Validate Milenage C parameter - 32 hex characters (16 bytes)"""
        if not value or len(value) == 0:
            return True, None  # Optional, has defaults
        return Validators.validate_hex_string(value, 32, name)

    @staticmethod
    def validate_tuak_res_size(value: str) -> Tuple[bool, Optional[str]]:
        """Validate TUAK RES size - 32, 64, 128, or 256"""
        if not value or len(value) == 0:
            return True, None  # Optional
        if value not in ['32', '64', '128', '256']:
            return False, "TUAK RES size must be 32, 64, 128, or 256"
        return True, None

    @staticmethod
    def validate_tuak_mac_size(value: str) -> Tuple[bool, Optional[str]]:
        """Validate TUAK MAC size - 64, 128, or 256"""
        if not value or len(value) == 0:
            return True, None  # Optional
        if value not in ['64', '128', '256']:
            return False, "TUAK MAC size must be 64, 128, or 256"
        return True, None

    @staticmethod
    def validate_tuak_ckik_size(value: str) -> Tuple[bool, Optional[str]]:
        """Validate TUAK CK/IK size - 128 or 256"""
        if not value or len(value) == 0:
            return True, None  # Optional
        if value not in ['128', '256']:
            return False, "TUAK CK/IK size must be 128 or 256"
        return True, None

    @staticmethod
    def validate_row(row_data: Dict[str, str], row_num: int, card_type: str = 'SJA5') -> List[ValidationError]:
        """Validate a complete row of CSV data"""
        errors = []

        # Required fields
        valid, error = Validators.validate_imsi(row_data.get('IMSI', ''))
        if not valid:
            errors.append(ValidationError(row_num, 'IMSI', error))

        valid, error = Validators.validate_iccid(row_data.get('ICCID', ''))
        if not valid:
            errors.append(ValidationError(row_num, 'ICCID', error))

        valid, error = Validators.validate_ki(row_data.get('Ki', ''))
        if not valid:
            errors.append(ValidationError(row_num, 'Ki', error))

        # Algorithm validation
        algo_2g = row_data.get('ALGO_2G', 'MILENAGE')
        valid, error = Validators.validate_algorithm(algo_2g, card_type)
        if not valid:
            errors.append(ValidationError(row_num, 'ALGO_2G', error))

        algo_3g = row_data.get('ALGO_3G', 'MILENAGE')
        valid, error = Validators.validate_algorithm(algo_3g, card_type)
        if not valid:
            errors.append(ValidationError(row_num, 'ALGO_3G', error))

        # OPc validation (depends on algorithm)
        valid, error = Validators.validate_opc(row_data.get('OPc', ''), algo_2g)
        if not valid:
            errors.append(ValidationError(row_num, 'OPc', error))

        valid, error = Validators.validate_mnc_length(row_data.get('MNC_LENGTH', '2'))
        if not valid:
            errors.append(ValidationError(row_num, 'MNC_LENGTH', error))

        # Optional advanced fields
        for i in range(1, 6):
            valid, error = Validators.validate_milenage_r(row_data.get(f'MILENAGE_R{i}', ''), f'MILENAGE_R{i}')
            if not valid:
                errors.append(ValidationError(row_num, f'MILENAGE_R{i}', error))

            valid, error = Validators.validate_milenage_c(row_data.get(f'MILENAGE_C{i}', ''), f'MILENAGE_C{i}')
            if not valid:
                errors.append(ValidationError(row_num, f'MILENAGE_C{i}', error))

        # TUAK parameters (if applicable)
        if card_type == 'SJA5':
            valid, error = Validators.validate_tuak_res_size(row_data.get('TUAK_RES_SIZE', ''))
            if not valid:
                errors.append(ValidationError(row_num, 'TUAK_RES_SIZE', error))

            valid, error = Validators.validate_tuak_mac_size(row_data.get('TUAK_MAC_SIZE', ''))
            if not valid:
                errors.append(ValidationError(row_num, 'TUAK_MAC_SIZE', error))

            valid, error = Validators.validate_tuak_ckik_size(row_data.get('TUAK_CKIK_SIZE', ''))
            if not valid:
                errors.append(ValidationError(row_num, 'TUAK_CKIK_SIZE', error))

        return errors


# Default values for optional parameters
DEFAULT_VALUES = {
    'USE_OPC': '1',
    'ALGO_2G': 'MILENAGE',
    'ALGO_3G': 'MILENAGE',
    'ALGO_4G5G': 'MILENAGE',
    'MNC_LENGTH': '2',
    'MILENAGE_R1': '40',
    'MILENAGE_R2': '00',
    'MILENAGE_R3': '20',
    'MILENAGE_R4': '40',
    'MILENAGE_R5': '60',
    'MILENAGE_C1': '00000000000000000000000000000000',
    'MILENAGE_C2': '00000000000000000000000000000001',
    'MILENAGE_C3': '00000000000000000000000000000002',
    'MILENAGE_C4': '00000000000000000000000000000004',
    'MILENAGE_C5': '00000000000000000000000000000008',
    'SQN_IND_SIZE_BITS': '5',
    'SQN_CHECK_ENABLED': '1',
    'SQN_AGE_LIMIT_ENABLED': '0',
    'SQN_MAX_DELTA_ENABLED': '1',
    'SQN_CHECK_SKIP_FIRST': '1',
    'TUAK_RES_SIZE': '128',
    'TUAK_MAC_SIZE': '128',
    'TUAK_CKIK_SIZE': '128',
    'TUAK_NUM_KECCAK': '12',
    # PLMN and network selection (critical for network registration)
    'HPLMN': '',  # Home PLMN (5-6 digits: MCC + MNC)
    'OPLMN_ACT': '',  # Operator PLMN list with Access Technology (optional)
    # 5G SUCI parameters (required for 5G SA networks)
    'ROUTING_INDICATOR': '0000',  # 4-digit routing indicator for SUCI
    'PROTECTION_SCHEME_ID': '1',  # 0=Null, 1=ProfileA (ECIES), 2=ProfileB
    'HNET_PUBKEY_ID': '1',  # Home network public key identifier (1-255)
    'HNET_PUBKEY': '',  # Home network public key (64 hex chars for ProfileA/ECIES)
}
