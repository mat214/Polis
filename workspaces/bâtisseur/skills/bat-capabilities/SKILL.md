---
name: bat-capabilities
description: Auto-provisioning 6 étapes : détection → plan → exécution → test → intégration → notification. Orchestre bat-*.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Auto-provisioning — le cycle complet

## Principe

Ce skill formalise le cycle par lequel `bâtisseur` détecte un manque de capacité
(une dépendance manquante, un script à créer, un service à mettre en place),
construit un plan d'acquisition, l'exécute pas à pas, et vérifie le résultat.

**Les étapes sont enregistrées dans le session state** (shared-state) pour permettre
la reprise en cas d'interruption.

---

## Le cycle en 6 étapes

### ÉTAPE 1 — DÉTECTION

**Déclencheurs possibles :**
- L'agent reçoit une demande ou identifie un besoin qu'il ne peut pas satisfaire
- Un skill (int-mail, int-telegram, int-daily-brief...) a besoin d'une dépendance manquante
- Un script échoue parce qu'un outil requis n'est pas installé
- L'audit quotidien détecte une mise à jour critique à appliquer
- Demande explicite de l'utilisateur

**Action :** Identifier précisément ce qui manque, générer un DIAGNOSTIC.

```
[DIAGNOSTIC][TIMESTAMP][bâtisseur]
Symptôme : {description du besoin non satisfait}
Manque  : {dépendance, script, service ou outil requis}
Contexte : {quel skill ou agent en a besoin, dans quel but}
Solution : {plan d'acquisition proposé}
```

### ÉTAPE 2 — PLANIFICATION

Construire le plan d'acquisition complet avec classification de chaque étape :

**Structure de l'ACTION_PLAN :**

```
[ACTION_PLAN][TIMESTAMP][bâtisseur]
Contexte : {problème ou besoin identifié}

Étapes :
 1. [S|N|ST] {action} — {impact attendu} — {rollback}
 2. ...

Catégories par étape :
 - apt install : S si catalogue approuvé, N sinon
 - pip install : S (toujours dans venv)
 - création script : S (dans /opt/openclaw/scripts/)
 - modification skill int-* : N (notification intendant)
 - création service système : ST (Human Gate)

Score de risque max : {score de l'étape la plus risquée}
Confirmation requise : oui si ≥ 1 étape ST ou N avec score ≥ 70
```

### ÉTAPE 3 — EXÉCUTION CONTRÔLÉE

Pour chaque étape du plan, dans l'ordre :

```
POUR CHAQUE ÉTAPE :
  │
  ├─ Session state : marquer étape "in_progress"
  │
  ├─ S  : exécuter directement + log N2
  │     → upsert(step, action, result, "done")
  │
  ├─ N (score < 70) : exécuter + log N2
  │     → upsert(step, action, result, "done")
  │
  ├─ N (score ≥ 70) ou ST : Human Gate
  │     → upsert(step, action, "en attente confirmation", "gated")
  │     → attendre confirmation
  │     → si approuvé : exécuter + upsert "done"
  │     → si refusé : upsert "skipped" + continuer ou arrêter selon impact
  │
  └─ ÉCHEC : upsert "failed" + rollback automatique si disponible
        Si rollback échoue → ALERT HAUT + attendre instruction
```

### ÉTAPE 4 — TEST

Pipeline de test obligatoire pour toute création ou modification (voir bat-scripts) :

```
1. Test statique (syntaxe, analyse)
2. Test isolé (/tmp/openclaw-test/ avec données de test)
3. Si applicable : vérification d'intégration (le skill cible fonctionne-t-il ?)
4. Monitoring post-déploiement (15 min)
```

Si le test échoue → rollback de l'étape → DIAGNOSTIC → correction → retest.

### ÉTAPE 5 — INTÉGRATION

- Commit git du ou des scripts créés/modifiés (bat-scripts)
- Enregistrement dans l'inventaire (bat-audit)
- Mise à jour de README.md dans `/opt/openclaw/scripts/`
- Si modification d'un skill `int-*` : notification à `intendant`
 via le session state partagé

### ÉTAPE 6 — NOTIFICATION ET DOCUMENTATION

```
📋 *Nouvelle capacité acquise*

Capacité : {description}
Étapes  : {n} dont [S: n, N: n, ST: n]
Scripts  : {liste des scripts créés ou modifiés}
Dépendances : {liste des paquets installés}
Services : {liste des services créés}

Rapport déposé dans Notion OPENCLAW.
```

Dépôt dans Notion OPENCLAW :
- Format : `REPORT` (shared-reporting)
- Type : `capability`
- Titre : `[CAPACITÉ] YYYY-MM-DD — {description courte}`

---

## Exemple concret — Transcription vocale Telegram

```
DÉTECTION : intendant reçoit un message vocal depuis Telegram
      → int-telegram ne sait pas traiter les messages vocaux
      → bâtisseur est notifié via le session state

PLANIFICATION :
 Manque identifié :
  1. ffmpeg (conversion audio) : apt, catalogue approuvé → S
  2. openai-whisper (transcription) : pip venv, catalogue approuvé → S
  3. audio-transcribe.py : création script → S
  4. Modification int-telegram (ajout handler vocal) → N (score 15)

 Score max : 15 (modification skill int-*)
 Confirmation : NON (score < 70, tout le reste est S)

EXÉCUTION :
 1. apt install ffmpeg → S → exécuté
 2. pip install openai-whisper dans venv → S → exécuté
 3. Créer audio-transcribe.py → S → exécuté, commit git
 4. Modifier int-telegram → N (score 15) → exécuté, commit git

TEST :
 - Syntaxe valide (shellcheck, py_compile)
 - Test isolé avec fichier .ogg de test → transcription correcte
 - Monitoring 15 min : aucun service tombé

INTÉGRATION :
 - Script committé : /opt/openclaw/scripts/audio/audio-transcribe.py
 - intendant notifié de la modification de int-telegram
 - README.md mis à jour

NOTIFICATION :
 ✅ Nouvelle capacité acquise : transcription vocale Telegram
 Dépendances installées : ffmpeg, openai-whisper
 Script créé : audio-transcribe.py
 Intégré dans : int-telegram (handler vocal)
```

---

## Interaction avec les autres agents

`bâtisseur` peut modifier les skills d'autres agents (`int-*`, `shared-*`),
mais uniquement dans le cadre du cycle d'auto-provisioning, avec ces règles :

| Cas | Classification | Notification |
|---|---|---|
| Ajout d'une ligne d'import dans un skill existant | N (score 15) | Notification à l'agent concerné |
| Ajout d'un handler de commande dans int-telegram | N (score 20) | Notification + commit git |
| Création d'un nouveau fichier de skill | ST | Human Gate |
| Suppression de code existant dans un skill | N (score 30) | Rollback documenté obligatoire |
| Modification de AGENTS.md (workspace bâtisseur) | ST | Human Gate + confirmation explicite |

---

## Classification des actions

| Action | Guardrail | Catégorie |
|---|---|---|
| `detect_gap` | READ | — |
| `build_acquisition_plan` | READ | — |
| `execute_step_S` | WRITE | S |
| `execute_step_N` | WRITE_SENSITIVE | N (avec score calculé) |
| `execute_step_ST` | IRREVERSIBLE | ST (Human Gate) |
| `rollback_step` | WRITE | N (selon étape) |
| `register_capability` | WRITE | S |
| `notify_agent` | WRITE | S |
