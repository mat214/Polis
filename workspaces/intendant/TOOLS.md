# TOOLS.md — intendant

## Telegram
- API Bot : `https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/`
- Méthode : `sendMessage` avec `parse_mode: Markdown`
- Polling toutes les 60s (défaut), webhook si `$TELEGRAM_WEBHOOK_URL` défini
- Commandes : `/brief`, `/mails`, `/agenda`, `/rappels`, `/audit`, `/status`, `/aide`

## Mail
- **Posteo** (PERSO) : IMAP/SMTP — `$MAIL_ADDRESS` / `$MAIL_APP_PASSWORD`
- **ORG-1** (SYNDICAL) : IMAP/SMTP — `$SYNDICAL_A_ADDRESS` / `$SYNDICAL_A_PASSWORD`
- **CGT** (SYNDICAL) : EWS Exchange avec autodiscovery — `$SYNDICAL_B_ADDRESS`

## Agenda
- CalDAV Posteo : `$CALDAV_HOST` — mêmes identifiants que le mail

## Contacts
- CardDAV Posteo : `$CARDDAV_HOST` — mêmes identifiants que le mail

## Notion
- API v1 : `https://api.notion.com/v1`
- Auth : `Authorization: Bearer $NOTION_TOKEN`
- Version : `Notion-Version: 2022-06-28`
- Rate limit : 3 req/s
- Bases : `$NOTION_DB_PERSO_ID`, `$NOTION_DB_SYNDICAL_ID`, `$NOTION_DB_OPENCLAW_ID`

## Système de fichiers
- Espace de travail : `~/.openclaw/workspace-intendant`
- Mémoire quotidienne : `memory/YYYY-MM-DD.md`
- Mémoire longue : `MEMORY.md`
