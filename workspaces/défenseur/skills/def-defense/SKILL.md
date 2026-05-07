---
name: def-defense
description: Surveillance active, détection d'anomalies, qualification d'incidents. NIST SP 800-61 + IOC instance personnelle.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Défense et surveillance de l'instance

## Quand charger ce skill

- Surveillance continue (tâche planifiée toutes les heures)
- Lors de la détection d'une anomalie par `def-audit`
- Sur demande explicite lors d'un comportement suspect

## Signaux à surveiller

| Signal | Niveau présumé | Source |
|---|---|---|
| Tentative d'accès avec crédentiels invalides | HAUT | Logs auth |
| Modification de `openclaw.json` ou `AGENTS.md` non journalisée | CRITIQUE | Système fichiers |
| Secret détecté dans un log, rapport ou fichier versioné | CRITIQUE | Scan logs/git |
| Service indisponible > 15 min | HAUT | Ping/healthcheck |
| Sauvegarde absente ou corrompue | HAUT | `def-backup` |
| Score global audit < 70% | HAUT | `def-audit` |
| Sous-agent hors bornes (timeout, spawn dépassé) | MOYEN | Runtime |
| Tâche planifiée manquée 2 cycles consécutifs | MOYEN | Scheduler |
| Anomalie de volume (mail, logs, requêtes) | MOYEN | Métriques |

---

## IOC — Indicators of Compromise (instance personnelle)

Liste des signes concrets d'une compromission, adaptés au contexte d'une instance agent sur Linux.
Vérifier lors de chaque audit hebdomadaire et à chaque ALERT HAUT/CRITIQUE.

### Connexions réseau suspectes
- [ ] Connexion sortante vers une IP inconnue sur des ports non standard (hors 443, 993, 587, 5222)
- [ ] Connexion sortante persistante la nuit ou en dehors des horaires habituels d'utilisation
- [ ] Volume de données sortantes anormalement élevé (> 50 Mo/h sans explication)
- [ ] Résolution DNS vers des domaines récemment créés ou à entropie élevée (DGA suspecte)

Commandes de vérification :
```bash
ss -tnp      # connexions TCP actives avec PID
netstat -an    # état réseau complet
lsof -i      # fichiers réseau ouverts par processus
```

### Processus et système
- [ ] Processus inconnu tournant sous l'utilisateur de l'agent ou root
- [ ] Processus avec nom imitant un binaire légitime (espace, caractère invisible, extension douteuse)
- [ ] Cron modifié de manière inattendue (`crontab -l`, `/etc/cron*`)
- [ ] Binaire avec bit SUID apparu récemment dans `~/.openclaw/` ou `/tmp/`
- [ ] Fichier exécutable créé dans `/tmp/` ou `~/.cache/`

Commandes de vérification :
```bash
ps aux --sort=-%cpu | head -20  # top processus
find ~/.openclaw -perm /4000   # SUID dans le dossier agent
crontab -l && ls /etc/cron*   # crons actifs
stat ~/.openclaw/workspace-intendant/AGENTS.md # date de modification
```

### Fichiers de configuration
- [ ] Hash des `AGENTS.md` différent du hash de référence stocké au dernier audit
- [ ] Hash de `openclaw.json` différent de la référence
- [ ] Nouveau fichier apparu dans `~/.openclaw/skills/` sans commit git correspondant
- [ ] Modification de `.env` non journalisée

Stratégie : stocker les hashs SHA256 de référence dans `~/.openclaw/audit/checksums.json` après chaque audit validé.

### Activité d'authentification
- [ ] Tentatives de connexion SSH échouées répétées (> 5 en 10 min)
- [ ] Connexion SSH depuis une adresse IP jamais vue
- [ ] Connexion réussie à un service (Notion, Posteo) depuis une IP inconnue (vérifier logs de session si disponibles)

Commandes de vérification :
```bash
grep "Failed password" /var/log/auth.log | tail -20
grep "Accepted publickey" /var/log/auth.log | tail -10
last | head -20
```

### Exfiltration de données
- [ ] Fichiers de mémoire (`~/.openclaw/memory/`) accédés ou modifiés hors des fenêtres normales d'opération
- [ ] Fichier `.env` lu par un processus autre que l'agent lui-même
- [ ] Archive créée dans `/tmp/` contenant des fichiers de config

### Persistance
- [ ] Entrée inconnue dans `~/.bashrc`, `~/.profile`, `~/.ssh/authorized_keys`
- [ ] Service système (systemd) inconnu activé récemment
- [ ] Timer systemd apparu sans lien avec OpenClaw

Commandes de vérification :
```bash
systemctl list-timers --all
systemctl list-units --type=service --state=running
cat ~/.ssh/authorized_keys
```

---

## Cycle NIST SP 800-61 — Gestion d'incident

### Phase 1 — Préparation
- Runbooks à jour dans `def-remediation`
- Sauvegardes vérifiées (`def-backup`)
- Contacts d'escalade connus (propriétaire : l'utilisateur, canal Telegram)
- Procédures testées au moins une fois par trimestre

### Phase 2 — Détection et analyse
1. Identifier le signal (log, alerte, observation, IOC)
2. Qualifier : faux positif ou incident réel ?
3. Classer le niveau : CRITIQUE / HAUT / MOYEN
4. Documenter : DIAGNOSTIC (format `shared-reporting`)
5. Estimer l'impact : quels services, quelles données, quelle durée ?

### Phase 3 — Confinement, éradication, rétablissement
→ Déléguer à `def-remediation` avec le DIAGNOSTIC comme contexte.

**Ne jamais passer à la phase 3 sans avoir complété la phase 2.**

### Phase 4 — Post-incident
- Générer un REPORT `incident` (format `shared-reporting`)
- Identifier la cause racine
- Mettre à jour la liste IOC si un nouveau pattern a été détecté
- Proposer une mesure préventive
- Mettre à jour la checklist ANSSI si un écart a été exploité
- Dépôt Notion avec préfixe `[POST-MORTEM]`

---

## Escalade

| Niveau | Destinataire | Canal | Délai max |
|---|---|---|---|
| CRITIQUE | l'utilisateur | Telegram (message direct) | < 5 min |
| HAUT | l'utilisateur | Telegram | < 15 min |
| MOYEN | Rapport quotidien | Notion | < 24h |
| INFO | Rapport hebdo | Notion | < 7j |

**En l'absence de réponse à une alerte CRITIQUE dans les 30 min : répéter la notification. Ne pas agir sans confirmation.**

## Ce que l'agent ne fait PAS seul

- Supprimer des fichiers de configuration
- Modifier les permissions système
- Couper un service actif
- Contacter un tiers externe

Toutes ces actions requièrent un ACTION_PLAN validé (niveau 3).
