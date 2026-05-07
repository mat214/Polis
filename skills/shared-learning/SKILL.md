---
name: shared-learning
description: Cycle d'apprentissage pour les agents défenseur et bâtisseur : observation, validation, mémorisation.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Apprentissage système — défenseur et bâtisseur

## Principe

Les agents défenseur et bâtisseur apprennent des patterns au fil du temps, comme l'intendant avec ses segments mémoire. Le cycle ajoute une étape de publication avant la mémorisation définitive :

```
OBSERVATION → HYPOTHÈSE → VALIDATION → PUBLICATION → MÉMOIRE LONGUE → AUTOMATISATION PROGRESSIVE
```

La validation croisée (LEARN-5) n'est plus un veto — c'est une fenêtre de contestation. Chaque agent est responsable de ses apprentissages. Le contrôle vient de la transparence, pas de l'autorisation.

## Storage

Les observations sont stockées dans le daily journal du workspace :
- `workspace-défenseur/memory/YYYY-MM-DD.md`
- `workspace-bâtisseur/memory/YYYY-MM-DD.md`

Les faits durables et préférences vont dans `MEMORY.md` du workspace respectif.

## Ce qui peut être mémorisé

Toute observation récurrente (3 occurrences) ou validée par l'utilisateur peut être mémorisée. Les observations isolées ne le sont jamais (LEARN-1).

## Cycle de révision

- **Guardian et Sys** : chaque lundi, proposer les mémorisations, supprimer les obsolètes.
- Rétention : 90 jours pour les contextes, indéfinie pour les préférences.

## Validation croisée (LEARN-5)

Toute proposition est publiée `[PROVISOIRE]` avec fenêtre de contestation 48h.

**Mécanisme** : après 3 occurrences ou validation utilisateur, l'agent écrit la règle dans `MEMORY.md` en `[PROVISOIRE]` (T+48h) et dépose la proposition dans `shared/learning_proposals/`. Le journaliste intègre à la gazette. Tout agent peut contester par motion (Article 47bis). Sans contestation → `[PERMANENT]`. Motion déposée → escalade standard, l'utilisateur tranche. Override possible par « oui valide » ou « confirme ».

**LEARN-5** : validation croisée obligatoire. Le journaliste documente les issues dans la gazette.

## Règles

- **LEARN-1** : jamais d'observation unique comme préférence. 3 occurrences requises.
- **LEARN-2** : jamais de secret en mémoire (Article 10).
- **LEARN-3/4** : en cas de doute, demander. La révision est proposée, jamais imposée.

## Rétroaction utilisateur (FEEDBACK — Article 49bis)

Défini à l'Article 49bis. Le présent SKILL.md précise les aspects opérationnels.

**Enregistrement** : écrire dans `shared/feedback/YYYY-MM-DD-agent-enseignement.md` :

```
[FEEDBACK][TIMESTAMP][AGENT]
Contexte : [déclencheur] | Comportement : [action] | Correction : [parole utilisateur]
Enseignement : [règle générale actionnable]
Type : [règle_comportement | préférence_utilisateur | correction_contextuelle]
Statut : [provisoire]
```

**Règles** : FEED-1 à FEED-5 définies à l'Article 49bis de la Constitution.
