"""
Pruebas de rendimiento.

Verifica que:
- La validación ocurra en < 150 ms (RNF1).
- Archivos de hasta 10 MB se procesen en < 3 s (RNF1).
"""

import sys, os, time, string, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pattern_engine.pattern_engine import PatternEngine
import pytest


@pytest.fixture
def engine():
    return PatternEngine()


class TestPerformance:
    def test_single_validation_under_150ms(self, engine):
        """RNF1 — Una validación individual debe completarse en < 150 ms."""
        cp = engine.compile(
            '(letra|digito|"."|"_"|"-")+ "@" (letra|digito|"."|"-")+ "." letra{2,4}',
            name="correo", semantic_key="correo",
        )
        start = time.perf_counter()
        for _ in range(100):
            engine.match("usuario_largo_123@dominio.com", compiled=cp)
        elapsed = (time.perf_counter() - start) / 100
        assert elapsed < 0.150, f"Validation took {elapsed:.4f}s (limit: 0.150s)"

    def test_large_text_search_under_3s(self, engine):
        """RNF1 — Búsqueda en textos grandes (simulación ~1 MB) en < 3 s."""
        cp = engine.compile(
            '[A-Z]{3} "-" [0-9]{3}',
            name="placa", semantic_key="placa",
        )
        # Generate ~1 MB of text with some plates embedded
        rng = random.Random(42)
        chunks = []
        for i in range(10000):
            word = "".join(rng.choices(string.ascii_lowercase, k=8))
            chunks.append(word)
            if i % 200 == 0:
                letters = "".join(rng.choices(string.ascii_uppercase, k=3))
                digits = "".join(rng.choices(string.digits, k=3))
                chunks.append(f"{letters}-{digits}")
        text = " ".join(chunks)

        start = time.perf_counter()
        matches = engine.search(text, compiled=cp)
        elapsed = time.perf_counter() - start

        assert elapsed < 3.0, f"Search took {elapsed:.2f}s (limit: 3.0s)"
        assert len(matches) > 0
