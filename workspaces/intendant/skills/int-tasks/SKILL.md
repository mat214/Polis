---
name: int-tasks
description: Gestion des tâches et rappels : capture, suivi, relances, priorisation. Persiste dans Notion.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Gestion des tâches et rappels

## Pourquoi ce skill

`int-mail` identifie des actions à faire, `int-calendar` gère les événements.
`int-tasks` est le pont : il transforme les actions identifiées en tâches suivables
avec une échéance et une relance, et il évite qu'elles se perdent.

## Sources de capture

| Source | Déclencheur |
|---|---|
| Mail triage | `int-mail` détecte une action → proposer création de tâche |
| Message Telegram | Demande directe ("rappelle-moi de...", "n'oublie pas") |
| Agenda | Événement passé avec suivi nécessaire |
| Demande manuelle | Commande `/rappels` ou phrase libre |

## Structure d'une tâche

```
Titre   : [action claire — verbe + objet]
Échéance  : [date + heure si pertinent, ou "sans échéance"]
Priorité  : HAUTE | MOYENNE | BASSE
Contexte  : PERSO | SYNDICAL
Source   : [mail ID | telegram | manuel]
Statut   : À faire | En cours | En attente | Terminé
Relance  : [date de relance automatique si non traitée]
```

## Procédure de capture

1. Identifier l'action (quoi faire)
2. Proposer une échéance (si non précisée, suggérer J+2 par défaut)
3. Déterminer le contexte (PERSO / SYNDICAL)
4. Confirmer avec l'utilisateur si action > 30 min ou contexte SYNDICAL
5. Créer dans Notion via `int-notion`
6. Confirmer par message Telegram court

## Relances automatiques

- Tâche échue non terminée : rappel Telegram le jour de l'échéance à 09h00
- Tâche en retard de 2 jours : rappel de relance
- Tâche en retard de 7 jours : incluse en ALERT MOYEN dans le brief du soir
- Tâche SYNDICAL urgente non traitée en 24h : ALERT HAUT via Telegram

## Opérations

| Opération | Niveau |
|---|---|
| Lister les tâches du jour et en retard | 1 |
| Créer une tâche | 2 |
| Marquer terminée, modifier priorité | 2 |
| Supprimer une tâche | 3 |
| Vider toutes les tâches terminées | 3 — confirmation |

## Format de synthèse des tâches

```
✅ *Tâches — [DATE]*

En retard ([n]) :
→ 🔴 [Titre] — échue le [DATE]

Aujourd'hui ([n]) :
→ 🟠 [Titre] — [HH:MM si échéance horaire]

Cette semaine ([n]) :
→ 🟡 [Titre] — [DATE]
```
