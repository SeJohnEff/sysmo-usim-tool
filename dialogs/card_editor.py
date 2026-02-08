#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manual Card Editor Dialog - Read, Edit, Write single cards

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validators, DEFAULT_VALUES


class CardEditorDialog(tk.Toplevel):
    """Dialog for manually editing a single card configuration"""

    def __init__(self, parent, card_manager=None):
        super().__init__(parent)
        self.title("Card Editor - Read/Write Single Card")
        self.geometry("800x700")
        self.transient(parent)

        self.card_manager = card_manager
        self.card_data = DEFAULT_VALUES.copy()

        # Add basic required fields
        self.card_data.update({
            'IMSI': '',
            'ICCID': '',
            'Ki': '',
            'OPc': '',
        })

        self.show_advanced = tk.BooleanVar(value=False)
        self.validation_errors = {}

        self._create_widgets()
        self._update_validation()

    def _create_widgets(self):
        """Create main widget structure"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Basic tab
        self.basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.basic_frame, text="Basic Parameters")

        # Advanced tab
        self.advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.advanced_frame, text="Advanced Parameters")

        # Create scrollable frames
        self._create_basic_tab()
        self._create_advanced_tab()

        # Button bar at bottom
        self._create_button_bar()

    def _create_basic_tab(self):
        """Create basic parameters tab"""
        # Canvas for scrolling
        canvas = tk.Canvas(self.basic_frame)
        scrollbar = ttk.Scrollbar(self.basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.basic_entries = {}
        row = 0

        # Basic fields
        basic_fields = [
            ('IMSI', '15 digits', 'International Mobile Subscriber Identity'),
            ('ICCID', '19-20 digits', 'Integrated Circuit Card ID'),
            ('Ki', '32 hex chars (16 bytes)', 'Authentication Key'),
            ('OPc', '32 hex chars (16 bytes)', 'Operator Code (for MILENAGE)'),
            ('ALGO_2G', 'Algorithm name', '2G Authentication Algorithm'),
            ('ALGO_3G', 'Algorithm name', '3G Authentication Algorithm'),
            ('ALGO_4G5G', 'Algorithm name', '4G/5G Authentication Algorithm'),
            ('MNC_LENGTH', '1-3', 'MNC Length'),
            ('USE_OPC', '0 or 1', 'Use OPc (1) or OP (0)'),
        ]

        for field, hint, description in basic_fields:
            self._create_field(scrollable_frame, field, hint, description, row)
            row += 1

    def _create_advanced_tab(self):
        """Create advanced parameters tab"""
        # Canvas for scrolling
        canvas = tk.Canvas(self.advanced_frame)
        scrollbar = ttk.Scrollbar(self.advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.advanced_entries = {}
        row = 0

        # Milenage R parameters
        ttk.Label(scrollable_frame, text="Milenage R Parameters", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        row += 1

        for i in range(1, 6):
            field = f'MILENAGE_R{i}'
            self._create_field(scrollable_frame, field, '2 hex chars', f'Milenage R{i} parameter', row, advanced=True)
            row += 1

        # Milenage C parameters
        ttk.Label(scrollable_frame, text="Milenage C Parameters", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        row += 1

        for i in range(1, 6):
            field = f'MILENAGE_C{i}'
            self._create_field(scrollable_frame, field, '32 hex chars', f'Milenage C{i} parameter', row, advanced=True)
            row += 1

        # TUAK parameters
        ttk.Label(scrollable_frame, text="TUAK Parameters (SJA5 only)", font=('TkDefaultFont', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        row += 1

        tuak_fields = [
            ('TUAK_RES_SIZE', '32/64/128/256', 'TUAK RES Size in bits'),
            ('TUAK_MAC_SIZE', '64/128/256', 'TUAK MAC Size in bits'),
            ('TUAK_CKIK_SIZE', '128/256', 'TUAK CK/IK Size in bits'),
            ('TUAK_NUM_KECCAK', '0-255', 'Number of Keccak iterations'),
        ]

        for field, hint, description in tuak_fields:
            self._create_field(scrollable_frame, field, hint, description, row, advanced=True)
            row += 1

    def _create_field(self, parent, field_name, hint, description, row, advanced=False):
        """Create a single field with label, entry, and validation"""
        # Label
        label = ttk.Label(parent, text=f"{field_name}:", width=20)
        label.grid(row=row, column=0, sticky=tk.W, pady=3, padx=5)

        # Entry
        entry = ttk.Entry(parent, width=40)
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=3, padx=5)
        entry.insert(0, self.card_data.get(field_name, ''))

        # Bind validation
        entry.bind('<KeyRelease>', lambda e, f=field_name: self._validate_field(f))

        # Validation indicator
        indicator = ttk.Label(parent, text="", width=3)
        indicator.grid(row=row, column=2, sticky=tk.W, pady=3, padx=5)

        # Hint/description
        hint_label = ttk.Label(parent, text=f"{hint}", foreground="gray", font=('TkDefaultFont', 8))
        hint_label.grid(row=row, column=3, sticky=tk.W, pady=3, padx=5)

        # Store references
        if advanced:
            self.advanced_entries[field_name] = {
                'entry': entry,
                'indicator': indicator,
                'hint': hint_label
            }
        else:
            self.basic_entries[field_name] = {
                'entry': entry,
                'indicator': indicator,
                'hint': hint_label
            }

        parent.columnconfigure(1, weight=1)

    def _create_button_bar(self):
        """Create button bar with all actions"""
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Card operations (left side)
        card_ops = ttk.LabelFrame(button_frame, text="Card Operations", padding="5")
        card_ops.pack(side=tk.LEFT, padx=5)

        ttk.Button(card_ops, text="📖 Read from Card", command=self._read_card, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(card_ops, text="✍️ Write to Card", command=self._write_card, width=18).pack(side=tk.LEFT, padx=2)

        # File operations (center)
        file_ops = ttk.LabelFrame(button_frame, text="File Operations", padding="5")
        file_ops.pack(side=tk.LEFT, padx=5)

        ttk.Button(file_ops, text="📂 Load from File", command=self._load_file, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_ops, text="💾 Save to File", command=self._save_file, width=18).pack(side=tk.LEFT, padx=2)

        # Close button (right side)
        ttk.Button(button_frame, text="Close", command=self.destroy, width=12).pack(side=tk.RIGHT, padx=5)

        # Validation status
        self.validation_label = ttk.Label(button_frame, text="", foreground="gray")
        self.validation_label.pack(side=tk.RIGHT, padx=10)

    def _validate_field(self, field_name):
        """Validate a single field"""
        # Get entry from either basic or advanced
        if field_name in self.basic_entries:
            entry_dict = self.basic_entries[field_name]
        elif field_name in self.advanced_entries:
            entry_dict = self.advanced_entries[field_name]
        else:
            return

        entry = entry_dict['entry']
        indicator = entry_dict['indicator']
        value = entry.get()

        # Update card_data
        self.card_data[field_name] = value

        # Validate based on field type
        if field_name == 'IMSI':
            valid, error = Validators.validate_imsi(value)
        elif field_name == 'ICCID':
            valid, error = Validators.validate_iccid(value)
        elif field_name == 'Ki':
            valid, error = Validators.validate_ki(value)
        elif field_name == 'OPc':
            algo = self.card_data.get('ALGO_2G', 'MILENAGE')
            valid, error = Validators.validate_opc(value, algo)
        elif field_name.startswith('ALGO_'):
            valid, error = Validators.validate_algorithm(value)
        elif field_name == 'MNC_LENGTH':
            valid, error = Validators.validate_mnc_length(value)
        elif field_name.startswith('MILENAGE_R'):
            valid, error = Validators.validate_milenage_r(value, field_name)
        elif field_name.startswith('MILENAGE_C'):
            valid, error = Validators.validate_milenage_c(value, field_name)
        elif field_name == 'USE_OPC':
            valid, error = Validators.validate_boolean(value, field_name)
        elif field_name == 'TUAK_RES_SIZE':
            valid, error = Validators.validate_tuak_res_size(value)
        elif field_name == 'TUAK_MAC_SIZE':
            valid, error = Validators.validate_tuak_mac_size(value)
        elif field_name == 'TUAK_CKIK_SIZE':
            valid, error = Validators.validate_tuak_ckik_size(value)
        else:
            valid, error = True, None

        # Update indicator
        if not value:
            indicator.config(text="", foreground="gray")
            self.validation_errors.pop(field_name, None)
        elif valid:
            indicator.config(text="✓", foreground="green")
            self.validation_errors.pop(field_name, None)
        else:
            indicator.config(text="✗", foreground="red")
            self.validation_errors[field_name] = error

        self._update_validation()

    def _update_validation(self):
        """Update overall validation status"""
        if self.validation_errors:
            error_count = len(self.validation_errors)
            self.validation_label.config(
                text=f"❌ {error_count} validation error(s)",
                foreground="red"
            )
        else:
            # Check if required fields are filled
            required = ['IMSI', 'ICCID', 'Ki', 'OPc']
            missing = [f for f in required if not self.card_data.get(f)]
            if missing:
                self.validation_label.config(
                    text=f"⚠️ Missing required fields",
                    foreground="orange"
                )
            else:
                self.validation_label.config(
                    text="✓ All validations passed",
                    foreground="green"
                )

    def _read_card(self):
        """Read data from inserted card"""
        if not self.card_manager:
            messagebox.showerror("Error", "No card manager available")
            return

        if not self.card_manager.card:
            result = messagebox.askyesno(
                "Detect Card",
                "No card detected. Detect card now?"
            )
            if result:
                success, message = self.card_manager.detect_card()
                if not success:
                    messagebox.showerror("Detection Failed", message)
                    return

        if not self.card_manager.authenticated:
            messagebox.showwarning(
                "Not Authenticated",
                "Please authenticate with ADM1 key first.\n\n"
                "Use the main window to authenticate, then try again."
            )
            return

        # Read card data
        try:
            data = self.card_manager.read_card_data()
            if not data:
                messagebox.showerror("Error", "Failed to read card data")
                return

            # Update fields
            if data.get('imsi'):
                self._set_field_value('IMSI', data['imsi'])
            if data.get('iccid'):
                self._set_field_value('ICCID', data['iccid'])
            if data.get('mnc_length'):
                self._set_field_value('MNC_LENGTH', str(data['mnc_length']))

            messagebox.showinfo("Success", "Card data read successfully!\n\nNote: Ki and OPc cannot be read from card for security reasons.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read card: {e}")

    def _write_card(self):
        """Write data to card"""
        if not self.card_manager:
            messagebox.showerror("Error", "No card manager available")
            return

        if not self.card_manager.authenticated:
            messagebox.showerror(
                "Not Authenticated",
                "Please authenticate with ADM1 key first.\n\n"
                "Use the main window to authenticate."
            )
            return

        # Validate all fields
        if self.validation_errors:
            messagebox.showerror(
                "Validation Errors",
                f"Please fix {len(self.validation_errors)} validation error(s) before writing to card."
            )
            return

        # Check required fields
        required = ['IMSI', 'ICCID', 'Ki', 'OPc']
        missing = [f for f in required if not self.card_data.get(f)]
        if missing:
            messagebox.showerror(
                "Missing Fields",
                f"Please fill in required fields: {', '.join(missing)}"
            )
            return

        # Confirm write
        result = messagebox.askyesno(
            "Confirm Write",
            f"Write this configuration to card?\n\n"
            f"IMSI: {self.card_data.get('IMSI')}\n"
            f"ICCID: {self.card_data.get('ICCID')}\n\n"
            f"This will permanently modify the card!",
            icon=messagebox.WARNING
        )

        if not result:
            return

        # Write to card
        try:
            success, message = self.card_manager.program_card(self.card_data)

            if success:
                messagebox.showinfo("Success", "Card programmed successfully!")
            else:
                messagebox.showerror("Error", f"Failed to program card:\n{message}")

        except Exception as e:
            messagebox.showerror("Error", f"Programming error: {e}")

    def _load_file(self):
        """Load card configuration from file"""
        filename = filedialog.askopenfilename(
            title="Load Card Configuration",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Support both direct format and backup format
            if 'card_data' in data:
                # Backup format
                card_data = data['card_data']
                # Convert backup format to card editor format
                if 'authentication' in card_data:
                    auth = card_data['authentication']
                    data = {
                        'IMSI': str(card_data.get('imsi', '')),
                        'ICCID': str(card_data.get('iccid', '')),
                        'MNC_LENGTH': str(card_data.get('mnc_length', '2')),
                        'Ki': auth.get('ki', ''),
                        'OPc': auth.get('opc', ''),
                        'USE_OPC': '1' if auth.get('use_opc', True) else '0',
                        'ALGO_2G': auth.get('algo_2g', 'MILENAGE'),
                        'ALGO_3G': auth.get('algo_3g', 'MILENAGE'),
                        'ALGO_4G5G': auth.get('algo_4g5g', 'MILENAGE'),
                    }

            # Load values into fields
            for field, value in data.items():
                self._set_field_value(field, str(value))

            messagebox.showinfo("Success", f"Configuration loaded from:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def _save_file(self):
        """Save card configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Card Configuration",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        # Get all current values
        config = {}
        for field in list(self.basic_entries.keys()) + list(self.advanced_entries.keys()):
            value = self.card_data.get(field, '')
            if value:  # Only save non-empty fields
                config[field] = value

        # Add metadata
        save_data = {
            'version': '1.0',
            'type': 'card_configuration',
            'config': config
        }

        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            messagebox.showinfo("Success", f"Configuration saved to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def _set_field_value(self, field_name, value):
        """Set value of a field and trigger validation"""
        if field_name in self.basic_entries:
            entry = self.basic_entries[field_name]['entry']
        elif field_name in self.advanced_entries:
            entry = self.advanced_entries[field_name]['entry']
        else:
            return

        entry.delete(0, tk.END)
        entry.insert(0, value)
        self._validate_field(field_name)


# Test dialog
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dialog = CardEditorDialog(root)
    root.mainloop()
