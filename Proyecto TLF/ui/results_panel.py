"""
Panel de resultados detallados.

Muestra los resultados de las búsquedas con opciones de filtrado
y exportación.
"""

from __future__ import annotations
import json
import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

from .styles import Colors, Fonts


class ResultsPanel(ttk.Frame):
    """Panel de visualización y exportación de resultados."""

    def __init__(self, parent: tk.Widget, **kw) -> None:
        super().__init__(parent, style="TFrame", **kw)
        self._data: List[dict] = []
        self._build_ui()

    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(24, 4))
        ttk.Label(header, text="Resultados", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Historial de coincidencias encontradas en la sesión actual",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(12, 8))

        # Filter bar
        filter_frame = ttk.Frame(self, style="TFrame")
        filter_frame.pack(fill="x", padx=24, pady=(0, 8))

        ttk.Label(filter_frame, text="Filtrar por patrón:", style="TLabel").pack(side="left")
        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", lambda *_: self._apply_filter())
        filter_entry = tk.Entry(
            filter_frame,
            textvariable=self._filter_var,
            font=Fonts.BODY,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief="flat",
            width=30,
        )
        filter_entry.pack(side="left", padx=8)

        ttk.Button(filter_frame, text="Limpiar historial", command=self._clear).pack(side="right")

        # Table
        table_frame = ttk.Frame(self, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=24, pady=8)

        self._tree = ttk.Treeview(
            table_frame,
            columns=("id", "pattern", "match", "start", "end", "source"),
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("id", text="#")
        self._tree.heading("pattern", text="Patrón")
        self._tree.heading("match", text="Coincidencia")
        self._tree.heading("start", text="Inicio")
        self._tree.heading("end", text="Fin")
        self._tree.heading("source", text="Fuente")
        self._tree.column("id", width=40, anchor="center")
        self._tree.column("pattern", width=140)
        self._tree.column("match", width=200)
        self._tree.column("start", width=60, anchor="center")
        self._tree.column("end", width=60, anchor="center")
        self._tree.column("source", width=120)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Export + status
        bottom = ttk.Frame(self, style="TFrame")
        bottom.pack(fill="x", padx=24, pady=(0, 12))
        ttk.Button(bottom, text="Exportar CSV", command=self._export_csv).pack(side="left", padx=4)
        ttk.Button(bottom, text="Exportar JSON", command=self._export_json).pack(side="left", padx=4)
        self._status = ttk.Label(bottom, text="0 resultados", style="Muted.TLabel")
        self._status.pack(side="right")

    # ── Public API ──────────────────────────────────────────────────────

    def add_results(self, results: List[dict], source: str = "búsqueda") -> None:
        """Append new results to the history."""
        for r in results:
            r["source"] = source
        self._data.extend(results)
        self._apply_filter()

    # ── Internal ────────────────────────────────────────────────────────

    def _apply_filter(self) -> None:
        self._tree.delete(*self._tree.get_children())
        query = self._filter_var.get().lower()
        filtered = [d for d in self._data if query in d.get("pattern", "").lower()] if query else self._data
        for i, d in enumerate(filtered, 1):
            self._tree.insert("", "end", values=(
                i, d.get("pattern", ""), d.get("match", ""),
                d.get("start", ""), d.get("end", ""), d.get("source", ""),
            ))
        self._status.config(text=f"{len(filtered)} resultado(s)")

    def _clear(self) -> None:
        self._data.clear()
        self._tree.delete(*self._tree.get_children())
        self._status.config(text="0 resultados")

    def _export_csv(self) -> None:
        if not self._data:
            messagebox.showinfo("Aviso", "No hay resultados para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["pattern", "match", "start", "end", "source"])
            w.writeheader()
            w.writerows(self._data)

    def _export_json(self) -> None:
        if not self._data:
            messagebox.showinfo("Aviso", "No hay resultados para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
