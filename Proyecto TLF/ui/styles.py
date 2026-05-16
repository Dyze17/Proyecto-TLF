"""
Unified style configuration for the application.

Provides a modern, minimalist dark theme using ttk styles.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk


# ── Color Palette ────────────────────────────────────────────────────────────

class Colors:
    """Minimalist color palette."""
    # Backgrounds
    BG_PRIMARY    = "#1a1b26"   # Main background (deep navy)
    BG_SECONDARY  = "#24283b"   # Panel / card background
    BG_TERTIARY   = "#2f3346"   # Input fields, hover
    BG_ELEVATED   = "#363b54"   # Elevated elements

    # Text
    TEXT_PRIMARY   = "#c0caf5"   # Main text
    TEXT_SECONDARY = "#565f89"   # Muted text
    TEXT_DISABLED  = "#3b4261"   # Disabled text
    TEXT_HEADING   = "#e0e6ff"   # Headings

    # Accent
    ACCENT         = "#7aa2f7"   # Primary accent (soft blue)
    ACCENT_HOVER   = "#89b4fa"   # Hover accent
    ACCENT_DIM     = "#3d59a1"   # Dimmed accent

    # Semantic
    SUCCESS        = "#9ece6a"   # Valid / pass
    ERROR          = "#f7768e"   # Invalid / fail
    WARNING        = "#e0af68"   # Warning
    INFO           = "#7dcfff"   # Information

    # Borders
    BORDER         = "#3b4261"
    BORDER_FOCUS   = "#7aa2f7"

    # Tab
    TAB_BG         = "#1f2235"
    TAB_SELECTED   = "#24283b"


# ── Fonts ────────────────────────────────────────────────────────────────────

class Fonts:
    FAMILY      = "Segoe UI"
    MONO_FAMILY = "Consolas"

    HEADING_1 = (FAMILY, 18, "bold")
    HEADING_2 = (FAMILY, 14, "bold")
    HEADING_3 = (FAMILY, 12, "bold")
    BODY      = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, "bold")
    SMALL     = (FAMILY, 9)
    MONO      = (MONO_FAMILY, 11)
    MONO_SM   = (MONO_FAMILY, 10)


# ── Apply theme ──────────────────────────────────────────────────────────────

def apply_theme(root: tk.Tk) -> ttk.Style:
    """Configure the ttk theme on *root* and return the Style object."""

    style = ttk.Style(root)
    style.theme_use("clam")  # clam is the most customizable built-in theme

    # ─ Global defaults ──────────────────────────────────────────────────
    root.configure(bg=Colors.BG_PRIMARY)
    root.option_add("*Font", Fonts.BODY)
    root.option_add("*Background", Colors.BG_PRIMARY)
    root.option_add("*Foreground", Colors.TEXT_PRIMARY)

    # ─ TFrame ───────────────────────────────────────────────────────────
    style.configure("TFrame", background=Colors.BG_PRIMARY)
    style.configure("Card.TFrame", background=Colors.BG_SECONDARY)
    style.configure("Elevated.TFrame", background=Colors.BG_ELEVATED)

    # ─ TLabel ───────────────────────────────────────────────────────────
    style.configure(
        "TLabel",
        background=Colors.BG_PRIMARY,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY,
    )
    style.configure("Heading.TLabel", font=Fonts.HEADING_1, foreground=Colors.TEXT_HEADING)
    style.configure("Heading2.TLabel", font=Fonts.HEADING_2, foreground=Colors.TEXT_HEADING)
    style.configure("Heading3.TLabel", font=Fonts.HEADING_3, foreground=Colors.TEXT_HEADING)
    style.configure("Muted.TLabel", foreground=Colors.TEXT_SECONDARY)
    style.configure("Success.TLabel", foreground=Colors.SUCCESS)
    style.configure("Error.TLabel", foreground=Colors.ERROR)
    style.configure("Card.TLabel", background=Colors.BG_SECONDARY, foreground=Colors.TEXT_PRIMARY)
    style.configure("CardMuted.TLabel", background=Colors.BG_SECONDARY, foreground=Colors.TEXT_SECONDARY)

    # ─ TButton ──────────────────────────────────────────────────────────
    style.configure(
        "TButton",
        background=Colors.ACCENT_DIM,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY_BOLD,
        borderwidth=0,
        padding=(16, 8),
        focuscolor=Colors.ACCENT,
    )
    style.map(
        "TButton",
        background=[
            ("active", Colors.ACCENT),
            ("pressed", Colors.ACCENT_HOVER),
            ("disabled", Colors.BG_TERTIARY),
        ],
        foreground=[
            ("disabled", Colors.TEXT_DISABLED),
        ],
    )
    style.configure(
        "Accent.TButton",
        background=Colors.ACCENT,
        foreground="#1a1b26",
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", Colors.ACCENT_HOVER),
            ("pressed", Colors.ACCENT_DIM),
        ],
    )
    style.configure(
        "Success.TButton",
        background=Colors.SUCCESS,
        foreground="#1a1b26",
    )
    style.configure(
        "Danger.TButton",
        background=Colors.ERROR,
        foreground="#1a1b26",
    )

    # ─ TEntry ───────────────────────────────────────────────────────────
    style.configure(
        "TEntry",
        fieldbackground=Colors.BG_TERTIARY,
        foreground=Colors.TEXT_PRIMARY,
        insertcolor=Colors.TEXT_PRIMARY,
        borderwidth=1,
        padding=(8, 6),
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", Colors.BG_ELEVATED)],
        bordercolor=[("focus", Colors.BORDER_FOCUS)],
    )

    # ─ TNotebook (tabs) ─────────────────────────────────────────────────
    style.configure(
        "TNotebook",
        background=Colors.BG_PRIMARY,
        borderwidth=0,
        tabmargins=(4, 4, 4, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=Colors.TAB_BG,
        foreground=Colors.TEXT_SECONDARY,
        padding=(18, 10),
        font=Fonts.BODY_BOLD,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", Colors.TAB_SELECTED)],
        foreground=[("selected", Colors.ACCENT)],
    )

    # ─ Treeview (tables) ────────────────────────────────────────────────
    style.configure(
        "Treeview",
        background=Colors.BG_SECONDARY,
        foreground=Colors.TEXT_PRIMARY,
        fieldbackground=Colors.BG_SECONDARY,
        borderwidth=0,
        rowheight=32,
        font=Fonts.BODY,
    )
    style.configure(
        "Treeview.Heading",
        background=Colors.BG_TERTIARY,
        foreground=Colors.TEXT_HEADING,
        font=Fonts.BODY_BOLD,
        borderwidth=0,
        padding=(8, 6),
    )
    style.map(
        "Treeview",
        background=[("selected", Colors.ACCENT_DIM)],
        foreground=[("selected", Colors.TEXT_PRIMARY)],
    )

    # ─ TScrollbar ───────────────────────────────────────────────────────
    style.configure(
        "TScrollbar",
        background=Colors.BG_TERTIARY,
        troughcolor=Colors.BG_PRIMARY,
        borderwidth=0,
        arrowsize=0,
    )
    style.map(
        "TScrollbar",
        background=[("active", Colors.BG_ELEVATED)],
    )

    # ─ TCheckbutton ─────────────────────────────────────────────────────
    style.configure(
        "TCheckbutton",
        background=Colors.BG_PRIMARY,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY,
        focuscolor=Colors.BG_PRIMARY,
    )
    style.map(
        "TCheckbutton",
        background=[("active", Colors.BG_PRIMARY)],
    )
    style.configure(
        "Card.TCheckbutton",
        background=Colors.BG_SECONDARY,
        foreground=Colors.TEXT_PRIMARY,
    )
    style.map(
        "Card.TCheckbutton",
        background=[("active", Colors.BG_SECONDARY)],
    )

    # ─ TLabelframe ──────────────────────────────────────────────────────
    style.configure(
        "TLabelframe",
        background=Colors.BG_SECONDARY,
        foreground=Colors.TEXT_HEADING,
        borderwidth=1,
        relief="flat",
    )
    style.configure(
        "TLabelframe.Label",
        background=Colors.BG_SECONDARY,
        foreground=Colors.ACCENT,
        font=Fonts.HEADING_3,
    )

    # ─ Separator ────────────────────────────────────────────────────────
    style.configure("TSeparator", background=Colors.BORDER)

    # ─ TPanedwindow ─────────────────────────────────────────────────────
    style.configure("TPanedwindow", background=Colors.BG_PRIMARY)

    return style
