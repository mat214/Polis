# Changelog — OpenClaw

Ce fichier retrace l'historique des modifications du dépôt, reconstruit à partir des commits Git.

---

## [2026-05-08] — Première mise en production : déploiement réel, audits et corrections

### Première mise en production réelle de l'instance OpenClaw Polis.
Cette session a couvert le déploiement effectif sur VPS, les corrections nécessaires, et la documentation des apprentissages.

### Ajouté
- **`scripts/talk`** : utilitaire conversationnel pour ouvrir une session interactive avec n'importe quel agent OpenClaw depuis le terminal. Supporte la recherche floue des noms d'agents (accents, tirets). Usage : `talk bâtisseur`, `talk defenseur`, `talk` (intendant par défaut).
- **`.gitignore`** : règle `*.egg-info/` pour exclure les artefacts de build setuptools.

### Corrigé
- **`polis/setup.py`** : import corrigé de `setuptools` (`from setuptools import find_packages, setup`) avec `packages=find_packages()` pour inclure automatiquement le package `polis` et ses sous-modules.
- **`pyproject.toml`** : `build-backend` corrigé de `setuptools.backends._legacy:_Backend` (inexistant) vers `setuptools.build_meta` (officiel).

### Apprentissages (déploiement réel)
- **Profil d'outils** : le profil `messaging` est trop restrictif pour un usage réel. Les agents ont besoin des groupes `fs`, `runtime`, `sessions`, `exec`. Passage en `coding` avec `tools.allow` explicite.
- **Exécution shell** : la clé `sudo` dans `tools.allow` n'existe pas. L'accès root passe par `exec.host: "gateway"` avec `security: "full"` et `sudo` configuré via sudoers (`NOPASSWD`).
- **Parsing des noms d'agents** : les accents (bâtisseur, défenseur) causent des erreurs silencieuses en CLI. Le script `talk` compense par une normalisation Unicode.
- **Skills lazy** : les skills OpenClaw sont chargés au premier appel d'un agent, pas au démarrage du gateway. `shared-notion-openclaw` nécessite `NOTION_DB_OPENCLAW_ID` renseigné dans `.env`.
- **Cron** : les jobs cron ne se définissent pas dans `openclaw.json` mais via la CLI `openclaw cron add`. Deux jobs créés : brief-matin (07:30) et brief-soir (19:00).
- **Transport des tokens** : le push Git nécessite un PAT classique (les fine-grained PAT nécessitent une autorisation explicite du dépôt).

---

## [2026-05-07] — Nettoyage tests et synchronisation documentation

