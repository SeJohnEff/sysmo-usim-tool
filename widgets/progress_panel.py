#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Progress Panel Widget

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk


class ProgressPanel(ttk.LabelFrame):
    """Panel showing batch programming progress"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Batch Programming Progress", padding="10", **kwargs)

        self._create_widgets()
        self.reset()

    def _create_widgets(self):
        """Create panel widgets"""
        # Current card indicator
        card_frame = ttk.Frame(self)
        card_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(card_frame, text="Current Card:", font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        self.card_number_label = ttk.Label(card_frame, text="0 of 0", font=('TkDefaultFont', 10))
        self.card_number_label.pack(side=tk.LEFT)

        # Status text
        ttk.Label(self, text="Status:", font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.status_label = ttk.Label(self, text="Ready", foreground="gray")
        self.status_label.grid(row=2, column=0, sticky=tk.W)

        # Progress bar
        ttk.Label(self, text="Progress:", font=('TkDefaultFont', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        self.progress_bar = ttk.Progressbar(self, mode='determinate', maximum=100)
        self.progress_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)

        self.progress_percent_label = ttk.Label(self, text="0%", font=('TkDefaultFont', 9))
        self.progress_percent_label.grid(row=5, column=0, sticky=tk.E)

        # Statistics
        stats_frame = ttk.Frame(self)
        stats_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(15, 5))

        # Success count
        success_frame = ttk.Frame(stats_frame)
        success_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(success_frame, text="Success:", foreground="green").pack()
        self.success_label = ttk.Label(success_frame, text="0", font=('TkDefaultFont', 14, 'bold'), foreground="green")
        self.success_label.pack()

        # Failed count
        failed_frame = ttk.Frame(stats_frame)
        failed_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(failed_frame, text="Failed:", foreground="red").pack()
        self.failed_label = ttk.Label(failed_frame, text="0", font=('TkDefaultFont', 14, 'bold'), foreground="red")
        self.failed_label.pack()

        # Skipped count
        skipped_frame = ttk.Frame(stats_frame)
        skipped_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(skipped_frame, text="Skipped:", foreground="orange").pack()
        self.skipped_label = ttk.Label(skipped_frame, text="0", font=('TkDefaultFont', 14, 'bold'), foreground="orange")
        self.skipped_label.pack()

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=7, column=0, pady=(15, 0))

        self.start_button = ttk.Button(button_frame, text="Start Batch", command=self._on_start)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(button_frame, text="Pause", command=self._on_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.skip_button = ttk.Button(button_frame, text="Skip Card", command=self._on_skip, state=tk.DISABLED)
        self.skip_button.grid(row=0, column=2, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self._on_stop, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5)

        # Callbacks
        self.on_start_callback = None
        self.on_pause_callback = None
        self.on_skip_callback = None
        self.on_stop_callback = None

        # Grid weight for expansion
        self.grid_columnconfigure(0, weight=1)

    def set_total_cards(self, total: int):
        """Set total number of cards"""
        self.total_cards = total
        self.current_card = 0
        self.card_number_label.config(text=f"0 of {total}")

    def set_current_card(self, card_num: int):
        """Set current card number (1-indexed)"""
        self.current_card = card_num
        self.card_number_label.config(text=f"{card_num} of {self.total_cards}")

        # Update progress bar
        if self.total_cards > 0:
            progress = int((card_num / self.total_cards) * 100)
            self.progress_bar['value'] = progress
            self.progress_percent_label.config(text=f"{progress}%")

    def set_status(self, status: str, color: str = "black"):
        """Set status message"""
        self.status_label.config(text=status, foreground=color)

    def update_stats(self, success: int = None, failed: int = None, skipped: int = None):
        """Update success/failed/skipped counts"""
        if success is not None:
            self.success_label.config(text=str(success))
        if failed is not None:
            self.failed_label.config(text=str(failed))
        if skipped is not None:
            self.skipped_label.config(text=str(skipped))

    def set_running(self, running: bool):
        """Set running state"""
        if running:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.skip_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.skip_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)

    def reset(self):
        """Reset progress panel"""
        self.total_cards = 0
        self.current_card = 0
        self.card_number_label.config(text="0 of 0")
        self.status_label.config(text="Ready", foreground="gray")
        self.progress_bar['value'] = 0
        self.progress_percent_label.config(text="0%")
        self.success_label.config(text="0")
        self.failed_label.config(text="0")
        self.skipped_label.config(text="0")
        self.set_running(False)

    def _on_start(self):
        """Handle start button"""
        if self.on_start_callback:
            self.on_start_callback()

    def _on_pause(self):
        """Handle pause button"""
        if self.on_pause_callback:
            self.on_pause_callback()

    def _on_skip(self):
        """Handle skip button"""
        if self.on_skip_callback:
            self.on_skip_callback()

    def _on_stop(self):
        """Handle stop button"""
        if self.on_stop_callback:
            self.on_stop_callback()


# Test panel
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Progress Panel Test")

    panel = ProgressPanel(root)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Simulate progress
    def test_start():
        panel.set_total_cards(5)
        panel.set_running(True)
        panel.set_status("Programming card 1...", "blue")
        simulate_progress(1)

    def simulate_progress(card):
        if card <= 5:
            panel.set_current_card(card)
            panel.set_status(f"Programming card {card}...", "blue")
            panel.update_stats(success=card-1)
            root.after(1000, lambda: simulate_progress(card + 1))
        else:
            panel.set_status("Batch complete!", "green")
            panel.set_running(False)
            panel.update_stats(success=5)

    panel.on_start_callback = test_start

    root.mainloop()
