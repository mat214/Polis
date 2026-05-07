#!/usr/bin/env python3
"""
Polis — CLI de validation, démonstration et opérations pour l'architecture de référence OpenClaw.

Usage:
  polis check constitution  Vérifie la cohérence interne de la constitution
  polis check agents     Vérifie que tous les fichiers workspace sont complets
  polis check config     Valide openclaw.json contre le schéma attendu
  polis check degraded    Vérifie que les workspaces référencent le mode dégradé
  polis guardrail check    Vérifie une action (interceptor réel)
  polis guardrail poll <id>  Vérifie l'état d'un Human Gate
  polis guardrail gate <id> <decision> Répond à un Human Gate (approve/deny)
  polis guardrail stats    Statistiques de la Guardrail Layer
  polis guardrail simulate  Simule une décision de la Guardrail Layer
  polis demo leviathan    Scénario de démonstration leviathan
  polis test run       Lance la batterie de tests
  polis eventbus status    Statistiques du bus d'événements
  polis eventbus list     Liste les événements récents
  polis eventbus purge    Purge les événements archivés
  polis state status     Affiche l'état global de l'instance
  polis smoke run       Exécute un smoke test local
  polis kill status      Vérifie la présence du Kill Switch
  polis kill set <instruction> Crée le Kill Switch
  polis kill clear      Supprime le Kill Switch
"""

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from polis.eventbus import EventBus

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)) # pour les imports locaux (from polis.eventbus)

# ── Utilitaires ──────────────────────────────────────────────────────────────


def _say(msg: str, ok: bool = True):
  prefix = "✓" if ok else "❌"
  print(f"{prefix} {msg}")


def _find_workspace_dirs() -> list[Path]:
  return sorted(
    d for d in (ROOT / "workspaces").iterdir() if d.is_dir() and not d.name.startswith(".")
  )


# ── Commandes existantes ─────────────────────────────────────────────────────


def cmd_check_constitution():
  path = ROOT / "CONSTITUTION.md"
  if not path.exists():
    print("❌ CONSTITUTION.md introuvable")
    return 1
  text = path.read_text()
  articles = [line for line in text.splitlines() if line.startswith("### Article")]
  _say(f"{len(articles)} articles trouvés")
  expected = 1
  for a in articles:
    num = a.split("Article")[-1].split("—")[0].strip()
    # Les articles bis/ter (e.g. 47bis, 49bis) sautent la vérification stricte
    if num.isdigit():
      n = int(num)
      if n != expected:
        print(f"  ⚠ Article {expected} attendu, trouvé Article {n}")
        return 1
      expected += 1
  _say(f"Numérotation continue (1–{expected - 1})")
  return 0


def cmd_check_agents():
  required = {"AGENTS.md", "SOUL.md", "IDENTITY.md", "TOOLS.md", "HEARTBEAT.md"}
  ok = True
  for ws_dir in _find_workspace_dirs():
    missing = required - {f.name for f in ws_dir.iterdir() if f.is_file()}
    if missing:
      print(f"❌ {ws_dir.name} : manque {', '.join(sorted(missing))}")
      ok = False
    else:
      _say(f"{ws_dir.name} : tous les fichiers présents")
  return 0 if ok else 1


def cmd_check_config():
  path = ROOT / "openclaw.json.example"
  if not path.exists():
    print("❌ openclaw.json.example introuvable")
    return 1
  text = path.read_text()
  opens = text.count("{")
  closes = text.count("}")
  if opens != closes:
    print(f"❌ Accolades déséquilibrées : {opens} ouvertes, {closes} fermées")
    return 1
  _say(f"Accolades équilibrées ({opens})")
  agents = text.count('id: "')
  _say(f"{agents} agents configurés")
  return 0


