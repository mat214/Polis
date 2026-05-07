# Polis — Architecture de référence OpenClaw

> Configuration de référence pour une instance OpenClaw structurée, maintenable et évolutive — 7 agents, 8 skills partagés, gouvernance constitutionnelle, pipeline CI, cycles d'apprentissage et de rétroaction. **Polis** est le nom de cette architecture.

[![Validate](https://github.com/mat214/Polis/actions/workflows/validate.yml/badge.svg)](https://github.com/mat214/Polis/actions/workflows/validate.yml)
[![Security](https://github.com/mat214/Polis/actions/workflows/security.yml/badge.svg)](https://github.com/mat214/Polis/actions/workflows/security.yml)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Constitution

L'instance repose sur **[`CONSTITUTION.md`](./CONSTITUTION.md)** — 77 articles en 12 titres qui définissent quatre forces en tension, des cycles d'apprentissage et des mécanismes de rétroaction :

| Force | Incarnée par | Mission |
|---|---|---|
| **Innovation** | Chercheur | Proposer, explorer, améliorer |
| **Infrastructure et moyens** | bâtisseur + défenseur | Bâtir, outiller, défendre, maintenir |
| **Stabilité** | leviathan | Surveiller, préserver, corriger |
| **Transparence** | Journaliste | Documenter, révéler, éclairer |

L'utilisateur est la raison d'être du système (Article 1). La constitution prévaut sur toute autre règle.

## Architecture

```
~/.openclaw/
├── openclaw.json       # Configuration JSON5 (gateway, channels, bindings)
├── .env            # Secrets et tokens (jamais commité)
├── skills/          # Skills partagés (tous les agents)
│  ├── shared-governance/   # Règles de gouvernance (priorité absolue)
│  ├── shared-reporting/   # Formats de sortie obligatoires
│  ├── shared-state/     # SessionManager
│  ├── shared-guardrail/   # Couche de sécurité active + Kill Switch
│  ├── shared-notion-openclaw/
│  ├── shared-interagent/   # Coordination inter-agents + bus d'événements
│  ├── shared-learning/    # Apprentissage ops/sys + rétroaction utilisateur
│  └── shared-smoketest/   # Smoke test post-démarrage et heartbeat
├── workspace-intendant/    # intendant
├── workspace-défenseur/    # défenseur
├── workspace-bâtisseur/    # bâtisseur
├── workspace-chercheur/    # chercheur (veille et innovation)
├── workspace-leviathan/    # leviathan (surveillance philosophique)
├── workspace-journaliste/   # journaliste (transparence et investigation)
└── workspace-anarchiste/   # anarchiste (force critique et contestation)
```

## Agents

| Agent | Rôle | Temp. | Canal |
|---|---|---|---|
| **intendant** | Assistant personnel : mail, agenda, contacts, tâches, Telegram | 0.4 | Telegram (défaut) |
| **défenseur** | Infrastructure : audit, sécurité, sauvegardes, mises à jour | 0.1 | Heartbeat · `openclaw-run défenseur "..."` |
| **bâtisseur** | Machine hôte : paquets, scripts, services, auto-provisioning | 0.1 | Heartbeat · `openclaw-run bâtisseur "..."` |
| **chercheur** | Veille technologique, innovation, projets de recherche | 0.3 | Heartbeat · `openclaw-run chercheur "..."` |
| **leviathan** | Surveillance philosophique et architecturale | 0.05 | Heartbeat · `openclaw-run leviathan "..."` |
| **journaliste** | Transparence, gazette quotidienne, investigation | 0.2 | Heartbeat · `openclaw-run journaliste "..."` |
| **anarchiste** | Force critique, contestation, motion, mise à l'épreuve | 0.15 | Heartbeat · `openclaw-run anarchiste "..."` |

> **Heartbeat** : l'agent s'exécute sur un timer et n'écoute pas en continu. Pour lui parler directement depuis le terminal : `openclaw-run <agent> "<message>"` (nécessite `openclaw` et le Gateway actif).

## Prérequis

- **Python ≥ 3.12** — nécessaire pour le CLI Polis et le bus d'événements SQLite (`polis/eventbus.py`)
- **OpenClaw Gateway** — voir [openclaw.dev](https://openclaw.dev) pour l'installation
- **Git** — pour cloner le dépôt

Dépendances Python supplémentaires (développement) : `ruff`, `mypy`, `pytest`, `coverage`.
Installation : `pip install -e "polis[dev]"` ou `make dev-setup`.

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/mat214/Polis.git
cd openclaw-projet

# 2. Créer la structure ~/.openclaw/
mkdir -p ~/.openclaw/skills ~/.openclaw/shared
mkdir -p ~/.openclaw/workspace-intendant ~/.openclaw/workspace-défenseur
mkdir -p ~/.openclaw/workspace-bâtisseur ~/.openclaw/workspace-chercheur
mkdir -p ~/.openclaw/workspace-leviathan ~/.openclaw/workspace-journaliste
mkdir -p ~/.openclaw/workspace-anarchiste

# 3. Copier les templates
cp -r skills/* ~/.openclaw/skills/
cp -r workspaces/intendant/* ~/.openclaw/workspace-intendant/
cp -r workspaces/défenseur/* ~/.openclaw/workspace-défenseur/
cp -r workspaces/bâtisseur/* ~/.openclaw/workspace-bâtisseur/
cp -r workspaces/chercheur/* ~/.openclaw/workspace-chercheur/
cp -r workspaces/leviathan/* ~/.openclaw/workspace-leviathan/
cp -r workspaces/journaliste/* ~/.openclaw/workspace-journaliste/
cp -r workspaces/anarchiste/* ~/.openclaw/workspace-anarchiste/
cp openclaw.json.example ~/.openclaw/openclaw.json
cp .env.example ~/.openclaw/.env

# 4. Éditer vos tokens
$EDITOR ~/.openclaw/.env

# 5. Lancer OpenClaw
openclaw setup --workspace ~/.openclaw/workspace-intendant
```

> **Option automatisée** : `make install` fait la même chose en une commande (avec `--dry-run` pour simuler).

## Polis CLI

Le projet fournit un outil en ligne de commande pour valider et interagir avec l'architecture :

```bash
# Installation
pip install -e polis/

# Validation
polis check constitution  # 71 articles, numérotation continue
polis check agents     # 7 workspaces, fichiers complets
polis check config     # JSON5 valide, vars d'env cohérentes

# Opérations
polis eventbus status   # Statistiques du bus d'événements
polis smoke run      # Vérification de santé locale
polis kill status     # État du Kill Switch

# Démonstrations
polis guardrail simulate  # Simule un blocage Guardrail
polis demo leviathan    # Scénario de surveillance leviathan
```

## Tests

```bash
python3 -m pytest tests/ -v  # ~95 tests d'intégration et runtime
make validate          # Validation bash (10 catégories)
make lint            # ruff + mypy + ShellCheck
make coverage          # Tests avec couverture (seuil 40%)
```

Les tests, le linting et le type checking s'exécutent automatiquement sur chaque push via GitHub Actions.

## Tâches planifiées (Cron)

L'instance utilise le planificateur cron intégré d'OpenClaw. Détail complet des jobs, messages et horaires dans [`DESCRIPTION.md`](./DESCRIPTION.md#tâches-planifiées-cron).

## Gouvernance

Toutes les actions sont classifiées en 3 niveaux (définis par la constitution, Article 47) :

| Niveau | Type | Confirmation | Log |
|---|---|---|---|
| **N1** | Lecture seule | Non | Non |
| **N2** | Action réversible | Non | Oui |
| **N3** | Action sensible/irréversible | **Oui** | Oui |

Trois cycles d'évolution permanente :

- **FEEDBACK** (Article 49bis) : l'utilisateur corrige un agent → enregistrement dans `shared/feedback/` → validation technique par le défenseur → application immédiate → fenêtre de contestation 48h → mémorisation permanente.
- **SKILL-PIPE** (Article 49ter) : le chercheur détecte un besoin → proposition dans `shared/skill_proposals/` → validation technique par le défenseur → construction par bâtisseur → déploiement → 7j d'observation.
- **LEARN-5** (Article 49) : apprentissage par patterns (3 occurrences) → publication `[PROVISOIRE]` → contestation 48h → mémorisation permanente sans gatekeeper central.

## Documentation complémentaire

- [`CONSTITUTION.md`](./CONSTITUTION.md) — Loi fondamentale de l'instance (77 articles, 12 titres)
- [`DESCRIPTION.md`](./DESCRIPTION.md) — Architecture complète, agents, skills, sécurité
- [`TESTING.md`](./TESTING.md) — Stratégie de test et comment ajouter un test
- [`PRODUCTION_READY_CHECKLIST.md`](./PRODUCTION_READY_CHECKLIST.md) — Checklist de mise en production
- [`CHANGELOG.md`](./CHANGELOG.md) — Historique des modifications par chantier
- [`SECURITY.md`](./SECURITY.md) — Politique de sécurité et runbooks d'urgence

## CI

Trois workflows GitHub Actions s'exécutent automatiquement sur chaque push :
- **validate** : ShellCheck + validation complète du dépôt + tests + lint + type checking
- **security** : Gitleaks (scan de secrets)

---

> Dépôt : https://github.com/mat214/Polis
> Projet : Polis — architecture de référence OpenClaw
> Licence : MIT
