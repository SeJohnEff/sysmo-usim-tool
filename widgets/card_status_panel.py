#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Card Status Panel Widget

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk


class CardStatusPanel(ttk.LabelFrame):
    """Panel showing card detection and status"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Card Status", padding="10", **kwargs)

        self._create_widgets()
        self.set_status("waiting", "Waiting for card...")

    def _create_widgets(self):
        """Create panel widgets"""
        # Status indicator
        status_frame = ttk.Frame(self)
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(status_frame, text="Status:", font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))

        self.status_indicator = tk.Canvas(status_frame, width=20, height=20)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, fill='gray', outline='')

        self.status_label = ttk.Label(status_frame, text="Not detected", font=('TkDefaultFont', 10))
        self.status_label.pack(side=tk.LEFT)

        # Card type
        ttk.Label(self, text="Card Type:", width=12).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.card_type_label = ttk.Label(self, text="Unknown", font=('TkDefaultFont', 10, 'bold'))
        self.card_type_label.grid(row=1, column=1, sticky=tk.W, pady=3)

        # IMSI
        ttk.Label(self, text="IMSI:", width=12).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.imsi_label = ttk.Label(self, text="-", foreground="gray")
        self.imsi_label.grid(row=2, column=1, sticky=tk.W, pady=3)

        # ICCID
        ttk.Label(self, text="ICCID:", width=12).grid(row=3, column=0, sticky=tk.W, pady=3)
        self.iccid_label = ttk.Label(self, text="-", foreground="gray")
        self.iccid_label.grid(row=3, column=1, sticky=tk.W, pady=3)

        # Authentication status
        ttk.Label(self, text="Auth Status:", width=12).grid(row=4, column=0, sticky=tk.W, pady=3)
        self.auth_label = ttk.Label(self, text="Not authenticated", foreground="orange")
        self.auth_label.grid(row=4, column=1, sticky=tk.W, pady=3)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        self.detect_button = ttk.Button(button_frame, text="Detect Card", command=self._on_detect)
        self.detect_button.grid(row=0, column=0, padx=5)

        self.auth_button = ttk.Button(
            button_frame, text="Authenticate", command=self._on_authenticate, state=tk.DISABLED
        )
        self.auth_button.grid(row=0, column=1, padx=5)

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
            self.imsi_label.config(text=imsi, foreground="black")
        if iccid:
            self.iccid_label.config(text=iccid, foreground="black")

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
        self.imsi_label.config(text="-", foreground="gray")
        self.iccid_label.config(text="-", foreground="gray")
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
