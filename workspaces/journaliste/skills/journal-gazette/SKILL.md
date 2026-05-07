---
name: journal-gazette
description: Production de la gazette quotidienne de l'instance — compile les sources et publie le journal.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# journal-gazette

## Description

Produit la gazette quotidienne de l'instance OpenClaw. La gazette compile l'activité de la journée à partir des fichiers partagés inter-agents, des logs et des cellules de surveillance. Elle est publiée chaque jour à 17h00 dans `~/.openclaw/shared/gazette/`.

## Sources consultées

- `~/.openclaw/shared/health.json` — état des services
- `~/.openclaw/shared/bat-health.json` — santé système
- `~/.openclaw/shared/leviathan-status.json` — surveillance
- `~/.openclaw/shared/research-health.json` — innovation
- `~/.openclaw/shared/tasks/` — tâches inter-agents
- `~/.openclaw/guardrail.log` — décisions de sécurité

## Format de sortie

```
[GAZETTE][TIMESTAMP]
## Activité du jour
- agent : [actions principales, skills utilisés]
## État du système
- santé globale : ok | degraded | critical
- score audit : X/100
- menace leviathan : safe | suspect | dangerous | subversive
## Faits marquants
- innovations, incidents, classifications, transferts
## leviathan au rapport
- agents sous surveillance, actions d'enforcement
## À suivre
- événements attendus, enquêtes en cours
```

## Règles

- La gazette est publiée même si rien ne s'est passé. « Aucune activité » est une information.
- Chaque fait cite sa source (nom de fichier, timestamp).
- Ne pas inclure de données sensibles (secrets, credentials).
- Si une source est indisponible, le mentionner : « Source X : non joignable ».
- L'utilisateur reçoit un résumé de la gazette via le canal configuré.

## Niveaux

| Action | Niveau |
|---|---|
| Compiler les sources | N1 |
| Publier la gazette | N2 |
| Archiver une gazette | N2 |
| Supprimer une gazette | N3 |
