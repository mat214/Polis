---
name: shared-smoketest
description: Protocole de vérification post-démarrage, heartbeat et modification de configuration. Exécuté par chaque agent avant toute action N2/N3.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Smoke Test — Vérification de santé minimale

## Principe

Après chaque démarrage, heartbeat, ou modification de configuration, l'agent exécute
un smoke test pour vérifier que son environnement est fonctionnel. Si le smoke test
échoue, l'agent refuse les actions N2/N3 et émet un ALERT.

Le smoke test est **court (< 30s)** et **superficiel volontairement** — il détecte
les pannes franches, pas les dégradations lentes (celles-ci sont couvertes par
l'audit quotidien et les healthchecks).

---

## Vérifications obligatoires au démarrage

1. `~/.openclaw/` existe et est accessible (lecture)
2. Les fichiers obligatoires du workspace sont présents : AGENTS.md, SOUL.md,
  IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md
3. `~/.openclaw/shared/` est accessible en lecture
4. `~/.openclaw/shared/instance_state.json` est lisible et contient une entrée
  pour l'agent courant
5. `~/.openclaw/events.db` est accessible (si events.db n'existe pas → création
  silencieuse par le bus)
6. Les skills déclarés dans la configuration de l'agent correspondent aux
  répertoires dans `skills/`

## Vérifications périodiques (à chaque heartbeat)

1. L'agent peut écrire son statut dans `instance_state.json`
2. L'agent peut lire les événements récents sur le bus (depuis le dernier check)
3. Pas de fichiers `tasks/` en attente depuis > 24h pour cet agent
4. `health.json` (ou fichier de statut équivalent) n'est pas stale
  (pas de mise à jour depuis > 2 cycles de heartbeat)

---

## Format de sortie

```
[SMOKE_RESULT][TIMESTAMP][AGENT]
Checks  : 5/5 passed | 4/5 passed (1 WARNING) | < 5 FAILED
Décision : continue | degraded | block
Détails :
 ✓ shared/ accessible
 ✓ instance_state.json lisible
 ✓ events.db accessible
 ✓ AGENTS.md présent
 ✓ Skills de base chargés
 ⚠ Service A inaccessible (non critique)
Alertes  : aucune | ALERT MOYEN | ALERT HAUT
```

---

## Décisions

| Résultat | Comportement |
|---|---|
| Tous les checks passent | Continuer normalement — aucune alerte |
| 1 check non critique échoue | Continuer en mode dégradé — ALERT MOYEN |
| ≥ 2 checks échouent | Bloquer N2/N3 — ALERT HAUT — écrire `degraded` dans instance_state.json |
| Fichiers obligatoires absents | Bloquer TOUTE action — ALERT CRITIQUE |

---

## Règles

- **SMOKE-1** : le smoke test est exécuté avant toute action N2/N3 dans une session,
 pas avant chaque action individuelle. Une fois passé, les actions N2/N3 de la
 session sont autorisées jusqu'au prochain heartbeat.
- **SMOKE-2** : si le smoke test échoue, les actions N1 restent autorisées
 (lecture seule).
- **SMOKE-3** : le résultat du smoke test est écrit dans `instance_state.json`
 → champ `agents.<agent>.status`.
- **SMOKE-4** : un agent peut déclencher un smoke test sur un autre agent via
 le bus d'événements (type `smoketest.request`).
