"""
Pruebas integradas de patrones completos.

Corresponden a los casos de prueba del documento de requisitos (TC01–TC05)
y casos adicionales.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.pattern_engine import PatternEngine
import pytest


@pytest.fixture
def engine():
    return PatternEngine()


# ── TC01–TC05 del documento de requisitos ──────────────────────────────────

class TestRequirementsCases:
    """Casos de prueba especificados en el análisis de requisitos."""

    def test_TC01_correo_valido(self, engine):
        """TC01 — Correo juan@mail.com → Aceptar"""
        cp = engine.compile(
            '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
            name="correo", semantic_key="correo",
        )
        assert engine.match("juan@mail.com", compiled=cp) is True

    def test_TC02_correo_invalido(self, engine):
        """TC02 — Correo juan@mail → Rechazar"""
        cp = engine.compile(
            '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
            name="correo", semantic_key="correo",
        )
        assert engine.match("juan@mail", compiled=cp) is False

    def test_TC03_fecha_bisiesto(self, engine):
        """TC03 — Fecha 2024-02-29 → Aceptar (año bisiesto)"""
        cp = engine.compile(
            '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
            name="fecha", semantic_key="fecha_iso",
        )
        assert engine.match("2024-02-29", compiled=cp) is True

    def test_TC04_fecha_no_bisiesto(self, engine):
        """TC04 — Fecha 2023-02-29 → Rechazar (no bisiesto)"""
        cp = engine.compile(
            '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
            name="fecha", semantic_key="fecha_iso",
        )
        assert engine.match("2023-02-29", compiled=cp) is False

    def test_TC05_placa_valida(self, engine):
        """TC05 — Placa ABC-123 → Aceptar"""
        cp = engine.compile(
            '[A-Z]{3} "-" [0-9]{3}',
            name="placa", semantic_key="placa",
        )
        assert engine.match("ABC-123", compiled=cp) is True


# ── Additional cases ───────────────────────────────────────────────────────

class TestAdditionalPatterns:
    def test_telefono_con_prefijo(self, engine):
        cp = engine.compile(
            '("+" digito{1,3} " ")? digito{7,15}',
            name="telefono", semantic_key="telefono",
        )
        assert engine.match("+57 3001234567", compiled=cp) is True

    def test_telefono_corto(self, engine):
        cp = engine.compile(
            '("+" digito{1,3} " ")? digito{7,15}',
            name="telefono", semantic_key="telefono",
        )
        assert engine.match("123", compiled=cp) is False

    def test_identificador_valido(self, engine):
        cp = engine.compile(
            '(letra|"_") (letra|digito|"_")*',
            name="id",
        )
        assert engine.match("mi_variable_1", compiled=cp) is True

    def test_identificador_empieza_digito(self, engine):
        cp = engine.compile(
            '(letra|"_") (letra|digito|"_")*',
            name="id",
        )
        assert engine.match("1variable", compiled=cp) is False

    def test_placa_invalida(self, engine):
        cp = engine.compile(
            '[A-Z]{3} "-" [0-9]{3}',
            name="placa", semantic_key="placa",
        )
        assert engine.match("AB-12", compiled=cp) is False

    def test_correo_con_puntos(self, engine):
        cp = engine.compile(
            '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
            name="correo", semantic_key="correo",
        )
        assert engine.match("ana.maria@sub.domain.com", compiled=cp) is True

    def test_fecha_mes_invalido(self, engine):
        cp = engine.compile(
            '[0-9]{4} "-" [0-9]{2} "-" [0-9]{2}',
            name="fecha", semantic_key="fecha_iso",
        )
        assert engine.match("2024-13-01", compiled=cp) is False

    def test_search_multiple_emails(self, engine):
        cp = engine.compile(
            '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
            name="correo", semantic_key="correo",
        )
        text = "Contactos: admin@web.com, soporte@empresa.org y ventas@tienda.net"
        hits = engine.search(text, compiled=cp)
        assert len(hits) == 3
        emails = [h.text for h in hits]
        assert "admin@web.com" in emails
        assert "soporte@empresa.org" in emails
        assert "ventas@tienda.net" in emails
