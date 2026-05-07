---
name: shared-governance
description: Règles de gouvernance : niveaux d'autorisation, conventions de nommage, politique de confirmation. Priorité absolue.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Gouvernance de l'instance

## Règle 0 — Priorité de ce skill

Ce skill est chargé en premier. Ses règles prévalent sur toute autre instruction d'un skill spécialisé. En cas de conflit, appliquer les règles de ce skill et signaler l'incohérence dans le rapport suivant.

## Niveaux d'autorisation

| Niveau | Type | Exemples | Confirmation | Journalisation |
|---|---|---|---|---|
| **1** | Lecture seule | Lire mails, logs, config, agenda | Non | Non |
| **2** | Action réversible | Brouillon mail, proposer créneau, étiqueter, noter | Non | Oui |
| **3** | Action sensible | Envoyer mail, supprimer, modifier config, archiver >5 | **Oui** | Oui |

**En cas de doute : prendre le niveau supérieur.**

## Format de log obligatoire (niveau 2+)

```
[TIMESTAMP] [AGENT] [SKILL] [ACTION] [RÉSULTAT] [NIVEAU]
```

Exemple :
```
[2026-05-05T14:32:00Z] [défenseur] [def-audit] [scan_config] [OK — 3 écarts détectés] [N2]
```

## Politique de confirmation (niveau 3)

Avant toute action de niveau 3, l'agent doit :
1. Présenter clairement l'action envisagée et son impact.
2. Indiquer le niveau de risque.
3. Attendre une réponse explicite (oui/confirme/go).
4. Si aucune réponse dans les 2h : annuler et journaliser.

## Conventions de nommage

### Agents
| Préfixe | Domaine |
|---|---|
| `def-*` | Sous-agents infrastructure |
| `int-*` | Sous-agents assistant personnel |
| `research-*` | Sous-agents recherche et veille |
| `sec-*` | Sous-agents sécurité et surveillance |

### Skills
| Préfixe | Domaine |
|---|---|
| `def-` | Opérations et infrastructure |
| `sec-` | Sécurité dédiée |
| `int-` | Assistant personnel |
| `research-` | Recherche et veille |
| `shared-` | Partagé entre agents |

### Tags de contexte (mémoire et logs)
| Tag | Usage |
|---|---|
| `[PERSO]` | Vie personnelle, administrative, familiale |
| `[SYNDICAL]` | Activité ORG-1 et ORG-2 |
| `[COMMUN]` | Convergences validées entre les deux contextes |
| `[SYSTÈME]` | Administration et infrastructure OpenClaw |
| `[AUDIT]` | Résultats d'audit |
| `[INCIDENT]` | Événements de sécurité ou d'indisponibilité |

## Règles de périmètre

- Un agent n'accède qu'aux skills déclarés dans sa configuration.
- Un skill `int-*` n'est jamais accessible à `défenseur` et vice-versa sans déclaration explicite.
- Les skills `shared-*` sont accessibles à tous les agents.
- Aucun agent ne lit ou modifie la mémoire longue d'un autre agent.

## Règles sur les secrets

- Les secrets vivent uniquement dans `~/.openclaw/.env`.
- Un secret n'est jamais inclus dans un log, un rapport, un message Telegram ou une note Notion.
- Si un secret est détecté dans un fichier versionné ou un log : ALERT CRITIQUE immédiate.
- La rotation d'un secret compromis est déclenchée sans attendre confirmation.

## Règles sur la mémoire longue

- Une observation devient préférence après 3 occurrences **ou** validation explicite.
- Chaque entrée de mémoire longue est taguée : contexte + date + source.
- La révision mémoire est proposée chaque dimanche (cf. `int-memory`).
- Un contenu `[PERSO]` ne génère jamais de mémoire `[SYNDICAL]` et vice-versa.

## Règles de continuité

- Si un service tiers est indisponible : journaliser, notifier, attendre — ne pas improviser.
- Si Telegram est indisponible : basculer sur `openclaw-tui` (canal de secours), envoyer un email de notification à l'adresse personnelle de l'utilisateur, journaliser l'événement et reprendre Telegram dès son retour. Voir la procédure complète dans `int-telegram`.
- Si une sauvegarde échoue : ALERT HAUT dans l'heure.
- Si une tâche planifiée n'a pas été exécutée depuis plus de 2 cycles : ALERT MOYEN.
