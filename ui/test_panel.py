"""
Panel de casos de prueba.

Muestra una tabla con casos de prueba predefinidos y permite
ejecutarlos automáticamente para verificar el motor de patrones.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import List

from .styles import Colors, Fonts
from pattern_engine.pattern_engine import PatternEngine


# ── Default test cases (from the requirements document) ─────────────────────

DEFAULT_TEST_CASES: List[dict] = [
    {"id": "TC01", "pattern_name": "Correo electrónico",
     "pattern": '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
     "semantic_key": "correo",
     "input": "juan@mail.com", "expected": True},
    {"id": "TC02", "pattern_name": "Correo electrónico",
     "pattern": '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
     "semantic_key": "correo",
     "input": "juan@mail", "expected": False},
    {"id": "TC03", "pattern_name": "Fecha ISO",
     "pattern": '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
     "semantic_key": "fecha_iso",
     "input": "2024-02-29", "expected": True},
    {"id": "TC04", "pattern_name": "Fecha ISO",
     "pattern": '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
     "semantic_key": "fecha_iso",
     "input": "2023-02-29", "expected": False},
    {"id": "TC05", "pattern_name": "Placa vehicular",
     "pattern": '[A-Z]{3} "-" [0-9]{3}',
     "semantic_key": "placa",
     "input": "ABC-123", "expected": True},
    {"id": "TC06", "pattern_name": "Placa vehicular",
     "pattern": '[A-Z]{3} "-" [0-9]{3}',
     "semantic_key": "placa",
     "input": "AB-12", "expected": False},
    {"id": "TC07", "pattern_name": "Teléfono",
     "pattern": '("+" digito{1,3} " ")? digito{7,15}',
     "semantic_key": "telefono",
     "input": "+57 3001234567", "expected": True},
    {"id": "TC08", "pattern_name": "Teléfono",
     "pattern": '("+" digito{1,3} " ")? digito{7,15}',
     "semantic_key": "telefono",
     "input": "123", "expected": False},
    {"id": "TC09", "pattern_name": "Identificador",
     "pattern": '(letra|"_") (letra|digito|"_")*',
     "semantic_key": None,
     "input": "mi_variable_1", "expected": True},
    {"id": "TC10", "pattern_name": "Identificador",
     "pattern": '(letra|"_") (letra|digito|"_")*',
     "semantic_key": None,
     "input": "1variable", "expected": False},
    {"id": "TC11", "pattern_name": "Correo electrónico",
     "pattern": '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
     "semantic_key": "correo",
     "input": "ana_99@test.org", "expected": True},
    {"id": "TC12", "pattern_name": "Fecha ISO",
     "pattern": '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
     "semantic_key": "fecha_iso",
     "input": "2024-13-01", "expected": False},
]


class TestPanel(ttk.Frame):
    """Panel de ejecución de casos de prueba."""

    def __init__(self, parent: tk.Widget, engine: PatternEngine, **kw) -> None:
        super().__init__(parent, style="TFrame", **kw)
        self.engine = engine
        self.test_cases = list(DEFAULT_TEST_CASES)
        self._build_ui()
        self._populate_table()

    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(24, 4))
        ttk.Label(header, text="Casos de Prueba", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Ejecute los casos de prueba para verificar el motor de patrones",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(12, 8))

        # Toolbar
        toolbar = ttk.Frame(self, style="TFrame")
        toolbar.pack(fill="x", padx=24, pady=(0, 8))
        ttk.Button(
            toolbar, text="▶  Ejecutar todas", style="Accent.TButton",
            command=self._run_all,
        ).pack(side="left", padx=(0, 8))

        self._summary = ttk.Label(toolbar, text="", style="TLabel", font=Fonts.BODY_BOLD)
        self._summary.pack(side="right")

        # Table
        table_frame = ttk.Frame(self, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=24, pady=8)

        self._tree = ttk.Treeview(
            table_frame,
            columns=("id", "pattern", "input", "expected", "result", "status"),
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("id", text="ID")
        self._tree.heading("pattern", text="Patrón")
        self._tree.heading("input", text="Entrada")
        self._tree.heading("expected", text="Esperado")
        self._tree.heading("result", text="Resultado")
        self._tree.heading("status", text="Estado")
        self._tree.column("id", width=50, anchor="center")
        self._tree.column("pattern", width=150)
        self._tree.column("input", width=180)
        self._tree.column("expected", width=80, anchor="center")
        self._tree.column("result", width=80, anchor="center")
        self._tree.column("status", width=80, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Treeview tags for colors
        self._tree.tag_configure("pass", foreground=Colors.SUCCESS)
        self._tree.tag_configure("fail", foreground=Colors.ERROR)
        self._tree.tag_configure("pending", foreground=Colors.TEXT_SECONDARY)

    def _populate_table(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for tc in self.test_cases:
            exp_str = "Aceptar" if tc["expected"] else "Rechazar"
            self._tree.insert("", "end", values=(
                tc["id"], tc["pattern_name"], tc["input"],
                exp_str, "—", "Pendiente",
            ), tags=("pending",))

    def _run_all(self) -> None:
        self._tree.delete(*self._tree.get_children())
        passed = 0
        failed = 0

        for tc in self.test_cases:
            try:
                cp = self.engine.compile(
                    tc["pattern"],
                    name=tc["pattern_name"],
                    semantic_key=tc.get("semantic_key"),
                )
                result = self.engine.match(tc["input"], compiled=cp)
            except Exception:
                result = None

            expected = tc["expected"]
            exp_str = "Aceptar" if expected else "Rechazar"

            if result is None:
                res_str = "Error"
                status = "✗ FAIL"
                tag = "fail"
                failed += 1
            elif result == expected:
                res_str = "Aceptar" if result else "Rechazar"
                status = "✓ PASS"
                tag = "pass"
                passed += 1
            else:
                res_str = "Aceptar" if result else "Rechazar"
                status = "✗ FAIL"
                tag = "fail"
                failed += 1

            self._tree.insert("", "end", values=(
                tc["id"], tc["pattern_name"], tc["input"],
                exp_str, res_str, status,
            ), tags=(tag,))

        total = passed + failed
        color = Colors.SUCCESS if failed == 0 else Colors.ERROR
        self._summary.config(
            text=f"{passed}/{total} pruebas exitosas",
            foreground=color,
        )
