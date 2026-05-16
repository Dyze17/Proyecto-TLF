"""
Semantic validators — post-match validation that goes beyond what a
regular expression (automaton) can check.

For example, ``2024-02-29`` matches the *format* ``YYYY-MM-DD`` but
whether it's a real date requires checking leap-year rules.
"""

from __future__ import annotations
from typing import Callable, Dict, Optional
import calendar


# ── Validator registry ───────────────────────────────────────────────────────

ValidatorFunc = Callable[[str], bool]
_VALIDATORS: Dict[str, ValidatorFunc] = {}


def register_validator(name: str) -> Callable[[ValidatorFunc], ValidatorFunc]:
    """Decorator to register a semantic validator by name."""
    def decorator(fn: ValidatorFunc) -> ValidatorFunc:
        _VALIDATORS[name] = fn
        return fn
    return decorator


def get_validator(name: str) -> Optional[ValidatorFunc]:
    """Return the validator for *name*, or ``None``."""
    return _VALIDATORS.get(name)


def validate(name: str, text: str) -> bool:
    """Run the semantic validator named *name* on *text*.

    Returns ``True`` if the validator does not exist (no extra check).
    """
    fn = _VALIDATORS.get(name)
    if fn is None:
        return True
    return fn(text)


# ── Built-in validators ─────────────────────────────────────────────────────

@register_validator("fecha_iso")
def _validate_fecha_iso(text: str) -> bool:
    """Validate a date in ``YYYY-MM-DD`` format (semantic check)."""
    parts = text.split("-")
    if len(parts) != 3:
        return False
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return False
    if month < 1 or month > 12:
        return False
    max_day = calendar.monthrange(year, month)[1]
    return 1 <= day <= max_day


@register_validator("fecha_dmy")
def _validate_fecha_dmy(text: str) -> bool:
    """Validate a date in ``DD/MM/YYYY`` format."""
    parts = text.split("/")
    if len(parts) != 3:
        return False
    try:
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return False
    if month < 1 or month > 12:
        return False
    max_day = calendar.monthrange(year, month)[1]
    return 1 <= day <= max_day


@register_validator("correo")
def _validate_correo(text: str) -> bool:
    """Basic semantic check for e-mail addresses."""
    # Must have exactly one @
    if text.count("@") != 1:
        return False
    local, domain = text.split("@")
    if not local or not domain:
        return False
    # Domain must have at least one dot
    if "." not in domain:
        return False
    # TLD must be 2-4 letters
    tld = domain.rsplit(".", 1)[-1]
    if not tld.isalpha() or not (2 <= len(tld) <= 4):
        return False
    # No consecutive dots
    if ".." in local or ".." in domain:
        return False
    return True


@register_validator("telefono")
def _validate_telefono(text: str) -> bool:
    """Semantic check for phone numbers."""
    # Remove spaces and dashes for checking
    cleaned = text.replace(" ", "").replace("-", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    # Must be all digits after cleaning
    if not cleaned.isdigit():
        return False
    # Reasonable length: 7 to 15 digits
    return 7 <= len(cleaned) <= 15


@register_validator("url")
def _validate_url(text: str) -> bool:
    """Semantic check for URLs."""
    # Must start with a scheme
    if "://" not in text:
        return False
    scheme, rest = text.split("://", 1)
    if not scheme.isalpha():
        return False
    if not rest:
        return False
    # Host must be present
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    if not host:
        return False
    return True


@register_validator("placa")
def _validate_placa(text: str) -> bool:
    """Semantic check for Colombian license plates (ABC-123 / ABC123)."""
    cleaned = text.replace("-", "").replace(" ", "").upper()
    if len(cleaned) != 6:
        return False
    return cleaned[:3].isalpha() and cleaned[3:].isdigit()
