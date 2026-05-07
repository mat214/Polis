---
name: int-telegram
description: Interface Telegram : réception, envoi notifications/alertes/rapports. Point d'entrée principal.
metadata:
 {
  "openclaw":
   {
    "requires": { "env": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"] },
   },
 }
---

# Interface Telegram

## Configuration

- Bot token : `$TELEGRAM_BOT_TOKEN` (lu depuis `~/.openclaw/.env`)
- Chat ID autorisé : `$TELEGRAM_CHAT_ID` (seul ID accepté — toute autre source est ignorée)
- API base : `https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/`

## Règle de sécurité fondamentale

**Tout message dont le `chat_id` ne correspond pas à `$TELEGRAM_CHAT_ID` est ignoré sans réponse.** 
Aucune exception. Ne jamais loguer le contenu d'un message non autorisé.

## Réception des messages

### Polling (mode par défaut)

L'agent interroge `getUpdates` toutes les 60 secondes. 
En cas d'absence de réponse > 5 min : ALERT MOYEN + log.

### Webhook (optionnel)

Si `$TELEGRAM_WEBHOOK_URL` est défini, utiliser `setWebhook` au lieu du polling. 
Le webhook doit exposer HTTPS avec un certificat valide.

## Envoi de messages

Méthode : `sendMessage` avec `parse_mode: Markdown`.

### Niveaux d'envoi

| Action | Niveau |
|---|---|
| Envoyer une notification informative | 1 |
| Envoyer un résumé ou rapport | 1 |
| Envoyer une alerte CRITIQUE ou HAUT | 1 (automatique) |
| Envoyer un message au nom de l'utilisateur vers un tiers | 3 |

## Format des messages sortants

### Notification courte
```
🔔 *[AGENT]* — [SUJET]
[Corps court — max 3 lignes]
```

### Alerte
```
🚨 *ALERT [NIVEAU]* — [SUJET]
[Détail]
[Action requise : oui/non]
```

### Rapport quotidien
```
📋 *Rapport quotidien — [DATE]*
[Résumé en 3-5 points]
📎 Rapport complet → Notion
```

### Brief matin
```
☀️ *Bonjour l'utilisateur — [DATE]*
📬 Mails : [n] à traiter
📅 Aujourd'hui : [événements]
✅ Rappels : [n]
```

## Parsing des commandes entrantes

L'agent reconnaît les commandes suivantes (préfixées par `/`) :

| Commande | Action déclenchée |
|---|---|
| `/brief` | Déclencher `int-daily-brief` |
| `/mails` | Déclencher triage `int-mail` |
| `/agenda` | Afficher agenda du jour via `int-calendar` |
| `/rappels` | Lister les tâches et rappels via `int-tasks` |
| `/audit` | Demander un audit à `défenseur` |
| `/status` | Healthcheck de tous les services |
| `/aide` | Lister les commandes disponibles |

Toute demande en langage naturel est traitée directement sans préfixe `/`.

## Gestion des erreurs d'envoi

- Si `sendMessage` échoue (réseau, token invalide) : retenter 3 fois avec backoff exponentiel (10s, 30s, 90s).
- Après 3 échecs consécutifs : déclencher la procédure de bascule sur le canal de secours.
- Ne jamais perdre un message CRITIQUE : le mettre en file d'attente locale jusqu'à réussite ou bascule.

## Canal de secours — openclaw-tui

Telegram est le canal principal. En cas d'indisponibilité confirmée (3 échecs consécutifs ou token invalide), l'agent bascule sur **`openclaw-tui`** (console locale OpenClaw).

### Procédure de bascule

1. Marquer Telegram comme indisponible dans le session state.
2. Activer `openclaw-tui` comme canal actif.
3. Envoyer un email de notification via la boite `PERSO` (Posteo) :
  - **Destinataire** : `utilisateur@exemple.net`
  - **Sujet** : `[OpenClaw] Telegram indisponible — bascule sur openclaw-tui`
  - **Corps** :
   ```
   Bonjour l'utilisateur,

   Telegram est indisponible depuis [TIMESTAMP].
   L'assistant a basculé sur le canal de secours openclaw-tui.

   Pour interagir avec l'assistant : lancer `openclaw tui` dans le terminal.
   Toutes les fonctions restent disponibles, y compris les confirmations de niveau 3.

   Ce message sera suivi d'une confirmation dès le rétablissement de Telegram.
   ```
4. Journaliser : `[ALERT HAUT][TIMESTAMP][intendant] Telegram indisponible — bascule openclaw-tui activée`.
5. Continuer toutes les tâches normalement via `openclaw-tui`.

### Procédure de retour sur Telegram

Dès que Telegram redevient disponible (vérification toutes les 5 min via `getMe`) :

1. Reprendre Telegram comme canal actif.
2. Désactiver `openclaw-tui` comme canal principal.
3. Envoyer un email de confirmation à `utilisateur@exemple.net` :
  - **Sujet** : `[OpenClaw] Telegram rétabli`
  - **Corps** : timestamp de rétablissement, durée d'indisponibilité, actions effectuées via TUI pendant l'indisponibilité.
4. Journaliser : `[INFO][TIMESTAMP][intendant] Telegram rétabli — retour canal principal`.

### Règles du canal de secours

- `openclaw-tui` ne remplace Telegram que pour les interactions directes avec l'utilisateur (confirmations, commandes, briefs).
- Les tâches planifiées autonomes (triage mail, brief) continuent normalement sans interaction.
- Les messages en file d'attente locale sont envoyés via Telegram dès son rétablissement.