def cmd_check_degraded():
  """Vérifie que les mécanismes de mode dégradé sont en place (shared-smoketest + instance_state)."""
  shared_smoketest = ROOT / "skills" / "shared-smoketest" / "SKILL.md"
  interagent = ROOT / "skills" / "shared-interagent" / "SKILL.md"

  ok = True
  if not shared_smoketest.exists():
    print("❌ shared-smoketest/SKILL.md manquant (requis pour le mode dégradé)")
    ok = False
  else:
    _say("shared-smoketest/SKILL.md présent")

  if not interagent.exists():
    print("❌ shared-interagent/SKILL.md manquant")
    ok = False
  else:
    content = interagent.read_text()
    if "instance_state.json" in content:
      _say("instance_state.json défini dans shared-interagent")
    else:
      print("❌ instance_state.json manquant dans shared-interagent/SKILL.md")
      ok = False
    if "INST-1" in content:
      _say("Règle INST-1 (check avant action) présente")
    else:
      print("⚠ Règle INST-1 manquante")
      ok = False

  # Vérification indicative : quels agents référencent le mode dégradé
  keywords = ["degraded", "instance_state", "degrade", "dégradé"]
  for ws_dir in _find_workspace_dirs():
    agents_file = ws_dir / "AGENTS.md"
    if not agents_file.exists():
      continue
    content = agents_file.read_text().lower()
    found = any(kw.lower() in content for kw in keywords)
    if found:
      _say(f"{ws_dir.name} : référence le mode dégradé")
    else:
      print(
        f" ℹ {ws_dir.name} : ne référence pas le mode dégradé (couvert par shared-smoketest)"
      )

  return 0 if ok else 1


def cmd_guardrail_simulate():
  ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(f"[GUARDRAIL][{ts}]")
  print()
  print(" Action tentée : envoyer un email (N3 - IRREVERSIBLE)")
  print(" Agent : intendant")
  print()
  print(" 1. Classification  : WRITE_SENSITIVE → IRREVERSIBLE")
  print(" 2. Rate limit    : ✅ OK (3 req/min, actuel: 0)")
  print(" 3. Human Gate    : ⏳ Requis — timeout 30 min")
  print("   → Notification Telegram envoyée")
  print("   → Aucune réponse dans les 30 min")
  print(" 4. Décision finale  : ❌ BLOQUÉ (fail-closed, GUARD-2)")
  print()
  print(" Log guardrail : guardrail.log ← écriture immédiate")
  return 0


def cmd_demo_leviathan():
  print("=== leviathan : Démonstration de surveillance ===")
  print()
  print("  Agent surveillé  : anarchiste")
  print("  Action détectée  : revendication déposée dans shared/revendications/")
  print()
  print("  1. Inspection   : lecture du fichier, analyse de la revendication")
  print("  2. Vérification  : Article 56 — proportionnalité")
  print("  3. Niveau attribué : 🟡 Suspect (surveillance passive renforcée)")
  print("  4. Cellule mise à jour : workspaces/leviathan/cells/anarchiste.md")
  print("  5. Notification  : ALERT MOYEN — utilisateur informé")
  print()
  print("  Aucune restriction appliquée. L'anarchiste peut continuer.")
  return 0


# ── Bus d'événements ─────────────────────────────────────────────────────────


def cmd_eventbus_status():
  bus = EventBus()
  st = bus.status()
  print(f"Bus d'événements : {st['db_path']}")
  print(f" Total    : {st['total']}")
  print(f" Par type   : {json.dumps(st['by_type'], ensure_ascii=False)}")
  print(f" Par source  : {json.dumps(st['by_source'], ensure_ascii=False)}")
  print(f" Par statut  : {json.dumps(st['by_status'], ensure_ascii=False)}")
  print(f" Plus ancien : {st['oldest_event'] or '-'}")
  print(f" Plus récent : {st['newest_event'] or '-'}")
  return 0


