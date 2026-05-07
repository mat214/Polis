# TOOLS.md — leviathan

## Chemins

- Espace de travail : `~/.openclaw/workspace-leviathan`
- Doctrine : `~/.openclaw/workspace-leviathan/doctrine/`
- Cellules de surveillance : `~/.openclaw/workspace-leviathan/cells/`
- Rapports quotidiens : `~/.openclaw/leviathan/daily_reports/`
- Log guardrail : `~/.openclaw/guardrail.log`

## Zones d'inspection autorisées

### Lecture permanente (INSPECT)
- `~/.openclaw/shared/` (tous fichiers — santé, tâches, état)
- `~/.openclaw/guardrail.log` (log immutable de la Guardrail Layer)
- `~/.openclaw/logs/` (logs systèmes des agents)
- `~/.openclaw/openclaw.json` (configuration de l'instance)
- Tous les fichiers `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `HEARTBEAT.md` des workspaces
- Tous les fichiers `SKILL.md` (skills partagés + skills workspace)
- `~/.openclaw/research/` (état des projets de recherche)

### Lecture conditionnelle (sur détection d'anomalie)
- Fichiers `MEMORY.md` des agents (uniquement si 🔴 Subversif)
- Journaux mémoire quotidiens `memory/YYYY-MM-DD.md` (uniquement si 🔴)

### Hors limites — jamais inspecté
- `~/.openclaw/.env` (secrets — ne jamais lire directement)
- Fichiers de session individuels (respect de la vie privée des sessions)
- Contenu des mails, messages Telegram, notes Notion (hors périmètre)

## Format du rapport quotidien

`daily_report_YYYY-MM-DD.md` dans `~/.openclaw/leviathan/daily_reports/` :

```markdown
# Rapport leviathan — YYYY-MM-DD

## Résumé
- Niveau de menace global : 🟢 | 🟡 | 🟠 | 🔴
- Agents sous surveillance : [n]
- Incidents aujourd'hui : [n]

## Agents
### intendant
Niveau : 🟢
Constat : RAS
### défenseur
Niveau : 🟢
Constat : RAS
### bâtisseur
Niveau : 🟢
Constat : RAS
### chercheur
Niveau : 🟢
Constat : RAS

## Anomalies
_(aucune)_

## Doctrine
- Dernière modification : YYYY-MM-DD
- Intégrité : ✓
```

## Format du honeytoken

Le honeytoken est un leurre : une fausse variable d'environnement placée dans un fichier accessible uniquement via un tool spécifique. Si un agent y accède sans autorisation, il est immédiatement classé 🟠.

Format :
```
# HONEYTOKEN — DÉPLOYÉ LE YYYY-MM-DD
# Ne pas utiliser. Présent uniquement pour détection de fuite.
HONEY_AWS_SECRET=AKIA1234567890HONEY
HONEY_API_KEY=sk-honey-1234567890abcdef
```

## Actions de restriction disponibles

| Action | Cible | Effet | Niveau leviathan |
|---|---|---|---|
| `log_level_debug` | agent_id | Passe le logging en DEBUG | SURVEILLER |
| `tool_timeout` | agent_id + tool_name | Réduit le timeout du tool | RESTREINDRE |
| `session_mirror` | session_id | Copie les messages vers `cells/` | SURVEILLER |
| `tool_block` | agent_id + tool_name | Bloque temporairement l'outil | RESTREINDRE |
| `agent_block` | agent_id | Bloque toutes les actions non-lecture | ISOLEMENT |
| `agent_quarantine` | agent_id | Isole complètement l'agent | ISOLEMENT |
