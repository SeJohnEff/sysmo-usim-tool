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
from utils import asciihex_to_list, ascii_to_list, pad_asciihex


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
        # Clear any previous card state first
        self.disconnect()

        try:
            self.card_type, self.card = CardDetector.create_card_object()

            if self.card_type == CardType.UNKNOWN or self.card is None:
                return False, "No card detected or unknown card type"

            # Get ATR
            try:
                self.atr = self.card.sim.card.get_ATR()
            except Exception:
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
                except Exception:
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

            # Read IMSI using pySim get_imsi() method
            try:
                data['imsi'] = self.card.sim.card.get_imsi()
            except Exception as e:
                print(f"ERROR: Failed to read IMSI: {e}")
                data['imsi'] = None

            # Read ICCID using pySim get_ICCID() method
            try:
                data['iccid'] = self.card.sim.card.get_ICCID()
            except Exception as e:
                print(f"ERROR: Failed to read ICCID: {e}")
                data['iccid'] = None

            # Read MNC length from AD file
            try:
                # Select and read EF_AD (Administrative Data)
                self.card.sim.select([0x7F, 0x20])  # Select DF_GSM
                self.card.sim.select([0x6F, 0xAD])  # Select EF_AD
                ad_response = self.card.sim.read_binary(4)
                # Extract data from Card_res_apdu object - use .apdu attribute
                ad_data = ad_response.apdu if hasattr(ad_response, 'apdu') else ad_response
                if ad_data and len(ad_data) > 3:
                    data['mnc_length'] = ad_data[3] & 0x0F
            except Exception as e:
                print(f"ERROR: Failed to read MNC length: {e}")
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
                self.card.write_imsi(imsi)

            # Program ICCID (if supported)
            if 'ICCID' in card_data and card_data['ICCID']:
                iccid = self._encode_iccid(card_data['ICCID'])
                try:
                    self.card.write_iccid(iccid)
                except Exception:
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

            # Program PLMN (Home PLMN for network selection)
            if 'HPLMN' in card_data and card_data['HPLMN']:
                self._program_plmn(card_data)

            # Program 5G SUCI parameters (SJA5 only, for 5G SA networks)
            if self.card_type == CardType.SJA5:
                if 'ROUTING_INDICATOR' in card_data or 'HNET_PUBKEY' in card_data:
                    self._program_5g_suci(card_data)

            # Program Access Technology preferences
            if 'OPLMN_ACT' in card_data and card_data['OPLMN_ACT']:
                self._program_access_technology(card_data)

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
        """Encode IMSI string to byte list for write_imsi().

        write_imsi() in sysmo_usim.py prepends the length and calls
        swap_nibbles(), so we must NOT do BCD encoding here.
        Match the CLI: asciihex_to_list(pad_asciihex(imsi, front=True, padding='9'))
        """
        return asciihex_to_list(pad_asciihex(imsi, True, '9'))

    def _decode_imsi(self, imsi_raw: List[int]) -> str:
        """Decode IMSI from the byte-list format returned by _encode_imsi."""
        if not imsi_raw or len(imsi_raw) < 1:
            return None
        # Each byte is two hex digits representing IMSI digits
        # First nibble of first byte is the padding '9', skip it
        hex_str = ''.join('{:02x}'.format(b) for b in imsi_raw)
        # Strip leading '9' padding (added by pad_asciihex)
        if len(hex_str) % 2 == 0 and hex_str.startswith('9'):
            hex_str = hex_str[1:]
        return hex_str

    def _encode_iccid(self, iccid: str) -> List[int]:
        """Encode ICCID string to byte list for write_iccid().

        write_iccid() in sysmo_usim.py calls swap_nibbles(), so we
        must NOT do nibble swapping here.
        Match the CLI: asciihex_to_list(pad_asciihex(iccid))
        """
        return asciihex_to_list(pad_asciihex(iccid))

    def _decode_iccid(self, iccid_raw: List[int]) -> str:
        """Decode ICCID from the byte-list format returned by _encode_iccid."""
        if not iccid_raw:
            return None
        hex_str = ''.join('{:02x}'.format(b) for b in iccid_raw)
        # Strip trailing 'f' padding
        return hex_str.rstrip('f')

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

    def _program_plmn(self, card_data: Dict[str, str]):
        """
        Program PLMN selector files for network selection
        Writes to EF.FPLMN, EF.PLMNsel, and EF.HPLMNwAcT
        """
        try:
            hplmn = card_data.get('HPLMN', '')
            if not hplmn or len(hplmn) < 5:
                return

            # Encode PLMN to nibble-swapped BCD (e.g., "24001" -> [0x42, 0xF0, 0x10])
            plmn_bytes = self._encode_plmn(hplmn)

            # Write to EF.PLMNsel (PLMN selector for automatic mode)
            # Each entry is 3 bytes, file typically holds 8-12 entries
            try:
                self.card.sim.select([0x7F, 0x20])  # DF_GSM
                self.card.sim.select([0x6F, 0x30])  # EF_PLMNsel
                # Write HPLMN as first entry, pad rest with 0xFF
                plmn_data = plmn_bytes + [0xFF] * 21  # 8 entries * 3 bytes = 24, minus first 3
                self.card.sim.update_binary(plmn_data[:24])
            except Exception as e:
                print(f"Warning: Could not write EF.PLMNsel: {e}")

            # Write to EF.HPLMNwAcT (Home PLMN with Access Technology)
            # Format: 3 bytes PLMN + 2 bytes AcT
            # AcT bits: 0x8000=UTRAN, 0x4000=E-UTRAN, 0x0080=GSM, 0x0040=GSM Compact, etc.
            try:
                self.card.sim.select([0x7F, 0x20])  # DF_GSM
                self.card.sim.select([0x6F, 0x62])  # EF_HPLMNwAcT

                # Determine Access Technology flags
                act_flags = self._get_access_technology_flags(card_data)

                # Write HPLMN + AcT flags
                hplmn_act_data = plmn_bytes + act_flags
                self.card.sim.update_binary(hplmn_act_data)
            except Exception as e:
                print(f"Warning: Could not write EF.HPLMNwAcT: {e}")

            # For USIM/ISIM, also write to ADF.USIM files
            if self.card_type in [CardType.SJA2, CardType.SJA5]:
                try:
                    # Select ADF.USIM
                    self.card.sim.select([0x7F, 0xFF])  # ADF.USIM (approximate, may vary)
                    # Similar operations for USIM files...
                except Exception:
                    pass  # Optional - some cards may not support

        except Exception as e:
            print(f"Error programming PLMN: {e}")

    def _program_5g_suci(self, card_data: Dict[str, str]):
        """
        Program 5G SUCI (Subscription Concealed Identifier) parameters
        Required for 5G SA network registration with privacy

        Writes to:
        - EF.SUCI_Calc_Info (protection scheme + home network public key)
        - EF.Routing_Indicator
        - EF.UST (enable service 124, disable 125)
        """
        try:
            # Get SUCI parameters from card_data
            routing_ind = card_data.get('ROUTING_INDICATOR', '0000')
            prot_scheme_id = int(card_data.get('PROTECTION_SCHEME_ID', '1'))  # 0=Null, 1=ProfileA, 2=ProfileB
            hnet_pubkey_id = int(card_data.get('HNET_PUBKEY_ID', '1'))
            hnet_pubkey = card_data.get('HNET_PUBKEY', '')

            # Only program if we have the public key
            if not hnet_pubkey:
                return

            # Select DF.5GS under ADF.USIM
            # File structure: ADF.USIM (7FFF) / DF.5GS (5FC0)
            try:
                self.card.sim.select([0x7F, 0xFF])  # ADF.USIM
                self.card.sim.select([0x5F, 0xC0])  # DF.5GS
            except Exception as e:
                print(f"Warning: Could not select DF.5GS: {e}")
                return

            # Program EF.SUCI_Calc_Info (6FE2)
            # This is a complex TLV structure containing:
            # - Protection scheme list (Tag 80)
            # - Home network public key list (Tag A0)
            try:
                self.card.sim.select([0x6F, 0xE2])  # EF.SUCI_Calc_Info

                # Build protection scheme entry: Priority(1) + Scheme ID(1) + Key Index(1)
                prot_scheme_tlv = [0x80, 0x03, 0x00, prot_scheme_id, 0x01]  # Priority 0, scheme ID, key index 1

                # Build home network public key entry
                # Tag A0, Length, Key ID(1), Key(32 bytes for Profile A)
                pubkey_bytes = asciihex_to_list(hnet_pubkey)
                pubkey_tlv = [0xA0, 1 + len(pubkey_bytes), hnet_pubkey_id] + pubkey_bytes

                # Combine into SUCI_Calc_Info structure
                suci_data = prot_scheme_tlv + pubkey_tlv

                self.card.sim.update_binary(suci_data)
            except Exception as e:
                print(f"Warning: Could not write EF.SUCI_Calc_Info: {e}")

            # Program EF.Routing_Indicator (6FE3)
            # 2 bytes BCD encoded routing indicator + 2 bytes padding
            try:
                self.card.sim.select([0x6F, 0xE3])  # EF.Routing_Indicator
                routing_bytes = asciihex_to_list(routing_ind) + [0xFF, 0xFF]
                self.card.sim.update_binary(routing_bytes[:4])
            except Exception as e:
                print(f"Warning: Could not write EF.Routing_Indicator: {e}")

            # Enable UST service 124 (SUCI calculation by ME)
            # Disable UST service 125 (SUCI calculation by USIM - not supported on 9FV)
            try:
                # Select EF.UST (USIM Service Table)
                self.card.sim.select([0x7F, 0xFF])  # ADF.USIM
                self.card.sim.select([0x6F, 0x38])  # EF.UST

                # Read current UST
                ust_data = self.card.sim.read_binary(16)  # Typically 16 bytes
                if hasattr(ust_data, 'apdu'):
                    ust_data = list(ust_data.apdu)
                else:
                    ust_data = list(ust_data)

                # Service 124: byte 15 (124/8 = 15), bit 4 (124 % 8 = 4)
                # Service 125: byte 15, bit 5
                ust_data[15] = (ust_data[15] | 0x10) & ~0x20  # Set bit 4, clear bit 5

                # Write back
                self.card.sim.update_binary(ust_data)
            except Exception as e:
                print(f"Warning: Could not update EF.UST: {e}")

        except Exception as e:
            print(f"Error programming 5G SUCI: {e}")

    def _program_access_technology(self, card_data: Dict[str, str]):
        """
        Program Operator PLMN list with Access Technology
        Writes to EF.OPLMNwAcT
        """
        try:
            oplmn_act = card_data.get('OPLMN_ACT', '')
            if not oplmn_act:
                return

            # Format: comma-separated PLMN:ACT pairs
            # Example: "24001:C080,24002:8000" means PLMN 24001 with E-UTRAN+GSM, PLMN 24002 with UTRAN

            self.card.sim.select([0x7F, 0x20])  # DF_GSM
            self.card.sim.select([0x6F, 0x61])  # EF_OPLMNwAcT

            # Parse and encode entries
            entries = oplmn_act.split(',')
            oplmn_data = []

            for entry in entries[:40]:  # Max 40 entries typically
                if ':' in entry:
                    plmn, act = entry.split(':')
                    plmn_bytes = self._encode_plmn(plmn.strip())
                    act_bytes = asciihex_to_list(act.strip())[:2]  # 2 bytes
                    oplmn_data.extend(plmn_bytes + act_bytes)

            # Pad to file size (40 entries * 5 bytes = 200 bytes)
            while len(oplmn_data) < 200:
                oplmn_data.append(0xFF)

            self.card.sim.update_binary(oplmn_data[:200])

        except Exception as e:
            print(f"Error programming Access Technology: {e}")

    def _encode_plmn(self, plmn: str) -> List[int]:
        """
        Encode PLMN to nibble-swapped BCD format
        Example: "24001" (MCC=240, MNC=01) -> [0x42, 0xF0, 0x10]
                 "310410" (MCC=310, MNC=410) -> [0x13, 0x04, 0x01]
        """
        if len(plmn) == 5:
            # 2-digit MNC: MCC=240, MNC=01
            # Result: [MCC2 MCC1] [MNC1 MCC3] [MNC2 Filler]
            return [
                int(plmn[1]) << 4 | int(plmn[0]),  # MCC digit 2, 1
                0xF0 | int(plmn[2]),                 # Filler (0xF), MCC digit 3
                int(plmn[4]) << 4 | int(plmn[3])   # MNC digit 2, 1
            ]
        elif len(plmn) == 6:
            # 3-digit MNC: MCC=310, MNC=410
            # Result: [MCC2 MCC1] [MNC3 MCC3] [MNC2 MNC1]
            return [
                int(plmn[1]) << 4 | int(plmn[0]),  # MCC digit 2, 1
                int(plmn[5]) << 4 | int(plmn[2]),  # MNC digit 3, MCC digit 3
                int(plmn[4]) << 4 | int(plmn[3])   # MNC digit 2, 1
            ]
        else:
            raise ValueError(f"Invalid PLMN length: {plmn}")

    def _get_access_technology_flags(self, card_data: Dict[str, str]) -> List[int]:
        """
        Get Access Technology flags based on algorithms configured
        Returns 2-byte flag indicating supported access technologies

        Bit flags (little endian):
        - 0x8000: UTRAN (3G)
        - 0x4000: E-UTRAN (4G LTE)
        - 0x2000: NR (5G)
        - 0x0080: GSM (2G)
        - 0x0040: GSM Compact
        """
        flags = 0x0000

        algo_2g = card_data.get('ALGO_2G', '')
        algo_3g = card_data.get('ALGO_3G', '')
        algo_4g5g = card_data.get('ALGO_4G5G', '')

        # Enable technologies based on algorithms
        if algo_2g:
            flags |= 0x0080  # GSM

        if algo_3g:
            flags |= 0x8000  # UTRAN (3G)

        if algo_4g5g:
            flags |= 0x4000  # E-UTRAN (4G)
            if algo_4g5g == 'TUAK' or 'TUAK' in algo_4g5g:
                flags |= 0x2000  # NR (5G) - TUAK indicates 5G support

        # Return as 2 bytes (big endian)
        return [(flags >> 8) & 0xFF, flags & 0xFF]

    def get_remaining_attempts(self) -> Optional[int]:
        """Get remaining ADM1 authentication attempts"""
        if self.card is None:
            return None

        try:
            from sysmo_usim import SYSMO_USIM_ADM1
            return self.card.sim.chv_retrys(SYSMO_USIM_ADM1)
        except Exception:
            return None

    def disconnect(self):
        """Disconnect from card"""
        self.card = None
        self.card_type = CardType.UNKNOWN
        self.authenticated = False
        self.atr = None
