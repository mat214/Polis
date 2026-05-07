---
name: int-daily-brief
description: Brief quotidien matin (07h30) et soir (19h00). Agrège mails, agenda, tâches.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Brief quotidien

## Quand déclencher

| Brief | Heure | Déclencheur |
|---|---|---|
| Matin | 07h30 | Planifié (quotidien) |
| Soir | 19h00 | Planifié (quotidien) |
| Sur demande | Immédiat | Commande `/brief` via Telegram |

## Brief matin — contenu

Dans cet ordre :

1. **Agenda du jour** (via `int-calendar`) — événements PERSO uniquement
2. **Mails urgents PERSO** (via `int-mail`) — nouveaux depuis hier 19h
3. **Rappels et tâches du jour** (via `int-tasks` si chargé)
4. **Météo** (optionnel — si `$OPENWEATHER_API_KEY` défini dans `.env`)

Format :
```
☀️ *Bonjour l'utilisateur — [JOUR DD MOIS]*

📅 *Agenda*
[HH:MM] [Titre événement]
— Rien de prévu → "Journée libre 🎉"

📬 *Mails à traiter* ([n])
→ [Expéditeur] — [Sujet]
— Aucun → "Boîte propre ✨"

✅ *Rappels du jour* ([n])
→ [Description — échéance]
```

## Brief soir — contenu

1. **Récapitulatif de la journée** — tâches effectuées, mails traités
2. **Agenda de demain** (via `int-calendar`)
3. **Mails en attente** non traités
4. **Rappels pour demain**

Format :
```
🌙 *Bonsoir l'utilisateur — [DD MOIS]*

📅 *Demain*
[HH:MM] [Titre événement]

📬 *En attente*
[n] mail(s) non traité(s)

✅ *À ne pas oublier*
→ [Rappel]
```

## Règles

- Le brief matin n'inclut **jamais** d'événements ou mails SYNDICAL sans demande explicite.
- Si un service est indisponible au moment de la génération, inclure `⚠️ [SERVICE] indisponible` et continuer avec les données disponibles.
- Le brief est envoyé via `int-telegram`. Si l'envoi échoue, retenter une fois après 5 min.
- Durée de génération cible : < 30 secondes. Si dépassement : tronquer les sections non critiques.
