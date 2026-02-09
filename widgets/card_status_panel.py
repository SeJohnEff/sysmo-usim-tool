#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Card Status Panel Widget

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import ModernTheme


class CardStatusPanel(ttk.LabelFrame):
    """Panel showing card detection and status"""

    def __init__(self, parent, **kwargs):
        padding = ModernTheme.get_padding('medium')
        super().__init__(parent, text="Card Status", padding=padding, **kwargs)

        self._create_widgets()
        self.set_status("waiting", "Waiting for card...")

    def _create_widgets(self):
        """Create panel widgets"""
        pad_small = ModernTheme.get_padding('small')
        pad_medium = ModernTheme.get_padding('medium')

        # Status indicator with modern styling
        status_frame = ttk.Frame(self)
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, pad_medium))

        ttk.Label(status_frame, text="Status:", style='Subheading.TLabel').pack(
            side=tk.LEFT, padx=(0, pad_small))

        self.status_indicator = tk.Canvas(status_frame, width=12, height=12,
                                           bg=ModernTheme.get_color('panel_bg'),
                                           highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, pad_small))
        self.status_circle = self.status_indicator.create_oval(1, 1, 11, 11, fill='gray', outline='')

        self.status_label = ttk.Label(status_frame, text="Not detected")
        self.status_label.pack(side=tk.LEFT)

        # Info section with modern spacing
        info_pad = pad_small

        # Card type
        ttk.Label(self, text="Card Type:", width=12).grid(
            row=1, column=0, sticky=tk.W, pady=info_pad)
        self.card_type_label = ttk.Label(self, text="Unknown", style='Subheading.TLabel')
        self.card_type_label.grid(row=1, column=1, sticky=tk.W, pady=info_pad)

        # IMSI (read-only entry for easy copy)
        ttk.Label(self, text="IMSI:", width=12).grid(
            row=2, column=0, sticky=tk.W, pady=info_pad)
        self.imsi_var = tk.StringVar(value="-")
        self.imsi_entry = ttk.Entry(self, textvariable=self.imsi_var, state='readonly', width=20)
        self.imsi_entry.grid(row=2, column=1, sticky=tk.W, pady=info_pad)

        # ICCID (read-only entry for easy copy)
        ttk.Label(self, text="ICCID:", width=12).grid(
            row=3, column=0, sticky=tk.W, pady=info_pad)
        self.iccid_var = tk.StringVar(value="-")
        self.iccid_entry = ttk.Entry(self, textvariable=self.iccid_var, state='readonly', width=24)
        self.iccid_entry.grid(row=3, column=1, sticky=tk.W, pady=info_pad)

        # Authentication status
        ttk.Label(self, text="Auth Status:", width=12).grid(
            row=4, column=0, sticky=tk.W, pady=info_pad)
        self.auth_label = ttk.Label(self, text="Not authenticated",
                                     foreground=ModernTheme.get_color('warning'))
        self.auth_label.grid(row=4, column=1, sticky=tk.W, pady=info_pad)

        # Buttons with modern styling
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(pad_medium, 0))

        self.detect_button = ttk.Button(button_frame, text="Detect Card",
                                         command=self._on_detect, style='Primary.TButton')
        self.detect_button.grid(row=0, column=0, padx=(0, pad_small))

        self.auth_button = ttk.Button(
            button_frame, text="Authenticate", command=self._on_authenticate,
            state=tk.DISABLED, style='Primary.TButton'
        )
        self.auth_button.grid(row=0, column=1)

        # Callbacks
        self.on_detect_callback = None
        self.on_authenticate_callback = None

    def set_status(self, status: str, message: str):
        """
        Set card status

        Args:
            status: 'waiting', 'detected', 'authenticated', 'error'
            message: Status message
        """
        colors = {
            'waiting': ('gray', 'Waiting for card...'),
            'detected': ('yellow', 'Card detected'),
            'authenticated': ('green', 'Authenticated'),
            'error': ('red', 'Error'),
        }

        color, _ = colors.get(status, ('gray', message))
        self.status_indicator.itemconfig(self.status_circle, fill=color)
        self.status_label.config(text=message)

        # Enable/disable buttons based on status
        if status == 'detected':
            self.auth_button.config(state=tk.NORMAL)
        elif status == 'authenticated':
            self.auth_button.config(state=tk.DISABLED)
            self.detect_button.config(state=tk.DISABLED)
        else:
            self.auth_button.config(state=tk.DISABLED)

    def set_card_info(self, card_type: str = None, imsi: str = None, iccid: str = None):
        """Set card information"""
        if card_type:
            self.card_type_label.config(text=card_type)
        if imsi:
            self.imsi_var.set(imsi)
        if iccid:
            self.iccid_var.set(iccid)

    def set_auth_status(self, authenticated: bool, message: str = None):
        """Set authentication status"""
        if authenticated:
            self.auth_label.config(text="✓ Authenticated", foreground="green")
            self.auth_button.config(state=tk.DISABLED)
        else:
            text = message or "Not authenticated"
            self.auth_label.config(text=text, foreground="orange")

    def _on_detect(self):
        """Handle detect button"""
        if self.on_detect_callback:
            self.on_detect_callback()

    def _on_authenticate(self):
        """Handle authenticate button"""
        if self.on_authenticate_callback:
            self.on_authenticate_callback()

    def reset(self):
        """Reset panel to initial state"""
        self.set_status("waiting", "Waiting for card...")
        self.card_type_label.config(text="Unknown")
        self.imsi_var.set("-")
        self.iccid_var.set("-")
        self.auth_label.config(text="Not authenticated", foreground="orange")
        self.detect_button.config(state=tk.NORMAL)
        self.auth_button.config(state=tk.DISABLED)


# Test panel
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Card Status Panel Test")

    panel = CardStatusPanel(root)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Simulate detection
    def test_detect():
        panel.set_status("detected", "Card detected: sysmoISIM-SJA5")
        panel.set_card_info(card_type="sysmoISIM-SJA5", imsi="001010000000001", iccid="8988211000000000001")

    def test_auth():
        panel.set_status("authenticated", "Authenticated successfully")
        panel.set_auth_status(True)

    panel.on_detect_callback = test_detect
    panel.on_authenticate_callback = test_auth

    root.mainloop()
