---
name: bat-bootstrap
description: Vérification démarrage bâtisseur. REPORT bootstrap. Bloque les actions si état dégradé.
metadata:
 {
  "openclaw":
   {
    "requires":
     {
      "env":
       ["SYS_VENV_PATH", "SYS_SCRIPTS_PATH", "SYS_TEST_PATH"],
     },
   },
 }
---

# Bootstrap système — vérification de démarrage

## Quand charger ce skill

- **Toujours**, avant tout autre skill, au démarrage de chaque session.
- Après un redémarrage non planifié détecté.
- Sur demande via la commande `/status` depuis Telegram.

## Checklist de survie (dans cet ordre)

### 1. Structure des répertoires OpenClaw système

- [ ] `/opt/openclaw/` présent — permissions 750, propriétaire user courant
- [ ] `/opt/openclaw/venv/` présent et activable (`source /opt/openclaw/venv/bin/activate && python3 -c "import sys; print(sys.version)"`)
- [ ] `/opt/openclaw/scripts/` présent
- [ ] `/opt/openclaw/scripts/.git/` présent et intègre (`git -C /opt/openclaw/scripts status`)

**Si répertoires manquants :** créer automatiquement (N2, idempotent), log dans REPORT bootstrap.

### 2. Espace disque

- [ ] Partition `/` : espace libre > 2 Go
- [ ] Partition `/home` (si séparée) : espace libre > 1 Go
- [ ] Partition hébergeant `/opt` : espace libre > 500 Mo

### 3. Environnement Python venv

- [ ] Python accessible dans le venv : `/opt/openclaw/venv/bin/python3 --version`
- [ ] Paquets critiques présents : `pip show requests exchangelib` dans le venv

### 4. Services systemd OpenClaw

- [ ] Lister les services actifs contenant "openclaw" : `systemctl list-units --all | grep openclaw`
- [ ] Aucun service en état `failed`

### 5. Intégrité des scripts

- [ ] `git -C /opt/openclaw/scripts log --oneline -1` retourne une entrée

## Décision après bootstrap

| Résultat | Comportement |
|---|---|
| Tous les checks OK | Continuer normalement — REPORT `bootstrap` INFO |
| Répertoires manquants créés | Continuer — REPORT `bootstrap` avec liste des créations |
| Disque < 500 Mo sur `/opt` | Bloquer les installations — ALERT HAUT |
| Venv cassé | Bloquer les tâches Python — ALERT HAUT — recréer venv (N2) |
| Scripts git corrompu | ALERT HAUT — attendre instruction |
| Disque < 100 Mo | ALERT CRITIQUE — bloquer tout |

## Format de sortie

```
[REPORT][TIMESTAMP][bâtisseur][TYPE: bootstrap]

## Résumé exécutif
<État global : OK / DÉGRADÉ / BLOQUÉ>

## Checks effectués
- [✅|❌] Répertoires /opt/openclaw/ — [détail si KO]
- [✅|❌] Espace disque — [valeurs]
- [✅|❌] Python venv — [version si OK]
- [✅|❌] Services systemd OpenClaw — [liste si actifs]

## Décision
<Continuer | Continuer en mode dégradé | Bloqué — en attente>

## Prochaine vérification
<prochain audit planifié : 02h00>
```
