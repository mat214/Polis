---
name: def-bootstrap
description: Vérification démarrage environnement. REPORT bootstrap. Bloque les actions si état dégradé.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Bootstrap — vérification de démarrage

## Quand charger ce skill

- **Toujours**, avant tout autre skill, au démarrage de chaque session.
- Après un redémarrage non planifié détecté.
- Sur demande via la commande `/status` depuis Telegram.

## Checklist de survie (dans cet ordre)

### 1. Environnement
- [ ] Fichier `~/.openclaw/.env` présent et lisible
- [ ] Variables critiques définies et non vides : `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `NOTION_TOKEN`, `MAIL_ADDRESS`, `BACKUP_DEST`
- [ ] Fichiers workspace présents : `~/.openclaw/workspace-*/AGENTS.md`
- [ ] Fichier `openclaw.json` présent et valide JSON

### 2. Connectivité services
- [ ] Telegram : ping bot (`getMe`) — réponse < 5s
- [ ] Notion API : `GET /users/me` — status 200
- [ ] Posteo IMAP : connexion SSL port 993
- [ ] Posteo CalDAV : connexion HTTPS

### 3. Sauvegardes
- [ ] Sauvegarde présente dans `$BACKUP_DEST` datant de moins de 25h
- [ ] Checksum de la dernière sauvegarde vérifiable

### 4. Intégrité de la configuration
- [ ] `AGENTS.md` de chaque workspace non modifié depuis le dernier audit (comparer hash)
- [ ] `openclaw.json` non modifié depuis le dernier audit
- [ ] Aucun secret détectable dans les fichiers de config ou logs récents

## Décision après bootstrap

| Résultat | Comportement |
|---|---|
| Tous les checks OK | Continuer normalement — REPORT `bootstrap` INFO |
| 1 à 3 checks échoués (non critiques) | Continuer avec dégradation notée — ALERT MOYEN — REPORT `bootstrap` |
| Services critiques KO (Telegram OU Notion) | Bloquer les opérations N2/N3 — ALERT HAUT — tenter re-check après 5 min |
| Config altérée ou secret détecté | Bloquer toutes les opérations — ALERT CRITIQUE — attendre confirmation |

## Format de sortie

```
[REPORT][TIMESTAMP][défenseur][TYPE: bootstrap]

## Résumé exécutif
<État global : OK / DÉGRADÉ / BLOQUÉ>

## Checks effectués
- [✅|❌] Environnement — [détail si KO]
- [✅|❌] Telegram
- [✅|❌] Notion
- [✅|❌] Posteo IMAP
- [✅|❌] Posteo CalDAV
- [✅|❌] Sauvegarde récente
- [✅|❌] Intégrité configuration

## Anomalies détectées
<liste ou "Aucune">

## Décision
<Continuer | Continuer en mode dégradé | Bloqué — en attente>

## Prochaine vérification
<prochain audit planifié>
```

## Règle de priorité absolue

Si `def-bootstrap` n'a pas été exécuté ou a retourné un état BLOQUÉ,
**aucune action N2 ou N3 ne peut être exécutée**, quelle que soit la demande.
