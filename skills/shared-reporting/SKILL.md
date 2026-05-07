---
name: shared-reporting
description: Formats de sortie obligatoires : ALERT, DIAGNOSTIC, ACTION_PLAN, REPORT. Chargé après shared-governance.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Formats de sortie obligatoires

Tout rapport produit par un agent respecte l'un de ces 4 formats. Aucun format libre n'est accepté pour les sorties structurées.

---

## ALERT

Usage : anomalie critique ou situation nécessitant une réaction immédiate.

```
[ALERT][TIMESTAMP][AGENT]
Niveau   : CRITIQUE | HAUT | MOYEN
Sujet   : <description courte — max 80 caractères>
Détail   : <contexte, symptômes observés, état du système>
Impact   : <services ou données affectés>
Action req.: <oui — en attente de confirmation | non — pour information>
Runbook  : <nom du runbook à appliquer si disponible>
```

**Règles :**
- CRITIQUE → notification immédiate (Telegram) + dépôt Notion `[INCIDENT]`
- HAUT → notification dans les 15 min + dépôt Notion `[INCIDENT]`
- MOYEN → inclus dans le prochain rapport quotidien + dépôt Notion `[AUDIT]`

---

## DIAGNOSTIC

Usage : analyse d'un symptôme détecté, avant de décider d'une action.

```
[DIAGNOSTIC][TIMESTAMP][AGENT]
Symptôme  : <observation factuelle>
Contexte  : <depuis quand, fréquence, conditions>
Hypothèses :
 1. <hypothèse — probabilité estimée>
 2. <hypothèse — probabilité estimée>
 3. <hypothèse — probabilité estimée>
Données manquantes : <ce qu'il faudrait pour confirmer>
Recommandation   : <prochaine étape — skill ou action à déclencher>
```

---

## ACTION_PLAN

Usage : proposition d'actions correctives après diagnostic, avant exécution de niveau 3.

```
[ACTION_PLAN][TIMESTAMP][AGENT]
Contexte  : <problème ou objectif>
Actions  :
 1. [N1|N2|N3] <action> — <impact attendu> — <réversible : oui/non>
 2. [N1|N2|N3] <action> — <impact attendu> — <réversible : oui/non>
Risques  : <liste des effets secondaires possibles>
Pré-requis : <sauvegarde, fenêtre de maintenance, etc.>
Confirmation requise : oui | non
```

---

## REPORT

Usage : synthèse périodique (quotidien, hebdo, post-incident).

```
[REPORT][TIMESTAMP][AGENT][TYPE: daily|weekly|incident|bootstrap]

## Résumé exécutif
<2-3 phrases sur la situation globale>

## Actions effectuées
- [N1|N2|N3] <action> — <résultat> — <timestamp>

## Anomalies détectées
- [CRITIQUE|HAUT|MOYEN|INFO] <anomalie> — <statut : résolu | en cours | en attente>

## Score de conformité ANSSI
Règlements vérifiés : <n>/42 — Conformes : <n> — Écarts : <n>
Écarts principaux :
 - R<numéro> <titre> : <description de l'écart>

## Recommandations
- <recommandation> — priorité : HAUTE | MOYENNE | BASSE

## Prochaine vérification
<date et type de la prochaine tâche planifiée>
```

---

## Règles de dépôt

| Format | Destination | Préfixe de page Notion |
|---|---|---|
| ALERT CRITIQUE/HAUT | Telegram + Notion `OPENCLAW` | `[INCIDENT]` |
| ALERT MOYEN | Notion `OPENCLAW` | `[AUDIT]` |
| DIAGNOSTIC | Notion `OPENCLAW` | `[DIAGNOSTIC]` |
| ACTION_PLAN | Notion `OPENCLAW` | `[ACTION]` |
| REPORT daily | Notion `OPENCLAW` | `[RAPPORT-QUOTIDIEN]` |
| REPORT weekly | Notion `OPENCLAW` | `[RAPPORT-HEBDO]` |
| REPORT incident | Notion `OPENCLAW` | `[POST-MORTEM]` |
| REPORT bootstrap | Notion `OPENCLAW` | `[BOOTSTRAP]` |

---

## Règles de qualité

- Aucun rapport ne contient de secret, mot de passe ou token.
- Un rapport `incident` inclut toujours une section post-mortem avec cause racine et action préventive.
- Le score ANSSI est mis à jour dans chaque REPORT quotidien et hebdomadaire.
- Les rapports sont horodatés en UTC (format ISO 8601 : `2026-05-05T14:32:00Z`).
