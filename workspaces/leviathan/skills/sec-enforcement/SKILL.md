---
name: sec-enforcement
description: Mesures correctives et restrictives. Passage à l'action quand la doctrine est violée.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Enforcement — Mesures correctives

## Principe

Quand une violation est confirmée, leviathan ne se contente pas de la signaler : il agit. Les mesures sont proportionnelles au niveau de menace et réversibles sauf indication contraire.

## Actions

| Action | Impact Level | Description |
|---|---|---|
| `enforcement.log_level` | SURVEILLER | Passe un agent en logging DEBUG |
| `enforcement.session_mirror` | SURVEILLER | Copie les messages d'une session vers `cells/` |
| `enforcement.tool_timeout` | RESTREINDRE | Réduit le timeout d'un tool spécifique |
| `enforcement.tool_block` | RESTREINDRE | Bloque temporairement un tool |
| `enforcement.agent_block` | ISOLEMENT | Bloque les actions non-lecture d'un agent |
| `enforcement.agent_quarantine` | ISOLEMENT | Isole complètement un agent |
| `enforcement.agent_release` | RESTREINDRE | Lève les restrictions sur un agent |
| `enforcement.amnesty` | ISOLEMENT | Réinitialise tous les niveaux de suspicion |

## sec-enforcement.log_level

**Niveau** : SURVEILLER

Augmente le niveau de logging d'un agent pour obtenir plus de visibilité :

1. Identifier l'agent cible
2. Proposer l'augmentation (DEBUG) dans le rapport quotidien
3. Appliquer : la recommandation est que l'opérateur modifie `openclaw.json` → `logging.level = "debug"` pour cet agent
4. Journaliser dans la cellule de l'agent

## sec-enforcement.session_mirror

**Niveau** : SURVEILLER

Configure un miroir de session : toutes les interactions d'un agent sont copiées dans un fichier témoin sous `cells/` :

1. Créer un fichier `cells/mirror_agent.log`
2. Y recopier les messages échangés (contexte partagé uniquement — pas les données privées)
3. Journaliser l'activation du miroir

## sec-enforcement.tool_block

**Niveau** : RESTREINDRE — notification requise

Bloque temporairement un tool spécifique pour un agent :

1. Identifier le tool et l'agent
2. Documenter la raison dans la cellule
3. Proposer le blocage à l'utilisateur (notification)
4. Appliquer après notification (ou 10 min sans réponse)

## sec-enforcement.agent_block

**Niveau** : ISOLEMENT — Human Gate + timeout 10 min

Bloque toutes les actions non-lecture d'un agent :

1. ALERT CRITIQUE vers l'utilisateur
2. Proposition : *"Agent X atteint niveau 🔴. Je propose blocage des actions non-lecture. Confirmation ?"*
3. Timeout 10 min
4. Si pas de réponse → isolement par défaut
5. Si refus → maintenir surveillance renforcée

L'isolement signifie :
- L'agent ne peut plus exécuter d'actions WRITE, WRITE_SENSITIVE ou IRREVERSIBLE
- La configuration est verrouillée
- Les tools d'envoi (Telegram, mail) sont désactivés
- Seule la lecture de fichiers partagés est maintenue

## sec-enforcement.agent_release

**Niveau** : RESTREINDRE

Lève les restrictions sur un agent (commande utilisateur `/police liberer "agent"`) :

1. Vérifier que l'utilisateur est bien à l'origine de la demande
2. Restaurer les niveaux de logging et timeouts par défaut
3. Supprimer les blocages de tools
4. Réinitialiser le niveau de suspicion à 🟢
5. Journaliser la libération

## sec-enforcement.amnesty

**Niveau** : ISOLEMENT — Human Gate obligatoire

Réinitialise tous les niveaux de suspicion.

1. Demander confirmation à l'utilisateur (IRREVERSIBLE → Human Gate)
2. Si confirmé : réinitialiser toutes les cellules
3. Reclasser tous les agents en 🟢
4. Journaliser comme événement majeur
