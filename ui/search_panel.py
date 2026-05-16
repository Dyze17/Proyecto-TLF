"""
Panel de búsqueda de patrones en texto.

Permite cargar texto manual o desde archivo, seleccionar patrones
a buscar, y muestra coincidencias resaltadas con posiciones.
"""

from __future__ import annotations
import json
import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional, Callable

from .styles import Colors, Fonts
from pattern_engine.pattern_engine import PatternEngine, CompiledPattern
from pattern_engine.dfa_simulator import Match


class SearchPanel(ttk.Frame):
    """Panel de búsqueda de patrones en texto/archivo."""

    def __init__(
        self,
        parent: tk.Widget,
        engine: PatternEngine,
        rules: List[dict],
        on_results_found: Optional[Callable[[List[dict]], None]] = None,
        **kw,
    ) -> None:
        super().__init__(parent, style="TFrame", **kw)
        self.engine = engine
        self.rules = rules
        self.on_results_found = on_results_found
        self._compiled: Dict[str, CompiledPattern] = {}
        self._matches: List[dict] = []

        self._compile_rules()
        self._build_ui()

    def _compile_rules(self) -> None:
        for r in self.rules:
            if r.get("enabled", True):
                self._compiled[r["name"]] = self.engine.compile(
                    r["pattern"], name=r["name"], semantic_key=r.get("semantic_key"),
                )

    def refresh_rules(self, rules: List[dict]) -> None:
        self.rules = rules
        self._compiled.clear()
        self._compile_rules()
        self._update_pattern_checkboxes()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(24, 4))
        ttk.Label(header, text="Búsqueda de Patrones", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Cargue texto o un archivo y busque coincidencias de patrones",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(12, 8))

        # Main content: left (text) + right (controls + results)
        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=24, pady=8)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Left: text input ────────────────────────────────────────────
        left = ttk.Frame(body, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ttk.Frame(left, style="Card.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))

        ttk.Label(toolbar, text="Texto de entrada", style="Card.TLabel",
                  font=Fonts.HEADING_3).pack(side="left")

        btn_load = ttk.Button(toolbar, text="📂 Cargar archivo", command=self._load_file)
        btn_load.pack(side="right", padx=4)

        btn_clear = ttk.Button(toolbar, text="🗑 Limpiar", command=self._clear_text)
        btn_clear.pack(side="right", padx=4)

        # Text widget
        text_frame = ttk.Frame(left, style="Card.TFrame")
        text_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 12))
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._text = tk.Text(
            text_frame,
            wrap="word",
            font=Fonts.MONO,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief="flat",
            highlightthickness=0,
            padx=10,
            pady=8,
        )
        self._text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self._text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._text.config(yscrollcommand=scrollbar.set)

        # Tag for highlighting matches
        self._text.tag_configure(
            "match",
            background=Colors.ACCENT_DIM,
            foreground=Colors.TEXT_HEADING,
        )

        # ── Right: controls + results ──────────────────────────────────
        right = ttk.Frame(body, style="TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        # Pattern selection
        pat_frame = ttk.LabelFrame(right, text="  Patrones a buscar  ")
        pat_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._pattern_vars: Dict[str, tk.BooleanVar] = {}
        self._pat_container = ttk.Frame(pat_frame, style="Card.TFrame")
        self._pat_container.pack(fill="x", padx=8, pady=8)
        self._update_pattern_checkboxes()

        # Search button
        ttk.Button(
            right, text="🔍  Buscar", style="Accent.TButton", command=self._search
        ).grid(row=1, column=0, sticky="ew", pady=8)

        # Results table
        res_frame = ttk.LabelFrame(right, text="  Resultados  ")
        res_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 0))

        self._tree = ttk.Treeview(
            res_frame,
            columns=("pattern", "match", "start", "end"),
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("pattern", text="Patrón")
        self._tree.heading("match", text="Coincidencia")
        self._tree.heading("start", text="Inicio")
        self._tree.heading("end", text="Fin")
        self._tree.column("pattern", width=100)
        self._tree.column("match", width=140)
        self._tree.column("start", width=50, anchor="center")
        self._tree.column("end", width=50, anchor="center")

        self._tree.pack(fill="both", expand=True, padx=8, pady=8)
        self._tree.bind("<<TreeviewSelect>>", self._on_result_select)

        # Export buttons
        export_frame = ttk.Frame(res_frame, style="Card.TFrame")
        export_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(export_frame, text="CSV", command=self._export_csv).pack(side="left", padx=4)
        ttk.Button(export_frame, text="JSON", command=self._export_json).pack(side="left", padx=4)

        # Status
        self._status = ttk.Label(right, text="", style="Muted.TLabel")
        self._status.grid(row=3, column=0, sticky="w", pady=(4, 0))

    def _update_pattern_checkboxes(self) -> None:
        for w in self._pat_container.winfo_children():
            w.destroy()
        self._pattern_vars.clear()
        for r in self.rules:
            if not r.get("enabled", True):
                continue
            var = tk.BooleanVar(value=True)
            self._pattern_vars[r["name"]] = var
            cb = ttk.Checkbutton(
                self._pat_container,
                text=r["name"],
                variable=var,
                style="Card.TCheckbutton",
            )
            cb.pack(anchor="w", padx=4, pady=2)

    # ── Actions ─────────────────────────────────────────────────────────

    def _load_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto", "*.txt *.csv *.log *.md"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            size = os.path.getsize(path)
            if size > 10 * 1024 * 1024:
                messagebox.showerror("Error", "El archivo supera los 10 MB permitidos.")
                return
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._text.delete("1.0", "end")
            self._text.insert("1.0", content)
            self._status.config(
                text=f"Archivo cargado: {os.path.basename(path)} ({size:,} bytes)"
            )
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{ex}")

    def _clear_text(self) -> None:
        self._text.delete("1.0", "end")
        self._text.tag_remove("match", "1.0", "end")
        self._tree.delete(*self._tree.get_children())
        self._matches.clear()
        self._status.config(text="")

    def _search(self) -> None:
        text = self._text.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Aviso", "Ingrese o cargue texto antes de buscar.")
            return

        # Clear previous
        self._text.tag_remove("match", "1.0", "end")
        self._tree.delete(*self._tree.get_children())
        self._matches.clear()

        selected = [n for n, v in self._pattern_vars.items() if v.get()]
        if not selected:
            messagebox.showinfo("Aviso", "Seleccione al menos un patrón.")
            return

        total = 0
        for name in selected:
            cp = self._compiled.get(name)
            if cp is None:
                continue
            hits = self.engine.search(text, compiled=cp)
            for m in hits:
                self._tree.insert("", "end", values=(name, m.text, m.start, m.end))
                self._matches.append({
                    "pattern": name,
                    "match": m.text,
                    "start": m.start,
                    "end": m.end,
                })
                # Highlight in text widget
                start_idx = f"1.0+{m.start}c"
                end_idx = f"1.0+{m.end}c"
                self._text.tag_add("match", start_idx, end_idx)
                total += 1

        if total > 0 and self.on_results_found:
            matches_copy = [m.copy() for m in self._matches]
            self.on_results_found(matches_copy)

        self._status.config(
            text=f"{total} coincidencia(s) encontrada(s) en {len(selected)} patrón(es)",
            foreground=Colors.SUCCESS if total > 0 else Colors.TEXT_SECONDARY,
        )

    def _on_result_select(self, _event: tk.Event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        values = self._tree.item(sel[0], "values")
        start = int(values[2])
        end = int(values[3])
        idx = f"1.0+{start}c"
        self._text.see(idx)
        self._text.tag_remove("sel", "1.0", "end")

    # ── Export ──────────────────────────────────────────────────────────

    def _export_csv(self) -> None:
        if not self._matches:
            messagebox.showinfo("Aviso", "No hay resultados para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["pattern", "match", "start", "end"])
            w.writeheader()
            w.writerows(self._matches)
        self._status.config(text=f"Exportado a {os.path.basename(path)}")

    def _export_json(self) -> None:
        if not self._matches:
            messagebox.showinfo("Aviso", "No hay resultados para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._matches, f, indent=2, ensure_ascii=False)
        self._status.config(text=f"Exportado a {os.path.basename(path)}")
