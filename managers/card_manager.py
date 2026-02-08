#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Card Manager - Interface with physical SIM cards

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import sys
import os
from typing import Optional, Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.card_detector import CardDetector, CardType
from utils import asciihex_to_list, hexdump, ascii_to_list


class CardError(Exception):
    """Base class for card-related errors"""
    pass


class CardNotPresentError(CardError):
    """Card not inserted in reader"""
    pass


class CardAuthenticationError(CardError):
    """ADM1 authentication failed"""
    def __init__(self, remaining_attempts: int):
        self.remaining_attempts = remaining_attempts
        super().__init__(f"Authentication failed. {remaining_attempts} attempts remaining")


class CardLockError(CardError):
    """Card locked after failed authentication"""
    pass


class CardManager:
    """Manage card detection, authentication, and operations"""

    def __init__(self):
        self.card = None
        self.card_type = CardType.UNKNOWN
        self.authenticated = False
        self.atr = None

    def detect_card(self) -> Tuple[bool, str]:
        """
        Detect and initialize card

        Returns:
            Tuple of (success, message)
        """
        try:
            self.card_type, self.card = CardDetector.create_card_object()

            if self.card_type == CardType.UNKNOWN or self.card is None:
                return False, "No card detected or unknown card type"

            # Get ATR
            try:
                self.atr = self.card.sim.card.get_ATR()
            except:
                self.atr = None

            card_name = CardDetector.get_card_type_name(self.card_type)
            return True, f"Card detected: {card_name}"

        except Exception as e:
            self.card = None
            self.card_type = CardType.UNKNOWN
            return False, f"Error detecting card: {str(e)}"

    def authenticate(self, adm1: str, force: bool = False) -> Tuple[bool, str]:
        """
        Authenticate with ADM1 key

        Args:
            adm1: 8-digit ADM1 key
            force: Force authentication even if attempts < 3

        Returns:
            Tuple of (success, message)
        """
        if self.card is None:
            return False, "No card detected"

        try:
            # Convert ADM1 to byte list
            from utils import ascii_to_list
            adm1_bytes = ascii_to_list(adm1)

            # Authenticate using card's method
            success = self.card.admin_auth(adm1_bytes, force)

            if success:
                self.authenticated = True
                return True, "Authentication successful"
            else:
                # Get remaining attempts
                try:
                    from sysmo_usim import SYSMO_USIM_ADM1
                    attempts = self.card.sim.chv_retrys(SYSMO_USIM_ADM1)
                    if attempts == 0:
                        raise CardLockError()
                    raise CardAuthenticationError(attempts)
                except CardLockError:
                    return False, "Card is locked! No attempts remaining."
                except CardAuthenticationError as e:
                    return False, str(e)
                except:
                    return False, "Authentication failed"

        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    def read_card_data(self) -> Optional[Dict[str, any]]:
        """
        Read all card data for backup

        Returns:
            Dictionary with card data or None on error
        """
        if not self.authenticated:
            return None

        try:
            data = {
                'card_type': self.card_type.name,
                'atr': self.atr if self.atr else [],
            }

            # Read IMSI
            try:
                imsi_raw = self.card.sim.read_imsi()
                # IMSI is BCD encoded, need to decode
                data['imsi'] = self._decode_imsi(imsi_raw)
            except:
                data['imsi'] = None

            # Read ICCID
            try:
                iccid_raw = self.card.sim.read_iccid()
                data['iccid'] = self._decode_iccid(iccid_raw)
            except:
                data['iccid'] = None

            # Read MNC length
            try:
                mnc_len = self.card.sim.read_ad()
                if mnc_len and len(mnc_len) > 3:
                    data['mnc_length'] = mnc_len[3]
            except:
                data['mnc_length'] = None

            # Read authentication key (Ki)
            # Note: This requires card-specific methods
            # For now, we'll mark it as not readable (security)
            data['ki_readable'] = False

            # Read algorithm settings (if available)
            # This is card-specific and may not be directly readable

            return data

        except Exception as e:
            print(f"Error reading card data: {e}")
            return None

    def program_card(self, card_data: Dict[str, str]) -> Tuple[bool, str]:
        """
        Program card with configuration

        Args:
            card_data: Dictionary with card parameters

        Returns:
            Tuple of (success, message)
        """
        if not self.authenticated:
            return False, "Not authenticated"

        try:
            # Program IMSI
            if 'IMSI' in card_data and card_data['IMSI']:
                imsi = self._encode_imsi(card_data['IMSI'])
                self.card.sim.write_imsi(imsi)

            # Program ICCID (if supported)
            if 'ICCID' in card_data and card_data['ICCID']:
                iccid = self._encode_iccid(card_data['ICCID'])
                try:
                    self.card.sim.write_iccid(iccid)
                except:
                    pass  # Not all cards support ICCID writing

            # Program Ki
            if 'Ki' in card_data and card_data['Ki']:
                ki = asciihex_to_list(card_data['Ki'])
                self.card.write_key_params(ki)

            # Program OPc/OP
            if 'OPc' in card_data and card_data['OPc']:
                opc = asciihex_to_list(card_data['OPc'])
                use_opc = card_data.get('USE_OPC', '1') == '1'
                self.card.write_opc_params(1 if use_opc else 0, opc)

            # Program algorithms
            algo_2g = card_data.get('ALGO_2G', 'MILENAGE')
            algo_3g = card_data.get('ALGO_3G', 'MILENAGE')
            algo_4g5g = card_data.get('ALGO_4G5G', '')

            if algo_4g5g and hasattr(self.card, 'write_auth_params'):
                # SJA2/SJA5 with 4G/5G support
                self.card.write_auth_params(algo_2g, algo_3g, algo_4g5g)
            else:
                # SJS1 or older cards
                self.card.write_auth_params(algo_2g, algo_3g)

            # Program MNC length
            if 'MNC_LENGTH' in card_data and card_data['MNC_LENGTH']:
                mnc_len = int(card_data['MNC_LENGTH'])
                self.card.write_mnclen([mnc_len])

            # Program Milenage parameters (if provided)
            if 'MILENAGE_R1' in card_data:
                self._program_milenage_params(card_data)

            # Program TUAK parameters (if SJA5 and provided)
            if self.card_type == CardType.SJA5 and 'TUAK_RES_SIZE' in card_data:
                self._program_tuak_params(card_data)

            return True, "Card programmed successfully"

        except Exception as e:
            return False, f"Programming error: {str(e)}"

    def verify_card(self, expected_data: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Verify card data matches expected values

        Args:
            expected_data: Expected card parameters

        Returns:
            Tuple of (all_match, list_of_mismatches)
        """
        if not self.authenticated:
            return False, ["Not authenticated"]

        mismatches = []

        try:
            # Read current data
            current_data = self.read_card_data()
            if not current_data:
                return False, ["Could not read card data"]

            # Compare IMSI
            if 'IMSI' in expected_data and current_data.get('imsi'):
                if current_data['imsi'] != expected_data['IMSI']:
                    mismatches.append(f"IMSI: expected {expected_data['IMSI']}, got {current_data['imsi']}")

            # Compare ICCID
            if 'ICCID' in expected_data and current_data.get('iccid'):
                if current_data['iccid'] != expected_data['ICCID']:
                    mismatches.append(f"ICCID: expected {expected_data['ICCID']}, got {current_data['iccid']}")

            return len(mismatches) == 0, mismatches

        except Exception as e:
            return False, [f"Verification error: {str(e)}"]

    def _encode_imsi(self, imsi: str) -> List[int]:
        """Encode IMSI string to BCD format"""
        # IMSI encoding: length byte + BCD encoded digits
        encoded = [len(imsi)]
        for i in range(0, len(imsi), 2):
            if i + 1 < len(imsi):
                byte = int(imsi[i+1]) << 4 | int(imsi[i])
            else:
                byte = 0xF0 | int(imsi[i])
            encoded.append(byte)
        return encoded

    def _decode_imsi(self, imsi_raw: List[int]) -> str:
        """Decode IMSI from BCD format"""
        if not imsi_raw or len(imsi_raw) < 2:
            return None

        imsi = ""
        length = imsi_raw[0]
        for byte in imsi_raw[1:]:
            digit1 = byte & 0x0F
            digit2 = (byte >> 4) & 0x0F
            if digit1 != 0xF:
                imsi += str(digit1)
            if digit2 != 0xF:
                imsi += str(digit2)
            if len(imsi) >= length:
                break
        return imsi

    def _encode_iccid(self, iccid: str) -> List[int]:
        """Encode ICCID string to nibble-swapped format"""
        encoded = []
        for i in range(0, len(iccid), 2):
            if i + 1 < len(iccid):
                byte = int(iccid[i+1]) << 4 | int(iccid[i])
            else:
                byte = 0xF0 | int(iccid[i])
            encoded.append(byte)
        return encoded

    def _decode_iccid(self, iccid_raw: List[int]) -> str:
        """Decode ICCID from nibble-swapped format"""
        if not iccid_raw:
            return None

        iccid = ""
        for byte in iccid_raw:
            digit1 = byte & 0x0F
            digit2 = (byte >> 4) & 0x0F
            if digit1 != 0xF:
                iccid += str(digit1)
            if digit2 != 0xF:
                iccid += str(digit2)
        return iccid

    def _program_milenage_params(self, card_data: Dict[str, str]):
        """Program Milenage R and C parameters"""
        try:
            # Build 85-byte Milenage config structure
            r_params = []
            for i in range(1, 6):
                r_val = card_data.get(f'MILENAGE_R{i}', '')
                if r_val:
                    r_params.extend(asciihex_to_list(r_val))

            c_params = []
            for i in range(1, 6):
                c_val = card_data.get(f'MILENAGE_C{i}', '')
                if c_val:
                    c_params.extend(asciihex_to_list(c_val))

            if len(r_params) == 5 and len(c_params) == 80:
                milenage_cfg = r_params + c_params
                self.card.write_milenage_params(milenage_cfg)

        except Exception as e:
            print(f"Error programming Milenage params: {e}")

    def _program_tuak_params(self, card_data: Dict[str, str]):
        """Program TUAK parameters (SJA5 only)"""
        try:
            res_size = card_data.get('TUAK_RES_SIZE', '128')
            mac_size = card_data.get('TUAK_MAC_SIZE', '128')
            ckik_size = card_data.get('TUAK_CKIK_SIZE', '128')
            num_keccak = card_data.get('TUAK_NUM_KECCAK', '12')

            if hasattr(self.card, 'write_tuak_cfg'):
                self.card.write_tuak_cfg(res_size, mac_size, ckik_size, num_keccak)

        except Exception as e:
            print(f"Error programming TUAK params: {e}")

    def get_remaining_attempts(self) -> Optional[int]:
        """Get remaining ADM1 authentication attempts"""
        if self.card is None:
            return None

        try:
            from sysmo_usim import SYSMO_USIM_ADM1
            return self.card.sim.chv_retrys(SYSMO_USIM_ADM1)
        except:
            return None

    def disconnect(self):
        """Disconnect from card"""
        self.card = None
        self.card_type = CardType.UNKNOWN
        self.authenticated = False
        self.atr = None
