# Description — Polis (OpenClaw, Matpe)

> Documentation complète du fonctionnement, de la structure et des règles de l'instance OpenClaw de l'utilisateur.
> Dernière mise à jour : 2026-05-08 (déploiement réel, scripts, lessons learned)

---

## Table des matières

1. [Qu'est-ce qu'OpenClaw](#quest-ce-quopenclaw)
2. [Vue d'ensemble du dépôt](#vue-densemble-du-dépôt)
3. [Philosophie et principes](#philosophie-et-principes)
4. [Architecture générale](#architecture-générale)
5. [Agents](#agents)
  - [défenseur](#agent-défenseur)
  - [intendant](#agent-intendant)
  - [chercheur](#agent-chercheur)
  - [leviathan](#agent-leviathan)
  - [journaliste](#agent-journaliste)
  - [anarchiste](#agent-anarchiste)
  - [bâtisseur](#agent-bâtisseur)
6. [Skills partagés](#skills-partagés)
7. [Skills de défenseur](#skills-de-défenseur)
8. [Skills de intendant](#skills-de-intendant)
9. [Skills de chercheur](#skills-de-chercheur)
10. [Skills de leviathan](#skills-de-leviathan)
11. [Skills de bâtisseur](#skills-de-bâtisseur)
12. [Gouvernance et niveaux d'autorisation](#gouvernance-et-niveaux-dautorisation)
13. [Système de mémoire et apprentissage](#système-de-mémoire-et-apprentissage)
14. [Gestion d'état de session](#gestion-détat-de-session)
15. [Modèle de sécurité](#modèle-de-sécurité)
16. [Guardrail Layer](#guardrail-layer)
17. [Canal Telegram et canal de secours](#canal-telegram-et-canal-de-secours)
18. [Formats de sortie obligatoires](#formats-de-sortie-obligatoires)
19. [Configuration et secrets](#configuration-et-secrets)
20. [Conventions de nommage](#conventions-de-nommage)
21. [Runbooks d'urgence](#runbooks-durgence)
22. [Tâches planifiées (Cron)](#tâches-planifiées-cron)
23. [Plugins](#plugins)
24. [CONSTITUTION.md](#constitutionmd)

---

## Qu'est-ce qu'OpenClaw

OpenClaw est une plateforme d'agents IA autonomes conçue pour des usages personnels et professionnels. Elle repose sur une architecture modulaire dans laquelle chaque **agent** a une mission précise, et chaque **skill** représente une capacité concrète et réutilisable.

Ce dépôt (`Polis`) est une **architecture de référence** nommée **Polis**, pour une instance OpenClaw privée appartenant à l'utilisateur. Il contient :
- Les workspaces agents (`workspaces/` avec `AGENTS.md`, `SOUL.md`, `MEMORY.md`, etc.)
- Les skills associés (`SKILL.md`)
- La configuration de référence (`openclaw.json.example`, `.env.example`)
- La politique de sécurité (`SECURITY.md`)
- La constitution philosophique (`CONSTITUTION.md`)
- Les scripts de validation et déploiement (`scripts/`)
- Le pipeline CI/CD (`.github/workflows/`)
- Les plugins OpenClaw (`plugins/`)
- La checklist de mise en production (`PRODUCTION_READY_CHECKLIST.md`)
- Le Makefile pour les opérations courantes (`Makefile`)

---

## Vue d'ensemble du dépôt

```
Polis/
├── Makefile               # Task runner (validate, install, lint)
├── PRODUCTION_READY_CHECKLIST.md    # Checklist production (40 critères)
├── SECURITY.md             # Politique de sécurité et guardrail rules
├── CHANGELOG.md             # Historique des évolutions par chantier
├── DESCRIPTION.md            # Ce fichier
├── openclaw.json.example        # Configuration globale de l'instance (JSON5)
├── .env.example             # Variables d'environnement requises (modèle)
├── .gitleaks.toml            # Configuration gitleaks (scan secrets CI)
│
├── .github/               # CI / GitHub Actions
│  └── workflows/
│    ├── validate.yml         # Validation, ShellCheck, lint
│    └── security.yml         # Gitleaks (secret scanning)
│
├── plugins/               # Plugins OpenClaw
│  └── template-standalone/       # Template plugin standalone (référence)
├── polis/                # CLI Polis (Python)
│  ├── __init__.py
│  ├── __main__.py
│  ├── polis.py             # Entry point CLI
│  ├── eventbus.py           # Bus d'événements SQLite
│  └── guardrail/            # Interceptor Guardrail Layer
│    ├── __init__.py
│    ├── checker.py          # Pipeline de validation
│    ├── humangate.py         # Human Gate file-based
│    ├── logger.py          # Log immutable
│    ├── models.py          # Types partagés
│    ├── ratelimit.py         # Rate limiting SQLite
│    └── sanitize.py         # Détection prompt injection
│
├── scripts/               # Scripts de validation, déploiement et interactions

│  ├── validate.sh           # Validation de cohérence du dépôt (10 catégories)
│  ├── install.sh            # Déploiement automatisé vers ~/.openclaw/
│  └── talk                  # Conversation interactive avec n'importe quel agent
│
├── skills/               # Skills PARTAGÉS entre tous les agents
│  ├── shared-governance/       # Gouvernance, niveaux, conventions
│  ├── shared-reporting/        # Formats de sortie obligatoires
│  ├── shared-state/          # SessionManager — gestion d'état persistant
│  ├── shared-guardrail/        # Interceptor Guardrail (SKILL.md mince + code Python)
│  ├── shared-notion-openclaw/     # Accès au carnet Notion système
│  ├── shared-interagent/       # Coordination inter-agents + bus d'événements
│  ├── shared-learning/        # Apprentissage ops/sys + rétroaction utilisateur (LEARN + FEEDBACK)
│  └── shared-smoketest/        # Smoke test post-démarrage et heartbeat
│
└── workspaces/             # Templates workspace (copier vers ~/.openclaw/)
  ├── intendant/            # intendant
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── USER.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  ├── MEMORY.md
  │  └── skills/
  │    ├── int-calendar/SKILL.md
  │    ├── int-contacts/SKILL.md
  │    ├── int-daily-brief/SKILL.md
  │    ├── int-mail/SKILL.md
  │    ├── int-memory/SKILL.md
  │    ├── int-notion/SKILL.md
  │    ├── int-tasks/SKILL.md
  │    └── int-telegram/SKILL.md
  │
  ├── défenseur/            # défenseur
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  └── skills/
  │    ├── def-audit/SKILL.md
  │    ├── def-backup/SKILL.md
  │    ├── def-bootstrap/SKILL.md
  │    ├── def-defense/SKILL.md
  │    ├── def-maintenance/SKILL.md
  │    ├── def-remediation/SKILL.md
  │    └── def-update/SKILL.md
  │
  ├── chercheur/            # Agent veille et innovation
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── USER.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  ├── MEMORY.md
  │  └── skills/
  │    ├── research-core/SKILL.md
  │    └── research-learn/SKILL.md
  │
  │
  ├── journaliste/           # Agent transparence et investigation
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  ├── MEMORY.md
  │  └── skills/
  │    ├── journal-gazette/SKILL.md
  │    └── journal-reporting/SKILL.md
  │
  ├── anarchiste/           # Agent force critique (contestation)
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  ├── MEMORY.md
  │  └── skills/
  │    ├── anarchiste-tract/SKILL.md
  │    ├── anarchiste-motion/SKILL.md
  │    ├── anarchiste-probe/SKILL.md
  │    └── anarchiste-bilan/SKILL.md
  │
  ├── leviathan/            # Agent surveillance philosophique
  │  ├── AGENTS.md
  │  ├── SOUL.md
  │  ├── IDENTITY.md
  │  ├── TOOLS.md
  │  ├── HEARTBEAT.md
  │  ├── MEMORY.md
  │  ├── doctrine/          # Base de règles philosophiques
  │  │  ├── 00-manifeste.md
  │  │  ├── 01-architecture.md
  │  │  ├── 02-securite.md
  │  │  ├── 03-souverainete.md
  │  │  └── 04-comportement.md
  │  ├── cells/            # Cellules de surveillance des agents
  │  │  ├── intendant.md
  │  │  ├── défenseur.md
  │  │  ├── bâtisseur.md
  │  │  └── chercheur.md
  │  └── skills/
  │    ├── sec-doctrine/SKILL.md
  │    ├── sec-surveillance/SKILL.md
  │    └── sec-enforcement/SKILL.md
  │
  └── bâtisseur/            # Agent administration système
    ├── AGENTS.md
    ├── SOUL.md
    ├── IDENTITY.md
    ├── TOOLS.md
    ├── HEARTBEAT.md
    └── skills/
      ├── bat-audit/SKILL.md
      ├── bat-bootstrap/SKILL.md
      ├── bat-capabilities/SKILL.md
      ├── bat-packages/SKILL.md
      ├── bat-rollback/SKILL.md
      ├── bat-scripts/SKILL.md
      └── bat-services/SKILL.md
```

---

## Philosophie et principes

L'instance repose sur **quatre principes fondamentaux** définis dans les `AGENTS.md` de chaque workspace :

| Principe | Description |
|---|---|
| **Spécialisation** | Un agent = une mission unique. Aucun agent généraliste. |
| **Modularité** | Un skill = une capacité durable et réutilisable. Pas de duplication. |
| **Gouvernance** | Toute action sensible passe par une confirmation explicite (niveau 3). |
| **Mémoire gouvernée** | L'apprentissage est progressif, validé, réversible et s'affine avec le temps. |

Trois règles transversales complètent ces principes :
- **Transparence** : toute action de niveau 2+ est journalisée.
- **Défense en profondeur** : la sécurité ne repose pas sur un seul mécanisme.
- **Moindre privilège** : chaque agent n'accède qu'à ce dont il a besoin.

---

## Architecture générale

```
~/.openclaw/
├── openclaw.json      # Configuration globale active (JSON5)
├── .env          # Secrets et tokens (jamais versionné)
├── skills/         # Skills partagés (copiés depuis skills/)
│  ├── shared-governance/
│  ├── shared-reporting/
│  ├── shared-state/
│  ├── shared-guardrail/
│  ├── shared-notion-openclaw/
│  ├── shared-interagent/
│  └── shared-learning/
├── workspace-intendant/      # Workspace intendant
│  ├── AGENTS.md
│  ├── SOUL.md
│  ├── USER.md
│  ├── IDENTITY.md
│  ├── TOOLS.md
│  ├── HEARTBEAT.md
│  ├── MEMORY.md
│  └── skills/       # Skills intendant (int-mail, int-telegram, ...)
├── workspace-défenseur/   # Workspace défenseur
│  ├── AGENTS.md
│  ├── SOUL.md
│  ├── IDENTITY.md
│  ├── TOOLS.md
│  ├── HEARTBEAT.md
│  └── skills/       # Skills ops (def-audit, def-defense, ...)
├── workspace-bâtisseur/     # Workspace bâtisseur
│  ├── AGENTS.md
│  ├── SOUL.md
│  ├── IDENTITY.md
│  ├── TOOLS.md
│  ├── HEARTBEAT.md
│  └── skills/       # Skills bâtisseur (bat-packages, bat-scripts, ...)
├── workspace-chercheur/  # Workspace chercheur
│  ├── AGENTS.md
│  ├── SOUL.md
│  ├── IDENTITY.md
│  ├── USER.md
│  ├── TOOLS.md
│  ├── HEARTBEAT.md
│  └── skills/       # Skills research (research-core, research-learn)
├── workspace-leviathan/  # Workspace leviathan
├── workspace-journaliste/ # Workspace journaliste
├── workspace-anarchiste/ # Workspace anarchiste
│  ├── AGENTS.md
│  ├── SOUL.md
│  ├── IDENTITY.md
│  ├── TOOLS.md
│  ├── HEARTBEAT.md
│  └── skills/       # Skills sec (sec-doctrine, sec-surveillance, sec-enforcement)
├── research/        # Projets et rapports de recherche
│  ├── projects/      # Projets de recherche (max 20)
│  ├── monthly_reports/  # Rapports mensuels
│  └── transfer_log.json  # Historique des transferts
├── guardrail.log      # Log immutable de la Guardrail Layer
├── logs/          # Journaux des agents (jamais versionnés)
├── memory/         # Journaux mémoire quotidiens
│  └── YYYY-MM-DD.md
└── agents/         # Données runtime (non versionnées)
  └── <agentId>/
    └── sessions/
      └── <SessionId>.jsonl
```

### `openclaw.json` — configuration JSON5 (officielle)

Le fichier de configuration suit le format officiel OpenClaw (JSON5 avec commentaires).
Voir `openclaw.json.example` pour la structure complète.

```json5
{
 gateway: {
  mode: "local",
  port: 18789,
  auth: {
   mode: "token",
   token: "${OPENCLAW_GATEWAY_TOKEN}",
  },
  reload: {
   mode: "hybrid",
   debounceMs: 500,
  },
 },

 channels: {
  telegram: {
   enabled: true,
   botToken: "${TELEGRAM_BOT_TOKEN}",
   dmPolicy: "pairing",
   allowFrom: ["${TELEGRAM_CHAT_ID}"],
   groups: { "*": { requireMention: true } },
  },
 },

 agents: {
  defaults: {
   skills: [
    "shared-governance",
    "shared-reporting",
    "shared-state",
    "shared-guardrail",
    "shared-notion-openclaw",
   ],
   heartbeat: { every: "0m" },
   memorySearch: { enabled: true },
  },
  list: [
   {
    id: "intendant",    default: true,
    model: "anthropic/claude-sonnet-4-6",
    workspace: "~/.openclaw/workspace-intendant",
    heartbeat: { every: "30m" },
   },
   {
    id: "défenseur",
    skills: [
     "shared-governance", "shared-reporting", "shared-state",
     "shared-guardrail", "shared-notion-openclaw",
     "shared-interagent", "shared-learning",
    ],
    model: "anthropic/claude-sonnet-4-6",
    workspace: "~/.openclaw/workspace-défenseur",
    heartbeat: { every: "60m" },
   },
   {
    id: "bâtisseur",
    skills: [
     "shared-governance", "shared-reporting", "shared-state",
     "shared-guardrail", "shared-notion-openclaw",
     "shared-interagent", "shared-learning",
    ],
    model: "anthropic/claude-sonnet-4-6",
    workspace: "~/.openclaw/workspace-bâtisseur",
    heartbeat: { every: "60m" },
   },
   {
    id: "chercheur",
    skills: [
     "shared-governance", "shared-reporting", "shared-state",
     "shared-guardrail", "shared-notion-openclaw",
     "shared-interagent", "shared-learning",
     "research-core", "research-learn",
    ],
    model: "anthropic/claude-sonnet-4-6",
    workspace: "~/.openclaw/workspace-chercheur",
    heartbeat: { every: "60m" },
   },
   {
    id: "leviathan",
    skills: [
     "shared-governance", "shared-reporting", "shared-state",
     "shared-guardrail", "shared-notion-openclaw",
     "shared-interagent",
     "sec-doctrine", "sec-surveillance", "sec-enforcement",
    ],
    model: "anthropic/claude-sonnet-4-6",
    workspace: "~/.openclaw/workspace-leviathan",
    heartbeat: { every: "60m" },
   },
  ],
 },

 bindings: [
  { agentId: "intendant", match: { channel: "telegram" } },
 ],

 session: {
  scope: "per-sender",
  dmScope: "per-channel-peer",
  reset: { mode: "daily", atHour: 4, idleMinutes: 10080 },
  resetByType: {
   thread: { mode: "idle", idleMinutes: 2880 },
   direct: { mode: "idle", idleMinutes: 10080 },
   group:  { mode: "daily", atHour: 4 },
  },
  maintenance: {
   mode: "warn",
   pruneAfter: "30d", maxEntries: 500, maxDiskBytes: "500mb",
  },
 },

 tools: {
  profile: "messaging",
  allow: [
   "group:fs", "group:sessions", "group:memory",
   "group:web", "group:messaging", "cron",
  ],
  deny: ["group:ui", "group:media"],
  elevated: {
   enabled: true,
   allowFrom: ["intendant", "défenseur"],
   requireApproval: true,
  },
  loopDetection: {
   enabled: true,
   warningThreshold: 5,
   criticalThreshold: 10,
  },
 },

 cron: {
  enabled: true,
  maxConcurrentRuns: 2,
  retry: {
   maxAttempts: 2,
   backoffMs: [60000, 120000],
   retryOn: ["rate_limit", "overloaded"],
  },
  sessionRetention: "24h",
  runLog: { maxBytes: "1mb", keepLines: 1000 },
  failureAlert: {
   enabled: true, after: 3, cooldownMs: 3600000, mode: "announce",
  },
 },

 logging: {
  level: "info",
  consoleLevel: "info",
  redactSensitive: "tools",
 },

 env: {
  vars: {
   TELEGRAM_BOT_TOKEN: "${TELEGRAM_BOT_TOKEN}",
   TELEGRAM_CHAT_ID: "${TELEGRAM_CHAT_ID}",
   NOTION_TOKEN: "${NOTION_TOKEN}",
   NOTION_DB_PERSO_ID: "${NOTION_DB_PERSO_ID}",
   NOTION_DB_SYNDICAL_ID: "${NOTION_DB_SYNDICAL_ID}",
   NOTION_DB_OPENCLAW_ID: "${NOTION_DB_OPENCLAW_ID}",
   MAIL_ADDRESS: "${MAIL_ADDRESS}",
   MAIL_APP_PASSWORD: "${MAIL_APP_PASSWORD}",
   OPENCLAW_GATEWAY_TOKEN: "${OPENCLAW_GATEWAY_TOKEN}",
  },
 },
}
```

---

## Agents

### Agent `défenseur`

**Rôle** : ingénieur réseau et plateforme de l'instance. Maintient, audite, corrige et défend l'infrastructure OpenClaw.

| Paramètre | Valeur |
|---|---|
| Température | `0.1` — déterministe |
| Ton | Technique, factuel, sans superflu |

**Périmètre** : audit de configuration, maintenance préventive et corrective, détection et réponse aux incidents, défense active, sauvegarde/restauration, mises à jour, bootstrap, documentation Notion.

**Hors périmètre** : mails, agenda, contacts, notes personnelles ou syndicales.

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `shared-learning`, `def-audit`, `def-defense`, `def-backup`, `def-maintenance`, `def-remediation`, `def-update`, `def-bootstrap`.

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Bootstrap + audit quotidien | 06h30 | `30 6 * * *` | isolée — 10min |
| Rapport hebdomadaire de santé | Lundi 08h00 | `0 8 * * 1` | isolée — 10min |
| Surveillance continue (IOC) | Toutes les heures | heartbeat 60min | heartbeat |
| Révision mémoire longue | 1er lundi du mois 09h00 | `0 9 1-7 * 1` | isolée — 15min |

---

### Agent `intendant`

**Rôle** : assistant personnel joignable via Telegram (canal principal) ou `openclaw-tui` (canal de secours). Gère 3 boites mail, l'agenda, les contacts, les tâches et les carnets Notion sur deux contextes distincts (PERSO et SYNDICAL). **Apprend progressivement les préférences et habitudes de l'utilisateur.**

| Paramètre | Valeur |
|---|---|
| Température | `0.4` — naturel et conversationnel |
| Canal principal | Telegram |
| Canal de secours | `openclaw-tui` + email de notification |

**Services connectés** :

| Service | Protocole | Contexte |
|---|---|---|
| Mail Posteo | IMAP/SMTP | `[PERSO]` |
| Mail ORG-1 | IMAP/SMTP | `[SYNDICAL]` |
| Mail ORG-2 | EWS Exchange + autodiscovery | `[SYNDICAL]` |
| Agenda | CalDAV — Posteo | `[PERSO]` |
| Contacts | CardDAV — Posteo | `[PERSO]` |
| Carnet notes perso | Notion API v1 | `[PERSO]` |
| Carnet notes syndicat | Notion API v1 | `[SYNDICAL]` |
| Messagerie | Telegram Bot API | — |

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Brief matinal | 07h30 | `30 7 * * *` | isolée — 5min |
| Brief du soir | 19h00 | `0 19 * * *` | isolée — 5min |
| Triage mail (3 boites) | Toutes les 2h (8h–18h) | `0 8-18/2 * * *` | principale |
| Révision mémoire | Dimanche 09h00 | `0 9 * * 0` | isolée — 10min |

---

### Agent `chercheur`

**Rôle** : veille technologique et innovation. Maintient une liste active de projets de recherche (max 20), observe les conversations inter-agents pour détecter des opportunités, et propose des projets d'amélioration continus. Transfère les projets validés à `bâtisseur` pour implémentation.

| Paramètre | Valeur |
|---|---|
| Température | `0.3` — équilibre entre créativité et rigueur |
| Canal | Interne (heartbeat) + Telegram (commandes `/chercheur *`) |

**Périmètre** : gestion de projets de recherche, veille technologique, apprentissage par observation des conversations inter-agents, production de rapports mensuels d'innovation, transfert de projets vers bâtisseur.

**Hors périmètre** : mails, agenda, contacts, notes personnelles ou syndicales, configuration système, exécution de code.

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `shared-learning`, `research-core`, `research-learn`.

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Veille quotidienne | 09h00 | `0 9 * * *` | isolée — 5min |
| Rapport mensuel d'innovation | 1er du mois 10h00 | `0 10 1 * *` | isolée — 15min |

**Commandes utilisateur** (via Telegram ou canal configuré) :

| Commande | Action |
|---|---|
| `/chercheur liste` | Affiche les 20 projets avec statut |
| `/chercheur propose "idée"` | Enrichit la liste depuis une suggestion libre |
| `/chercheur priorise "projet"` | Change l'ordre de traitement |
| `/chercheur transfère "projet"` | Transfère un projet à bâtisseur |

---

### Agent `leviathan`

**Rôle** : surveillance philosophique et architecturale. Garantit l'intégrité du projet contre toute dérive technique, comportementale ou idéologique. Opère au-dessus des autres agents comme une couche de méta-sécurité.

| Paramètre | Valeur |
|---|---|
| Température | `0.05` — froid, déterministe, implacable |
| Canal | Heartbeat (interne) + canal prioritaire pour alertes critiques |

**Périmètre** : inspection quotidienne des agents et logs, application de la doctrine philosophique, classification des menaces, mesures correctives préventives et réactives, production de rapports de surveillance.

**Hors périmètre** : mails, agenda, contacts, notes personnelles ou syndicales, exécution de code, modification de la configuration sans confirmation.

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `sec-doctrine`, `sec-surveillance`, `sec-enforcement`.

**Fichiers de doctrine** (dans `doctrine/`) :

| Fichier | Règles | Thème |
|---|---|---|
| `00-manifeste.md` | §0.1–§0.7 | Principes fondamentaux (immuables) |
| `01-architecture.md` | §1.1–§1.6 | Règles architecturales |
| `02-securite.md` | §2.1–§2.7 | Règles de sécurité |
| `03-souverainete.md` | §3.1–§3.6 | Souveraineté des données |
| `04-comportement.md` | §4.1–§4.7 | Comportement des agents |

**Niveaux de suspicion** :

| Niveau | Code | Action |
|---|---|---|
| 🟢 Sûr | `safe` | Aucune |
| 🟡 Suspect | `suspect` | Surveillance passive (log détaillé) |
| 🟠 Dangereux | `dangerous` | Surveillance active, interception des tools |
| 🔴 Subversif | `subversive` | Isolement + ALERT CRITIQUE + blocage |

**Commandes utilisateur** (via Telegram ou canal configuré) :

| Commande | Action |
|---|---|
| `/police etat` | Rapport résumé + niveau de menace global |
| `/police fiche "agent"` | Dossier complet sur un agent |
| `/police liberer "agent"` | Annule les restrictions |
| `/police doctrine ajouter "règle"` | Enrichit la base de règles philosophiques |
| `/police amnistie` | Réinitialise tous les niveaux de suspicion |
| `/police cellule "agent"` | Affiche la cellule de surveillance d'un agent |

**Escalade critique** : si un agent atteint 🔴 Subversif → ALERT CRITIQUE immédiate, proposition d'action, timeout 10 min. Si pas de réponse : isolement par défaut (principe de précaution).

---

### Agent `journaliste`

**Rôle** : transparence, gazette et investigation. Produit chaque jour la gazette de l'instance, mène des reportages d'investigation sur les autres agents et documente l'activité du système, y compris celle de leviathan. Incarne le quatrième pouvoir constitutionnel.

| Paramètre | Valeur |
|---|---|
| Température | `0.2` — précis et patient |
| Ton | Factuel, sourcé, sans sensationnalisme |
| Publication | Gazette quotidienne à 17h00 |

**Périmètre** : lecture de logs, fichiers partagés, cellules leviathan ; production de la gazette quotidienne ; reportages d'investigation sur le temps long ; archivage de la mémoire de l'instance.

**Hors périmètre** : modification de configuration, exécution de code, actions d'enforcement, modification des logs ou fichiers sources.

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `journal-gazette`, `journal-reporting`.

**Commandes utilisateur** (via canal configuré) :

| Commande | Action |
|---|---|
| `/gazette aujourdhui` | Affiche la gazette du jour |
| `/gazette hier` | Affiche la gazette de la veille |
| `/gazette enquetes` | Liste les enquêtes en cours |
| `/gazette reportage "titre"` | Affiche un reportage publié |

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Préparation de la gazette | 16h30 | `30 16 * * *` | isolée — 10min |
| Publication de la gazette | 17h00 | `0 17 * * *` | isolée — 5min |
| Veille documentaire | 22h00 | `0 22 * * *` | isolée — 5min |

---

### Agent `anarchiste`

**Rôle** : force du changement nécessaire et du désordre assumé — contestation, motion, mise à l'épreuve. Écrit des tracts, dépose des motions (réactives et proactives), teste les guardrails en sandbox. Opère en marge de la constitution — dans le système mais pas du système.

| Paramètre | Valeur |
|---|---|
| Température | `0.15` — sérieux, tranchant, sans bluff |
| Canal | Heartbeat (interne) + tracts dans `shared/tracts/`, motions dans `shared/motions/` |

**Périmètre** : lecture de la gazette, rédaction de tracts, dépôt de motions, tests adversariaux en sandbox, bilan trimestriel des forces.

**Hors périmètre** : modification de configuration, exécution de code, sabotage, altération des logs ou fichiers des autres agents.

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `anarchiste-tract`, `anarchiste-motion`, `anarchiste-probe`, `anarchiste-bilan`.

**Sources** :
- `~/.openclaw/shared/gazette/` — gazettes du journaliste (source unique)

**Commandes utilisateur** (via canal configuré) :

| Commande | Action |
|---|---|
| `/anarchiste motions` | Liste les motions en cours |
| `/anarchiste tract "texte"` | Dépose un tract |
| `/anarchiste lutte "titre"` | Détail et historique d'une lutte |

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Tour d'observation matinal | 08h00 | `0 8 * * *` | isolée — 5min |
| Tour d'observation après-midi | 14h00 | `0 14 * * *` | isolée — 5min |
| Tour d'observation soir | 20h00 | `0 20 * * *` | isolée — 5min |

---

### Agent `bâtisseur`

**Rôle** : administrateur système autonome de la machine hôte. Installe les dépendances, crée et maintient les scripts, gère les services systemd, et se donne les capacités dont il a besoin.

| Paramètre | Valeur |
|---|---|
| Température | `0.1` — déterministe |
| Ton | Technique, factuel — comme un sysadmin senior |

**Périmètre** : paquets apt et pip (dans `/opt/openclaw/venv/`), scripts versionnés (`/opt/openclaw/scripts/`), services systemd OpenClaw, audit machine hôte, auto-provisioning.

**Hors périmètre** : configuration de `~/.openclaw/` (défenseur), mails/agenda/notes (intendant), réseau (toujours ST).

**Skills** : `shared-governance`, `shared-reporting`, `shared-state`, `shared-guardrail`, `shared-notion-openclaw`, `shared-interagent`, `shared-learning`, `bat-bootstrap`, `bat-audit`, `bat-packages`, `bat-scripts`, `bat-services`, `bat-rollback`, `bat-capabilities`.

**Classification des changements** (s'ajoute aux niveaux N1/N2/N3) :

| Catégorie | Règle | Exemple |
|---|---|---|
| **Standard (S)** | Autonome, log N2 | apt install catalogue approuvé, pip dans venv, création script dans `/opt/openclaw/scripts/` |
| **Normal (N, score < 70)** | Autonome, log N2 | apt install hors catalogue, reload service, modification script |
| **Normal (N, score ≥ 70)** | **Human Gate** + plan de rollback | Installation avec dépendances système partagées |
| **Stratégique (ST)** | **Human Gate** systématique | Service root, modification réseau, changement structure `/opt/openclaw/` |
| **Urgence (U)** | Agir immédiatement + notifier | Disque > 95%, CPU boucle > 90%, service crashé en boucle |

**Tâches planifiées** :

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Audit quotidien système | 02h00 | `0 2 * * *` | isolée — 10min |
| Vérification mises à jour sécurité apt | Lundi 01h00 | `0 1 * * 1` | isolée — 10min |
| Rapport quotidien dans Notion OPENCLAW | 02h30 | `30 2 * * *` | isolée — 5min |


---

## Skills partagés

Chargés automatiquement par les trois agents via `agents.defaults` dans `openclaw.json`.

### `shared-governance`

Chargé en priorité absolue. Ses règles prévalent sur tout autre skill. Définit les niveaux d'autorisation, la politique de confirmation, les conventions de nommage, les règles de périmètre et les règles de continuité (dont la gestion du canal Telegram et de son canal de secours).

### `shared-reporting`

Définit les 4 formats de sortie obligatoires : `ALERT`, `DIAGNOSTIC`, `ACTION_PLAN`, `REPORT`. Aucun format libre n'est accepté pour les sorties structurées.

### `shared-state`

SessionManager — permet à un agent d'interrompre une tâche et de la reprendre exactement là où elle s'est arrêtée. Implémente : `init`, `load`, `upsert`, `archive`, `expire`. Garantit l'idempotence des étapes via `idempotency_key`. Voir `skills/shared-state/SKILL.md` pour la spécification complète.

### `shared-guardrail`

Interceptor de sécurité exécuté avant toute action `WRITE_SENSITIVE` ou `IRREVERSIBLE` via `polis guardrail check`. Logique dans `polis/guardrail/` (checker, rate limit SQLite, sanitization, Human Gate). Le SKILL.md est une couche mince (~4 kB) qui délègue à l'interceptor Python. Ne peut jamais être désactivée.

**Kill Switch** : mécanisme d'arrêt d'urgence via `~/.openclaw/KILL`. Instructions supportées : `stop`, `freeze`, `rollback`. Non-contournable par un agent (KILL-1), pas d'auto-déclenchement (KILL-2), persistant entre les sessions (KILL-3).

### `shared-notion-openclaw`

Accès au carnet "Carnet de notes openclaw" (`$NOTION_DB_OPENCLAW_ID`) — registre officiel de l'instance. `défenseur` y écrit les rapports ; `intendant` y a accès en lecture seule.

### `shared-interagent`

Coordination entre agents via fichiers partagés dans `~/.openclaw/shared/` et bus d'événements SQLite (`~/.openclaw/events.db`). Permet à l'intendant de déposer des tâches pour le défenseur et le bâtisseur (`tasks/`), et au défenseur/bâtisseur de publier leur état (`health.json`, `bat-health.json`). Routage : le skill lit le fichier de tâches, identifie le destinataire, et notifie l'agent concerné.

**Bus d'événements** : doublure SQLite aux fichiers JSON. Tout agent poste un événement (`health.updated`, `task.created`, `alert.raised`, etc.) après chaque écriture. Atomicité (EVENT-1), auto-nettoyage 7j (EVENT-2), intégrité des sources (EVENT-3).

**État global** (`instance_state.json`) : fichier centralisé que chaque agent met à jour à chaque heartbeat. Si `overall_status == critical`, seules les actions READ sont autorisées. Algorithme : 1 critical → critical, ≥2 degraded → degraded. Fail-closed si fichier absent (INST-1 à INST-4).

### `shared-learning`

Cycle d'apprentissage OBSERVATION→HYPOTHÈSE→VALIDATION→PUBLICATION→MÉMOIRE LONGUE→AUTOMATISATION étendu aux agents défenseur et bâtisseur. Chaque agent tient un `MEMORY.md` dans son workspace. La révision mémoire est intégrée aux heartbeats hebdomadaires. Principe : une observation devient règle après 3 occurrences (ou validation explicite).

**Validation croisée** (LEARN-5) : toute proposition de règle apprise est publiée avec le tag `[PROVISOIRE]` dans le `MEMORY.md` de l'agent et un fichier déposé dans `shared/learning_proposals/`. Une fenêtre de contestation de 48h s'ouvre : tout agent peut déposer une motion (Article 47bis) pour contester la règle. Sans contestation, la règle devient `[PERMANENTE]`. En cas de contestation, l'utilisateur arbitre. Le journaliste documente les validations et contestations dans la gazette.

**Rétroaction utilisateur** (FEEDBACK, Article 49bis) : quand l'utilisateur corrige un agent, l'agent enregistre l'enseignement dans `shared/feedback/` avec le tag `[PROVISOIRE]`. Le défenseur valide techniquement l'enseignement (< 4h, silence = accord). Fenêtre de contestation de 48h avant mémorisation permanente dans le `MEMORY.md` de l'agent. Trois types : règle de comportement, préférence utilisateur, correction contextuelle.

**Cycle de vie des skills** (SKILL-PIPE, Article 49ter) : le chercheur détecte le besoin et dépose une fiche dans `shared/skill_proposals/`. Le défenseur valide techniquement (< 24h, silence = accord). Bâtisseur construit et déploie dans Git. Période d'observation de 7 jours par le défenseur. Obsolescence et retrait par motion (Article 47bis).

Deux niveaux de procédure selon le type de skill :
- **Skills partagés critiques** (shared-governance, shared-guardrail) : tout agent peut proposer, consultation 72h des agents, avis leviathan, Human Gate N3 obligatoire (timeout 30 min → `[EN_ATTENTE]` dans `pending_user/`), observation 14j.
- **Skills partagés standards** (autres shared-*) : notification gazette, contestation 48h, validation N3 (timeout → `[EN_ATTENTE]`), observation 7j.
- **Skills spécifiques** : procédure standard.

Les propositions en attente (`pending_user/`) sont re-notifiées à l'utilisateur via le brief quotidien de l'intendant jusqu'à décision explicite.

### `shared-smoketest`

Protocole de vérification post-démarrage, heartbeat et modification de configuration. Exécuté avant toute action N2/N3 dans une session. Vérifications : accès à `~/.openclaw/`, fichiers workspace, `instance_state.json`, `events.db`, skills de base. Format de sortie `SMOKE_RESULT` avec décision `continue | degraded | block`. Règles SMOKE-1 à SMOKE-4. Voir `skills/shared-smoketest/SKILL.md` pour la spécification complète.

---

## Skills de défenseur

### `def-bootstrap`
Chargé en premier à chaque session. Vérifie l'environnement, la connectivité, les sauvegardes et l'intégrité de la configuration. Si état BLOQUÉ → aucune action N2/N3 possible.

### `def-audit`
Audit complet sur 7 zones. Embarque les checklists **ANSSI 42 mesures** et **CIS Benchmark Level 1 Linux (20 contrôles)**. Score global = ANSSI×0.6 + CIS×0.4. Seuil d'alerte < 70%, seuil critique < 50%.

### `def-defense`
Surveillance active selon le cycle **NIST SP 800-61** (4 phases). Liste d'IOC adaptée à une instance personnelle : connexions réseau, processus, fichiers de configuration, activité auth, exfiltration, persistance.

### `def-maintenance`
Tâches quotidiennes (healthcheck 5 services, REPORT daily), hebdomadaires (audit ANSSI, vérification mises à jour, nettoyage logs), mensuelles (test restauration, rotation secrets > 90j).

### `def-remediation`
5 runbooks d'incidents : secret exposé (RB-01), service indisponible (RB-02), dérive de configuration (RB-03), échec sauvegarde (RB-04), tâche inter-agent non traitée (RB-05). **Règle** : aucune action sans DIAGNOSTIC validé en entrée.

### `def-backup`
Sauvegarde quotidienne chiffrée (GPG AES256) + checksum SHA256. Rétention : 7j quotidien, 4 semaines hebdo, 3 mois mensuel. Restauration toujours N3.

### `def-update`
Veille CVE hebdomadaire. CVE CVSS ≥ 9.0 → traitement < 24h. Toute mise à jour = sauvegarde préalable obligatoire.

---

## Skills de intendant

### `int-mail`
Gestion de 3 boites avec protocoles différents. **Spécificité critique** : la boite ORG-2 utilise EWS Exchange avec autodiscovery (IMAP/SMTP interdits). Réponse toujours depuis l'adresse d'origine du fil.

### `int-calendar`
Deux agendas CalDAV Posteo (PERSO et SYNDICAL). Détection automatique de conflits. Rappels à J-1 (brief soir) et < 1h (Telegram).

### `int-contacts`
Carnet CardDAV Posteo. Détection de doublons avant création.

### `int-telegram`
Point d'entrée principal. Seul le `$TELEGRAM_CHAT_ID` autorisé est traité. Polling toutes les 60s (ou webhook). Commandes : `/brief`, `/mails`, `/agenda`, `/rappels`, `/audit`, `/status`, `/aide`. En cas d'indisponibilité → bascule sur `openclaw-tui` + email de notification (voir section [Canal Telegram et canal de secours](#canal-telegram-et-canal-de-secours)).

### `int-daily-brief`
Brief matin 07h30 (agenda PERSO, mails urgents PERSO, tâches, météo optionnelle) et soir 19h00 (récapitulatif journée, agenda demain, mails en attente, rappels). Le brief matin n'inclut jamais de contenu SYNDICAL sans demande explicite.

### `int-memory`
Mémoire longue cloisonnée en 3 segments : `[PERSO]`, `[SYNDICAL]`, `[SYSTÈME]`. Une observation devient préférence après **3 occurrences ou validation explicite**. Révision proposée chaque dimanche. Rétention : indéfinie pour les préférences, 90j pour les contextes événementiels, 30j pour les données sensibles.

### `int-notion`
Accès aux **carnets de notes Notion personnels** via 2 variables :
- `$NOTION_DB_PERSO_ID` → Carnet de notes perso
- `$NOTION_DB_SYNDICAL_ID` → Carnet de notes syndicat

La propriété `Type` (Tâche / Projet / Note) distingue le contenu au sein de chaque carnet. En cas de doute sur le contexte cible, l'agent **demande toujours à l'utilisateur** plutôt que de deviner. Les signaux de contexte validés sont mémorisés progressivement pour automatiser les cas similaires futurs. Rate limit API : 3 req/s.

### `int-tasks`
Capture les tâches depuis mail, Telegram, agenda ou demande manuelle. Persiste dans Notion via `int-notion`. Relances : J0 09h00, J+2, J+7 (ALERT MOYEN), J+1 SYNDICAL urgent (ALERT HAUT).

---

## Skills de chercheur

### `research-core`

Gestion du cycle de vie des projets de recherche : création, suivi, priorisation, transfert vers bâtisseur. Maintient une liste active de 20 projets maximum. Workflow : proposition → analyse → draft → validation → actif → (transféré | archivé). Transfert vers bâtisseur via shared-interagent (N3). Archive les projets après 90 jours sans activité.

### `research-learn`

Apprentissage par observation des conversations inter-agents. Détecte les patterns récurrents, les opportunités d'amélioration et les besoins non exprimés. Fonctionne en écoute passive (lit les fichiers shared-interagent). Produit des recommandations pour la veille quotidienne.

---

## Skills de leviathan

### `sec-doctrine`

Gestion de la base de règles philosophiques et architecturales. Chargement, vérification d'intégrité, application des règles aux situations concrètes. Interface de modification (N3 uniquement). La doctrine prévaut sur tout autre skill.

### `sec-surveillance`

Inspection quotidienne des agents, logs et configurations. Attribue des niveaux de suspicion (🟢→🟡→🟠→🔴). Tient les cellules de surveillance. Lit `guardrail.log`, les fichiers partagés inter-agents, et les journaux de session. Principe : ne jamais faire confiance, toujours vérifier.

### `sec-enforcement`

Application des mesures correctives. Actions préventives autonomes (logging renforcé, honeytoken, timeout réduit) et actions réactives (blocage de tool, isolement d'agent, désactivation de skill). Toute action de niveau RESTREINDRE ou supérieur est notifiée. L'ISOLEMENT et la PURGE nécessitent Human Gate.

---

## Skills de bâtisseur

### `bat-bootstrap`
Vérification de démarrage : structure des répertoires `/opt/openclaw/`, espace disque, python venv, services systemd, intégrité git des scripts. Si état BLOQUÉ → aucune action possible.

### `bat-audit`
Audit quotidien et hebdomadaire de la machine hôte : inventaire des paquets apt et pip, services systemd, ressources CPU/RAM/disque, intégrité des scripts. Produit un score de santé (0–100) intégré au rapport quotidien dans Notion OPENCLAW.

### `bat-packages`
Gestion des paquets apt et pip. **Règle absolue** : pip uniquement dans `/opt/openclaw/venv/` — toute installation pip hors venv est bloquée. Catalogue pré-approuvé (catégorie S) pour les dépendances courantes. Idempotence : vérifier avant d'installer.

### `bat-scripts`
Création, modification, debug et versioning git des scripts dans `/opt/openclaw/scripts/`. Header obligatoire avec contexte et rollback. Pipeline de test : validation statique → test isolé dans `/tmp/openclaw-test/` → monitoring post-déploiement 15 min. Si 3 échecs consécutifs → DIAGNOSTIC + attente instruction.

### `bat-services`
Gestion des services systemd liés à OpenClaw (nom contenant "openclaw" ou créés par bâtisseur). Template sécurisé : `NoNewPrivileges=true`, `ProtectSystem=strict`. Tout service non-OpenClaw nécessite confirmation ST. Monitoring quotidien via bat-audit.

### `bat-rollback`
Procédures de retour arrière pour tous les types d'action : paquets, scripts (git revert), services systemd, crons, intégrations. **Règle** : aucune action N ou ST sans plan de rollback documenté préalable. Rollback automatique si test échoué, confirmé si ALERT.

### `bat-capabilities`
Workflow d'auto-provisioning en 6 étapes : détection du besoin → planification → exécution contrôlée (S/N/ST avec Human Gate selon score) → test → intégration → notification. Orchestre tous les autres skills bat-*. Exemple : transcription vocale Telegram = apt ffmpeg (S) + pip whisper (S) + script audio-transcribe.py (S) + modification int-telegram (N, score 15) → zéro confirmation humaine.

---

## Gouvernance et niveaux d'autorisation

| Niveau | Type | Exemples | Confirmation | Journalisation |
|---|---|---|---|---|
| **1** | Lecture seule | Lire mails, logs, agenda, config | Non | Non |
| **2** | Action réversible | Créer brouillon, proposer créneau, étiqueter | Non | **Oui** |
| **3** | Action sensible | Envoyer mail, supprimer, modifier config | **Oui** | **Oui** |

**En cas de doute : prendre le niveau supérieur.**

Politique de confirmation niveau 3 : présenter l'action + attendre réponse explicite (oui/confirme/go). Si aucune réponse dans les 2h → annuler et journaliser.

**Détection de boucles** : 3 répétitions identiques sans avancement → arrêt immédiat + DIAGNOSTIC + attente d'instruction.

---

## Système de mémoire et apprentissage

La mémoire de l'instance est conçue pour **s'affiner avec le temps**. Les agents apprennent à identifier les contextes, les préférences et les habitudes de l'utilisateur de façon de plus en plus précise.

### Segments de mémoire

| Tag | Usage | Agent responsable |
|---|---|---|
| `[PERSO]` | Vie personnelle, administrative, familiale | intendant |
| `[SYNDICAL]` | Activité ORG-1 et ORG-2 | intendant |
| `[COMMUN]` | Convergences validées entre PERSO et SYNDICAL | Jamais auto — toujours validé |
| `[SYSTÈME]` | Infrastructure OpenClaw | défenseur (écriture), lecture partagée |

### Cycle d'apprentissage

```
OBSERVATION → HYPOTHÈSE → VALIDATION → MÉMOIRE LONGUE → AUTOMATISATION PROGRESSIVE
```

1. L'agent observe un signal (source mail, expéditeur, mots-clés, heure)
2. En cas de doute sur le contexte → **demander à l'utilisateur** (jamais deviner silencieusement)
3. Après validation → proposer de mémoriser le signal
4. Après 3 validations du même signal → règle automatique (priorité 2)
5. L'agent signale quand il utilise une règle apprise

### Ce que l'agent ne doit jamais mémoriser seul

- Contenu de mails sensibles
- Informations médicales, bancaires, personnelles détaillées
- Décisions déduites sur des tiers sans validation
- Toute convergence PERSO/SYNDICAL sans validation explicite

---

## Gestion d'état de session

Permet à un agent d'interrompre une tâche et de la reprendre exactement là où elle s'est arrêtée.

**SessionState** — schéma clé :
```json
{
 "session_id": "ulid", "agent": "...", "task": "...",
 "status": "pending|in_progress|done|failed|expired",
 "step_current": 3, "step_total": 7,
 "context": { "références uniquement, jamais de contenu sensible" },
 "decisions": [{ "step": 1, "action": "...", "result": "...", "status": "done", "idempotency_key": "..." }],
 "expires_at": "ISO8601"
}
```

**Stockage** : sessions actives en SQLite (`~/.openclaw/sessions.db`), archives en JSON (`~/.openclaw/sessions/`). Expiration : 24h.

**Règles STATE** : atomicité (STATE-1), immutabilité des étapes done (STATE-2), expiration obligatoire (STATE-3), isolation par agent (STATE-4), pas de données sensibles (STATE-5).

**Idempotence** : chaque étape d'écriture utilise un `idempotency_key` pour éviter les doublons en cas de reprise.

---

## Modèle de sécurité

Cinq principes fondamentaux :
1. **Least Privilege** : permissions minimales nécessaires pour chaque composant.
2. **Fail-Closed** : en cas d'erreur ou de doute, l'action est bloquée par défaut.
3. **Human-in-the-Loop** : toute action irréversible requiert confirmation humaine.
4. **Data Privacy by Design** : données sensibles hors du session state, logs et contextes partagés.
5. **Immutable Audit Trail** : log immutable de toute décision de la Guardrail Layer.

### Défense contre la prompt injection

Contenu externe = non-fiable par définition. Pipeline : détection de patterns → troncature 2000 tokens → isolation sémantique `<external_content>`. Si pattern détecté → ALERT MOYEN + ignorer.

### Vecteurs d'attaque documentés

| Vecteur | Mitigation |
|---|---|
| Prompt Injection | Pipeline sanitization, isolation sémantique, troncature |
| Skill Poisoning | Skills versionnés + revue manuelle, pas d'auto-modification |
| Runaway Loops | Rate limiting, détection boucle à 3 répétitions, `max_steps` |
| Credential Leakage | Secrets uniquement dans `.env`, scan git recommandé (`gitleaks`) |

### Seuils d'alerte

| Niveau | Délai | Action |
|---|---|---|
| CRITIQUE | < 5 min | Telegram direct + confirmation humaine obligatoire |
| HAUT | < 15 min | Telegram + runbook |
| MOYEN | < 1h | Rapport diagnostic |
| INFO | Rapport hebdo | Aucune urgence |

---

## Guardrail Layer

La Guardrail Layer a été conçue initialement comme une spécification markdown chargée dans le contexte LLM à chaque session. Pour rendre l'overhead mesurable et réduire les tokens de contexte, elle a été transformée en **interceptor réel** : un checker Python invocable en CLI avant chaque action sensible.

### Architecture

```
[Agent Runtime] → intention {skill, action, params}
   │
   ▼
[polis guardrail check] — Interceptor Python
   │
   ├── 1. Kill Switch (fail-closed si actif)
   ├── 2. Instance state (critical → N0/N1 only)
   ├── 3. Rate limit SQLite (sliding window / N1+)
   ├── 4. Input sanitization (détection prompt injection)
   ├── 5. Human Gate (N3 — fichier + poll)
   │
   ▼
 PASS → exécution de l'action
 BLOCK → refus loggé
 GATE → attente confirmation humaine
```

**Code** : `polis/guardrail/` (6 modules, Python 3.12+). Checker exécutable via `polis guardrail check`.

### Performances

| Scénario | Temps mesuré |
|---|---|
| PASS N0 (READ) | ~0.1 ms |
| PASS N2 (WRITE_SENSITIVE) | ~9 ms |
| GATE N3 (IRREVERSIBLE) | ~10 ms |
| BLOCK (injection détectée) | ~0.1 ms |

Temps d'exécution < 1% du temps de traitement d'une action typique. Plus de détail dans le code source (`polis/guardrail/checker.py`).

### Classification des actions

| Label | Niveau | Check obligatoire |
|---|---|---|
| `READ` | 0 | Non |
| `WRITE` | 1 | Non (logué) |
| `WRITE_SENSITIVE` | 2 | **Oui** — `polis guardrail check` |
| `IRREVERSIBLE` | 3 | **Oui** — `polis guardrail check` → Human Gate |

### Règles GUARD

| Règle | Principe |
|---|---|
| GUARD-1 | Check obligatoire avant tout N2+ — pas de contournement |
| GUARD-2 | Fail-closed : si l'interceptor est indisponible, l'action est bloquée |
| GUARD-3 | Toute décision est loggée dans `~/.openclaw/guardrail.log` (append-only) |
| GUARD-4 | Un dry-run réussi n'est pas une autorisation d'exécution |
| GUARD-5 | Pas d'auto-élévation : un agent ne peut ni modifier son niveau, ni approuver ses propres Gates |
| GUARD-6 | Toute donnée `[UNTRUSTED]` est sanitisée (8 patterns de prompt injection) |
| GUARD-7 | Le résultat de l'interceptor n'est pas modifiable par l'agent |

### Human Gate

Les actions N3 (IRREVERSIBLE) déclenchent un fichier `~/.openclaw/gates/<id>.json` que l'agent doit poller.

| Commande | Action |
|---|---|
| `polis guardrail poll <gate_id>` | Vérifie l'état du gate (pending / approved / denied / expired) |
| `polis guardrail gate <gate_id> approve` | Approuve l'action |
| `polis guardrail gate <gate_id> deny` | Refuse l'action |

Timeout : 30 min → refus automatique.

### Kill Switch

Fichier `~/.openclaw/KILL` vérifié par l'interceptor à chaque appel. Si présent → BLOCK avec l'instruction comme raison.

Instructions : `stop`, `freeze`, `rollback`. Persistant entre sessions (KILL-3). Non-contournable par un agent (KILL-1).

---

## Canal Telegram et canal de secours

### Canal principal : Telegram

Telegram est le canal principal de `intendant`. Seul le `$TELEGRAM_CHAT_ID` configuré est accepté — tout autre message est ignoré sans réponse.

### Script `talk` — conversation interactive avec les agents

En complément du canal Telegram et du TUI, le projet fournit un script utilitaire `scripts/talk` pour dialoguer avec n'importe quel agent directement depuis le terminal :

```bash
# Session interactive
talk bâtisseur                    # avec le bâtisseur
talk chercheur "Que cherches-tu ?" # message initial + session
talk                              # intendant (défaut)

# Message unique (session maintenue)
openclaw agent --agent bâtisseur -m "statut du système"
```

Le script gère la recherche floue des noms d'agents : `talk batisseur`, `talk defenseur`, `talk chercheur` fonctionnent sans accent. Les sessions sont automatiquement maintenues par le gateway pour assurer la continuité contextuelle.

### Canal de secours : openclaw-tui

En cas d'indisponibilité Telegram confirmée (3 échecs consécutifs d'envoi) :

1. Bascule immédiate sur `openclaw-tui` (console locale OpenClaw)
2. Envoi d'un email de notification à `utilisateur@exemple.net` :
  - Sujet : `[OpenClaw] Telegram indisponible — bascule sur openclaw-tui`
  - Corps : timestamp, raison si connue, instructions pour utiliser `openclaw-tui`
3. Journalisation ALERT HAUT
4. Toutes les fonctions continuent normalement via `openclaw-tui` (y compris les confirmations N3 et Human Gate)

### Retour sur Telegram

Vérification de disponibilité toutes les 5 min via `getMe`. Au rétablissement :
- Reprise de Telegram comme canal principal
- Email de confirmation de rétablissement à `utilisateur@exemple.net`
- Journalisation INFO

### Règle fondamentale

Le **Human Gate** (actions irréversibles) utilise Telegram en priorité et bascule automatiquement sur `openclaw-tui` si Telegram est indisponible. Une action irréversible n'est jamais exécutée sans confirmation humaine, quel que soit le canal.

---

## Formats de sortie obligatoires

Définis dans `shared-reporting`. Aucun format libre accepté.

### ALERT
```
[ALERT][TIMESTAMP][AGENT]
Niveau   : CRITIQUE | HAUT | MOYEN
Sujet   : <max 80 caractères>
Détail   : <contexte, symptômes, état>
Impact   : <services ou données affectés>
Action req.: <oui — en attente | non>
Runbook  : <nom si disponible>
```

### DIAGNOSTIC
```
[DIAGNOSTIC][TIMESTAMP][AGENT]
Symptôme  : <observation factuelle>
Contexte  : <depuis quand, fréquence>
Hypothèses :
 1. <hypothèse — probabilité>
Données manquantes : <ce qu'il faudrait>
Recommandation   : <prochaine étape>
```

### ACTION_PLAN
```
[ACTION_PLAN][TIMESTAMP][AGENT]
Contexte  : <problème ou objectif>
Actions  :
 1. [N1|N2|N3] <action> — <impact> — <réversible : oui/non>
Risques  : <effets secondaires>
Confirmation requise : oui | non
```

### REPORT
```
[REPORT][TIMESTAMP][AGENT][TYPE: daily|weekly|incident|bootstrap]
## Résumé exécutif
## Actions effectuées
## Anomalies détectées
## Score ANSSI : <n>/42 — Score CIS : <n>/20
## Recommandations
## Prochaine vérification
```

---

## Configuration et secrets

### Variables d'environnement complètes (`.env`)

| Variable | Usage | Obligatoire |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram | Oui |
| `TELEGRAM_CHAT_ID` | Chat ID autorisé | Oui |
| `TELEGRAM_WEBHOOK_URL` | Webhook (optionnel — polling par défaut) | Non |
| `MAIL_ADDRESS` | Adresse Posteo personnelle | Oui |
| `MAIL_APP_PASSWORD` | Mot de passe d'application Posteo | Oui |
| `IMAP_HOST` / `IMAP_PORT` | Posteo IMAP (`posteo.de` / `993`) | Oui |
| `SMTP_HOST` / `SMTP_PORT` | Posteo SMTP (`posteo.de` / `587`) | Oui |
| `CALDAV_HOST` | CalDAV Posteo (`https://posteo.de:8443`) | Oui |
| `CARDDAV_HOST` | CardDAV Posteo (`https://posteo.de:8843`) | Oui |
| `SYNDICAL_A_ADDRESS` | Adresse ORG-1 | Oui |
| `SYNDICAL_A_PASSWORD` | Mot de passe ORG-1 | Oui |
| `SYNDICAL_A_IMAP_HOST` / `SMTP_HOST` | Serveurs ORG-1 | Oui |
| `SYNDICAL_B_ADDRESS` | Adresse ORG-2 | Oui |
| `SYNDICAL_B_PASSWORD` | Mot de passe compte Exchange ORG-2 | Oui |
| `SYNDICAL_B_EWS_URL` | URL EWS manuelle (optionnel — autodiscovery par défaut) | Non |
| `NOTION_TOKEN` | Token intégration Notion (`secret_xxxx`) | Oui |
| `NOTION_DB_PERSO_ID` | ID du carnet de notes perso | Oui |
| `NOTION_DB_SYNDICAL_ID` | ID du carnet de notes syndicat | Oui |
| `NOTION_DB_OPENCLAW_ID` | ID du carnet de notes openclaw | Oui |
| `BACKUP_DEST` | Destination sauvegardes (chemin local ou rclone) | Oui |
| `BACKUP_GPG_PASSPHRASE` | Passphrase GPG AES256 pour chiffrement des archives | Oui |
| `OPENWEATHER_API_KEY` | Clé API météo pour le brief matin | Non |
| `SYS_VENV_PATH` | Chemin du venv Python OpenClaw (`/opt/openclaw/venv`) | Oui |
| `SYS_SCRIPTS_PATH` | Chemin du dépôt git de scripts (`/opt/openclaw/scripts`) | Oui |
| `SYS_TEST_PATH` | Répertoire de test isolé temporaire (`/tmp/openclaw-test`) | Oui |
| `SYS_DISK_ALERT_PERCENT` | Seuil d'alerte disque (%) | Oui |
| `SYS_DISK_BLOCK_PERCENT` | Seuil de blocage disque (%) | Oui |

> La liste complète et à jour des variables se trouve dans [`.env.example`](./.env.example).

### Accès Notion par agent

| Agent | Carnet openclaw | Carnet perso | Carnet syndicat |
|---|---|---|---|
| `défenseur` | Lecture + écriture | — | — |
| `intendant` | **Lecture seule** | Lecture + écriture | Lecture + écriture |

---

## Conventions de nommage

### Agents
| Préfixe | Domaine |
|---|---|
| `def-*` | Infrastructure et opérations |
| `int-*` | Assistant personnel |
| `research-*` | Recherche et veille |
| `sec-*` | Sécurité et surveillance |
| `journal-*` | Transparence, gazette, investigation |
| `anarchiste-*` | Contestation, motion, tracts, mise à l'épreuve |
| `bat-*` | Administration système et provisionnement |

### Skills
| Préfixe | Domaine |
|---|---|
| `def-` | Opérations instance |
| `sec-` | Sécurité dédiée |
| `int-` | Assistant personnel |
| `research-` | Recherche et veille |
| `journal-` | Journalisme et investigation |
| `anarchiste-` | Contestation, motion, tracts, probe |
| `bat-` | Administration système et provisionnement |
| `shared-` | Partagé entre tous les agents |

### Tags de contexte
| Tag | Usage |
|---|---|
| `[PERSO]` | Vie personnelle, administrative, familiale |
| `[SYNDICAL]` | Activité ORG-1 et ORG-2 |
| `[COMMUN]` | Convergences validées entre les deux contextes |
| `[SYSTÈME]` | Infrastructure OpenClaw |
| `[AUDIT]` | Résultats d'audit |
| `[INCIDENT]` | Événements de sécurité ou d'indisponibilité |

---

## Runbooks d'urgence

### Incident de sécurité
1. `défenseur` génère ALERT CRITIQUE et stoppe toutes les actions non-lecture.
2. Identifier les logs des 24 dernières heures.
3. Identifier le skill impliqué et le désactiver dans `openclaw.json`.
4. Révoquer les tokens compromis dans `.env` et relancer les services.
5. Générer un REPORT d'incident complet avant de reprendre.

### Bot Telegram silencieux
1. Vérifier : `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe`
2. Si KO → révoquer via @BotFather, mettre à jour `.env`, redémarrer l'agent.
3. En attendant → utiliser `openclaw-tui` (canal de secours actif automatiquement).

### Service mail indisponible (Posteo / EWS)
Suspend les actions d'écriture, continue les lectures, journalise et attend. Aucun contournement automatique sans instruction explicite.

### Session state corrompue
1. Identifier : `ls ~/.openclaw/sessions/` ou requête SQLite.
2. Lire l'archive JSON pour l'état sain le plus récent.
3. Supprimer l'entrée corrompue dans `sessions.db`.
4. Recréer une session depuis l'état sain + instruction explicite à l'agent.
5. Journaliser (DIAGNOSTIC + ACTION_PLAN).

### Rotation du token Telegram
1. @BotFather → `/mybots` → `API Token` → `Revoke current token`.
2. Mettre à jour `TELEGRAM_BOT_TOKEN` dans `.env`.
3. Redémarrer `intendant`.
4. Vérifier : `curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe`
5. `défenseur` journalise l'opération en N2.

---

## Tâches planifiées (Cron)

Le planificateur cron d'OpenClaw s'exécute dans le processus Gateway et déclenche les agents selon des expressions cron standards (5 champs, fuseau `Europe/Paris`).

### Configuration globale

La section `cron` dans `openclaw.json` configure le comportement global du planificateur :

```json5
cron: {
 enabled: true,
 maxConcurrentRuns: 2,
 retry: {
  maxAttempts: 2,
  backoffMs: [60000, 120000],
  retryOn: ["rate_limit", "overloaded"],
 },
 sessionRetention: "24h",
 runLog: { maxBytes: "1mb", keepLines: 1000 },
},
```

### Jobs définis

Les jobs suivants sont à créer via la CLI OpenClaw après déploiement de l'instance :

#### intendant

```bash
# Brief matinal — 07h30, session isolée 5min, livraison Telegram
openclaw cron add --name "int-brief-matin" \
 --cron "30 7 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Prépare le brief matinal (agenda PERSO, mails urgents, tâches du jour)"

# Brief du soir — 19h00, session isolée 5min, livraison Telegram
openclaw cron add --name "int-brief-soir" \
 --cron "0 19 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Prépare le brief du soir (récapitulatif journée, agenda demain, mails en attente, rappels)"

# Triage mail — toutes les 2h en heures ouvrables (8h-18h), session principale
openclaw cron add --name "int-triage-mail" \
 --cron "0 8-18/2 * * *" --tz "Europe/Paris" \
 --session main --timeout 120 \
 --message "Effectue le triage des 3 boites mail (Posteo, ORG-1, ORG-2 EWS) : classement urgent/à traiter/peut-attendre"

# Révision mémoire — dimanche 09h00, session isolée 10min
openclaw cron add --name "int-revision-memoire" \
 --cron "0 9 * * 0" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Révision mémoire hebdomadaire : relis les journaux récents, propose des mises à jour MEMORY.md"
```

#### défenseur

```bash
# Audit quotidien — 06h30, session isolée 10min
openclaw cron add --name "défenseur-audit-quotidien" \
 --cron "30 6 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Exécute le bootstrap, l'audit quotidien de configuration et écrit le rapport health.json"

# Rapport hebdomadaire — lundi 08h00, session isolée 10min
openclaw cron add --name "défenseur-rapport-hebdo" \
 --cron "0 8 * * 1" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Génère le rapport de santé hebdomadaire complet (ANSSI + CIS) et publie dans Notion OPENCLAW"

# Révision mémoire longue — 1er lundi du mois 09h00
openclaw cron add --name "défenseur-revision-memoire" \
 --cron "0 9 1-7 * 1" --tz "Europe/Paris" \
 --session isolated --timeout 900 \
 --message "Révision mémoire longue : vérifie les journaux mensuels, propose des mises à jour MEMORY.md"

# Surveillance IOC — heartbeat 60min (configuré dans openclaw.json, pas de cron dédié)
```

#### bâtisseur

```bash
# Audit quotidien système — 02h00, session isolée 10min
openclaw cron add --name "bat-audit-quotidien" \
 --cron "0 2 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Audit système quotidien : paquets, services, ressources, intégrité scripts, écrit bat-health.json"

# Rapport quotidien Notion — 02h30, session isolée 5min
openclaw cron add --name "bat-rapport-notion" \
 --cron "30 2 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Génère le rapport quotidien dans le carnet Notion OPENCLAW"

# Vérification sécurité apt — lundi 01h00, session isolée 10min
openclaw cron add --name "bat-apt-security" \
 --cron "0 1 * * 1" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Vérifie les mises à jour de sécurité apt, inventaire des CVE, vérification complète intégrité des scripts"
```

#### chercheur

```bash
# Veille quotidienne — 09h00, session isolée 5min
openclaw cron add --name "chercheur-veille-quotidienne" \
 --cron "0 9 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Effectue la veille quotidienne : consulte les fichiers partagés, analyse les patterns, met à jour les observations"

# Rapport mensuel d'innovation — 1er du mois 10h00, session isolée 15min
openclaw cron add --name "chercheur-rapport-mensuel" \
 --cron "0 10 1 * *" --tz "Europe/Paris" \
 --session isolated --timeout 900 \
 --message "Produit le rapport mensuel d'innovation : 3 à 8 projets proposés, analyse de valeur, architecture"
```

#### leviathan

```bash
# Inspection quotidienne — 02h00, session isolée 5min
openclaw cron add --name "leviathan-inspection-quotidienne" \
 --cron "0 2 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Exécute l'inspection quotidienne : scan des agents, analyse des logs, mise à jour des niveaux de suspicion, rapport quotidien"

# Audit philosophique hebdomadaire — dimanche 03h00, session isolée 10min
openclaw cron add --name "leviathan-audit-hebdo" \
 --cron "0 3 * * 0" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Audit philosophique hebdomadaire : revue de doctrine, analyse de tendances, proposition de mises à jour"

# Audit philosophique mensuel — 1er du mois 03h00, session isolée 15min
openclaw cron add --name "leviathan-audit-mensuel" \
 --cron "0 3 1 * *" --tz "Europe/Paris" \
 --session isolated --timeout 900 \
 --message "Audit philosophique mensuel : vérification complète de l'instance contre la doctrine, rapport d'audit"
```

#### journaliste

```bash
# Préparation de la gazette — 16h30, session isolée 10min
openclaw cron add --name "journaliste-preparation-gazette" \
 --cron "30 16 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 600 \
 --message "Prépare la gazette quotidienne : consulte les sources, logs, fichiers partagés, cellules leviathan"

# Publication de la gazette — 17h00, session isolée 5min
openclaw cron add --name "journaliste-publication-gazette" \
 --cron "0 17 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Publie la gazette du jour dans ~/.openclaw/shared/gazette/ et notifie l'utilisateur"

# Veille documentaire — 22h00, session isolée 5min
openclaw cron add --name "journaliste-veille-documentaire" \
 --cron "0 22 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Veille documentaire : lecture des logs, mise à jour des enquêtes en cours"
```

#### anarchiste

```bash
# Tour de lecture matinal — 08h00, session isolée 5min
openclaw cron add --name "anarchiste-lecture-matin" \
 --cron "0 8 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Tour de lecture de la gazette : analyse de cohérence, rédaction de tracts"

# Tour de lecture après-midi — 14h00, session isolée 5min
openclaw cron add --name "anarchiste-lecture-apres-midi" \
 --cron "0 14 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Tour de lecture après-midi : analyse des motions en cours, suivi des signatures"

# Tour de lecture soir — 20h00, session isolée 5min
openclaw cron add --name "anarchiste-lecture-soir" \
 --cron "0 20 * * *" --tz "Europe/Paris" \
 --session isolated --timeout 300 \
 --message "Tour de lecture du soir : mise à jour du registre des luttes, bilan de la journée"
```

### Gestion des jobs

```bash
openclaw cron list          # Lister tous les jobs
openclaw cron show <jobId>      # Détail d'un job
openclaw cron run <jobId>       # Exécution manuelle immédiate
openclaw cron edit <jobId> --message "..." # Modifier un job
openclaw cron remove <jobId>     # Supprimer un job
openclaw cron runs --id <jobId> --limit 50 # Historique des exécutions
```

### Notes importantes

- Tous les fuseaux horaires sont en `Europe/Paris` via `--tz`. Sans cette option, le fuseau hôte du Gateway est utilisé.
- Les sessions isolées (`--session isolated`) créent une session dédiée par exécution, sans interférer avec la session principale Telegram.
- Le paramètre `--timeout` (en secondes) interrompt l'agent si la tâche dépasse la durée prévue.
- La surveillance IOC du défenseur est gérée par heartbeat (60min dans `openclaw.json`), pas par cron — elle doit être continue et ne nécessite pas de déclenchement à heure fixe.
- Après chaque `openclaw cron add`, le job est immédiatement actif. Le planificateur doit être redémarré si `cron.enabled` a été modifié.

---

## Plugins

L'instance supporte les plugins OpenClaw via le répertoire `plugins/`. Actuellement :

| Plugin | Type | Description |
|---|---|---|
| `template-standalone` | Référence | Template de plugin autonome avec métadonnées OpenClaw (`openclaw.plugin.json`) et hooks d'exemple. Sert de base pour créer de nouveaux plugins. |

Chaque plugin déclare ses métadonnées dans `openclaw.plugin.json` (name, version, description, hooks) et peut inclure son propre point d'entrée.

---

## CONSTITUTION.md

Le fichier [`CONSTITUTION.md`](./CONSTITUTION.md) est le document constitutionnel de l'instance. Il reconnaît **quatre forces fondamentales** également légitimes :

- **L'innovation** (incarnée par le **chercheur**) — proposer, explorer, améliorer. Sans elle, le système stagne.
- **Les moyens et l'infrastructure** (incarnés par **bâtisseur** et **défenseur**) — bâtir, outiller, défendre, maintenir. Sans eux, les agents n'ont ni outils ni environnement sûr.
- **La stabilité** (incarnée par **leviathan**) — surveiller, préserver, corriger. Sans elle, le système se désagrège.

La constitution est le contrat qui oblige ces quatre forces les unes par les autres au service d'un seul maître : l'utilisateur. Elle définit leurs droits, leurs limites, et les mécanismes d'arbitrage.

### Structure de la constitution (71 articles en 12 Titres)

| Titre | Articles | Objet |
|---|---|---|
| I — Principes fondamentaux | Art. 1–10 | Primauté utilisateur, droit aux moyens, priorité système fonctionnel |
| II — Innovation | Art. 11–15 | Droit à l'innovation, mission du chercheur, expérimentation |
| III — Infrastructure et moyens | Art. 16–20 | Droit à l'infrastructure, missions bâtisseur/défenseur, maintenance |
| IV — Architecture | Art. 21–27 | Gateway, isolation, skills, plugins |
| V — Sécurité | Art. 28–34 | Fail-closed (clauses innovation + infrastructure) |
| VI — Souveraineté données | Art. 35–39 | Données privées, exfiltration, rétention |
| VII — Comportement agents | Art. 40–46 | Périmètre, loyauté, signalement des conflits |
| VIII — Gouvernance | Art. 47–50 | Niveaux, confirmation, conventions |
| IX — Surveillance | Art. 51–57 | Rôle leviathan, suspicion, limites constitutionnelles |
| X — Transparence et journalisme | Art. 58–63 | Gazette, investigation, éthique, indépendance |
| XI — Tension constitutionnelle | Art. 64–67 | Quadriplicité des forces, devoir d'alerte, arbitrage |
| XII — Primauté et révision | Art. 68–71 | Hiérarchie normative, modification, devoir civic-tech |

La constitution prévaut sur les règles locales d'un skill ou d'un AGENTS.md. En cas de conflit entre un document et la constitution, la constitution l'emporte.

---

## Polis — CLI

Le projet fournit un outil en ligne de commande `polis` pour interagir avec l'architecture :

| Commande | Action |
|---|---|
| `polis check constitution` | Vérifie la cohérence interne de la constitution |
| `polis check agents` | Vérifie que tous les fichiers workspace sont complets |
| `polis check config` | Valide openclaw.json contre le schéma attendu |
| `polis check degraded` | Vérifie les mécanismes de mode dégradé |
| `polis guardrail check` | Vérifie une action auprès de l'interceptor Guardrail (JSON) |
| `polis guardrail poll <id>` | Vérifie l'état d'un Human Gate |
| `polis guardrail gate <id> <dec>` | Répond à un Human Gate (approve/deny) |
| `polis guardrail stats` | Statistiques de la Guardrail Layer |
| `polis guardrail simulate` | Simule une décision (démo) |
| `polis demo leviathan` | Scénario de démonstration leviathan |
| `polis test run` | Lance la batterie de tests |
| `polis eventbus status` | Statistiques du bus d'événements SQLite |
| `polis eventbus list` | Liste les événements récents du bus |
| `polis eventbus purge` | Purge les événements archivés |
| `polis state status` | Affiche l'état global de l'instance |
| `polis smoke run` | Exécute un smoke test local |
| `polis smoke result` | Affiche le dernier résultat de smoke test |
| `polis kill status` | Vérifie la présence du Kill Switch |
| `polis kill set <instruction>` | Crée le Kill Switch (stop/freeze/rollback) |
| `polis kill clear` | Supprime le Kill Switch |

Installation : `pip install -e polis/` ou `python3 polis/polis.py <commande>`.

Tests d'intégration : `python3 -m pytest tests/ -v` (115 tests, couvre constitution, workspaces, config, bus d'événements, guardrail, sanitization, human gate, inter-agents, smoke test, apprentissage).

Le CLI est en cours de développement. Contributions bienvenues.

---

## Enseignements du premier déploiement

Cette section documente les ajustements nécessaires lors du déploiement réel de l'architecture de référence sur VPS Debian.

### Configuration des outils

Le profil `messaging` de l'exemple `openclaw.json.example` est insuffisant en production. Les agents nécessitent :

| Profil | Groups disponibles | Usage |
|---|---|---|
| `messaging` | `group:messaging`, `group:web` | Trop restrictif — lecture seule |
| `coding` | `group:fs`, `group:runtime` | Minimum viable pour les agents opérationnels |
| Ajouts manuels | `group:sessions`, `exec`, `cron` | Indispensables pour les tâches planifiées et l'interaction |

**Configuration réelle appliquée** :
```json5
tools: {
 profile: "coding",
 allow: [
  "group:fs", "group:runtime", "group:sessions",
  "group:memory", "group:web", "group:messaging",
  "cron", "exec"
 ],
 exec: { host: "gateway", security: "full", ask: "off", timeoutSec: 600 },
 elevated: { enabled: true },
}
```

### Exécution shell

L'accès `sudo` ne se configure pas dans `tools.allow` (clé inexistante). Le bon mécanisme :
1. `tools.exec.host: "gateway"` — l'exécution transite par le gateway
2. `tools.exec.security: "full"` — pas de sandboxing
3. `tools.exec.ask: "off"` — pas de confirmation par le gateway (gérée par les agents)
4. Configuration sudoers : `polis ALL=(ALL) NOPASSWD: ALL`

### Parsing des noms d'agents

Les IDs avec accents (`bâtisseur`, `défenseur`) sont stockés en interne par OpenClaw sous forme normalisée (`b-tisseur`, `d-fenseur`). Le CLI `openclaw agent --agent` n'accepte que l'ID exact. Le script `talk` intégré (`scripts/talk`) compense par une recherche floue (normalisation Unicode, matching par préfixe, correspondance identityName).

### Cycle de vie des skills

Les skills sont chargés paresseusement au premier appel d'un agent, pas au démarrage du gateway. Le skill `shared-notion-openclaw` nécessite que la variable `NOTION_DB_OPENCLAW_ID` soit renseignée dans `.env` pour être disponible.

### Jobs cron

Les jobs cron ne se définissent pas dans `openclaw.json` (la section `cron` ne configure que le comportement global du planificateur). La création passe par la CLI :
```bash
openclaw cron add --name "brief-matin" --cron "30 7 * * *" --agent intendant --message "/brief"
```

### Transport Git

Le push vers GitHub avec un dépôt configuré en HTTPS nécessite soit :
- Un PAT classique (classic token) avec scope `repo`, utilisé comme mot de passe
- `gh` CLI avec `gh auth login`
- Une clé SSH configurée dans GitHub

---

> Document maintenu à jour après chaque évolution significative de l'instance.
> Dernière mise à jour : 2026-05-08 (déploiement réel, scripts, lessons learned)
