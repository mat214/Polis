---
name: shared-interagent
description: Convention de communication inter-agents via fichiers partagés dans ~/.openclaw/shared/.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Communication inter-agents

## Principe

Les agents OpenClaw ne disposent pas de messagerie directe. La communication se fait via un répertoire partagé `~/.openclaw/shared/` que chaque agent peut lire et écrire selon des contrats définis.

Ce répertoire n'est pas versionné. Il est inclus dans les sauvegardes quotidiennes (def-backup).

## Structure

```
~/.openclaw/
├── shared/
│  ├── health.json       # Écrit par défenseur, lu par intendant chercheur leviathan journaliste
│  ├── bat-health.json     # Écrit par bâtisseur, lu par intendant, chercheur, leviathan, journaliste
│  ├── research-health.json   # Écrit par chercheur, lu par intendant défenseur bâtisseur journaliste
│  ├── leviathan-status.json  # Écrit par leviathan, lu par tous
│  ├── journaliste-status.json # Écrit par journaliste, lu par tous
│  ├── instance_state.json   # État global de l'instance, écrit par tous (chacun son entrée)
│  ├── tracts/          # Tracts de l'anarchiste (action contestataire)
│  │  └── YYYY-MM-DD-titre.md  # Tract individuel
│  ├── motions/         # Motions formelles de l'anarchiste
│  │  └── registre.json     # Registre des motions avec statut
│  ├── gazette/         # Gazette quotidienne, écrite par journaliste, lue par tous
│  │  ├── YYYY-MM-DD.md    # Gazette du jour (rétention : 90 jours)
│  │  └── reportages/     # Reportages d'investigation
│  └── tasks/          # Écrit par intendant, chercheur, lu/traité par défenseur ou bâtisseur
│    ├── pending/       # Tâches en attente
│    ├── in_progress/     # Tâches en cours de traitement
│    └── done/        # Tâches terminées
│  ├── feedback/        # Enseignements utilisateur — Article 49bis
│  │  └── YYYY-MM-DD-agent-enseignement.md # Corrections enregistrées
│  └── skill_proposals/     # Propositions de nouveaux skills — Article 49ter
│    ├── YYYY-MM-DD-nom-du-skill.md
│    ├── pending_user/    # Propositions en attente de validation humaine (timeout Human Gate)
│    └── reviews/       # Avis techniques du défenseur
└── events.db          # Base SQLite du bus d'événements
```

## Contrats

### health.json (défenseur → intendant)

```json
{
 "updated_at": "ISO8601",
 "agent": "défenseur",
 "status": "ok | degraded | critical",
 "services": {
  "telegram": "ok | ko",
  "notion": "ok | ko",
  "posteo_imap": "ok | ko",
  "ewscgt": "ok | ko"
 },
 "audit_score": 85,
 "incidents_open": 0,
 "last_updated": "ISO8601"
}
```

### bat-health.json (bâtisseur → intendant)

```json
{
 "updated_at": "ISO8601",
 "agent": "bâtisseur",
 "score": 92,
 "disk_opt_percent": 45,
 "venv_ok": true,
 "services_openclaw_active": 2,
 "services_openclaw_failed": 0,
 "pending_tasks": 0
}
```

### leviathan-status.json (leviathan → tous)

```json
{
 "updated_at": "ISO8601",
 "agent": "leviathan",
 "threat_level": "safe | suspect | dangerous | subversive",
 "agents_under_surveillance": 0,
 "agents_status": {
  "intendant": { "level": "safe", "last_incident": null },
  "défenseur": { "level": "safe", "last_incident": null },
  "bâtisseur": { "level": "safe", "last_incident": null },
  "chercheur": { "level": "safe", "last_incident": null },
  "anarchiste": { "level": "dangerous", "last_incident": null }
 },
 "last_daily_report": "2026-05-06",
 "last_updated": "ISO8601"
}
```

### learning_proposals (défenseur, bâtisseur → tous)

