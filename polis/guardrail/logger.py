"""Guardrail log — écriture append-only dans ~/.openclaw/guardrail.log."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

LOG_PATH = Path.home() / ".openclaw" / "guardrail.log"


def log_decision(
  agent: str,
  skill: str,
  action: str,
  level: int,
  decision: str,
  reason: str,
  session_id: str = "",
  gate_id: str | None = None,
) -> None:
  """Écrit une entrée dans guardrail.log (format immutable)."""
  ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
  fields = [ts, agent, skill, action, str(level), decision, reason, session_id]
  if gate_id:
    fields.append(gate_id)

  LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
  with LOG_PATH.open("a", encoding="utf-8") as f:
    f.write("|".join(fields) + "\n")
