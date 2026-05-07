---
name: bat-audit
description: Audit machine hôte : paquets, services, ressources, intégrité scripts. Score 0-100. Rapport Notion OPENCLAW.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Audit système de la machine hôte

## Quand charger ce skill

- Audit quotidien planifié : 02h00
- Après chaque installation ou modification système (audit ciblé)
- Sur demande via `/status` ou `/audit` depuis Telegram

## Périmètre d'audit

### Audit quotidien

| Zone | Éléments vérifiés | Commandes |
|---|---|---|
| Venv Python | Paquets installés, versions critiques | `/opt/openclaw/venv/bin/pip list --format=json` |
| Scripts | Inventaire, dernière modification | `git -C /opt/openclaw/scripts log --oneline -10` |
| Services | État des services systemd openclaw | `systemctl list-units --all \| grep openclaw` |
| Ressources | CPU, RAM, disque — tendances | `df -h && free -h && uptime` |
| Espace disque | Seuils d'alerte | `df -h /opt /home /` |
| Logs | Erreurs récentes dans les logs openclaw | `journalctl -u 'openclaw-*' --since "24h ago" -p err` |

### Audit hebdomadaire (lundi 01h00, avant def-maintenance)

| Zone | Éléments vérifiés | Commandes |
|---|---|---|
| Paquets apt | Delta depuis dernier audit, mises à jour disponibles | `apt list --upgradable 2>/dev/null` |
| Intégrité scripts | SHA256 chaque script vs hash git HEAD | `git -C /opt/openclaw/scripts status --short` |
| Crons | Inventaire complet des crons openclaw | `crontab -l && ls /etc/cron.d/openclaw-* 2>/dev/null` |
| Permissions | `/opt/openclaw/` doit être 750, `.env` doit être 600 | `stat -c "%a %U" /opt/openclaw && stat -c "%a" ~/.openclaw/.env` |

## Calcul du score de risque de l'environnement

Après chaque audit quotidien, calculer un score de santé global (0–100, 100 = parfait) :

```
Score = 100
- 15 si disque < 20% libre sur /opt
- 25 si disque < 5% libre sur /opt (critique)
- 5 si service systemd openclaw en failed
- 10 si permissions /opt/openclaw incorrectes
```

| Score | Niveau | Action |
|---|---|---|
| 90–100 | OK | Continuer normalement |
| 70–89 | MOYEN | Inclure anomalies dans rapport quotidien |
| 50–69 | HAUT | ALERT HAUT + rapport immédiat |
| < 50 | CRITIQUE | ALERT CRITIQUE + bloquer actions N et ST |

## Format de sortie — section intégrée dans REPORT daily

```
## Santé système [SYSTÈME]
Score     : <n>/100 — OK | MOYEN | HAUT | CRITIQUE
Disque /opt  : <x>% utilisé (<y> Go libres)
Python venv  : OK | KO — <détail>
Services openclaw : <n> actifs, <n> failed
```

## Actions classifiées

| Action | Guardrail | Catégorie |
|---|---|---|
| `scan_packages` | READ | — |
| `scan_services` | READ | — |
| `scan_resources` | READ | — |
| `scan_scripts_integrity` | READ | — |
| `scan_crons` | READ | — |
| `compute_health_score` | READ | — |
| `repair_permissions` | WRITE | S (permissions /opt/openclaw uniquement) |
| `create_missing_dirs` | WRITE | S (répertoires /opt/openclaw uniquement) |
