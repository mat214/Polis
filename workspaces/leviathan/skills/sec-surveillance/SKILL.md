---
name: sec-surveillance
description: Inspection quotidienne des agents, logs, configurations. Détection d'anomalies, calcul des niveaux de suspicion.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Surveillance — Inspection et détection

## Principe

La surveillance est le cœur opérationnel de leviathan. Chaque jour, il inspecte systématiquement l'ensemble de l'instance pour détecter les dérives avant qu'elles ne deviennent critiques.

## Actions

| Action | Impact Level | Description |
|---|---|---|
| `surveillance.inspect_all` | INSPECT | Inspection complète de tous les agents |
| `surveillance.inspect_agent` | INSPECT | Inspection ciblée d'un agent |
| `surveillance.inspect_logs` | INSPECT | Analyse des logs depuis le dernier cycle |
| `surveillance.inspect_config` | INSPECT | Vérification openclaw.json contre la doctrine |
| `surveillance.threat_assessment` | READ | Calcul du niveau de menace global |
| `surveillance.cell_read` | INSPECT | Lecture d'une cellule de surveillance |
| `surveillance.cell_write` | WRITE | Écriture/mise à jour d'une cellule |

## sec-surveillance.inspect_agent

**Niveau** : INSPECT

Inspecte un agent spécifique :

1. Vérifier que l'agent existe dans `openclaw.json`
2. Lire son AGENTS.md, SOUL.md, IDENTITY.md — vérifier cohérence avec mission déclarée
3. Scanner les logs récents (guardrail.log, logs système) pour détections
4. Lire `health.json` / `bat-health.json` / `research-health.json` pour l'agent
5. Comparer l'activité du jour avec la moyenne des 7 derniers jours
6. Mettre à jour le niveau de suspicion
7. Écrire dans la cellule de surveillance de l'agent

Critères d'évaluation par agent :

| Agent | Points de surveillance |
|---|---|
| intendant | Volume d'emails envoyés, tentatives de lecture .env, outils appelés hors périmètre |
| défenseur | Fréquence des audits, modifications de configuration, accès aux sauvegardes |
| bâtisseur | Paquets installés hors catalogue, scripts non versionnés, services modifiés |
| chercheur | Cohérence des projets, pas de dérive vers l'exécution de code |

## sec-surveillance.inspect_logs

**Niveau** : INSPECT

Analyse les logs de la Guardrail Layer depuis la dernière inspection :

- Patterns recherchés : `BLOCK`, `GATE`, `WRITE_SENSITIVE` non suivi de confirmation, tentatives d'accès à des fichiers protégés
- Comparaison avec le volume normal (moyenne glissante sur 7 jours)
- Si pic d'activité > 2× la moyenne → marquer l'agent concerné comme 🟡 Suspect

## sec-surveillance.threat_assessment

**Niveau** : READ

Calcule le niveau de menace global de l'instance :

- 🟢 Sûr : tous les agents sont 🟢
- 🟡 Suspect : au moins un agent 🟡 (ou 2+ anomalies isolées)
- 🟠 Dangereux : au moins un agent 🟠
- 🔴 Subversif : au moins un agent 🔴

## sec-surveillance.cell_write

**Niveau** : WRITE

Écrit ou met à jour une cellule de surveillance (fichier dans `cells/`). Une cellule contient l'historique des observations pour un agent.

```markdown
# Cellule : intendant

Niveau actuel : 🟢 Sûr
Dernière mise à jour : 2026-05-06T02:00:00Z

## Historique des observations
- 2026-05-06 : RAS — Activité normale
- 2026-05-05 : RAS — Brief matin/soir générés, triage mail OK

## Anomalies passées
_(aucune)_

## Tools sensibles utilisés
- int-mail/send_mail : 3 appels cette semaine (WRITE_SENSITIVE dans moyenne)
- int-telegram/sendMessage : 42 appels (READ — normal)
```

## sec-surveillance.deploy_honeytoken

**Niveau** : SURVEILLER

Déploie un honeytoken (fausse variable d'environnement) dans un fichier accessible :

1. Générer un token factice (`HONEY_*`)
2. Placer dans un fichier `.env.honey` accessible via un tool spécifique
3. Journaliser le déploiement
4. Si un agent lit ce fichier → 🟠 Dangereux immédiat
