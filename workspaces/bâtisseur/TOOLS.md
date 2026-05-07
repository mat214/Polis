# TOOLS.md — bâtisseur

## Chemins système
- Espace de travail : `~/.openclaw/workspace-bâtisseur`
- Venv : `/opt/openclaw/venv/`
- Scripts : `/opt/openclaw/scripts/` (suivi git)
- Test : `/tmp/openclaw-test/`

## Gestion des paquets
- apt : système entier, classifié S/N/ST
- pip : venv uniquement (`/opt/openclaw/venv/bin/pip`)
- Freeze avant modifications du venv : `pip freeze > requirements.backup.txt`

## Services
- systemd : unités `openclaw-*`
- Template : `NoNewPrivileges=true`, `ProtectSystem=strict`
- Vérifier : `systemd-analyze verify` avant installation

## Scripts
- Dépôt git dans `/opt/openclaw/scripts/`
- En-tête obligatoire : objectif, dépendances, commande de rollback
- Valider : `bash -n`, `shellcheck`, `python3 -m py_compile`