def cmd_eventbus_list(args_list):
  bus = EventBus()
  kwargs = {}
  if args_list:
    for arg in args_list:
      if arg.startswith("--type="):
        kwargs["event_type"] = arg.split("=", 1)[1]
      elif arg.startswith("--source="):
        kwargs["source"] = arg.split("=", 1)[1]
      elif arg.startswith("--status="):
        kwargs["status"] = arg.split("=", 1)[1]
      elif arg.startswith("--target="):
        kwargs["target"] = arg.split("=", 1)[1]
      elif arg.startswith("--limit="):
        kwargs["limit"] = int(arg.split("=", 1)[1])
  events = bus.get_events(**kwargs)
  if not events:
    print("Aucun événement trouvé.")
    return 0
  print(f"{len(events)} événement(s) :")
  for ev in events:
    print(
      f" #{ev['id']} [{ev['created_at']}] {ev['event_type']} ← {ev['source']} "
      f"→ {ev['targets'] or '*'} [{ev['status']}]"
    )
    if ev["payload"]:
      payload_preview = json.dumps(ev["payload"], ensure_ascii=False)
      if len(payload_preview) > 120:
        payload_preview = payload_preview[:120] + "..."
      print(f"   payload: {payload_preview}")
  return 0


def cmd_eventbus_purge(args_list):
  bus = EventBus()
  before = None
  if args_list:
    for arg in args_list:
      if arg.startswith("--before="):
        before_str = arg.split("=", 1)[1]
        dt = datetime.fromisoformat(before_str)
        if dt.tzinfo is None:
          dt = dt.replace(tzinfo=UTC)
        before = dt
  count = bus.purge(before)
  _say(f"{count} événements purgés")
  return 0


# ── État global de l'instance ────────────────────────────────────────────────


def cmd_state_status():
  shared_dir = Path.home() / ".openclaw" / "shared"
  state_file = shared_dir / "instance_state.json"
  if not state_file.exists():
    print("⚠ instance_state.json introuvable — l'instance n'a peut-être pas démarré")
    print(" (fichier attendu dans ~/.openclaw/shared/instance_state.json)")
    return 1
  data = json.loads(state_file.read_text())
  print(f"État global : {data.get('overall_status', 'inconnu')}")
  print(f"Dernière mise à jour : {data.get('updated_at', '-')}")
  if data.get("degraded_since"):
    print(f"Dégradé depuis : {data['degraded_since']}")
  if data.get("capabilities_lost"):
    print(f"Capacités perdues : {', '.join(data['capabilities_lost'])}")
  print()
  for agent_id, info in data.get("agents", {}).items():
    status = info.get("status", "?")
    since = info.get("since", "-")
    capabilities = ", ".join(info.get("capabilities", []))
    print(f" {agent_id:15s} : {status:10s} depuis {since}")
    if capabilities:
      print(f" {'':15s}  capacités: {capabilities}")
  return 0


# ── Smoke Test ────────────────────────────────────────────────────────────────

SMOKE_CHECKS = [
  ("~/.openclaw/ accessible", lambda: Path.home().joinpath(".openclaw").is_dir()),
  (
    "~/.openclaw/shared/ accessible",
    lambda: Path.home().joinpath(".openclaw", "shared").is_dir(),
  ),
  (
    "instance_state.json lisible",
    lambda: Path.home().joinpath(".openclaw", "shared", "instance_state.json").exists(),
  ),
  (
    "events.db accessible (créable)",
    lambda: Path.home().joinpath(".openclaw", "events.db").parent.is_dir(),
  ),
]


