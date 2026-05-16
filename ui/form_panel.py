"""
Formulario con validación en tiempo real.

Cada campo se valida al escribir (on KeyRelease) y muestra
indicadores visuales inmediatos (✓ verde / ✗ rojo).
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from .styles import Colors, Fonts
from pattern_engine.pattern_engine import PatternEngine, CompiledPattern


# ── Default form fields ─────────────────────────────────────────────────────

DEFAULT_FIELDS = [
    {
        "name": "correo",
        "label": "Correo electrónico",
        "pattern": '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
        "semantic_key": "correo",
        "placeholder": "usuario@ejemplo.com",
    },
    {
        "name": "telefono",
        "label": "Teléfono",
        "pattern": '("+" digito{1,3} " ")? digito{7,15}',
        "semantic_key": "telefono",
        "placeholder": "+57 3001234567",
    },
    {
        "name": "fecha",
        "label": "Fecha (YYYY-MM-DD)",
        "pattern": '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
        "semantic_key": "fecha_iso",
        "placeholder": "2024-12-31",
    },
    {
        "name": "placa",
        "label": "Placa vehicular",
        "pattern": '[A-Z]{3} "-" [0-9]{3}',
        "semantic_key": "placa",
        "placeholder": "ABC-123",
    },
    {
        "name": "identificador",
        "label": "Identificador",
        "pattern": '(letra|"_") (letra|digito|"_")*',
        "semantic_key": None,
        "placeholder": "mi_variable_1",
    },
]


class FormPanel(ttk.Frame):
    """Panel de formulario con validación en tiempo real."""

    def __init__(self, parent: tk.Widget, engine: PatternEngine, **kw) -> None:
        super().__init__(parent, style="TFrame", **kw)
        self.engine = engine

        # Compile patterns for each field
        self.compiled: Dict[str, CompiledPattern] = {}
        for fd in DEFAULT_FIELDS:
            self.compiled[fd["name"]] = engine.compile(
                fd["pattern"], name=fd["name"], semantic_key=fd["semantic_key"]
            )

        self._entries: Dict[str, tk.Entry] = {}
        self._indicators: Dict[str, ttk.Label] = {}
        self._messages: Dict[str, ttk.Label] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(24, 4))
        ttk.Label(
            header, text="Validación de Formulario", style="Heading.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Ingrese datos en cada campo — la validación ocurre en tiempo real",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(12, 8))

        # Form card
        card = ttk.Frame(self, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=24, pady=12)

        for i, fd in enumerate(DEFAULT_FIELDS):
            self._create_field(card, fd, row=i)

        # Summary label at bottom
        self._summary = ttk.Label(card, text="", style="Card.TLabel")
        self._summary.grid(row=len(DEFAULT_FIELDS) * 3, column=0, columnspan=3,
                           sticky="w", padx=16, pady=(16, 12))

    def _create_field(self, parent: ttk.Frame, field: dict, row: int) -> None:
        r = row * 3  # each field uses 3 rows: label, entry, message

        # Label
        ttk.Label(
            parent,
            text=field["label"],
            style="Card.TLabel",
            font=Fonts.BODY_BOLD,
        ).grid(row=r, column=0, sticky="w", padx=16, pady=(12, 2))

        # Entry
        entry = tk.Entry(
            parent,
            font=Fonts.MONO,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            highlightcolor=Colors.BORDER_FOCUS,
            bd=0,
        )
        entry.grid(row=r + 1, column=0, sticky="ew", padx=16, pady=2, ipady=6)
        parent.columnconfigure(0, weight=1)

        # Placeholder
        entry.insert(0, field["placeholder"])
        entry.config(fg=Colors.TEXT_DISABLED)
        entry._has_placeholder = True

        entry.bind("<FocusIn>", lambda e, en=entry, fd=field: self._on_focus_in(en, fd))
        entry.bind("<FocusOut>", lambda e, en=entry, fd=field: self._on_focus_out(en, fd))

        # Indicator (right of entry)
        indicator = ttk.Label(parent, text="", style="Card.TLabel", width=3)
        indicator.grid(row=r + 1, column=1, padx=(0, 16))

        # Error message
        msg = ttk.Label(parent, text="", style="CardMuted.TLabel", font=Fonts.SMALL)
        msg.grid(row=r + 2, column=0, columnspan=2, sticky="w", padx=16)

        self._entries[field["name"]] = entry
        self._indicators[field["name"]] = indicator
        self._messages[field["name"]] = msg

        # Bind validation
        entry.bind("<KeyRelease>", lambda e, name=field["name"]: self._validate_field(name))

    def _on_focus_in(self, entry: tk.Entry, field: dict) -> None:
        if getattr(entry, "_has_placeholder", False):
            entry.delete(0, "end")
            entry.config(fg=Colors.TEXT_PRIMARY)
            entry._has_placeholder = False

    def _on_focus_out(self, entry: tk.Entry, field: dict) -> None:
        if not entry.get():
            entry.insert(0, field["placeholder"])
            entry.config(fg=Colors.TEXT_DISABLED)
            entry._has_placeholder = True
            # Clear indicators
            self._indicators[field["name"]].config(text="")
            self._messages[field["name"]].config(text="")

    def _validate_field(self, name: str) -> None:
        entry = self._entries[name]
        if getattr(entry, "_has_placeholder", False):
            return

        text = entry.get().strip()
        indicator = self._indicators[name]
        msg = self._messages[name]

        if not text:
            indicator.config(text="")
            msg.config(text="")
            entry.config(highlightbackground=Colors.BORDER)
            return

        cp = self.compiled[name]
        is_valid = self.engine.match(text, compiled=cp)

        if is_valid:
            indicator.config(text="✓", foreground=Colors.SUCCESS)
            msg.config(text="Válido", foreground=Colors.SUCCESS)
            entry.config(highlightbackground=Colors.SUCCESS)
        else:
            indicator.config(text="✗", foreground=Colors.ERROR)
            msg.config(text="Formato inválido", foreground=Colors.ERROR)
            entry.config(highlightbackground=Colors.ERROR)

        self._update_summary()

    def _update_summary(self) -> None:
        total = 0
        valid = 0
        for name, entry in self._entries.items():
            if getattr(entry, "_has_placeholder", False) or not entry.get().strip():
                continue
            total += 1
            cp = self.compiled[name]
            if self.engine.match(entry.get().strip(), compiled=cp):
                valid += 1

        if total == 0:
            self._summary.config(text="")
        else:
            self._summary.config(
                text=f"{valid}/{total} campos válidos",
                foreground=Colors.SUCCESS if valid == total else Colors.WARNING,
            )