### Corrigé
- **Tests** : 11 tests en échec réparés (115 passants, 0 échec). Causes :
 - Article 47bis déplacé hors ordre numérique dans la constitution (entre 47 et 48 au lieu d'après 49ter)
 - Skills anarchiste obsolètes dans les tests (`anarchiste-observation` → `motion`, `probe`, `bilan`)
 - Tests de validation croisée mémoire obsolètes (leviathan n'est plus le gatekeeper, `pending_reviews` remplacé par `learning_proposals`)
 - Référence à `revendications/` remplacée par `tracts/` + `motions/`
- **`polis/polis.py`** : `cmd_check_constitution()` — l'algorithme de vérification ignorait les articles suffixés (bis/ter)

### Modifié
- **`skills/shared-interagent/SKILL.md`** : structure `revendications/` → `tracts/` + `motions/`
- **`DESCRIPTION.md`** : descriptions des préfixes anarchiste mises à jour
- **`README.md`** : nombre d'articles (77), description anarchiste (contestation, motion, mise à l'épreuve)

---

## [2026-05-07] — Robustification : event bus, instance state, kill switch, smoke test, validation croisée

### Ajouté
- **Bus d'événements SQLite** (`polis/eventbus.py`) : module Python avec table `events`, opérations `post_event`, `get_events`, `ack_event`, `purge`. Règles EVENT-1 (atomicité), EVENT-2 (auto-nettoyage 7j), EVENT-3 (intégrité des sources).
- **État global de l'instance** (`instance_state.json`) : fichier centralisé dans `~/.openclaw/shared/`. Chaque agent écrit son propre statut. Si `overall_status == critical`, seules les actions READ sont autorisées. Règles INST-1 à INST-4.
- **shared-smoketest** : nouveau skill partagé définissant le protocole de vérification post-démarrage et heartbeat. Vérifications obligatoires, format `SMOKE_RESULT`, décision continue/degraded/block. Règles SMOKE-1 à SMOKE-4.
- **Kill Switch** : mécanisme d'arrêt d'urgence via `~/.openclaw/KILL`. Instructions `stop`, `freeze`, `rollback`. Règles KILL-1 (non-contournable), KILL-2 (pas d'auto-déclenchement), KILL-3 (persistance).
- **Validation croisée mémoire** : étape `VALIDATION CROISÉE` ajoutée au cycle d'apprentissage. leviathan valide les propositions des autres agents via `leviathan-status.json` → `pending_reviews`. Règle LEARN-5.
- **CLI Polis** : nouvelles commandes `eventbus` (status/list/purge), `kill` (status/set/clear), `smoke` (run/result), `state status`, `check degraded`, `test run`.

### Modifié
- **skills/shared-interagent/SKILL.md** : ajout des sections Bus d'événements, État global de l'instance, mise à jour de la Structure et des Niveaux.
- **skills/shared-learning/SKILL.md** : cycle étendu avec VALIDATION CROISÉE, règle LEARN-5, mention de leviathan et pending_reviews.
- **skills/shared-guardrail/SKILL.md** : ajout du § Kill Switch et du déclenchement de smoke test post-blocage.
- **workspaces/leviathan/AGENTS.md** : 6e pilier — validation croisée mémoire.
- **DESCRIPTION.md** : documentation des 5 nouvelles conventions dans les skills partagés.
- **tests/** : 4 nouveaux fichiers de test (test_eventbus.py, test_smoketest.py, test_guardrail.py, test_learning.py) + extension de test_interagent.py.

---

## [2026-05-06] — Audit et mise en conformité

### Corrigé
- **openclaw.json.example** : Bug critique — les listes `skills` de guardian et sys remplaçaient les `defaults`, privant ces agents de 5 skills essentiels (`shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`). Ajout des skills manquants dans chaque liste.
- **DESCRIPTION.md** : Suppression d'un bloc de configuration obsolète (format pré-migration) qui ne correspondait plus au schéma officiel OpenClaw.
- **Arbre de déploiement DESCRIPTION.md** : Ajout de `shared-interagent` et `shared-learning` dans l'arbre `~/.openclaw/skills/`.

### Ajouté
- **validate.sh** : ShellCheck étendu à `install.sh` (ne vérifiait que lui-même auparavant).

### Modifié
- **Fichiers workspace** : Traduction complète en français des 17 fichiers AGENTS.md, SOUL.md, IDENTITY.md, USER.md, TOOLS.md, HEARTBEAT.md et MEMORY.md (intendant, défenseur, bâtisseur).
- **README.md** : Retrait de la mention CodeQL Analysis (workflow supprimé), retrait référence ROADMAP.md.
- **PRODUCTION_READY_CHECKLIST.md** : Remplacement ROADMAP.md par DESCRIPTION.md dans la checklist.
- **DESCRIPTION.md** : Mise à jour de l'exemple de configuration JSON5 (synchronisé avec openclaw.json.example).

### Supprimé
- **ROADMAP.md** : Faisait doublon avec DESCRIPTION.md (suivi d'avancement intégré dans les chantiers du CHANGELOG).

---

## [2026-05-06] — Chantier 7b : Mise en production professionnelle

### Corrigé
- **scripts/validate.sh** : Bug critique — pipeline `find | while read` créait un subshell, les erreurs étaient silencieusement ignorées depuis l'origine (le script rapportait toujours 0). Remplacé par substitution de processus `while ... done < <(find ...)`.

### Ajouté
- **validate.sh** : 5 nouvelles catégories de vérification (ShellCheck, JSON5 brace balance, scan secrets, variables config→.env.example, cross-réfs doc, fraîcheur CHANGELOG, couverture .gitignore) — 10 catégories au total
- **Makefile** : `make validate`, `make install`, `make lint`, `make help`
- **scripts/install.sh** : Déploiement automatisé vers `~/.openclaw/` avec option `--dry-run`, ne jamais écraser les fichiers existants
- **.github/workflows/security.yml** : Workflow Gitleaks (scan de secrets) + CodeQL Analysis
- **.gitleaks.toml** : Allowlist de faux positifs (variables `${VAR}`, exemples docs)
- **PRODUCTION_READY_CHECKLIST.md** : 40 critères répartis en 5 domaines (architecture, tests, CI/CD, sécurité, documentation)

### Modifié
- **.github/workflows/validate.yml** : Ajout ShellCheck, jq, job Makefile parallèle
- **README.md** : Badges CI, installation en 3 commandes via Makefile, documentation des workflows GitHub Actions

---

## [2026-05-06] — Tâches planifiées (Cron)

### Ajouté
- **openclaw.json.example** : Section `cron` (enabled, maxConcurrentRuns, retry, sessionRetention, runLog)
- **DESCRIPTION.md** : Section « Tâches planifiées (Cron) » — 11 jobs documentés avec expressions cron, modes de session, timeouts et commandes CLI
- Tables des tâches planifiées des 3 agents : ajout colonnes Cron et Session
- **README.md** : Section « Tâches planifiées (Cron) » avec commandes d'initialisation
- **description.md → DESCRIPTION.md** : Renommage en majuscules

---

## [2026-05-06] — Post-migration et documentation

### Modifié
- **README.md** : Réécriture complète alignée sur architecture officielle (commit `5c06edb`)
- **description.md** : Mise à jour post-migration (commit `0cc4117`)

---

## [2026-05-06] — Chantier 6 : CI/CD et validation automatisée

### Ajouté
- `scripts/validate.sh` : pipeline de validation (frontmatter, noms uniques, mapping config→skills, cohérence gouvernance)
- `.github/workflows/validate.yml` : GitHub Actions sur push et PR
- Détection de dérive entre workspaces (N1/N2/N3 dans les 3 AGENTS.md)

### Corrigé
- Pas de duplicats de noms de skills, pas de champs interdits dans les frontmatter

---

## [2026-05-06] — Chantier 5 : Communication inter-agents et apprentissage système

### Ajouté
- `shared-interagent` : coordination entre agents via `~/.openclaw/shared/` (health.json, tasks/)
- `shared-learning` : cycle OBSERVATION→VALIDATION→MÉMOIRE étendu à guardian et sys
- Fichiers `MEMORY.md` pour guardian et sys
- Révision mémoire intégrée aux heartbeats hebdomadaires

---

## [2026-05-06] — Chantier 4 : Multi-agents et routage (bindings)

### Ajouté
- Agent `bâtisseur` avec 7 skills (bat-bootstrap, bat-audit, bat-packages, bat-scripts, bat-services, bat-capabilities, bat-rollback)
- Routage déterministe via bindings dans openclaw.json
- Skills partagés `shared-state` et `shared-guardrail` (déplacés de Chantier 3)

### Modifié
- Migration complète vers architecture officielle OpenClaw (3 workspaces, bindings, isolation sessions)

### Supprimé
- `CLAUDE.md`, `CONSTITUTION.md`, `agents/` (absorbés dans workspaces/)
- Fichiers `agent.md` (remplacés par AGENTS.md + SOUL.md + IDENTITY.md)

---

## [2026-05-06] — Chantier 3 : Guardrails et couche de sécurité active

### Ajouté
- Classification des actions (READ/WRITE/WRITE_SENSITIVE/IRREVERSIBLE)
- Input sanitization, détection prompt injection, troncature 2000 tokens, isolation sémantique
- Rate limiting par niveau d'action, dry-run mode, Human Gate pour IRREVERSIBLE
- Log immutable de la Guardrail Layer
- Règles GUARD-1 à GUARD-6

---

## [2026-05-05] — Chantier 2 : Propriété d'état et réhydratation

### Ajouté
- SessionManager : init, load, upsert, archive, expire
- Stockage SQLite (actif) + JSON (archives)
- Idempotence des étapes via idempotency_key
- Règles STATE-1 à STATE-5
- Intégration dans la boucle ReAct
- Suivi d'avancement des chantiers intégré dans DESCRIPTION.md

### Sécurité
- SECURITY.md : Prompt injection defense, loop detection (3 répétitions → stop), dry-run L3
- Runbooks d'urgence : secret exposé, bot Telegram silencieux, service mail indisponible, session state corrompu, rotation token Telegram

---

## [2026-05-05] — Chantier 1 : Architecture documentaire (phase finale)

### Ajouté
- **CHANGELOG.md** : Création du fichier (commit `7aa87b7`)
- **CONSTITUTION.md** : Telegram canal unique, accès Notion par agent formalisé (lecture seule OPENCLAW pour PA)
- **agent.md** : Correction et enrichissement de défenseur et intendant
- **.gitignore** : Secrets, memory, logs, fichiers OS et éditeurs
- **openclaw.json.example** : Synchronisation skills (def-backup/bootstrap/update, int-tasks)
- **.env.example** : Anonymisation adresses réelles, ajout BACKUP_DEST, TELEGRAM_WEBHOOK_URL
- **int-telegram/SKILL.md** : TELEGRAM_WEBHOOK_URL optionnel, polling par défaut

---

## [2026-05-05] — Chantier 1 : Architecture documentaire (phase construction)

### Ajouté
- Socle commun : `shared-governance`, `shared-reporting` avec niveaux N1/N2/N3, formats de sortie ALERT/DIAGNOSTIC/ACTION_PLAN/REPORT
- Agent `défenseur` : 6 skills ops (audit CIS Level 1 + ANSSI 42 mesures, défense NIST SP 800-61, backup, maintenance, remediation, update)
- Agent `intendant` : 7 skills (mail, calendar, contacts, telegram, daily-brief, memory, tasks)
- Connectors : Posteo IMAP/SMTP/CalDAV/CardDAV, Telegram Bot API, Notion API v1
- Boites mail : Posteo (PERSO) + ORG-1 (SYNDICAL) + ORG-2 (EWS Exchange)
- Contextes PERSO/SYNDICAL avec détection de convergences
- Tags mémoire : [PERSO], [SYNDICAL], [COMMUN], [INSTANCE→SYSTÈME]
- Cycle d'apprentissage : OBSERVATION→HYPOTHÈSE→VALIDATION→MÉMOIRE→AUTOMATISATION
- Ajout `int-notion`, `shared-notion-openclaw`

---

## [2026-05-05] — Fondation

### Ajouté
- Structure initiale du dépôt (git init, commit `85e71f5`)
- Architecture 3 couches (Connector / Gateway / Agent Runtime)
- Boucle ReAct, skills modulaires, mémoire gouvernée
- Définition des 3 agents : intendant, défenseur, bâtisseur
- Variables d'environnement, configuration de base, philosophie du projet

---

> Reconstruit depuis l'historique Git du dépôt `Polis`.
> Dernière mise à jour : 2026-05-06