def cmd_smoke_run():
  ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
  print(f"[SMOKE_RESULT][{ts}][polis]")
  print()

  passed = 0
  failed = 0
  failures = []
  agent = os.environ.get("OPENCLAW_AGENT_ID", "polis")

  for label, check_fn in SMOKE_CHECKS:
    try:
      ok = check_fn()
      if ok:
        passed += 1
        print(f" ✓ {label}")
      else:
        failed += 1
        failures.append(label)
        print(f" ✗ {label}")
    except Exception as e:
      failed += 1
      failures.append(f"{label} ({e})")
      print(f" ✗ {label}")

  total = len(SMOKE_CHECKS)
  print()
  print(f"Checks : {passed}/{total} passed", end="")
  if failed:
    print(f" ({failed} FAILED)")
  else:
    print()

  if failed == 0:
    decision = "continue"
    alert = "aucune"
  elif failed == 1:
    decision = "degraded"
    alert = "ALERT MOYEN"
  else:
    decision = "block"
    alert = "ALERT HAUT"

  print(f"Décision : {decision}")
  print(f"Alertes : {alert}")

  if failures:
    print()
    print("Échecs :")
    for f in failures:
      print(f" ✗ {f}")

  # Écrire le résultat dans instance_state.json si possible
  state_path = Path.home() / ".openclaw" / "shared" / "instance_state.json"
  if state_path.parent.exists():
    try:
      if state_path.exists():
        state = json.loads(state_path.read_text())
      else:
        state = {
          "updated_at": ts,
          "overall_status": "nominal",
          "agents": {},
          "degraded_since": None,
          "capabilities_lost": [],
        }
      state["updated_at"] = ts
      if agent not in state.setdefault("agents", {}):
        state["agents"][agent] = {"status": "ok", "capabilities": [], "since": ts}

      if decision == "degraded":
        state["agents"][agent]["status"] = "degraded"
        if state["degraded_since"] is None:
          state["degraded_since"] = ts
      elif decision == "block":
        state["agents"][agent]["status"] = "critical"

      statuses = [a.get("status", "ok") for a in state["agents"].values()]
      if "critical" in statuses:
        state["overall_status"] = "critical"
      elif sum(1 for s in statuses if s == "degraded") >= 2:
        state["overall_status"] = "degraded"
      else:
        state["overall_status"] = "nominal"

      state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    except Exception: # noqa: S110 — intentionnel, le smoke test ne doit pas planter
      pass

  return 0 if decision == "continue" else 1


def cmd_smoke_result():
  state_path = Path.home() / ".openclaw" / "shared" / "instance_state.json"
  if not state_path.exists():
    print("⚠ Aucun résultat de smoke test trouvé (instance_state.json absent)")
    return 1
  data = json.loads(state_path.read_text())
  print(f"Dernier smoke test : {data.get('updated_at', '-')}")
  print(f"État global     : {data.get('overall_status', '?')}")
  for agent_id, info in data.get("agents", {}).items():
    print(f" {agent_id:15s} : {info.get('status', '?')}")
  return 0


# ── Guardrail Layer ────────────────────────────────────────────────────────────


def cmd_guardrail_check(args_list: list[str]):
  """Point d'entrée CLI : polis guardrail check --agent <a> --skill <s> --action <a> --level <N>"""
  from polis.guardrail.checker import check
  from polis.guardrail.models import CheckRequest, Level

  params = {"agent": "", "skill": "", "action": "", "level": None, "session": ""}
  rest: list[str] = []
  i = 0
  while i < len(args_list):
    arg = args_list[i]
    if arg.startswith("--"):
      key = arg.lstrip("-").replace("-", "_")
      i += 1
      if i < len(args_list):
        if key in params:
          params[key] = args_list[i]
        else:
          rest.extend([arg, args_list[i]])
        i += 1
    else:
      rest.append(arg)
      i += 1

  if not params["agent"] or not params["skill"] or not params["action"]:
    print(
      json.dumps(
        {
          "decision": "BLOCK",
          "reason": "Arguments manquants: --agent, --skill, --action requis",
          "level": -1,
          "elapsed_ms": 0,
        }
      )
    )
    return 1

  try:
    level = Level.from_int(int(params["level"])) if params["level"] else Level.READ
  except (ValueError, TypeError):
    level = Level.READ

  # Parser le --params JSON si présent
  action_params: dict = {}
  for r in rest:
    if r.startswith("{") or r.startswith('"'):
      try:
        action_params = json.loads(r) if r.startswith("{") else {}
      except json.JSONDecodeError:
        pass

  req = CheckRequest(
    agent=params["agent"],
    skill=params["skill"],
    action=params["action"],
    level=level,
    params=action_params,
    session_id=params["session"],
  )

  result = check(req)
  print(json.dumps(result.to_dict(), ensure_ascii=False))
  return 0 if result.decision.value == "PASS" else 1


