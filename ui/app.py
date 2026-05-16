"""
Ventana principal de la aplicación.

Contiene un Notebook (pestañas) con los paneles:
- Validador de formularios
- Buscador de patrones
- Gestión de reglas
- Resultados
- Casos de prueba
"""

from __future__ import annotations
import json
import os
import tkinter as tk
from tkinter import ttk
from typing import List

from .styles import Colors, Fonts, apply_theme
from .form_panel import FormPanel
from .search_panel import SearchPanel
from .rules_panel import RulesPanel
from .results_panel import ResultsPanel
from .test_panel import TestPanel

from pattern_engine.pattern_engine import PatternEngine


# ── Default rules ────────────────────────────────────────────────────────────

DEFAULT_RULES: List[dict] = [
    {
        "name": "Correo electrónico",
        "pattern": '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
        "semantic_key": "correo",
        "enabled": True,
    },
    {
        "name": "Teléfono",
        "pattern": '("+" digito{1,3} " ")? digito{7,15}',
        "semantic_key": "telefono",
        "enabled": True,
    },
    {
        "name": "Fecha ISO (YYYY-MM-DD)",
        "pattern": '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
        "semantic_key": "fecha_iso",
        "enabled": True,
    },
    {
        "name": "Fecha DD/MM/YYYY",
        "pattern": '[0-9]{2} "/" [0-9]{2} "/" [0-9]{4}',
        "semantic_key": "fecha_dmy",
        "enabled": True,
    },
    {
        "name": "Placa vehicular",
        "pattern": '[A-Z]{3} "-" [0-9]{3}',
        "semantic_key": "placa",
        "enabled": True,
    },
    {
        "name": "Identificador",
        "pattern": '(letra|"_") (letra|digito|"_")*',
        "semantic_key": None,
        "enabled": True,
    },
]


class Application:
    """Main application controller."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Motor de Patrones — Autómatas Finitos")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        # Apply theme
        self.style = apply_theme(self.root)

        # Engine
        self.engine = PatternEngine()

        # Load rules
        self.rules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "rules", "default_rules.json",
        )
        self.rules = self._load_rules()

        # Build UI
        self._build_ui()

    def _load_rules(self) -> List[dict]:
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Save defaults
        os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
        with open(self.rules_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_RULES, f, indent=2, ensure_ascii=False)
        return list(DEFAULT_RULES)

    def _build_ui(self) -> None:
        # Top bar with title
        top = ttk.Frame(self.root, style="TFrame")
        top.pack(fill="x", padx=0, pady=0)

        title_bar = ttk.Frame(top, style="Card.TFrame")
        title_bar.pack(fill="x")
        ttk.Label(
            title_bar,
            text="  ⚙  Motor de Patrones",
            style="Card.TLabel",
            font=Fonts.HEADING_2,
            foreground=Colors.ACCENT,
        ).pack(side="left", padx=12, pady=10)
        ttk.Label(
            title_bar,
            text="Teoría de Lenguajes Formales  ",
            style="CardMuted.TLabel",
            font=Fonts.SMALL,
        ).pack(side="right", padx=12, pady=10)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # Panels
        self.results_panel = ResultsPanel(self.notebook)
        self.form_panel = FormPanel(self.notebook, self.engine)
        self.search_panel = SearchPanel(
            self.notebook, self.engine, rules=self.rules,
            on_results_found=self.results_panel.add_results
        )
        self.rules_panel = RulesPanel(
            self.notebook, self.engine, self.rules, self.rules_path,
            on_rules_changed=self._on_rules_changed,
        )
        self.test_panel = TestPanel(self.notebook, self.engine)

        self.notebook.add(self.form_panel, text="  📝  Formulario  ")
        self.notebook.add(self.search_panel, text="  🔍  Búsqueda  ")
        self.notebook.add(self.rules_panel, text="  📋  Reglas  ")
        self.notebook.add(self.results_panel, text="  📊  Resultados  ")
        self.notebook.add(self.test_panel, text="  🧪  Pruebas  ")

    def _on_rules_changed(self, new_rules: List[dict]) -> None:
        self.rules = new_rules
        self.search_panel.refresh_rules(new_rules)

    def run(self) -> None:
        self.root.mainloop()
