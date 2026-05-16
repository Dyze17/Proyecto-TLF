"""
Panel de gestión de reglas (patrones).

Permite crear, editar, eliminar y activar/desactivar reglas.
Las reglas se persisten en un archivo JSON.
"""

from __future__ import annotations
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Dict, List, Optional

from .styles import Colors, Fonts
from pattern_engine.pattern_engine import PatternEngine


class RulesPanel(ttk.Frame):
    """Panel CRUD para reglas de patrones."""

    def __init__(
        self,
        parent: tk.Widget,
        engine: PatternEngine,
        rules: List[dict],
        rules_path: str,
        on_rules_changed: Optional[Callable[[List[dict]], None]] = None,
        **kw,
    ) -> None:
        super().__init__(parent, style="TFrame", **kw)
        self.engine = engine
        self.rules = rules
        self.rules_path = rules_path
        self.on_rules_changed = on_rules_changed
        self._build_ui()
        self._refresh_table()

    # ── UI ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=24, pady=(24, 4))
        ttk.Label(header, text="Gestión de Reglas", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Cree, edite y administre los patrones de búsqueda",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(12, 8))

        # Toolbar
        toolbar = ttk.Frame(self, style="TFrame")
        toolbar.pack(fill="x", padx=24, pady=(0, 8))

        ttk.Button(toolbar, text="➕  Nueva regla", style="Accent.TButton",
                   command=self._new_rule).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="✏️  Editar", command=self._edit_rule).pack(side="left", padx=4)
        ttk.Button(toolbar, text="🔄  Activar/Desactivar",
                   command=self._toggle_rule).pack(side="left", padx=4)
        ttk.Button(toolbar, text="🗑  Eliminar", style="Danger.TButton",
                   command=self._delete_rule).pack(side="right", padx=4)

        # Table
        table_frame = ttk.Frame(self, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=24, pady=8)

        self._tree = ttk.Treeview(
            table_frame,
            columns=("name", "pattern", "semantic", "enabled"),
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("name", text="Nombre")
        self._tree.heading("pattern", text="Patrón (DSL)")
        self._tree.heading("semantic", text="Validación semántica")
        self._tree.heading("enabled", text="Estado")
        self._tree.column("name", width=160)
        self._tree.column("pattern", width=350)
        self._tree.column("semantic", width=120, anchor="center")
        self._tree.column("enabled", width=80, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)

        self._tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Status
        self._status = ttk.Label(self, text="", style="Muted.TLabel")
        self._status.pack(fill="x", padx=24, pady=(0, 12))

    def _refresh_table(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for r in self.rules:
            state = "✓ Activa" if r.get("enabled", True) else "✗ Inactiva"
            sem = r.get("semantic_key", "—") or "—"
            self._tree.insert("", "end", values=(
                r["name"], r["pattern"], sem, state,
            ))
        self._status.config(text=f"{len(self.rules)} regla(s) registrada(s)")

    # ── Actions ─────────────────────────────────────────────────────────

    def _new_rule(self) -> None:
        dlg = _RuleDialog(self, title="Nueva regla")
        if dlg.result:
            self.rules.append(dlg.result)
            self._save_and_notify()

    def _edit_rule(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        rule = self.rules[idx]
        dlg = _RuleDialog(self, title="Editar regla", initial=rule)
        if dlg.result:
            self.rules[idx] = dlg.result
            self._save_and_notify()

    def _toggle_rule(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.rules[idx]["enabled"] = not self.rules[idx].get("enabled", True)
        self._save_and_notify()

    def _delete_rule(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        name = self.rules[idx]["name"]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la regla «{name}»?"):
            self.rules.pop(idx)
            self._save_and_notify()

    def _selected_index(self) -> Optional[int]:
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Seleccione una regla primero.")
            return None
        return self._tree.index(sel[0])

    def _save_and_notify(self) -> None:
        # Persist
        os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
        with open(self.rules_path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
        self._refresh_table()
        # Clear engine cache so recompilation picks up changes
        self.engine.clear_cache()
        if self.on_rules_changed:
            self.on_rules_changed(self.rules)


# ── Rule dialog ──────────────────────────────────────────────────────────────

class _RuleDialog(tk.Toplevel):
    """Modal dialog for creating / editing a rule."""

    result: Optional[dict] = None

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Regla",
        initial: Optional[dict] = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(bg=Colors.BG_SECONDARY)
        self.resizable(False, False)
        self.grab_set()

        init = initial or {}

        pad = {"padx": 16, "pady": 4}

        ttk.Label(self, text="Nombre:", style="Card.TLabel").grid(row=0, column=0, sticky="w", **pad)
        self._name_var = tk.StringVar(value=init.get("name", ""))
        tk.Entry(self, textvariable=self._name_var, width=40, font=Fonts.BODY,
                 bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY, insertbackground=Colors.TEXT_PRIMARY,
                 relief="flat").grid(row=0, column=1, **pad)

        ttk.Label(self, text="Patrón (DSL):", style="Card.TLabel").grid(row=1, column=0, sticky="w", **pad)
        self._pattern_var = tk.StringVar(value=init.get("pattern", ""))
        tk.Entry(self, textvariable=self._pattern_var, width=40, font=Fonts.MONO,
                 bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY, insertbackground=Colors.TEXT_PRIMARY,
                 relief="flat").grid(row=1, column=1, **pad)

        ttk.Label(self, text="Validación semántica:", style="Card.TLabel").grid(row=2, column=0, sticky="w", **pad)
        self._sem_var = tk.StringVar(value=init.get("semantic_key", ""))
        tk.Entry(self, textvariable=self._sem_var, width=40, font=Fonts.BODY,
                 bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY, insertbackground=Colors.TEXT_PRIMARY,
                 relief="flat").grid(row=2, column=1, **pad)

        self._enabled_var = tk.BooleanVar(value=init.get("enabled", True))
        ttk.Checkbutton(self, text="Activa", variable=self._enabled_var,
                        style="Card.TCheckbutton").grid(row=3, column=1, sticky="w", **pad)

        # Buttons
        btn_frame = ttk.Frame(self, style="Card.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Guardar", style="Accent.TButton",
                   command=self._on_save).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=8)

        # Test button
        ttk.Button(btn_frame, text="Probar patrón", command=self._test_pattern).pack(side="left", padx=8)

        self.wait_window()

    def _on_save(self) -> None:
        name = self._name_var.get().strip()
        pattern = self._pattern_var.get().strip()
        if not name or not pattern:
            messagebox.showwarning("Aviso", "El nombre y el patrón son obligatorios.")
            return
        # Try to compile to verify syntax
        try:
            from pattern_engine.pattern_engine import PatternEngine
            PatternEngine().compile(pattern, name=name)
        except Exception as ex:
            messagebox.showerror("Error de patrón", f"No se pudo compilar el patrón:\n{ex}")
            return

        self.result = {
            "name": name,
            "pattern": pattern,
            "semantic_key": self._sem_var.get().strip() or None,
            "enabled": self._enabled_var.get(),
        }
        self.destroy()

    def _test_pattern(self) -> None:
        pattern = self._pattern_var.get().strip()
        if not pattern:
            messagebox.showwarning("Aviso", "Ingrese un patrón primero.")
            return
        test_str = simpledialog.askstring(
            "Probar patrón", "Cadena de prueba:", parent=self,
        )
        if test_str is None:
            return
        try:
            eng = PatternEngine()
            sem = self._sem_var.get().strip() or None
            cp = eng.compile(pattern, semantic_key=sem)
            result = eng.match(test_str, compiled=cp)
            icon = "✓ Aceptada" if result else "✗ Rechazada"
            messagebox.showinfo("Resultado", f"{icon}\n\nCadena: {test_str!r}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
