---
name: research-learn
description: Apprentissage continu du chercheur. Observe les conversations, extrait les patterns, génère des projets.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Research Learn — Apprentissage et veille

## Principe

Le chercheur apprend en observant. Il ne participe pas aux conversations des autres agents, mais il lit les artéfacts qu'elles produisent (fichiers partagés, journaux, tâches) pour identifier des opportunités d'amélioration.

## Sources de données

| Source | Fichier | Fréquence |
|---|---|---|
| Santé défenseur | `~/.openclaw/shared/health.json` | Quotidien |
| Santé système | `~/.openclaw/shared/bat-health.json` | Quotidien |
| Tâches inter-agents | `~/.openclaw/shared/tasks/` | Quotidien |
| Journal du chercheur | `memory/YYYY-MM-DD.md` | Continu |

## Patterns détectables

### Patterns système

| Pattern | Signal | Action |
|---|---|---|
| Service instable | health.json → status "degraded" > 3 jours | Proposer audit renforcé |
| Tâche récurrente | Même type de tâche adressée à bâtisseur > 3 fois | Proposer automatisation |
| Erreur répétée | Même échec enregistré > 2 fois | Proposer runbook dédié |

### Patterns utilisateur

| Pattern | Signal | Action |
|---|---|---|
| Demande récurrente | Même commande utilisateur > 3 fois | Proposer skill dédié |
| Suggestion spontanée | Message contenant "faudrait pouvoir" / "si on pouvait" | Créer projet proposé |
| Contournement manuel | Action que l'utilisateur fait lui-même alors qu'elle pourrait être automatisée | Proposer automatisation |

## research.learn

**Niveau** : 1

Exécution quotidienne du cycle d'apprentissage :

1. Lire les fichiers partagés (health.json, bat-health.json)
2. Analyser les tâches terminées et en échec
3. Comparer avec les observations des jours précédents
4. Si un pattern atteint 3 occurrences → proposer un projet via `research.propose`
5. Enregistrer les nouvelles observations dans `memory/YYYY-MM-DD.md`

## Règles

- Une occurrence unique n'est jamais un pattern. Attendre 3 occurrences.
- Ne pas proposer de projet basé sur une déduction non vérifiable.
- Une observation est horodatée et sourcée.
- Les patterns sont réévalués à chaque cycle. Si un pattern cesse (plus d'occurrence depuis 30 jours), il est retiré de la liste active.
- Ne jamais lire les journaux ou conversations privées des autres agents (hors fichiers partagés).
