---
name: int-calendar
description: Gestion de deux agendas CalDAV Posteo (PERSO et SYNDICAL). Lecture, création, détection conflits.
metadata:
 {
  "openclaw":
   { "requires": { "env": ["CALDAV_HOST"], "bins": ["python3"] } },
 }
---

# Gestion des agendas

## Comptes configurés

| Identifiant | Protocole | Contexte |
|---|---|---|
| `PERSO` | CalDAV — Posteo | `[PERSO]` |
| `SYNDICAL` | CalDAV — Posteo (compte syndical) | `[SYNDICAL]` |

Toutes les valeurs de connexion sont lues depuis `~/.openclaw/.env`.

## Connexion CalDAV

Les identifiants Posteo sont partagés avec IMAP : `$MAIL_ADDRESS` / `$MAIL_APP_PASSWORD`.
Le serveur CalDAV est `$CALDAV_HOST`.

Bibliothèque recommandée : `caldav` (Python). 
Au premier appel, effectuer un `PROPFIND` pour lister les calendriers disponibles.

## Opérations supportées

| Opération | Niveau | Description |
|---|---|---|
| Lister / lire les événements | 1 | Fenêtre par défaut : J-1 à J+7 |
| Créer un événement | 2 | Confirmation si l'événement est dans < 24h |
| Modifier un événement | 2 | Confirmation si modification de date/heure |
| Supprimer un événement | 3 | Toujours confirmation |
| Déplacer un événement | 3 | Toujours confirmation |

## Format d'affichage des événements

### Vue journalière
```
📅 *Agenda — [DATE]*

[HH:MM] [Titre] — [Lieu si défini]
[HH:MM] [Titre]
...
Aucun événement : "Journée libre 🎉"
```

### Vue hebdomadaire (sur demande)
```
📅 *Semaine du [DATE] au [DATE]*

Lun [DD] : [n] événement(s) — [titre principal]
Mar [DD] : ...
...
```

## Règles de cloisonnement

- Un événement `SYNDICAL` ne génère jamais d'observation `[PERSO]` et vice-versa.
- En cas de conflit horaire entre un événement PERSO et SYNDICAL, signaler sans arbitrer.
- Les informations des événements SYNDICAL ne sont jamais incluses dans un brief PERSO.

## Détection de conflits

Avant toute création ou modification, vérifier l'absence de chevauchement sur la même plage horaire. 
Si conflit : afficher les deux événements et demander confirmation avant de procéder.

## Rappels automatiques

- Événement du lendemain : inclus dans le brief du soir (`int-daily-brief`).
- Événement dans < 1h : notification Telegram via `int-telegram`.
- Réunion SYNDICAL : rappel 24h avant + 1h avant.
