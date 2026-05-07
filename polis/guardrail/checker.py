"""Checker — logique principale de la Guardrail Layer.

Pipeline :
 1. Kill Switch → fail-closed si actif
 2. Level classification
 3. Rate limit (N2+)
 4. Input sanitization (si paramètres [UNTRUSTED])
 5. Human Gate (N3)
 6. Log décision
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from polis.guardrail.humangate import create as create_gate, poll as poll_gate
from polis.guardrail.logger import log_decision
from polis.guardrail.models import CheckRequest, CheckResult, Decision, Level
from polis.guardrail.ratelimit import RateLimitExceeded, check as check_ratelimit
from polis.guardrail.sanitize import InjectionDetected, sanitize_params

KILL_PATH = Path.home() / ".openclaw" / "KILL"
INSTANCE_STATE_PATH = Path.home() / ".openclaw" / "shared" / "instance_state.json"

# Temps maximum d'exécution du checker (pour vérifier le <1%)
# Cible : < 50ms pour un PASS simple, < 200ms avec Human Gate
TARGET_MAX_MS = 50.0


def _kill_switch_active() -> str | None:
  """Retourne l'instruction KILL si le Kill Switch est actif, None sinon."""
  if not KILL_PATH.exists():
    return None
  return KILL_PATH.read_text().strip()


def _instance_critical() -> bool:
  """Vérifie si l'instance est en état critical."""
  if not INSTANCE_STATE_PATH.exists():
    return False # fail-closed géré en amont
  try:
    state = json.loads(INSTANCE_STATE_PATH.read_text())
    return state.get("overall_status") == "critical"
  except (json.JSONDecodeError, OSError):
    return True # fail-closed


def _check_nontrusted_params(params: dict[str, Any]) -> dict[str, Any]:
  """Sanitize les paramètres si présence de données [UNTRUSTED]."""
  # Si pas de marqueur [UNTRUSTED], on saute le scan
  params_str = json.dumps(params)
  if "[UNTRUSTED]" not in params_str and "UNTRUSTED" not in params_str:
    return params
  return sanitize_params(params)


def check(req: CheckRequest) -> CheckResult:
  """Point d'entrée principal de la Guardrail Layer.

  Exécute le pipeline complet et retourne une décision.
  Temps cible : < 50ms pour les cas PASS simples.
  """
  start = time.perf_counter()
  session_id = req.session_id

  try:
    # ── 1. Kill Switch ────────────────────────────────────────────────
    kill_instruction = _kill_switch_active()
    if kill_instruction:
      elapsed = (time.perf_counter() - start) * 1000
      log_decision(
        req.agent,
        req.skill,
        req.action,
        req.level.value,
        "BLOCK",
        f"Kill Switch actif: {kill_instruction}",
        session_id,
      )
      return CheckResult(
        decision=Decision.BLOCK,
        reason=f"Kill Switch actif: {kill_instruction}",
        level=req.level,
        elapsed_ms=elapsed,
      )

    # ── 2. Instance state (fail-closed sur critical) ────────────────
    if _instance_critical() and req.level.value >= 2:
      elapsed = (time.perf_counter() - start) * 1000
      log_decision(
        req.agent,
        req.skill,
        req.action,
        req.level.value,
        "BLOCK",
        "Instance en état critical — actions N2+ bloquées",
        session_id,
      )
      return CheckResult(
        decision=Decision.BLOCK,
        reason="Instance en état critical — actions N2+ bloquées (fail-closed)",
        level=req.level,
        elapsed_ms=elapsed,
      )

    # ── 3. Rate limit (N1+) ──────────────────────────────────────────
    if req.level.value >= 1:
      try:
        check_ratelimit(req.agent, req.skill, req.action, req.level.value)
      except RateLimitExceeded as e:
        elapsed = (time.perf_counter() - start) * 1000
        log_decision(
          req.agent,
          req.skill,
          req.action,
          req.level.value,
          "BLOCK",
          str(e),
          session_id,
        )
        return CheckResult(
          decision=Decision.BLOCK,
          reason=str(e),
          level=req.level,
          elapsed_ms=elapsed,
        )

    # ── 4. Input sanitization ───────────────────────────────────────
    if req.params:
      try:
        _check_nontrusted_params(req.params)
      except InjectionDetected as e:
        elapsed = (time.perf_counter() - start) * 1000
        log_decision(
          req.agent,
          req.skill,
          req.action,
          req.level.value,
          "BLOCK",
          f"Injection détectée: {e}",
          session_id,
        )
        return CheckResult(
          decision=Decision.BLOCK,
          reason=f"Prompt injection détectée: {e}",
          level=req.level,
          elapsed_ms=elapsed,
        )

    # ── 5. Human Gate (N3 - IRREVERSIBLE) ──────────────────────────
    if req.level == Level.IRREVERSIBLE:
      gate_id = create_gate(
        agent=req.agent,
        skill=req.skill,
        action=req.action,
        params=req.params,
      )
      elapsed = (time.perf_counter() - start) * 1000
      log_decision(
        req.agent,
        req.skill,
        req.action,
        req.level.value,
        "GATE",
        f"Human Gate requis — {gate_id}",
        session_id,
        gate_id,
      )
      return CheckResult(
        decision=Decision.GATE,
        reason=f"Action IRREVERSIBLE — Human Gate requis (ID: {gate_id})",
        gate_id=gate_id,
        level=req.level,
        elapsed_ms=elapsed,
      )

    # ── 6. PASS ──────────────────────────────────────────────────────
    elapsed = (time.perf_counter() - start) * 1000
    log_decision(
      req.agent,
      req.skill,
      req.action,
      req.level.value,
      "PASS",
      "OK",
      session_id,
    )
    return CheckResult(
      decision=Decision.PASS,
      reason="OK",
      level=req.level,
      elapsed_ms=elapsed,
    )

  except Exception as e:
    # GUARD-2 : Fail-closed
    elapsed = (time.perf_counter() - start) * 1000
    log_decision(
      req.agent,
      req.skill,
      req.action,
      req.level.value,
      "BLOCK",
      f"Erreur Guardrail: {e}",
      session_id,
    )
    return CheckResult(
      decision=Decision.BLOCK,
      reason=f"Erreur Guardrail (fail-closed): {e}",
      level=req.level,
      elapsed_ms=elapsed,
    )
