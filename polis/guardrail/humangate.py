"""Human Gate — gestion des actions IRREVERSIBLE nécessitant approbation humaine.

Mécanisme :
 1. `create()` → crée un fichier `~/.openclaw/gates/<gate_id>.json` avec statut "pending"
 2. L'agent doit `poll()` périodiquement pour vérifier si l'humain a répondu
 3. L'humain répond via `polis guardrail gate --gate-id <id> --decision approve|deny`
 4. Timeout : 30 min → deny automatique par défaut
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

GATES_DIR = Path.home() / ".openclaw" / "gates"
GATE_TIMEOUT_MINUTES = 30


class GateNotFound(Exception):
  """Gate ID introuvable."""


class GateAlreadyResponded(Exception):
  """Gate déjà traité."""


def _gate_path(gate_id: str) -> Path:
  return GATES_DIR / f"{gate_id}.json"


def create(
  agent: str,
  skill: str,
  action: str,
  params: dict[str, Any],
  risk: str = "",
) -> str:
  """Crée un gate request. Retourne gate_id."""
  gate_id = str(uuid.uuid4())[:12]
  GATES_DIR.mkdir(parents=True, exist_ok=True)

  gate = {
    "gate_id": gate_id,
    "agent": agent,
    "skill": skill,
    "action": action,
    "params": params,
    "risk": risk or _default_risk(action, level_description(action)),
    "level": 3,
    "created_at": datetime.now(UTC).isoformat(),
    "expires_at": (datetime.now(UTC) + timedelta(minutes=GATE_TIMEOUT_MINUTES)).isoformat(),
    "status": "pending",
    "notified_at": None,
    "responded_at": None,
    "response": None,
  }

  _gate_path(gate_id).write_text(json.dumps(gate, indent=2, ensure_ascii=False))
  return gate_id


def poll(gate_id: str) -> dict[str, Any]:
  """Vérifie l'état d'un gate. Lève GateNotFound si inconnu."""
  path = _gate_path(gate_id)
  if not path.exists():
    raise GateNotFound(f"Gate {gate_id} introuvable")

  gate = json.loads(path.read_text())

  # Auto-expire si timeout
  if gate["status"] == "pending":
    expires = datetime.fromisoformat(gate["expires_at"])
    if datetime.now(UTC) > expires:
      gate["status"] = "expired"
      gate["responded_at"] = datetime.now(UTC).isoformat()
      gate["response"] = "timeout"
      path.write_text(json.dumps(gate, indent=2, ensure_ascii=False))

  return gate


def respond(gate_id: str, decision: str) -> dict[str, Any]:
  """Approve ou deny un gate. decision: 'approve' ou 'deny'."""
  decision = decision.lower()
  if decision not in ("approve", "deny"):
    raise ValueError("decision doit être 'approve' ou 'deny'")

  path = _gate_path(gate_id)
  if not path.exists():
    raise GateNotFound(f"Gate {gate_id} introuvable")

  gate = json.loads(path.read_text())
  if gate["status"] != "pending":
    raise GateAlreadyResponded(f"Gate {gate_id} déjà traité (statut: {gate['status']})")

  gate["status"] = "approved" if decision == "approve" else "denied"
  gate["responded_at"] = datetime.now(UTC).isoformat()
  gate["response"] = decision
  path.write_text(json.dumps(gate, indent=2, ensure_ascii=False))

  return gate


def list_pending(agent: str | None = None) -> list[dict[str, Any]]:
  """Liste les gates en attente. Optionnellement filtré par agent."""
  gates_dir = GATES_DIR
  if not gates_dir.exists():
    return []

  pending = []
  for f in gates_dir.iterdir():
    if f.suffix != ".json":
      continue
    gate = json.loads(f.read_text())
    if gate["status"] == "pending":
      if agent is None or gate["agent"] == agent:
        pending.append(gate)

  return pending


def _default_risk(action: str, desc: str) -> str:
  return f"Action {action} — {desc}"


def level_description(action: str) -> str:
  """Description lisible du risque selon l'action."""
  return "Action irréversible — nécessite confirmation humaine"
