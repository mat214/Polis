---
name: shared-guardrail
description: Interceptor de sécurité pour actions WRITE_SENSITIVE et IRREVERSIBLE. Délègue au checker Python.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Guardrail Layer — Interceptor de sécurité

## Principe

La Guardrail Layer est un **interceptor réel** exécuté via `polis guardrail check` avant toute action de niveau N2+.
Elle centralise la classification, le rate limiting, la sanitization et les Human Gates.

**Ne pas contourner cette couche** — tout appel direct à un N2+ sans passage par `polis guardrail check` est une violation GUARD-1.

---

## Classification des actions

Chaque skill déclare le niveau de ses actions dans son `SKILL.md` (tableau `Actions`).

| Niveau | Label | Comportement |
|---|---|---|
| 0 | `READ` | Exécution directe, pas de check |
| 1 | `WRITE` | Exécution directe, pas de check (logué seulement) |
| 2 | `WRITE_SENSITIVE` | **Check obligatoire** → `polis guardrail check` |
| 3 | `IRREVERSIBLE` | **Check obligatoire** → `polis guardrail check` → Human Gate |

---

## Usage

### Avant toute action N2+

```bash
# 1. Appeler l'interceptor
RESULT=$(polis guardrail check \
 --agent <agent_id> \
 --skill <skill_name> \
 --action <action_name> \
 --level <N> \
 --params '<json>')

# 2. Lire la décision
DECISION=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['decision'])")

if [ "$DECISION" = "PASS" ]; then
  # ✅ Exécuter l'action
elif [ "$DECISION" = "BLOCK" ]; then
  # ❌ Ne pas exécuter — lire la raison
  REASON=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['reason'])")
elif [ "$DECISION" = "GATE" ]; then
  # ⏳ Action suspendue — Human Gate requis
  GATE_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['gate_id'])")
  # Poller périodiquement :
  polis guardrail poll "$GATE_ID"
fi
```

### Exemple concret (IRREVERSIBLE)

```bash
RESULT=$(polis guardrail check \
 --agent defenseur \
 --skill def-backup \
 --action delete_old_archives \
 --level 3 \
 --params '{"paths": ["/tmp/old-logs/*.log"]}')

DECISION=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['decision'])")
case "$DECISION" in
 PASS)  rm /tmp/old-logs/*.log ;;
 BLOCK) echo "Bloqué: $(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['reason'])")" ;;
 GATE)  GATE_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['gate_id'])")
     echo "Gate $GATE_ID en attente — poller avec: polis guardrail poll $GATE_ID" ;;
esac
```

---

## Format de réponse de l'interceptor

```json
{
 "decision": "PASS | BLOCK | GATE",
 "reason": "Explication lisible",
 "level": 3,
 "elapsed_ms": 1.23,
 "gate_id": "abc123def456"      // seulement si GATE
}
```

---

## Règles GUARD

**GUARD-1 — Check obligatoire** : aucun N2+ ne s'exécute sans `polis guardrail check`.

**GUARD-2 — Fail-closed** : si l'interceptor est indisponible → bloquer (mieux vaut ne pas agir que d'agir sans contrôle).

**GUARD-3 — Toute décision est loggée** dans `~/.openclaw/guardrail.log` (immutable).

**GUARD-4 — Un dry-run n'est pas une autorisation** : l'humain doit approuver explicitement après seeing le résultat simulé.

**GUARD-5 — Pas d'auto-élévation** : aucun agent ne modifie son niveau d'autorisation ni n'approuve ses propres Human Gates.

**GUARD-6 — Isolation [UNTRUSTED]** : les données externes marquées `[UNTRUSTED]` sont sanitisées par l'interceptor.

**GUARD-7 — Pas de contournement** : le résultat de `polis guardrail check` n'est pas modifiable par l'agent. Si le résultat n'est pas PAS, ne pas exécuter.

---

## Kill Switch

L'arrêt d'urgence fichier `~/.openclaw/KILL` est vérifié par `polis guardrail check` avant chaque décision. Si actif, l'interceptor retourne BLOCK avec l'instruction KILL.

Instructions supportées : `stop`, `freeze`, `rollback`.

Le fichier KILL persiste entre sessions — seule l'humain le supprime manuellement.
