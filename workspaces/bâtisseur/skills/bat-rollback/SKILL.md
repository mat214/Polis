---
name: bat-rollback
description: Plans de rollback avant action N ou ST. Catalogue : paquets, scripts, services, crons. Impossible = ST.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Rollback — retour arrière standardisé

## Règle fondamentale

**Toute action de catégorie N ou ST doit avoir un plan de rollback documenté AVANT son exécution.**

Si le rollback n'est pas possible ou inconnu → l'action est reclassifiée ST automatiquement.

## Catalogue des procédures de rollback

### Paquets

| Action | Rollback | Délai | Données perdues |
|---|---|---|---|
| `apt install paquet` | `apt remove --purge paquet && apt autoremove` | < 1 min | Non |
| `apt remove paquet` | `apt install paquet` | < 2 min | Configuration si `--purge` utilisé |
| `pip install paquet` (venv) | `pip uninstall -y paquet` | < 30s | Non |
| `pip uninstall paquet` (venv) | `pip install paquet==version` | < 1 min | Non |
| `pip install -r requirements.txt` | `pip install -r requirements.backup.txt` | < 2 min | Non |

### Scripts

| Action | Rollback | Délai | Données perdues |
|---|---|---|---|
| Création script | `git rm script && git commit -m "revert: suppression script"` | < 1 min | Non |
| Modification script | `git revert HEAD` ou `git checkout HEAD~1 -- script` | < 1 min | Non |
| Suppression script | `git checkout HEAD~1 -- script` | < 1 min | Non si dans git |
| Déploiement script en prod | `git revert HEAD && git checkout main` | < 2 min | Non |

### Services systemd

| Action | Rollback | Délai | Données perdues |
|---|---|---|---|
| `systemctl enable service` | `systemctl disable --now service` | < 1 min | Non |
| `systemctl start service` | `systemctl stop service` | < 1 min | Non |
| Création unit file | `systemctl disable --now service && rm unit-file && systemctl daemon-reload` | < 2 min | Non |
| Modification unit file | Restaurer depuis git + `systemctl daemon-reload` | < 2 min | Non |

### Crons

| Action | Rollback | Délai | Données perdues |
|---|---|---|---|
| Ajout cron `/etc/cron.d/openclaw-*` | `rm /etc/cron.d/openclaw-{nom}` | < 30s | Non |
| Modification cron | Restaurer version précédente depuis git | < 1 min | Non |

### Intégrations (modification de skills int-* ou shared-*)

| Action | Rollback | Délai | Données perdues |
|---|---|---|---|
| Modification `int-telegram/SKILL.md` | `git revert HEAD` dans le dépôt openclaw | < 1 min | Non |
| Ajout handler dans skill PA | `git revert HEAD` dans le dépôt openclaw | < 1 min | Non |

## Format obligatoire du plan de rollback

À inclure dans tout ACTION_PLAN avant une action N ou ST :

```
[ROLLBACK_PLAN]
Action     : {description précise de l'action à annuler}
Commande    : {commande exacte, copiable-collable}
Données perdues : non | oui — {préciser}
Délai estimé  : {temps}
Rollback testé : oui ({date}) | non
Prérequis    : {ce qui doit être vrai pour que le rollback fonctionne}
```

## Exécution du rollback

### Rollback automatique (suite à échec de test ou monitoring post-déploiement)

Déclenché automatiquement si :
- Le test de l'étape 3 (test isolé) échoue
- Le monitoring post-déploiement (15 min) détecte une anomalie
- Un service OpenClaw tombe dans les 15 min après une modification

Procédure :
1. Exécuter la commande de rollback du plan (N2 — log obligatoire)
2. Vérifier que le rollback a réussi (`git status`, `systemctl status`, `pip show`)
3. Logger : `[ROLLBACK AUTO][TIMESTAMP] — action: {action} — raison: {anomalie}`
4. Notifier via Telegram : `⚠️ Rollback automatique effectué — {action} annulée — raison: {raison}`
5. Inclure dans le rapport quotidien

### Rollback confirmé (suite à ALERT ou demande explicite)

Toujours N3 — confirmation obligatoire avant exécution.
Présenter : l'action à annuler, la commande exacte, les données potentiellement perdues.

### Rollback en cascade (plusieurs étapes à annuler)

Si une série d'étapes doit être annulée :
1. Annuler dans l'ordre inverse (dernière étape en premier)
2. Chaque annulation est logguée individuellement
3. La cascade entière est toujours N3 si elle touche > 2 étapes

## Règle du rollback impossible

Si une action n'a pas de rollback possible (ex: envoi d'un mail, suppression définitive sans git) :
- L'action est automatiquement reclassifiée `IRREVERSIBLE` (Guardrail Layer)
- Le Human Gate est obligatoire avec mention explicite : "Cette action est irréversible"
- La confirmation doit être explicite : "oui, j'ai compris que c'est irréversible"
