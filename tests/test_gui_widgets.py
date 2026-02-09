"""
Tests for real GUI widgets (widgets/ and dialogs/).
Skipped automatically on headless systems without a display.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _display_available():
    """Check if a display is available for tkinter."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False


HAS_DISPLAY = _display_available()


@unittest.skipUnless(HAS_DISPLAY, "No display available (headless)")
class TestCardStatusPanel(unittest.TestCase):

    def setUp(self):
        import tkinter as tk
        from theme import ModernTheme
        self.root = tk.Tk()
        self.root.withdraw()
        ModernTheme.apply_theme(self.root)
        from widgets.card_status_panel import CardStatusPanel
        self.panel = CardStatusPanel(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        self.assertIsNotNone(self.panel)

    def test_set_status_detected(self):
        self.panel.set_status("detected", "Card detected: SJA5")
        self.assertEqual(self.panel.status_label.cget("text"), "Card detected: SJA5")

    def test_set_status_authenticated(self):
        self.panel.set_status("authenticated", "Authenticated")
        self.assertEqual(self.panel.status_label.cget("text"), "Authenticated")

    def test_set_status_error(self):
        self.panel.set_status("error", "Card error")
        self.assertEqual(self.panel.status_label.cget("text"), "Card error")

    def test_set_card_info(self):
        self.panel.set_card_info(card_type="sysmoISIM-SJA5",
                                 imsi="001010000000001",
                                 iccid="8988211000000000001")
        self.assertEqual(self.panel.card_type_label.cget("text"), "sysmoISIM-SJA5")
        self.assertEqual(self.panel.imsi_label.cget("text"), "001010000000001")
        self.assertEqual(self.panel.iccid_label.cget("text"), "8988211000000000001")

    def test_set_auth_status_true(self):
        self.panel.set_auth_status(True)
        text = self.panel.auth_label.cget("text")
        self.assertIn("Authenticated", text)

    def test_set_auth_status_false(self):
        self.panel.set_auth_status(False, "Wrong ADM1")
        self.assertEqual(self.panel.auth_label.cget("text"), "Wrong ADM1")

    def test_reset(self):
        self.panel.set_card_info(card_type="SJA5", imsi="001")
        self.panel.reset()
        self.assertEqual(self.panel.card_type_label.cget("text"), "Unknown")

    def test_callbacks_default_none(self):
        self.assertIsNone(self.panel.on_detect_callback)
        self.assertIsNone(self.panel.on_authenticate_callback)

    def test_detect_callback(self):
        called = []
        self.panel.on_detect_callback = lambda: called.append(True)
        self.panel._on_detect()
        self.assertEqual(len(called), 1)

    def test_authenticate_callback(self):
        called = []
        self.panel.on_authenticate_callback = lambda: called.append(True)
        self.panel._on_authenticate()
        self.assertEqual(len(called), 1)

    def test_button_states_on_detected(self):
        import tkinter as tk
        self.panel.set_status("detected", "Found card")
        self.assertEqual(str(self.panel.auth_button.cget("state")), "normal")

    def test_button_states_on_authenticated(self):
        import tkinter as tk
        self.panel.set_status("authenticated", "Authed")
        self.assertIn("disabled", str(self.panel.auth_button.cget("state")))


@unittest.skipUnless(HAS_DISPLAY, "No display available (headless)")
class TestProgressPanel(unittest.TestCase):

    def setUp(self):
        import tkinter as tk
        from theme import ModernTheme
        self.root = tk.Tk()
        self.root.withdraw()
        ModernTheme.apply_theme(self.root)
        from widgets.progress_panel import ProgressPanel
        self.panel = ProgressPanel(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        self.assertIsNotNone(self.panel)
        self.assertEqual(self.panel.total_cards, 0)
        self.assertEqual(self.panel.current_card, 0)

    def test_set_total_cards(self):
        self.panel.set_total_cards(10)
        self.assertEqual(self.panel.total_cards, 10)
        self.assertIn("10", self.panel.card_number_label.cget("text"))

    def test_set_current_card(self):
        self.panel.set_total_cards(5)
        self.panel.set_current_card(3)
        self.assertEqual(self.panel.current_card, 3)
        self.assertIn("3", self.panel.card_number_label.cget("text"))
        self.assertEqual(self.panel.progress_bar['value'], 60)

    def test_set_status(self):
        self.panel.set_status("Programming IMSI...", "blue")
        self.assertEqual(self.panel.status_label.cget("text"), "Programming IMSI...")

    def test_update_stats(self):
        self.panel.update_stats(success=5, failed=1, skipped=2)
        self.assertEqual(self.panel.success_label.cget("text"), "5")
        self.assertEqual(self.panel.failed_label.cget("text"), "1")
        self.assertEqual(self.panel.skipped_label.cget("text"), "2")

    def test_reset(self):
        self.panel.set_total_cards(10)
        self.panel.set_current_card(5)
        self.panel.update_stats(success=3)
        self.panel.reset()
        self.assertEqual(self.panel.total_cards, 0)
        self.assertEqual(self.panel.current_card, 0)
        self.assertEqual(self.panel.success_label.cget("text"), "0")

    def test_set_running_true(self):
        import tkinter as tk
        self.panel.set_running(True)
        self.assertIn("disabled", str(self.panel.start_button.cget("state")))
        self.assertEqual(str(self.panel.stop_button.cget("state")), "normal")

    def test_set_running_false(self):
        import tkinter as tk
        self.panel.set_running(False)
        self.assertEqual(str(self.panel.start_button.cget("state")), "normal")
        self.assertIn("disabled", str(self.panel.stop_button.cget("state")))

    def test_callbacks(self):
        called = {}
        self.panel.on_start_callback = lambda: called.update(start=True)
        self.panel.on_pause_callback = lambda: called.update(pause=True)
        self.panel.on_skip_callback = lambda: called.update(skip=True)
        self.panel.on_stop_callback = lambda: called.update(stop=True)

        self.panel._on_start()
        self.panel._on_pause()
        self.panel._on_skip()
        self.panel._on_stop()

        self.assertTrue(called.get('start'))
        self.assertTrue(called.get('pause'))
        self.assertTrue(called.get('skip'))
        self.assertTrue(called.get('stop'))


@unittest.skipUnless(HAS_DISPLAY, "No display available (headless)")
class TestADM1Dialog(unittest.TestCase):

    def setUp(self):
        import tkinter as tk
        from theme import ModernTheme
        self.root = tk.Tk()
        self.root.withdraw()
        ModernTheme.apply_theme(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_init(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        self.assertIsNotNone(dialog)
        self.assertIsNone(dialog.adm1_value)
        dialog.destroy()

    def test_init_low_attempts(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=1)
        self.assertEqual(dialog.remaining_attempts, 1)
        dialog.destroy()

    def test_validate_valid_input(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog.adm1_entry.insert(0, "12345678")
        dialog._validate_input()
        text = dialog.validation_label.cget("text")
        self.assertIn("Valid", text)
        dialog.destroy()

    def test_validate_too_short(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog.adm1_entry.insert(0, "1234")
        dialog._validate_input()
        text = dialog.validation_label.cget("text")
        self.assertIn("more digits", text)
        dialog.destroy()

    def test_validate_non_digit(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog.adm1_entry.insert(0, "1234ABCD")
        dialog._validate_input()
        text = dialog.validation_label.cget("text")
        self.assertIn("digits", text.lower())
        dialog.destroy()

    def test_validate_too_long(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog.adm1_entry.insert(0, "123456789")
        dialog._validate_input()
        text = dialog.validation_label.cget("text")
        self.assertIn("Too many", text)
        dialog.destroy()

    def test_cancel(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog._on_cancel()
        self.assertIsNone(dialog.adm1_value)

    def test_ok_with_valid_input(self):
        from dialogs.adm1_dialog import ADM1Dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=3)
        dialog.adm1_entry.insert(0, "12345678")
        dialog._on_ok()
        self.assertEqual(dialog.adm1_value, "12345678")


if __name__ == '__main__':
    unittest.main()