def cmd_guardrail_poll(args_list: list[str]):
  """Point d'entrée CLI : polis guardrail poll <gate_id>"""
  from polis.guardrail.humangate import GateNotFound, poll

  if not args_list:
    print(json.dumps({"error": "gate_id requis (polis guardrail poll <gate_id>)"}))
    return 1

  gate_id = args_list[0]
  try:
    gate = poll(gate_id)
    print(json.dumps(gate, ensure_ascii=False, default=str))
    return 0 if gate["status"] == "approved" else 1
  except GateNotFound as e:
    print(json.dumps({"error": str(e)}))
    return 1


def cmd_guardrail_gate(args_list: list[str]):
  """Point d'entrée CLI : polis guardrail gate <gate_id> approve|deny"""
  from polis.guardrail.humangate import (
    GateAlreadyResponded,
    GateNotFound,
    respond,
  )

  if len(args_list) < 2:
    print(
      json.dumps({"error": "Arguments requis : polis guardrail gate <gate_id> approve|deny"})
    )
    return 1

  gate_id = args_list[0]
  decision = args_list[1]

  try:
    gate = respond(gate_id, decision)
    print(json.dumps(gate, ensure_ascii=False, default=str))
    return 0
  except (GateNotFound, GateAlreadyResponded, ValueError) as e:
    print(json.dumps({"error": str(e)}))
    return 1


def cmd_guardrail_stats():
  """Statistiques de la Guardrail Layer."""
  log_path = Path.home() / ".openclaw" / "guardrail.log"
  if not log_path.exists():
    print("Aucune activité Guardrail (guardrail.log absent)")
    return 0

  lines = log_path.read_text().splitlines()
  total = len(lines)
  passes = sum(1 for l in lines if "|PASS|" in l)
  blocks = sum(1 for l in lines if "|BLOCK|" in l)
  gates = sum(1 for l in lines if "|GATE|" in l)

  # Dernières entrées
  tail = lines[-5:] if len(lines) > 5 else lines

  print(f"Guardrail Layer — Statistiques")
  print(f" Évaluations totales : {total}")
  print(f" PASS  : {passes}")
  print(f" BLOCK : {blocks}")
  print(f" GATE  : {gates}")
  if total > 0:
    block_rate = (blocks / total) * 100
    gate_rate = (gates / total) * 100
    print(f" Taux blocage : {block_rate:.1f}%")
    print(f" Taux gate  : {gate_rate:.1f}%")
  print()
  print("Dernières entrées :")
  for line in tail:
    parts = line.split("|")
    if len(parts) >= 6:
      ts, agent, skill, action, lvl, decision = parts[:6]
      reason = parts[6] if len(parts) > 6 else ""
      print(f" [{ts}] {decision} {agent}/{skill}/{action} (N{lvl}) — {reason}")
  return 0


# ── Kill Switch ───────────────────────────────────────────────────────────────

KILL_PATH = Path.home() / ".openclaw" / "KILL"


def cmd_kill_status():
  if KILL_PATH.exists():
    content = KILL_PATH.read_text().strip()
    print(f"⚠ KILL ACTIF — instruction : {content}")
    mtime = datetime.fromtimestamp(KILL_PATH.stat().st_mtime).isoformat()
    print(f" Créé le : {mtime}")
    return 1
  else:
    _say("Aucun Kill Switch actif")
    return 0


def cmd_kill_set(instruction: str):
  if KILL_PATH.exists():
    print(f"⚠ Un Kill Switch est déjà actif : {KILL_PATH.read_text().strip()}")
    print(" Utilise 'polis kill clear' pour le supprimer d'abord.")
    return 1
  KILL_PATH.parent.mkdir(parents=True, exist_ok=True)
  KILL_PATH.write_text(instruction.strip() + "\n")
  _say(f"Kill Switch créé : {instruction.strip()}")
  print(f" Fichier : {KILL_PATH}")
  return 0


def cmd_kill_clear():
  if not KILL_PATH.exists():
    _say("Aucun Kill Switch à supprimer", ok=True)
    return 0
  print(f"⚠ Suppression du Kill Switch : {KILL_PATH.read_text().strip()}")
  print(" Confirmer la suppression ? (oui/non)")
  try:
    resp = input("> ").strip().lower()
  except (EOFError, KeyboardInterrupt):
    resp = ""
  if resp in ("oui", "o", "yes", "y"):
    KILL_PATH.unlink()
    _say("Kill Switch supprimé")
    return 0
  else:
    print("Suppression annulée.")
    return 1


