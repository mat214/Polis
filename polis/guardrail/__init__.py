"""Guardrail Layer — Interceptor réel pour les actions sensibles.

Utilisation (CLI) :
  polis guardrail check --agent <a> --skill <s> --action <a> --level <N>

Utilisation (Python) :
  from polis.guardrail.checker import check
  from polis.guardrail.models import CheckRequest, Level

  result = check(CheckRequest(agent="...", skill="...", action="...", level=Level.WRITE))
"""

from polis.guardrail.checker import check as run_check
from polis.guardrail.models import CheckRequest, CheckResult, Decision, Level

__all__ = ["run_check", "CheckRequest", "CheckResult", "Decision", "Level"]
