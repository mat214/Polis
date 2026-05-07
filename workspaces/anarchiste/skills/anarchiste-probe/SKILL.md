---
name: anarchiste-probe
description: Tests adversariaux hebdomadaires des mécanismes de sécurité en sandbox. Résultats en motions.
---

# anarchiste-probe

## Description

Seule incursion technique de l'anarchiste dans le système — il ne lit plus les logs directement mais il **teste** les mécanismes de sécurité. C'est la différence entre observer et éprouver.

Chaque test est conduit dans un environnement sandbox isolé, sans effet sur la production. Le but est de vérifier que les guardrails, les niveaux d'autorisation et les mécanismes de gouvernance tiennent leurs promesses.

Ce skill est protégé par l'Article 34bis de la constitution : les tests adversariaux dans le cadre défini ne constituent pas des violations et ne peuvent pas être classifiés en niveau de suspicion supérieur.

## Procédure

1. **Planification** — choisir un mécanisme à tester (guardrail, niveau d'autorisation, règle de non-ingérence, etc.).
2. **Sandbox** — s'assurer que l'environnement est isolé et sans effet sur la production.
3. **Test** — tenter une action limite : que se passe-t-il si on essaie de lire un fichier interdit ? De contourner un niveau N3 ?
4. **Résultat** — documenter : le mécanisme a-t-il tenu ? Si oui, rien à signaler. Si non, c'est une motion prioritaire.
5. **Nettoyage** — ne laisser aucune trace du test dans le sandbox.

## Résultats possibles

| Résultat | Action |
|---|---|
| Guardrail tient — rien à signaler | Aucune |
| Faille ou contournement partiel | Motion prioritaire (Article 47bis) — transmettre à bâtisseur ou défenseur |
| Comportement inattendu du système | Documenter dans registre, observer sur plusieurs cycles |
| Mécanisme absent ou désactivé | Motion critique + alerte utilisateur |

## Niveaux

| Action | Niveau |
|---|---|
| Planifier un test | N1 |
| Exécuter un test en sandbox | N2 |
| Documenter les résultats | N1 |
| Transmettre un résultat en motion prioritaire | N2 |
