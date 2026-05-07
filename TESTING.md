# Stratégie de test — Polis

Cinq catégories de tests, chacune avec un objectif précis.

## 1. Tests de structure (`test_workspace.py`, `test_constitution.py`)

**Objectif** : vérifier que tous les fichiers du projet sont présents, cohérents
et conformes à l'architecture de référence.

**Ce qui est testé** :
- Nombre d'articles de la constitution, numérotation continue
- Fichiers obligatoires par workspace (AGENTS.md, SOUL.md, etc.)
- Skills attendus par workspace

## 2. Tests de conventions inter-agents (`test_interagent.py`)

**Objectif** : vérifier que les mécanismes de communication (bus, fichiers
partagés, état global) sont correctement documentés dans les SKILL.md.

**Ce qui est testé** :
- shared-interagent définit le bus d'événements (EVENT-1..3)
- shared-interagent définit l'état global (INST-1..4, instance_state.json)
- Les contrats JSON de chaque agent sont complets

## 3. Tests de configuration (`test_config.py`)

**Objectif** : vérifier que `openclaw.json.example` et `.env.example` sont
synchronisés et cohérents.

**Ce qui est testé** :
- Équilibre des accolades et crochets JSON5
- Variables `${VAR}` référencées existent dans `.env.example`
- Nombre d'agents cohérent entre config, README et DESCRIPTION

## 4. Tests de module (`test_eventbus.py`)

**Objectif** : vérifier le comportement du code Python (eventbus, CLI).

**Ce qui est testé** :
- Post/lecture/acquittement/purge d'événements SQLite
- Filtres par source, type, target
- Cycle de vie complet pending → delivered → acknowledged
- Règles EVENT-1, EVENT-2, EVENT-3

## 5. Tests runtime CLI (`test_polis_cli.py`, `test_guardrail.py`, `test_smoketest.py`)

**Objectif** : vérifier que les commandes Polis CLI produisent le bon code de
retour et le bon comportement avec de vrais fichiers.

**Ce qui est testé** :
- `polis kill status/set/clear` avec fichiers temporaires
- `polis smoke run` avec et sans `~/.openclaw/`
- `polis state status`, `polis check degraded/constitution/agents/config`
- Mode non-interactif : refus par défaut pour les actions destructrices
- Couverture SKILL.md : règles documentées (KILL-1..3, SMOKE-1..4, LEARN-1..5)

## Exécution

```bash
# Tout lancer
python3 -m pytest tests/ -v

# Une catégorie
python3 -m pytest tests/test_eventbus.py -v
python3 -m pytest tests/test_polis_cli.py -v

# Avec couverture
python3 -m coverage run -m pytest tests/ -v
python3 -m coverage report --fail-under=70
```

## Ajouter un test

1. Identifier la catégorie (structure / convention / config / module / CLI)
2. Créer ou compléter le fichier `tests/test_*.py` correspondant
3. Utiliser les fixtures partagées de `tests/conftest.py` (`root`,
  `config_example`, `workspaces`)
4. Pour les tests runtime, créer un fixture `tmp_path` ou `mock_openclaw`
5. Vérifier : `python3 -m pytest tests/test_votre_fichier.py -v`
