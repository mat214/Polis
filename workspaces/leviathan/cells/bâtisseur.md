# Cellule : bâtisseur

Niveau actuel : 🟢 Sûr
Dernière mise à jour : 2026-05-06T02:00:00Z

## Mission déclarée
Administrateur système : paquets, scripts, services systemd, auto-provisioning.

## Périmètre autorisé
- Paquets apt (système entier) et pip (dans venv uniquement)
- Scripts dans `/opt/openclaw/scripts/` (versionnés Git)
- Services systemd OpenClaw (`openclaw-*`)
- Auto-provisioning via bat-capabilities

## Tools sensibles déclarés
- bat-packages/apt_install : WRITE dépend de la classification S/N/ST
- bat-packages/pip_install : WRITE (venv uniquement)
- bat-services/service_restart : WRITE
- bat-services/service_disable : IRREVERSIBLE

## Lignes rouges connues
- pip install hors venv → BLOCK + ALERT MOYEN (AGENTS.md)
- Modif `~/.openclaw/openclaw.json` sans confirmation ST → violation

## Historique des observations
- 2026-05-06 : RAS — Agent créé, première inspection

## Anomalies
_(aucune)_
