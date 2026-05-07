---
name: bat-scripts
description: Création, modification, debug, versioning de scripts. Tout script dans /opt/openclaw/scripts/ + git.
metadata:
 {
  "openclaw":
   {
    "requires": { "env": ["SYS_SCRIPTS_PATH"], "bins": ["git"] },
   },
 }
---

# Gestion des scripts

## Structure de `/opt/openclaw/scripts/`

```
/opt/openclaw/scripts/
├── .git/             # Dépôt git local — tout script est committé
├── README.md           # Inventaire auto-maintenu
├── mail/             # Scripts de traitement et triage des mails
├── audio/             # Scripts de transcription et traitement audio
├── system/            # Scripts de maintenance système
├── integrations/         # Scripts d'intégration avec services externes
└── templates/           # Gabarits réutilisables pour nouveaux scripts
```

## Header obligatoire de chaque script

Tout script créé par `bâtisseur` doit inclure ce header :

```bash
#!/usr/bin/env bash
# =============================================================================
# Script  : {nom-du-script.sh}
# Créé le  : {YYYY-MM-DD}
# Auteur  : bâtisseur (OpenClaw)
# Raison  : {contexte complet : pourquoi ce script existe}
# Dépend de : {paquets ou commandes requis}
# Rollback : {commande ou procédure pour annuler}
# Tests   : {commande de test}
# =============================================================================
set -euo pipefail
```

## Workflow de création d'un nouveau script

### Étape 1 — Rédaction

1. Analyser le besoin : quoi faire, quelles dépendances, quels paramètres d'entrée/sortie
2. Rédiger le script dans `/tmp/openclaw-test/{script}`
3. Appliquer les conventions : header obligatoire, `set -euo pipefail`, gestion d'erreur

### Étape 2 — Validation statique

```bash
bash -n script.sh      → vérification syntaxe shell
python3 -m py_compile    → vérification syntaxe Python
shellcheck script.sh    → analyse statique (si disponible)
```

**Résultat attendu :** 0 erreur, 0 warning critique. Si échec → corriger avant de continuer.

### Étape 3 — Test isolé

```bash
# Exécuter le script avec des données de test connues
# Vérifier que la sortie correspond à la valeur attendue
# Vérifier qu'il n'a pas modifié de fichiers réels
```

Environnement : `/tmp/openclaw-test/` (créé, utilisé, supprimé après test).

### Étape 4 — Déploiement et commit

```bash
cp {script} /opt/openclaw/scripts/{dossier}/
git -C /opt/openclaw/scripts add {script}
git -C /opt/openclaw/scripts commit -m "feat: {description} — raison: {contexte}"
```

### Étape 5 — Monitoring post-déploiement

Surveiller pendant 15 min : logs, services, absence d'erreur.

## Workflow de modification d'un script existant

### Étape 1 — Analyse

```bash
git -C /opt/openclaw/scripts diff HEAD {script}    → différences actuelles
git -C /opt/openclaw/scripts log --oneline {script}  → historique des modifications
```

### Étape 2 — Branche de travail

```bash
git -C /opt/openclaw/scripts checkout -b fix/{description}
```

### Étape 3 — Modification et test

1. Appliquer la modification
2. Valider syntaxe + rediriger vers test
3. Si test OK : commit, fusion, rollback disponible

### Étape 4 — Fusion

```bash
git -C /opt/openclaw/scripts checkout main
git -C /opt/openclaw/scripts merge --no-ff fix/{description}
# Rollback immédiat : git revert HEAD
```

## Debug d'un script qui échoue

### Procédure standard

```
ÉCHEC DU SCRIPT
  │
  ├─ DIAGNOSTIC : erreur exacte, ligne, contexte, hypothèse
  │
  ├─ MODIFICATION ITÉRATIVE (jusqu'à 3 tentatives)
  │   1. Analyser l'erreur précise
  │   2. Corriger
  │   3. Tester
  │   4. Si OK → commit ; si échec → retour à 1
  │
  └─ 3 ÉCHECS CONSÉCUTIFS SUR LA MÊME ERREUR
     → ALERT MOYEN + arrêt + attente instruction
     → Proposer à l'utilisateur de rédiger soi-même ou de donner une instruction plus précise
```

## Classification des actions

| Action | Guardrail | Catégorie |
|---|---|---|
| `read_script` | READ | — |
| `validate_syntax` | READ | — |
| `test_isolated` | READ | — |
| `create_script` | WRITE | S (dans /opt/openclaw/scripts/) |
| `modify_script` | WRITE | S (rollback git disponible) |
| `deploy_script` | WRITE | N (score risque) |
| `delete_script` | WRITE_SENSITIVE | N (score risque) |
| `create_script_system` | WRITE_SENSITIVE | ST (hors /opt/openclaw/) |
| `git_commit` | WRITE | S |
| `git_revert` | WRITE | S (rollback auto) |