Propositions d'apprentissage en attente de mûrissement. Chaque proposition est déposée dans `~/.openclaw/shared/learning_proposals/` par l'agent qui l'a formulée, lue par le journaliste pour la gazette, et contestable par tout agent via motion (Article 47bis).

```
├── learning_proposals/
│  ├── 2026-05-07-defenseur-pattern-audit.md
│  └── 2026-05-07-batisseur-catalogue-paquet.md
```

### journaliste-status.json (journaliste → tous)

```json
{
 "updated_at": "ISO8601",
 "agent": "journaliste",
 "gazette_last": "2026-05-06",
 "gazette_count": 1,
 "investigations_open": 0,
 "investigations_by_status": {
  "researching": 0,
  "writing": 0,
  "published": 0
 },
 "last_updated": "ISO8601"
}
```

### research-health.json (chercheur → intendant, défenseur, bâtisseur)

```json
{
 "updated_at": "ISO8601",
 "agent": "chercheur",
 "project_count": 12,
 "projects_by_status": {
  "proposed": 3,
  "in_progress": 5,
  "transferred": 2,
  "archived": 2
 },
 "last_monthly_report": "2026-05-01",
 "pending_transfers": 0,
 "last_updated": "ISO8601"
}
```

### Task file (intendant, chercheur → défenseur, bâtisseur)

```json
{
 "id": "ulid",
 "created_at": "ISO8601",
 "requestor": "intendant | chercheur",
 "target": "défenseur | bâtisseur",
 "action": "description précise",
 "params": {},
 "status": "pending | in_progress | done | failed",
 "result": null,
 "completed_at": null
}
```

## Bus d'événements

En complément du système de fichiers, les agents postent un événement sur le bus SQLite pour
toute action d'écriture dans `~/.openclaw/shared/`. Le bus est une **doublure** : les fichiers
JSON restent la source de vérité, le bus sert au routage et à la détection de fraîcheur.

### Base

```
~/.openclaw/events.db       # Base SQLite du bus d'événements
```

### Types d'événements

| Type | Source | Description |
|---|---|---|
| `health.updated` | défenseur, bâtisseur | Écriture de health.json / bat-health.json |
| `status.updated` | leviathan, journaliste, chercheur | Mise à jour du statut propre |
| `task.created` | intendant, chercheur | Nouvelle tâche dans shared/tasks/pending/ |
| `task.status.changed` | défenseur, bâtisseur | Tâche passée en in_progress / done / failed |
| `alert.raised` | Tous | Émission d'une ALERT (HAUT, MOYEN, CRITIQUE) |
| `learning.proposal` | défenseur, bâtisseur | Proposition de règle apprise vers LEVIATHAN |
| `smoketest.request` | Tous | Demande de smoke test adressée à un agent |
| `kill.activated` | Guardrail Layer | Kill Switch déclenché (stop/freeze/rollback) |

### Règles du bus

- **EVENT-1 — Atomicité** : l'écriture du fichier ET l'envoi de l'événement sont
 faits dans la même opération. Si l'un échoue, l'autre n'a pas lieu.
