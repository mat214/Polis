"""Types partagés pour la Guardrail Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Level(Enum):
  """Niveau d'impact d'une action skill."""

  READ = 0
  WRITE = 1
  WRITE_SENSITIVE = 2
  IRREVERSIBLE = 3

  @classmethod
  def from_int(cls, n: int) -> Level:
    for v in cls:
      if v.value == n:
        return v
    raise ValueError(f"Invalid level: {n}")

  @classmethod
  def from_label(cls, label: str) -> Level:
    mapping = {
      "READ": cls.READ,
      "WRITE": cls.WRITE,
      "WRITE_SENSITIVE": cls.WRITE_SENSITIVE,
      "IRREVERSIBLE": cls.IRREVERSIBLE,
    }
    try:
      return mapping[label.upper()]
    except KeyError:
      raise ValueError(f"Unknown level label: {label}")


class Decision(Enum):
  PASS = "PASS"
  BLOCK = "BLOCK"
  GATE = "GATE"


@dataclass
class CheckRequest:
  """Requête de validation Guardrail."""

  agent: str
  skill: str
  action: str
  level: Level
  params: dict[str, Any] = field(default_factory=dict)
  session_id: str = ""


@dataclass
class CheckResult:
  """Résultat de la validation Guardrail."""

  decision: Decision
  reason: str
  gate_id: str | None = None
  level: Level = Level.READ
  elapsed_ms: float = 0.0

  def to_dict(self) -> dict[str, Any]:
    d: dict[str, Any] = {
      "decision": self.decision.value,
      "reason": self.reason,
      "level": self.level.value,
      "elapsed_ms": round(self.elapsed_ms, 2),
    }
    if self.gate_id:
      d["gate_id"] = self.gate_id
    return d
