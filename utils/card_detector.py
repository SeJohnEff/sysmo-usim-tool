#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Card type detection based on ATR (Answer To Reset)

(C) 2026 SysmoUSIM-Tool GUI Project
"""

from enum import Enum
import sys
import os

# Add parent directory to path to import card modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sysmo_isim_sja2 import Sysmo_isim_sja2, Sysmo_isim_sja5
from sysmo_usim_sjs1 import Sysmo_usim_sjs1


class CardType(Enum):
    """Supported card types"""
    UNKNOWN = 0
    SJA2 = 1
    SJA5 = 2
    SJS1 = 3


class CardDetector:
    """Detect card type based on ATR and create appropriate card object"""

    # ATR patterns from existing code
    # SJA2 ATR pattern
    SJA2_ATR_PREFIX = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                       0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x4C]  # "4C" = SJA2

    # SJA5 ATR patterns (multiple variants)
    SJA5_ATR_9FV = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                    0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x35]  # "35" = SJA5

    SJA5_ATR_SLM17 = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                      0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x34]

    SJA5_ATR_3FJ = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0xC7, 0x80, 0x31, 0xE0, 0x73,
                    0xFE, 0x21, 0x1B, 0x64, 0x10, 0x38, 0x0A, 0x00, 0x74]

    # SJS1 ATR pattern (from sysmo_usim_sjs1.py)
    SJS1_ATR = [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x31]  # "31" = SJS1

    @staticmethod
    def _atr_matches(atr: list, pattern: list, length: int = None) -> bool:
        """Check if ATR matches pattern up to specified length"""
        if length is None:
            length = len(pattern)
        if len(atr) < length:
            return False
        return atr[:length] == pattern[:length]

    @staticmethod
    def detect_card_type(atr: list) -> CardType:
        """
        Detect card type from ATR

        Args:
            atr: ATR as list of bytes

        Returns:
            CardType enum value
        """
        if not atr or len(atr) < 16:
            return CardType.UNKNOWN

        # Check SJA5 variants first (more specific)
        if CardDetector._atr_matches(atr, CardDetector.SJA5_ATR_9FV, 19):
            return CardType.SJA5
        if CardDetector._atr_matches(atr, CardDetector.SJA5_ATR_SLM17, 19):
            return CardType.SJA5
        if CardDetector._atr_matches(atr, CardDetector.SJA5_ATR_3FJ, 19):
            return CardType.SJA5

        # Check SJS1
        if CardDetector._atr_matches(atr, CardDetector.SJS1_ATR, 19):
            return CardType.SJS1

        # Check SJA2
        if CardDetector._atr_matches(atr, CardDetector.SJA2_ATR_PREFIX, 16):
            return CardType.SJA2

        return CardType.UNKNOWN

    @staticmethod
    def create_card_object(atr: list = None):
        """
        Create appropriate card object based on ATR

        Args:
            atr: ATR as list of bytes (optional, will auto-detect if None)

        Returns:
            Tuple of (card_type, card_object) or (CardType.UNKNOWN, None)
        """
        try:
            # If no ATR provided, try to detect card
            if atr is None:
                # Try to create SJA5 first (most recent card)
                # The constructor will automatically detect the card
                try:
                    card = Sysmo_isim_sja5()
                    # If we get here, SJA5 was detected successfully
                    return CardType.SJA5, card
                except Exception as e:
                    print(f"DEBUG: SJA5 detection failed: {e}")

                # Try SJA2
                try:
                    card = Sysmo_isim_sja2()
                    return CardType.SJA2, card
                except Exception as e:
                    print(f"DEBUG: SJA2 detection failed: {e}")

                # Try SJS1
                try:
                    card = Sysmo_usim_sjs1()
                    return CardType.SJS1, card
                except Exception as e:
                    print(f"DEBUG: SJS1 detection failed: {e}")

                # No card detected
                print("DEBUG: No supported card type detected")
                return CardType.UNKNOWN, None
            else:
                # ATR provided, create appropriate object
                card_type = CardDetector.detect_card_type(atr)

                if card_type == CardType.SJA2:
                    card = Sysmo_isim_sja2()
                elif card_type == CardType.SJA5:
                    card = Sysmo_isim_sja5()
                elif card_type == CardType.SJS1:
                    card = Sysmo_usim_sjs1()
                else:
                    return CardType.UNKNOWN, None

                return card_type, card

        except Exception as e:
            print(f"ERROR creating card object: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return CardType.UNKNOWN, None

    @staticmethod
    def get_card_type_name(card_type: CardType) -> str:
        """Get human-readable card type name"""
        names = {
            CardType.UNKNOWN: "Unknown",
            CardType.SJA2: "sysmoISIM-SJA2",
            CardType.SJA5: "sysmoISIM-SJA5",
            CardType.SJS1: "sysmoUSIM-SJS1",
        }
        return names.get(card_type, "Unknown")

    @staticmethod
    def atr_to_string(atr: list) -> str:
        """Convert ATR to human-readable hex string"""
        if not atr:
            return "No ATR"
        return ' '.join(f'{b:02X}' for b in atr)


# Example usage
if __name__ == "__main__":
    # Test with known ATRs
    test_atrs = {
        "SJA2": [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                 0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x4C, 0x75, 0x30, 0x34, 0x05, 0x4B, 0xA9],
        "SJA5": [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                 0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x35, 0x02, 0x59, 0xC4],
        "SJS1": [0x3B, 0x9F, 0x96, 0x80, 0x1F, 0x87, 0x80, 0x31, 0xE0, 0x73,
                 0xFE, 0x21, 0x1B, 0x67, 0x4A, 0x35, 0x75, 0x30, 0x31, 0x02, 0x65, 0xF8],
    }

    for name, atr in test_atrs.items():
        detected = CardDetector.detect_card_type(atr)
        atr_str = CardDetector.atr_to_string(atr)
        type_name = CardDetector.get_card_type_name(detected)
        print(f"{name}: {atr_str}")
        print(f"  Detected as: {type_name}")
        print()
