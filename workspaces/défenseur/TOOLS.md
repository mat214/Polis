# TOOLS.md — défenseur

## Notion (OPENCLAW)
- API v1 : `https://api.notion.com/v1`
- Auth : `$NOTION_TOKEN`
- DB : `$NOTION_DB_OPENCLAW_ID`
- Préfixes de page : `[AUDIT]`, `[INCIDENT]`, `[MAINTENANCE]`, `[CONFIG]`, `[POST-MORTEM]`

## Système de fichiers
- Espace de travail : `~/.openclaw/workspace-défenseur`
- Config OpenClaw : `~/.openclaw/openclaw.json`
- Secrets d'environnement : `~/.openclaw/.env`
- Gouvernance : fichiers `AGENTS.md` des workspaces
- Checksums d'audit : `~/.openclaw/audit/checksums.json`
- Log guardrail : `~/.openclaw/guardrail.log`

## Healthchecks
- Telegram : API `getMe`
- Posteo : IMAP SSL port 993, CalDAV HTTPS
- Notion : `GET /users/me`
- EWS ORG-2 : autodiscovery