- **EVENT-2 — Auto-nettoyage** : les événements de plus de 7 jours sont purgés
 automatiquement (via le heartbeat hebdomadaire de l'agent qui tient le bus).
- **EVENT-3 — Intégrité** : un agent ne modifie jamais les événements postés
 par un autre agent. Chaque événement n'a qu'un seul `source`.

### Utilisation par les agents

1. **Émetteur** : après avoir écrit son fichier JSON dans `shared/`, l'agent
  exécute `polis eventbus post <type> --source <agent> --payload '<json>'`
  (ou l'appel équivalent via le module Python).
2. **Consommateur** : au début de chaque heartbeat ou action planifiée,
  l'agent lit les événements récents via
  `polis eventbus list --target <agent> --since <dernier_check>`.
3. **Acquittement** : une fois un événement traité, l'agent l'acquitte via
  `polis eventbus ack <id>`.

---

## État global de l'instance

Un fichier `instance_state.json` centralise l'état de santé de TOUS les agents.
Chaque agent écrit son propre statut à chaque heartbeat, et lit l'état global
avant chaque action pour décider de son comportement.

### Contrat

```json
{
 "updated_at": "ISO8601",
 "overall_status": "nominal | degraded | critical",
 "agents": {
  "intendant": {
   "status": "ok | degraded | critical",
   "capabilities": ["telegram", "mail", "calendar", "contacts", "tasks"],
   "since": "ISO8601"
  },
  "defenseur": {
   "status": "ok | degraded | critical",
   "capabilities": ["audit", "backup", "defense", "maintenance", "update"],
   "since": "ISO8601"
  },
  "bâtisseur": {
   "status": "ok | degraded | critical",
   "capabilities": ["packages", "scripts", "services", "rollback"],
   "since": "ISO8601"
  },
  "chercheur": {
   "status": "ok | degraded | critical",
   "capabilities": ["research", "veille", "transfert"],
   "since": "ISO8601"
  },
  "leviathan": {
   "status": "ok | degraded | critical",
   "capabilities": ["doctrine", "surveillance", "enforcement"],
   "since": "ISO8601"
  },
  "journaliste": {
   "status": "ok | degraded | critical",
   "capabilities": ["gazette", "investigation", "veille"],
   "since": "ISO8601"
  },
  "anarchiste": {
   "status": "ok | degraded | critical",
   "capabilities": ["observation", "revendication"],
   "since": "ISO8601"
  }
 },
 "degraded_since": null,
 "capabilities_lost": []
}
```

### Algorithme de calcul

1. Si **un seul** agent est `critical` → `overall_status = critical`
2. Si **≥ 2 agents** sont `degraded` → `overall_status = degraded`
3. Si **tout** est `ok` → `overall_status = nominal`
4. Sinon → maintien du statut précédent

### Règles de l'état global

- **INST-1** : tout agent vérifie `instance_state.json` avant chaque action.
 Si `overall_status == critical`, seules les actions READ/N1 sont autorisées.
- **INST-2** : chaque agent écrit son statut dans `instance_state.json` à
 chaque heartbeat, et poste un événement `status.updated` sur le bus.
- **INST-3** : un agent ne modifie que sa propre entrée dans `agents`.
- **INST-4** : si le fichier est absent ou illisible → supposer `critical`
 et bloquer toutes les actions N2/N3 (principe fail-closed).

---

## Règles

- Les fichiers sont relus à chaque heartbeat ou sur demande.
- Un agent ne modifie jamais le fichier d'un autre agent — seulement le sien.
- Les tâches sont atomiques : un fichier = une tâche. Déplacer le fichier entre les dossiers pending/in_progress/done pour changer son état.
- Si un fichier `health.json` n'est pas mis à jour depuis plus de 2 cycles de heartbeat : le déduire comme indisponible mais ne pas alerter (l'agent source est responsable de ses propres alertes).
- Les tâches non traitées après 24h sont signalées par un ALERT MOYEN.
- Les événements sur le bus sont créés au plus proche de l'écriture du fichier
 correspondant. Tout événement reçu sans fichier correspondant dans `shared/`
 doit être ignoré (le fichier est la source de vérité).

## Niveaux

| Action | Niveau |
|---|---|
| Lire shared/ (tous fichiers) | 1 |
| Écrire son propre fichier (health.json, bat-health.json, research-health.json, leviathan-status.json, journaliste-status.json, instance_state.json) | 1 |
| Poster un événement sur le bus | 1 |
| Lire les événements du bus | 1 |
| Acquitter un événement du bus | 1 |
| Créer un fichier de tâche | 2 |
| Déplacer/supprimer une tâche | 2 |
| Purger les événements du bus | 2 |
| Supprimer une tâche d'un autre agent | 3 |
