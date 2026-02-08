#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Editor Panel Widget

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from managers.csv_manager import CSVManager
from theme import ModernTheme


class CSVEditorPanel(ttk.LabelFrame):
    """Panel for editing CSV card configurations"""

    # Basic columns (always shown)
    BASIC_COLUMNS = ['#', 'IMSI', 'ICCID', 'Ki', 'OPc', 'ALGO_2G', 'ALGO_3G', 'MNC_LENGTH']

    def __init__(self, parent, **kwargs):
        padding = ModernTheme.get_padding('medium')
        super().__init__(parent, text="Card Configurations", padding=padding, **kwargs)

        self.csv_manager = CSVManager()
        self.show_advanced = tk.BooleanVar(value=False)

        self._create_widgets()

    def _create_widgets(self):
        """Create panel widgets"""
        pad_small = ModernTheme.get_padding('small')
        pad_medium = ModernTheme.get_padding('medium')

        # Toolbar with modern spacing
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, pad_small))

        ttk.Button(toolbar, text="Load CSV", command=self._on_load_csv).pack(
            side=tk.LEFT, padx=(0, pad_small))
        ttk.Button(toolbar, text="Save CSV", command=self._on_save_csv).pack(
            side=tk.LEFT, padx=(0, pad_small))
        ttk.Button(toolbar, text="Add Row", command=self._on_add_row).pack(
            side=tk.LEFT, padx=(0, pad_small))
        ttk.Button(toolbar, text="Delete Row", command=self._on_delete_row).pack(
            side=tk.LEFT, padx=(0, pad_medium))

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y,
                                                         padx=(0, pad_medium))

        ttk.Checkbutton(
            toolbar,
            text="Show Advanced Columns",
            variable=self.show_advanced,
            command=self._toggle_advanced
        ).pack(side=tk.LEFT, padx=(0, pad_small))

        self.card_count_label = ttk.Label(toolbar, text="Cards: 0",
                                           style='Subheading.TLabel')
        self.card_count_label.pack(side=tk.RIGHT, padx=pad_small)

        # Table frame with scrollbars
        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))

        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.BASIC_COLUMNS,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=10
        )
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        self.tree.column('#', width=30, anchor=tk.CENTER)
        self.tree.column('IMSI', width=120, anchor=tk.W)
        self.tree.column('ICCID', width=150, anchor=tk.W)
        self.tree.column('Ki', width=150, anchor=tk.W)
        self.tree.column('OPc', width=150, anchor=tk.W)
        self.tree.column('ALGO_2G', width=100, anchor=tk.CENTER)
        self.tree.column('ALGO_3G', width=100, anchor=tk.CENTER)
        self.tree.column('MNC_LENGTH', width=80, anchor=tk.CENTER)

        # Headers
        for col in self.BASIC_COLUMNS:
            self.tree.heading(col, text=col)

        # Grid weight for expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _on_load_csv(self):
        """Handle load CSV button"""
        filename = filedialog.askopenfilename(
            title="Load CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        if self.csv_manager.load_csv(filename):
            self._refresh_table()

            if self.csv_manager.has_errors():
                error_count = len(self.csv_manager.validation_errors)
                messagebox.showwarning(
                    "Validation Errors",
                    f"CSV loaded but contains {error_count} validation error(s).\n"
                    "Check the log for details."
                )
        else:
            messagebox.showerror("Error", "Failed to load CSV file")

    def _on_save_csv(self):
        """Handle save CSV button"""
        filename = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        include_advanced = self.show_advanced.get()
        if self.csv_manager.save_csv(filename, include_advanced):
            messagebox.showinfo("Success", "CSV file saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save CSV file")

    def _on_add_row(self):
        """Handle add row button"""
        # Add empty card with defaults
        from utils.validators import DEFAULT_VALUES
        new_card = DEFAULT_VALUES.copy()
        new_card.update({
            'IMSI': '001010000000000',
            'ICCID': '8988211000000000000',
            'Ki': '00000000000000000000000000000000',
            'OPc': '00000000000000000000000000000000',
        })
        self.csv_manager.add_card(new_card)
        self._refresh_table()

    def _on_delete_row(self):
        """Handle delete row button"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to delete")
            return

        # Get row index
        item = selection[0]
        index = self.tree.index(item)

        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Delete card #{index + 1}?")
        if result:
            self.csv_manager.remove_card(index)
            self._refresh_table()

    def _toggle_advanced(self):
        """Toggle advanced columns visibility"""
        # For now, this just changes the CSV save behavior
        # In a full implementation, this would add/remove columns from the tree
        pass

    def _refresh_table(self):
        """Refresh table with current CSV data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add cards
        for i, card in enumerate(self.csv_manager.cards):
            values = (
                i + 1,
                card.get('IMSI', ''),
                card.get('ICCID', ''),
                card.get('Ki', '')[:16] + '...',  # Truncate for display
                card.get('OPc', '')[:16] + '...',
                card.get('ALGO_2G', ''),
                card.get('ALGO_3G', ''),
                card.get('MNC_LENGTH', ''),
            )
            item_id = self.tree.insert('', tk.END, values=values)

            # Highlight errors
            errors = self.csv_manager.get_errors_for_row(i)
            if errors:
                self.tree.item(item_id, tags=('error',))

        # Configure error tag
        self.tree.tag_configure('error', background='#ffcccc')

        # Update count
        self.card_count_label.config(text=f"Cards: {self.csv_manager.get_card_count()}")

    def get_csv_manager(self) -> CSVManager:
        """Get the CSV manager instance"""
        return self.csv_manager


# Test panel
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV Editor Panel Test")
    root.geometry("900x400")

    panel = CSVEditorPanel(root)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Load test CSV if available
    import os
    test_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_cards.csv")
    if os.path.exists(test_csv):
        panel.csv_manager.load_csv(test_csv)
        panel._refresh_table()

    root.mainloop()
