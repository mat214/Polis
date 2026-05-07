---
name: bat-packages
description: Paquets apt et pip (venv). Matrice S/N/ST. pip hors venv = BLOCK.
metadata:
 {
  "openclaw":
   {
    "requires": { "env": ["SYS_VENV_PATH"], "bins": ["apt", "pip"] },
   },
 }
---

# Gestion des paquets

## Règles absolues

1. **`pip install` hors de `/opt/openclaw/venv/`** → BLOCK immédiat + ALERT MOYEN. Sans exception.
2. **`apt upgrade` global** → toujours catégorie ST (Human Gate).
3. **`apt remove`** → vérifier les dépendances inverses avant toute suppression.
4. **Idempotence** : vérifier si le paquet est déjà installé avant d'agir.

## Chemins autorisés

| Outil | Chemin autorisé | Chemin interdit |
|---|---|---|
| pip | `/opt/openclaw/venv/bin/pip` uniquement | `/usr/bin/pip`, `pip3` système |
| apt | Système entier (avec classification) | — |
| venv | `/opt/openclaw/venv/` | Tout autre chemin |

## Catalogue pré-approuvé (catégorie S)

### Paquets apt approuvés

```
curl wget git jq ripgrep htop unzip rsync logrotate cron
python3-venv python3-dev build-essential
ffmpeg sox libsndfile1 libportaudio2
```

### Paquets pip approuvés (dans venv uniquement)

```
requests httpx
python-telegram-bot
exchangelib
caldav vobject
openai-whisper faster-whisper pydub ffmpeg-python
anthropic
safety
```

## Classification des changements

| Action | Guardrail | Catégorie | Condition |
|---|---|---|---|
| `apt install` (catalogue approuvé) | WRITE | S | Paquet dans la liste ci-dessus |
| `apt install` (hors catalogue) | WRITE_SENSITIVE | N (calcul score) | — |
| `apt remove` | WRITE_SENSITIVE | N (score + rdepends) | — |
| `apt upgrade paquet` | WRITE_SENSITIVE | N (calcul score) | Mise à jour unitaire |
| `apt upgrade` global | IRREVERSIBLE | ST | Toujours Human Gate |
| `pip install` (catalogue approuvé, venv) | WRITE | S | Dans /opt/openclaw/venv/ |
| `pip install` (hors catalogue, venv) | WRITE_SENSITIVE | N (calcul score) | Dans /opt/openclaw/venv/ |
| `pip install` (hors venv) | WRITE_SENSITIVE | BLOCK | Violation — ALERT MOYEN |
| `pip uninstall` | WRITE_SENSITIVE | N (calcul score) | Vérifier dépendances |
| `create_venv` | WRITE | S | Crée /opt/openclaw/venv/ |

## Workflow idempotent d'installation

```
VÉRIFICATION PRÉALABLE
  │
  ├─ apt : dpkg -l | grep "^ii" | grep paquet → déjà installé ?
  ├─ pip : /opt/openclaw/venv/bin/pip show paquet → déjà installé ?
  │
  ├─ OUI : log INFO "paquet déjà présent", sortir
  │
  └─ NON : classifier l'action
        │
        ├─ S  : installer directement + log N2
        ├─ N  : calculer score de risque
        │     ├─ score < 70 : installer + log N2
        │     └─ score ≥ 70 : Human Gate
        └─ ST : Human Gate systématique
```

## Calcul du score de risque pour apt (catégorie N)

Axes :
- **Scope** : paquet avec dépendances système partagées (+20), paquet standalone (+5)
- **Réversibilité** : `apt remove --purge` disponible (0), dépendances partagées (+15)
- **Test** : paquet connu et documenté (0), inconnu (+10)

Vérification des dépendances inverses avant suppression :
```bash
apt-cache rdepends --installed paquet
```
Si > 3 dépendances inverses : score +30 automatique.

## Gestion du venv

### Création (idempotente)

```bash
# Vérifier d'abord
test -d /opt/openclaw/venv && echo "existe" || python3 -m venv /opt/openclaw/venv
```

### Freeze (sauvegarde avant modification)

Avant toute modification du venv (installation ou suppression) :
```bash
/opt/openclaw/venv/bin/pip freeze > /opt/openclaw/venv/requirements.backup.txt
```
Ce fichier est le point de rollback pour la restauration du venv.

### Rollback venv

```bash
/opt/openclaw/venv/bin/pip install -r /opt/openclaw/venv/requirements.backup.txt
```
