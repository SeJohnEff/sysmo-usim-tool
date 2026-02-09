#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ADM1 Key Input Dialog

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import ModernTheme


class ADM1Dialog(tk.Toplevel):
    """Dialog for entering ADM1 key"""

    def __init__(self, parent, remaining_attempts: int = 3):
        super().__init__(parent)
        self.title("Enter ADM1 Key")
        self.transient(parent)
        self.grab_set()
        self.configure(bg=ModernTheme.get_color('bg'))

        self.remaining_attempts = remaining_attempts
        self.adm1_value = None
        self.force_auth = tk.BooleanVar(value=False)

        self._create_widgets()
        self._center_window()

        self._setup_clipboard()

        # Focus on entry field
        self.adm1_entry.focus()

    def _setup_clipboard(self):
        """Setup clipboard bindings with sanitization for this dialog"""
        self.bind_class('Entry', '<Control-v>', self._paste_sanitized)
        self.bind_class('Entry', '<Command-v>', self._paste_sanitized)

    def _paste_sanitized(self, event):
        """Paste from clipboard, stripping non-printable characters"""
        try:
            widget = event.widget
            text = widget.clipboard_get()
            text = ''.join(ch for ch in text if ch.isprintable())
            if hasattr(widget, 'select_present') and widget.select_present():
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            widget.insert(tk.INSERT, text)
            self._validate_input()
            return 'break'
        except tk.TclError:
            pass

    def _create_widgets(self):
        """Create dialog widgets"""
        pad_small = ModernTheme.get_padding('small')
        pad_medium = ModernTheme.get_padding('medium')
        pad_large = ModernTheme.get_padding('large')

        # Main frame with modern padding
        main_frame = ttk.Frame(self, padding=pad_large)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Warning if attempts < 3
        if self.remaining_attempts < 3:
            warning_frame = ttk.Frame(main_frame, relief=tk.SOLID, borderwidth=2)
            warning_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E),
                               pady=(0, pad_medium))

            warning_label = ttk.Label(
                warning_frame,
                text=f"⚠️  WARNING: Only {self.remaining_attempts} attempts remaining!\nCard will lock after {self.remaining_attempts} more failed attempts!",
                foreground=ModernTheme.get_color('error'),
                font=ModernTheme.get_font('subheading'),
                padding=pad_medium
            )
            warning_label.grid(row=0, column=0)

        # ADM1 label with modern font
        ttk.Label(main_frame, text="ADM1 Key:", style='Subheading.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=(0, ModernTheme.get_padding('small'))
        )

        # ADM1 entry with larger font
        entry_font = (ModernTheme.get_font('default')[0], 16)
        self.adm1_entry = ttk.Entry(main_frame, width=12, font=entry_font)
        self.adm1_entry.grid(row=1, column=1, sticky=(tk.W, tk.E),
                             pady=(0, ModernTheme.get_padding('small')))
        self.adm1_entry.bind('<Return>', lambda e: self._on_ok())

        # Validation label
        self.validation_label = ttk.Label(main_frame, text="8 digits required",
                                           foreground=ModernTheme.get_color('disabled'),
                                           font=ModernTheme.get_font('small'))
        self.validation_label.grid(row=2, column=1, sticky=tk.W)

        # Bind validation
        self.adm1_entry.bind('<KeyRelease>', self._validate_input)

        # Force authentication checkbox (only if attempts < 3)
        if self.remaining_attempts < 3:
            force_check = ttk.Checkbutton(
                main_frame,
                text="Force authentication (risky!)",
                variable=self.force_auth
            )
            force_check.grid(row=3, column=0, columnspan=2, sticky=tk.W,
                             pady=ModernTheme.get_padding('small'))

        # Buttons with modern styling
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(pad_medium, 0))

        self.ok_button = ttk.Button(button_frame, text="Authenticate", command=self._on_ok,
                                      state=tk.DISABLED, style='Primary.TButton')
        self.ok_button.grid(row=0, column=0, padx=(0, ModernTheme.get_padding('small')))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.grid(row=0, column=1)

        # Help text with modern font
        help_text = ttk.Label(
            main_frame,
            text="The ADM1 key is unique to each card.\nIt should be printed on your card carrier.",
            font=ModernTheme.get_font('small'),
            foreground=ModernTheme.get_color('disabled')
        )
        help_text.grid(row=5, column=0, columnspan=2, pady=(pad_small, 0))

    def _validate_input(self, event=None):
        """Validate ADM1 input"""
        value = self.adm1_entry.get()

        if len(value) == 0:
            self.validation_label.config(text="8 digits required", foreground="gray")
            self.ok_button.config(state=tk.DISABLED)
        elif not value.isdigit():
            self.validation_label.config(text="Only digits allowed", foreground="red")
            self.ok_button.config(state=tk.DISABLED)
        elif len(value) < 8:
            self.validation_label.config(text=f"{8 - len(value)} more digits needed", foreground="orange")
            self.ok_button.config(state=tk.DISABLED)
        elif len(value) == 8:
            self.validation_label.config(text="✓ Valid format", foreground="green")
            self.ok_button.config(state=tk.NORMAL)
        else:
            self.validation_label.config(text="Too many digits", foreground="red")
            self.ok_button.config(state=tk.DISABLED)

    def _on_ok(self):
        """Handle OK button"""
        value = self.adm1_entry.get()

        if len(value) != 8 or not value.isdigit():
            messagebox.showerror("Invalid Input", "ADM1 key must be exactly 8 digits")
            return

        # Confirm if attempts < 3
        if self.remaining_attempts < 3 and not self.force_auth.get():
            result = messagebox.askyesno(
                "Confirm",
                f"You have only {self.remaining_attempts} attempts remaining.\n\n"
                "Are you SURE this ADM1 key is correct?\n\n"
                "Wrong key will lock your card!",
                icon=messagebox.WARNING
            )
            if not result:
                return

        self.adm1_value = value
        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button"""
        self.adm1_value = None
        self.destroy()

    def _center_window(self):
        """Center dialog on parent"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def get_adm1(self) -> tuple[str, bool]:
        """
        Get ADM1 key from user

        Returns:
            Tuple of (adm1_key, force_auth)
        """
        self.wait_window()
        return self.adm1_value, self.force_auth.get()


# Test dialog
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dialog = ADM1Dialog(root, remaining_attempts=2)
    adm1, force = dialog.get_adm1()

    if adm1:
        print(f"ADM1: {adm1}")
        print(f"Force: {force}")
    else:
        print("Cancelled")
