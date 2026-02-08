#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sysmo-USIM-Tool GUI - Main Application Window

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import managers
from managers.card_manager import CardManager, CardNotPresentError, CardAuthenticationError, CardLockError
from managers.csv_manager import CSVManager
from managers.backup_manager import BackupManager

# Import widgets
from widgets.card_status_panel import CardStatusPanel
from widgets.csv_editor_panel import CSVEditorPanel
from widgets.progress_panel import ProgressPanel

# Import dialogs
from dialogs.adm1_dialog import ADM1Dialog
from dialogs.card_editor import CardEditorDialog

# Import utils
from utils.card_detector import CardDetector


class SysmoUSIMToolGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Sysmo-USIM-Tool - Batch Programmer")
        self.root.geometry("1200x800")

        # Managers
        self.card_manager = CardManager()
        self.backup_manager = BackupManager()

        # State
        self.programming_in_progress = False
        self.current_card_index = 0

        self._create_menu()
        self._create_widgets()
        self._setup_bindings()

        self.log("Application started")
        self.log("Ready to load CSV or detect card")

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV...", command=self._load_csv_menu)
        file_menu.add_command(label="Save CSV...", command=self._save_csv_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Load card-parameters.txt...", command=self._load_card_params)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Card menu
        card_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Card", menu=card_menu)
        card_menu.add_command(label="Detect Card", command=self._detect_card)
        card_menu.add_command(label="Authenticate...", command=self._authenticate_card)
        card_menu.add_separator()
        card_menu.add_command(label="📝 Manual Card Editor...", command=self._open_card_editor)
        card_menu.add_separator()
        card_menu.add_command(label="Backup Current Card...", command=self._backup_card)

        # Batch menu
        batch_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Batch", menu=batch_menu)
        batch_menu.add_command(label="Start Batch Programming", command=self._start_batch)
        batch_menu.add_separator()
        batch_menu.add_command(label="IMSI Editor...", command=self._imsi_editor)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_widgets(self):
        """Create main widgets"""
        # Main container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)

        # Card status panel
        self.card_status_panel = CardStatusPanel(left_panel)
        self.card_status_panel.pack(fill=tk.X, pady=(0, 10))
        self.card_status_panel.on_detect_callback = self._detect_card
        self.card_status_panel.on_authenticate_callback = self._authenticate_card

        # CSV editor panel
        self.csv_editor_panel = CSVEditorPanel(left_panel)
        self.csv_editor_panel.pack(fill=tk.BOTH, expand=True)

        # Right panel
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)

        # Progress panel
        self.progress_panel = ProgressPanel(right_panel)
        self.progress_panel.pack(fill=tk.X, pady=(0, 10))
        self.progress_panel.on_start_callback = self._start_batch
        self.progress_panel.on_stop_callback = self._stop_batch

        # Log panel
        log_frame = ttk.LabelFrame(right_panel, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Log text widget
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=('Courier', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Log buttons
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_button_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_button_frame, text="Save Log", command=self._save_log).pack(side=tk.LEFT, padx=2)

    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Control-o>', lambda e: self._load_csv_menu())
        self.root.bind('<Control-s>', lambda e: self._save_csv_menu())
        self.root.bind('<Control-d>', lambda e: self._detect_card())
        self.root.bind('<F5>', lambda e: self._detect_card())

    def log(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

        # Color coding
        if level == "ERROR":
            # Find the line and apply red color
            pass

    def _detect_card(self):
        """Detect and display card information"""
        self.log("Detecting card...")
        self.card_status_panel.set_status("waiting", "Detecting card...")

        success, message = self.card_manager.detect_card()

        if success:
            self.log(f"Card detected: {message}", "SUCCESS")
            card_name = CardDetector.get_card_type_name(self.card_manager.card_type)
            self.card_status_panel.set_status("detected", message)
            self.card_status_panel.set_card_info(card_type=card_name)

            # Try to read basic info
            if self.card_manager.card:
                try:
                    data = self.card_manager.read_card_data()
                    if data:
                        self.card_status_panel.set_card_info(
                            imsi=data.get('imsi'),
                            iccid=data.get('iccid')
                        )
                except:
                    pass
        else:
            self.log(f"Card detection failed: {message}", "ERROR")
            self.card_status_panel.set_status("error", message)
            messagebox.showerror("Card Detection Failed", message)

    def _authenticate_card(self):
        """Authenticate with ADM1 key"""
        if not self.card_manager.card:
            messagebox.showwarning("No Card", "Please detect a card first")
            return

        # Get remaining attempts
        attempts = self.card_manager.get_remaining_attempts()
        if attempts is None:
            attempts = 3

        self.log(f"Authentication requested ({attempts} attempts remaining)")

        # Show ADM1 dialog
        dialog = ADM1Dialog(self.root, remaining_attempts=attempts)
        adm1, force = dialog.get_adm1()

        if not adm1:
            self.log("Authentication cancelled by user")
            return

        # Attempt authentication
        self.log(f"Attempting authentication...")
        success, message = self.card_manager.authenticate(adm1, force)

        if success:
            self.log("Authentication successful!", "SUCCESS")
            self.card_status_panel.set_status("authenticated", "Authenticated successfully")
            self.card_status_panel.set_auth_status(True)
            messagebox.showinfo("Success", "Authentication successful!")
        else:
            self.log(f"Authentication failed: {message}", "ERROR")
            messagebox.showerror("Authentication Failed", message)

    def _open_card_editor(self):
        """Open manual card editor dialog"""
        self.log("Opening manual card editor...")
        dialog = CardEditorDialog(self.root, card_manager=self.card_manager)
        # Dialog is modal, will block until closed

    def _backup_card(self):
        """Create backup of current card"""
        if not self.card_manager.authenticated:
            messagebox.showwarning("Not Authenticated", "Please authenticate first")
            return

        self.log("Creating backup...")

        # Get card data
        card_data = self.card_manager.read_card_data()
        if not card_data:
            messagebox.showerror("Error", "Could not read card data")
            return

        # Create backup
        filepath = self.backup_manager.create_backup(card_data, self.card_manager)

        if filepath:
            self.log(f"Backup created: {filepath}", "SUCCESS")
            messagebox.showinfo("Success", f"Backup created:\n{filepath}")
        else:
            self.log("Backup failed", "ERROR")
            messagebox.showerror("Error", "Failed to create backup")

    def _start_batch(self):
        """Start batch programming"""
        csv_manager = self.csv_editor_panel.get_csv_manager()
        card_count = csv_manager.get_card_count()

        if card_count == 0:
            messagebox.showwarning("No Cards", "Please load a CSV file with card configurations first")
            return

        # Validate CSV
        errors = csv_manager.validate_all()
        if errors:
            result = messagebox.askyesno(
                "Validation Errors",
                f"CSV contains {len(errors)} validation error(s).\n\n"
                "Continue anyway?",
                icon=messagebox.WARNING
            )
            if not result:
                return

        self.log(f"Starting batch programming for {card_count} cards")
        self.progress_panel.set_total_cards(card_count)
        self.progress_panel.set_running(True)
        self.programming_in_progress = True
        self.current_card_index = 0

        # Program first card
        self._program_next_card()

    def _program_next_card(self):
        """Program the next card in the batch"""
        csv_manager = self.csv_editor_panel.get_csv_manager()

        if self.current_card_index >= csv_manager.get_card_count():
            # Batch complete
            self._finish_batch()
            return

        card_data = csv_manager.get_card(self.current_card_index)
        card_num = self.current_card_index + 1

        self.log(f"--- Programming Card {card_num} ---")
        self.progress_panel.set_current_card(card_num)
        self.progress_panel.set_status(f"Programming card {card_num}...", "blue")

        # For now, simulate programming
        # In full implementation, this would:
        # 1. Prompt to insert card
        # 2. Detect card
        # 3. Authenticate
        # 4. Backup (optional)
        # 5. Program
        # 6. Verify
        # 7. Move to next

        messagebox.showinfo(
            "Insert Card",
            f"Please insert card {card_num}\n\n"
            f"IMSI: {card_data.get('IMSI')}\n"
            f"ICCID: {card_data.get('ICCID')}\n\n"
            "Click OK when ready."
        )

        # TODO: Actual programming logic here

        # For now, mark as success and move to next
        self.current_card_index += 1
        self.progress_panel.update_stats(success=self.current_card_index)

        # Continue with next card
        if self.programming_in_progress:
            self.root.after(100, self._program_next_card)

    def _stop_batch(self):
        """Stop batch programming"""
        self.programming_in_progress = False
        self.log("Batch programming stopped by user", "WARNING")
        self.progress_panel.set_status("Stopped by user", "orange")
        self.progress_panel.set_running(False)

    def _finish_batch(self):
        """Finish batch programming"""
        self.log("Batch programming complete!", "SUCCESS")
        self.progress_panel.set_status("Batch complete!", "green")
        self.progress_panel.set_running(False)
        messagebox.showinfo("Complete", "Batch programming finished!")

    def _load_csv_menu(self):
        """Load CSV from menu"""
        self.csv_editor_panel._on_load_csv()

    def _save_csv_menu(self):
        """Save CSV from menu"""
        self.csv_editor_panel._on_save_csv()

    def _load_card_params(self):
        """Load card-parameters.txt file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Load card-parameters.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filename:
            return

        csv_manager = self.csv_editor_panel.get_csv_manager()
        if csv_manager.load_card_parameters_file(filename):
            self.csv_editor_panel._refresh_table()
            self.log(f"Loaded {csv_manager.get_card_count()} cards from card-parameters file", "SUCCESS")
        else:
            messagebox.showerror("Error", "Failed to load card-parameters file")

    def _imsi_editor(self):
        """Show IMSI editor dialog"""
        messagebox.showinfo("Coming Soon", "IMSI Editor dialog will be implemented next!")

    def _clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared")

    def _save_log(self):
        """Save log to file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"Log saved to {filename}", "SUCCESS")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")

    def _show_about(self):
        """Show about dialog"""
        about_text = """Sysmo-USIM-Tool GUI
Batch Programmer for SysmoUSIM Cards

Version: 1.0.0
(C) 2026 SysmoUSIM-Tool GUI Project

Supports:
• sysmoISIM-SJA2
• sysmoISIM-SJA5
• sysmoUSIM-SJS1

Features:
• CSV batch programming
• Card backup/restore
• IMSI pattern generation
• TUAK support (5G)
"""
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SysmoUSIMToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
