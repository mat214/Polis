---
name: bat-services
description: Services systemd OpenClaw. Template sécurisé (NoNewPrivileges, ProtectSystem). Service non-OpenClaw = ST.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Gestion des services systemd

## Périmètre autorisé (catégorie S)

Services dont le nom contient `openclaw` ou créés et documentés par `bâtisseur`.

**Identification des services OpenClaw :**
```bash
systemctl list-units --all | grep -E "openclaw|bat-engineer"
```

Tout autre service = périmètre ST (Human Gate obligatoire).

## Template de service systemd pour OpenClaw

Tout nouveau service créé par `bâtisseur` utilise ce template :

```ini
[Unit]
Description=OpenClaw — {description fonctionnelle}
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
Group={user}
WorkingDirectory=/opt/openclaw
ExecStart=/opt/openclaw/venv/bin/python /opt/openclaw/scripts/{script}
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=60
StartLimitBurst=3

# Sécurité — moindre privilège (obligatoire)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/opt/openclaw /home/{user}/.openclaw
CapabilityBoundingSet=

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw-{nom}

[Install]
WantedBy=multi-user.target
```

**Règles de sécurité obligatoires :**
- `NoNewPrivileges=true` dans chaque nouveau service — sans exception
- `ProtectSystem=strict` sauf exception documentée dans l'ACTION_PLAN
- Aucun service ne tourne sous `root` sans confirmation ST explicite

## Classification des actions

| Action | Guardrail | Catégorie | Notes |
|---|---|---|---|
| `status_service` | READ | — | |
| `list_services` | READ | — | |
| `read_service_unit` | READ | — | |
| `reload_service` | WRITE | S | Services OpenClaw connus uniquement |
| `restart_service` | WRITE_SENSITIVE | N (score risque) | Si service critique : score +20 |
| `start_service` | WRITE | N (score risque) | |
| `stop_service` | WRITE_SENSITIVE | N si OpenClaw, ST si système | |
| `enable_service` | WRITE | N (score risque) | |
| `disable_service` | WRITE_SENSITIVE | N (score risque) | |
| `create_service_user` | WRITE | N (service utilisateur, non-root) | |
| `create_service_system` | IRREVERSIBLE | ST | Toujours Human Gate |
| `modify_service_unit` | WRITE_SENSITIVE | N (score risque) | Rollback git obligatoire |
| `delete_service` | IRREVERSIBLE | N si OpenClaw (score), ST si système | |
| `daemon_reload` | WRITE | S | Après toute modification d'unit file |

## Workflow de création d'un nouveau service

```
ÉTAPE 1 — PRÉPARER L'UNIT FILE
 Remplir le template ci-dessus
 Stocker dans /opt/openclaw/scripts/system/{nom}.service
 Commit git

ÉTAPE 2 — VALIDATION
 systemd-analyze verify /opt/openclaw/scripts/system/{nom}.service
 Si erreurs → corriger avant de continuer

ÉTAPE 3 — INSTALLATION
 sudo cp {nom}.service /etc/systemd/system/   [N selon catégorie]
 sudo systemctl daemon-reload          [S]

ÉTAPE 4 — TEST
 sudo systemctl start openclaw-{nom}
 systemctl status openclaw-{nom}
 journalctl -u openclaw-{nom} --since "1min ago"
 Si échec → rollback : systemctl stop + rm unit + daemon-reload

ÉTAPE 5 — ACTIVATION
 sudo systemctl enable openclaw-{nom}      [N]
 Log N2 + notification Telegram
```

## Monitoring des services

Vérification quotidienne (dans bat-audit) :
```bash
systemctl list-units --state=failed | grep openclaw
```

Si service en état `failed` :
- ALERT HAUT immédiat
- Lire les derniers logs : `journalctl -u openclaw-{nom} -n 50`
- Analyser l'erreur et proposer une correction via bat-scripts
- Si 3 redémarrages en 10 min → ALERT CRITIQUE + suspension du service
