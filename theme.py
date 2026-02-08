#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern macOS-like Theme Configuration

(C) 2026 SysmoUSIM-Tool GUI Project
"""

import tkinter as tk
from tkinter import ttk
import platform


class ModernTheme:
    """Modern macOS-like theme configuration"""

    # Color palette - macOS Big Sur inspired
    COLORS = {
        'bg': '#F5F5F7',  # Light gray background
        'fg': '#1D1D1F',  # Almost black text
        'accent': '#007AFF',  # macOS blue
        'accent_hover': '#0051D5',  # Darker blue
        'success': '#34C759',  # Green
        'warning': '#FF9500',  # Orange
        'error': '#FF3B30',  # Red
        'border': '#D1D1D6',  # Light border
        'hover': '#E8E8ED',  # Hover state
        'selected': '#007AFF',  # Selection blue
        'panel_bg': '#FFFFFF',  # White panel background
        'input_bg': '#FFFFFF',  # White input background
        'disabled': '#8E8E93',  # Disabled text
    }

    # Fonts - SF Pro on macOS, fallback to system font on other platforms
    FONTS = {
        'default': ('SF Pro Text', 13) if platform.system() == 'Darwin' else ('Segoe UI', 10),
        'heading': ('SF Pro Display', 18, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 14, 'bold'),
        'subheading': ('SF Pro Text', 14, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 11, 'bold'),
        'small': ('SF Pro Text', 11) if platform.system() == 'Darwin' else ('Segoe UI', 9),
        'mono': ('SF Mono', 11) if platform.system() == 'Darwin' else ('Consolas', 9),
    }

    # Spacing
    PADDING = {
        'small': 8,
        'medium': 12,
        'large': 20,
        'xlarge': 30,
    }

    @staticmethod
    def apply_theme(root):
        """Apply modern theme to the application"""
        style = ttk.Style(root)

        # Use 'aqua' theme on macOS, 'clam' elsewhere for more customization
        if platform.system() == 'Darwin':
            style.theme_use('aqua')
        else:
            style.theme_use('clam')

        # Configure root window
        root.configure(bg=ModernTheme.COLORS['bg'])

        # Button styles
        style.configure('TButton',
                        font=ModernTheme.FONTS['default'],
                        borderwidth=0,
                        relief='flat',
                        padding=(12, 6))

        style.map('TButton',
                  background=[('active', ModernTheme.COLORS['accent_hover']),
                              ('!active', ModernTheme.COLORS['accent'])],
                  foreground=[('active', 'white'), ('!active', 'white')])

        # Primary button (for important actions)
        style.configure('Primary.TButton',
                        font=ModernTheme.FONTS['default'],
                        background=ModernTheme.COLORS['accent'],
                        foreground='white',
                        borderwidth=0,
                        relief='flat',
                        padding=(16, 8))

        style.map('Primary.TButton',
                  background=[('active', ModernTheme.COLORS['accent_hover']),
                              ('!active', ModernTheme.COLORS['accent'])])

        # Success button
        style.configure('Success.TButton',
                        background=ModernTheme.COLORS['success'],
                        foreground='white')

        style.map('Success.TButton',
                  background=[('active', '#2DB74A'), ('!active', ModernTheme.COLORS['success'])])

        # Danger button
        style.configure('Danger.TButton',
                        background=ModernTheme.COLORS['error'],
                        foreground='white')

        style.map('Danger.TButton',
                  background=[('active', '#D62C21'), ('!active', ModernTheme.COLORS['error'])])

        # Labels
        style.configure('TLabel',
                        font=ModernTheme.FONTS['default'],
                        background=ModernTheme.COLORS['bg'],
                        foreground=ModernTheme.COLORS['fg'])

        style.configure('Heading.TLabel',
                        font=ModernTheme.FONTS['heading'],
                        foreground=ModernTheme.COLORS['fg'])

        style.configure('Subheading.TLabel',
                        font=ModernTheme.FONTS['subheading'])

        # LabelFrame
        style.configure('TLabelframe',
                        background=ModernTheme.COLORS['panel_bg'],
                        borderwidth=1,
                        relief='solid',
                        bordercolor=ModernTheme.COLORS['border'])

        style.configure('TLabelframe.Label',
                        font=ModernTheme.FONTS['subheading'],
                        background=ModernTheme.COLORS['panel_bg'],
                        foreground=ModernTheme.COLORS['fg'])

        # Frame
        style.configure('TFrame',
                        background=ModernTheme.COLORS['bg'])

        style.configure('Card.TFrame',
                        background=ModernTheme.COLORS['panel_bg'],
                        relief='flat')

        # Entry
        style.configure('TEntry',
                        font=ModernTheme.FONTS['default'],
                        fieldbackground=ModernTheme.COLORS['input_bg'],
                        borderwidth=1,
                        relief='solid')

        # Treeview (for CSV table)
        style.configure('Treeview',
                        font=ModernTheme.FONTS['default'],
                        background=ModernTheme.COLORS['panel_bg'],
                        fieldbackground=ModernTheme.COLORS['panel_bg'],
                        foreground=ModernTheme.COLORS['fg'],
                        borderwidth=1,
                        relief='solid',
                        rowheight=28)

        style.configure('Treeview.Heading',
                        font=ModernTheme.FONTS['subheading'],
                        background=ModernTheme.COLORS['hover'],
                        foreground=ModernTheme.COLORS['fg'],
                        borderwidth=1,
                        relief='flat')

        style.map('Treeview',
                  background=[('selected', ModernTheme.COLORS['selected'])],
                  foreground=[('selected', 'white')])

        # Progressbar
        style.configure('TProgressbar',
                        background=ModernTheme.COLORS['accent'],
                        borderwidth=0,
                        thickness=8)

        # Notebook (tabs)
        style.configure('TNotebook',
                        background=ModernTheme.COLORS['bg'],
                        borderwidth=0)

        style.configure('TNotebook.Tab',
                        font=ModernTheme.FONTS['default'],
                        padding=(20, 10))

        # Scrollbar
        style.configure('TScrollbar',
                        background=ModernTheme.COLORS['hover'],
                        borderwidth=0,
                        arrowsize=13)

        # Separator
        style.configure('TSeparator',
                        background=ModernTheme.COLORS['border'])

        return style

    @staticmethod
    def get_color(name):
        """Get color from palette"""
        return ModernTheme.COLORS.get(name, '#000000')

    @staticmethod
    def get_font(name):
        """Get font from palette"""
        return ModernTheme.FONTS.get(name, ModernTheme.FONTS['default'])

    @staticmethod
    def get_padding(name):
        """Get padding value"""
        return ModernTheme.PADDING.get(name, 10)
