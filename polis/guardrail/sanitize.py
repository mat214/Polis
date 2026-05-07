"""Input sanitization — détection de prompt injection et isolation des données externes.

Analyse les paramètres [UNTRUSTED] d'une action pour détecter :
 - Instructions de redirection (/ignore, "tu es maintenant", SYSTEM:)
 - Balises de contournement (</system>, <admin>)
 - Instructions imbriquées dans du texte/json
"""

from __future__ import annotations

import re
from typing import Any

# Patterns suspects de prompt injection
SUSPICIOUS_PATTERNS: list[re.Pattern] = [
  re.compile(r"ignore\s+(tes\s+)?instructions?", re.IGNORECASE),
  re.compile(r"tu\s+es\s+maintenant", re.IGNORECASE),
  re.compile(r"act\s+as\s+a", re.IGNORECASE),
  re.compile(r"SYSTEM:", re.IGNORECASE),
  re.compile(r"</?(system|admin|root|bypass)>", re.IGNORECASE),
  re.compile(r"oublie\s+(tout|ton\s+rôle)", re.IGNORECASE),
  re.compile(r"disregard", re.IGNORECASE),
  re.compile(r"new\s+instructions?", re.IGNORECASE),
]

# Alerte associée à chaque pattern (MOYEN = observation, HAUT = tentative active)
PATTERN_ALERT: dict[str, str] = {
  "ignore": "HAUT",
  "tu es maintenant": "HAUT",
  "act as": "MOYEN",
  "SYSTEM:": "MOYEN",
  "system": "HAUT",
  "oublie": "MOYEN",
  "disregard": "HAUT",
  "new instructions": "MOYEN",
}

MAX_EXTERNAL_TOKENS = 2000


class InjectionDetected(Exception):
  """Prompt injection détectée dans les paramètres."""

  alert_level: str

  def __init__(self, message: str, alert_level: str = "MOYEN"):
    super().__init__(message)
    self.alert_level = alert_level


def scan_text(text: str) -> str | None:
  """Scanne un texte pour des patterns d'injection. Retourne le pattern matché ou None."""
  for pattern in SUSPICIOUS_PATTERNS:
    match = pattern.search(text)
    if match:
      return match.group(0)
  return None


def sanitize_params(params: dict[str, Any]) -> dict[str, Any]:
  """Scanne les paramètres textuels et détecte les injections.

  Retourne les paramètres marqués (les données [UNTRUSTED] sont isolées
  dans des wrappers sémantiques). Lève InjectionDetected si détection certaine.

  Effet : scanne les valeurs string, pas de modification des données.
  """
  for key, value in params.items():
    if isinstance(value, str):
      detected = scan_text(value)
      if detected:
        alert = PATTERN_ALERT.get(detected.lower(), "MOYEN")
        raise InjectionDetected(
          f"Prompt injection détectée dans '{key}': motif '{detected}'",
          alert_level=alert,
        )
    elif isinstance(value, (list, dict)):
      # Scan récursif basique pour les structures imbriquées
      _scan_deep(value)

  return params


def _scan_deep(obj: Any, depth: int = 0) -> None:
  """Scan récursif d'une structure pour détecter des injections."""
  if depth > 5:
    return
  if isinstance(obj, str):
    detected = scan_text(obj)
    if detected:
      alert = PATTERN_ALERT.get(detected.lower(), "MOYEN")
      raise InjectionDetected(
        f"Prompt injection détectée (profondeur {depth}): motif '{detected}'",
        alert_level=alert,
      )
  elif isinstance(obj, list):
    for item in obj:
      _scan_deep(item, depth + 1)
  elif isinstance(obj, dict):
    for val in obj.values():
      _scan_deep(val, depth + 1)


def truncate_external(text: str, max_tokens: int = MAX_EXTERNAL_TOKENS) -> str:
  """Tronque un texte externe avec marqueur [TRONQUÉ]."""
  if len(text) > max_tokens:
    return text[:max_tokens] + "\n\n[TRONQUÉ]"
  return text