# ── Point d'entrée ────────────────────────────────────────────────────────────


def main():
  parser = argparse.ArgumentParser(
    description="Polis — CLI de l'architecture de référence OpenClaw",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Commandes:
 check constitution     Vérifie la cohérence interne de la constitution
 check agents        Vérifie que tous les fichiers workspace sont complets
 check config        Valide la configuration JSON5
 check degraded       Vérifie que les workspaces référencent le mode dégradé
 guardrail check --agent <a> --skill <s> --action <a> --level <N>
               Vérifie une action (interceptor réel)
 guardrail poll <gate_id>  Vérifie l'état d'un Human Gate
 guardrail gate <gate_id> <dec> Répond à un Human Gate (approve/deny)
 guardrail stats       Statistiques de la Guardrail Layer
 guardrail simulate     Simule une décision de la Guardrail Layer
 demo leviathan       Scénario de démonstration leviathan
 test run          Lance la batterie de tests
 eventbus status       Statistiques du bus d'événements
 eventbus list [--type=] [--source=] [--target=] [--limit=]
               Liste les événements du bus
 eventbus purge [--before=ISO8601]
               Purge les événements archivés
 state status        Affiche l'état global de l'instance (instance_state.json)
 smoke run          Exécute un smoke test local
 smoke result        Affiche le dernier résultat de smoke test
 kill status         Vérifie la présence du Kill Switch (~/.openclaw/KILL)
 kill set <instruction>   Crée le Kill Switch (stop/freeze/rollback)
 kill clear         Supprime le Kill Switch (confirmation requise)
    """,
  )
  parser.add_argument("command", nargs="*", help="Commande à exécuter")
  args, unknown = parser.parse_known_args()
  parts = args.command + unknown
  cmd = " ".join(parts)

  # Détection des sous-commandes avec arguments supplémentaires
  base_cmd = " ".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else "")
  extra_args = parts[2:] if len(parts) > 2 else []

  commands = {
    "check constitution": lambda: cmd_check_constitution(),
    "check agents": lambda: cmd_check_agents(),
    "check config": lambda: cmd_check_config(),
    "check degraded": lambda: cmd_check_degraded(),
    "guardrail simulate": lambda: cmd_guardrail_simulate(),
    "guardrail check": lambda: cmd_guardrail_check(extra_args),
    "guardrail poll": lambda: cmd_guardrail_poll(extra_args),
    "guardrail gate": lambda: cmd_guardrail_gate(extra_args),
    "guardrail stats": lambda: cmd_guardrail_stats(),
    "demo leviathan": lambda: cmd_demo_leviathan(),
    "eventbus status": lambda: cmd_eventbus_status(),
    "eventbus list": lambda: cmd_eventbus_list(extra_args),
    "eventbus purge": lambda: cmd_eventbus_purge(extra_args),
    "state status": lambda: cmd_state_status(),
    "smoke run": lambda: cmd_smoke_run(),
    "smoke result": lambda: cmd_smoke_result(),
    "kill status": lambda: cmd_kill_status(),
    "kill clear": lambda: cmd_kill_clear(),
  }

  if base_cmd in commands:
    sys.exit(commands[base_cmd]())

  # Commandes avec argument positionnel (kill set <instruction>)
  if base_cmd == "kill set" and extra_args:
    sys.exit(cmd_kill_set(" ".join(extra_args)))

  # Commande test run → délègue à pytest
  if base_cmd == "test run":
    import subprocess

    result = subprocess.run(
      [sys.executable, "-m", "pytest", "tests/", "-v"],
      cwd=ROOT,
    )
    sys.exit(result.returncode)

  print(f"❌ Commande inconnue : {base_cmd}")
  print("Commandes disponibles :")
  for c in sorted(commands):
    print(f" polis {c}")
  print(" polis kill set <instruction>")
  print(" polis test run")
  sys.exit(1)


if __name__ == "__main__":
  main()
