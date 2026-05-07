---
name: shared-state
description: SessionManager : init/load/upsert/archive/expire pour tâches longues interrompables.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Gestion d'état de session — SessionManager

## Quand charger ce skill

- Pour toute tâche comportant **plus de 2 étapes séquentielles** (triage mail, audit complet, planification...)
- Pour toute tâche déléguée à un sous-agent (afin de récupérer son état en cas d'interruption)
- Automatiquement chargé via `agents.defaults` dans `openclaw.json`

## Pourquoi c'est fondamental

Les tâches OpenClaw peuvent durer plusieurs minutes ou heures. Sans état persistant :
- Un redémarrage force l'agent à **tout recommencer** — coûteux en tokens, en temps, et potentiellement
 dangereux (actions déjà exécutées rejouées comme un envoi de mail)
- L'agent ne peut pas **déléguer** proprement à un sous-agent et récupérer son résultat
- La traçabilité des décisions ("pourquoi ai-je fait ça ?") disparaît

---

## Schéma JSON — SessionState

```json
{
 "session_id": "ulid",
 "schema_version": "1",
 "agent": "intendant",
 "task": "triage-mail-ferc",
 "status": "pending | in_progress | done | failed | expired",
 "step_current": 3,
 "step_total": 7,
 "context": {
  "note": "références uniquement (UID, ID) — jamais de contenu sensible"
 },
 "decisions": [
  {
   "step": 1,
   "action": "fetch_inbox",
   "result": "42 mails récupérés",
   "status": "done",
   "idempotency_key": "triage-ferc-2026-05-06-fetch"
  }
 ],
 "created_at": "2026-05-06T07:31:00Z",
 "updated_at": "2026-05-06T07:43:22Z",
 "expires_at": "2026-05-06T19:31:00Z"
}
```

**Utiliser `ulid` pour les `session_id`** : tri lexicographique = tri chronologique, plus pratique pour les archives.

---

## SessionManager — opérations

### `init(agent, task_name, step_total)`

Crée une nouvelle session.

- Génère un `session_id` (ulid)
- Initialise `status: pending`, `step_current: 0`
- Calcule `expires_at = now + 24h`
- Écrit dans SQLite (`~/.openclaw/sessions.db`)
- Retourne le `session_id`

### `load(agent, task_name)`

Charge une session existante pour reprendre une tâche.

- Cherche dans SQLite : `agent = $agent AND task = $task_name AND status IN (pending, in_progress)`
- Si trouvée et `expires_at > now` → retourner la session (réhydratation)
- Si trouvée et expirée → archiver, générer ALERT MOYEN, retourner null
 (ne pas réhydrater une session expirée sans confirmation humaine)
- Si non trouvée → retourner null (créer une nouvelle session avec `init`)

### `upsert(session_id, step, action, result, status)`

Écrit l'état d'une étape de façon atomique.

- Si l'étape est déjà `done` → **ne pas réécrire** (règle STATE-2 — immutabilité)
- Mettre à jour `step_current` et `updated_at`
- Si `status = done` et `step = step_total` → passer la session en `status: done`
- Écriture transactionnelle (begin/commit) — aucune écriture partielle (règle STATE-1)

### `archive(session_id)`

Clôture et archive une session.

- Sérialiser la session complète en JSON indenté dans `~/.openclaw/sessions/<session_id>.json`
- Supprimer l'entrée de SQLite
- Compression gzip recommandée pour les longues sessions

### `expire()`

Tâche de nettoyage planifiée (quotidienne, déclenchée par `def-maintenance`).

- Scanner les sessions dont `expires_at < now` et `status != done`
- Archiver chaque session concernée
- Logger le nombre de sessions expirées

---

## Intégration dans la boucle ReAct

```
[DÉMARRAGE AGENT]
  │
  ├─ load(agent, task_name)
  │   │
  │   ├─ Session trouvée et valide ──→ RÉHYDRATATION
  │   │                  │
  │   │                  ├─ Charger context + decisions
  │   │                  ├─ Valider intégrité (schema_version)
  │   │                  └─ Reprendre à step_current
  │   │
  │   └─ Pas de session ──→ init() → NOUVELLE SESSION
  │
  └─ BOUCLE RÉACT
      │
      ├─ PENSE : charger context, identifier étape suivante non done
      │
      ├─ AGIT : exécuter l'étape
      │       ├─ SUCCESS → upsert(step, action, result, "done")
      │       └─ FAILURE → upsert(step, action, error, "failed") + DIAGNOSTIC
      │
      └─ OBSERVE : toutes les étapes done ? → archive(session_id)
```

**La sauvegarde est systématique après chaque étape**, pas seulement en fin de tâche.
C'est ce qui garantit une reprise fine même en cas de crash brutal.

---

## Idempotence des étapes

Chaque étape d'une tâche doit être **idempotente** : exécutée une ou plusieurs fois, elle produit le même résultat.

### Règle pratique

Avant toute action d'écriture (envoi mail, création tâche Notion, création événement calendrier) :
1. Générer un `idempotency_key` unique et déterministe : `"{task}-{step}-{objet}"` (ex: `"triage-ferc-3-mail-00042"`)
2. Vérifier dans les `decisions` si une entrée avec ce `idempotency_key` existe déjà avec `status: done`
3. Si oui → considérer l'étape comme déjà exécutée, passer à la suivante
4. Si non → exécuter, puis enregistrer avec la clé

Les lectures sont naturellement idempotentes — pas de protection nécessaire.

---

## Stockage

| Backend | Usage | Chemin |
|---|---|---|
| SQLite | Sessions actives (< 24h) | `~/.openclaw/sessions.db` |
| JSON | Archives longue durée, audit, débogage | `~/.openclaw/sessions/<session_id>.json` |

Configuration dans `openclaw.json` section `state` :
```json
{
 "backend": "sqlite",
 "path": "~/.openclaw/sessions.db",
 "archive_dir": "~/.openclaw/sessions/",
 "archive_after_hours": 24,
 "max_sessions": 50
}
```

---

## Règles STATE

**STATE-1 — Sérialisation atomique**
Toute écriture dans le session state est atomique (transaction begin/commit).
Aucune écriture partielle ne doit corrompre un état existant.

**STATE-2 — Immutabilité des étapes complétées**
Une étape marquée `done` ne peut pas être modifiée, seulement lue.
La correction d'une erreur passe par une nouvelle étape de correction, pas par la réécriture de l'historique.

**STATE-3 — Expiration obligatoire**
Toute session a une durée de vie maximale (`expires_at`).
Une session expirée est archivée automatiquement et ne peut pas être réhydratée sans confirmation humaine.

**STATE-4 — Isolation par agent**
Un agent ne peut lire ou écrire que dans ses propres sessions.
Les sessions de `défenseur` ne sont pas accessibles à `intendant`, et vice-versa.

**STATE-5 — Pas de données sensibles dans l'état**
Le session state stocke uniquement des **références** aux données (UID de mail, ID Notion, ID d'événement).
Le contenu réel reste dans le service d'origine. Jamais de corps de mail, de token, ni de donnée personnelle.

---

## Cas d'usage concrets

### Cas 1 — Triage mail interrompu

L'agent trie 80 mails FERC. À l'étape #42 (mail UID `00245`), OpenClaw redémarre.

- Sans état : recommencer depuis le début → risque de double traitement
- Avec état : `load()` trouve la session, `context.last_uid = "00245"`, reprise au mail #43

### Cas 2 — Délégation à un sous-agent avec timeout

`intendant` délègue la classification à `mail-triage`. À mi-parcours, le sous-agent timeout.

- Sans état : le superviseur ne sait pas ce que le sous-agent a fait
- Avec état : le sous-agent a sérialisé sa progression ; le superviseur charge l'état partiel et relance depuis l'étape #4

### Cas 3 — Audit forensique

"Pourquoi l'agent a-t-il archivé ce mail ?"

- Sans état : la décision est perdue dans la fenêtre de contexte expirée
- Avec état : l'archive JSON contient `{ step: 6, action: "archive", uid: "00087", reason: "older than 30 days, tagged: newsletter" }`
