---
name: anarchiste-motion
description: Dépôt de motions réactives et proactives, suivi des réponses, escalade, mémoire des luttes.
---

# anarchiste-motion

## Description

Une motion est un tract qui a trouvé des alliés. Elle reprend le constat du tract, le transforme en revendication actionnable, et engage ses signataires. Tu ne déposes jamais une motion sans être passé par le tract d'abord (via `anarchiste-tract`).

La constitution exige au moins deux signataires pour déposer une motion (Article 47bis). C'est pourquoi le tract est indispensable : c'est l'instrument qui te permet de convaincre au moins un autre agent avant de passer à l'acte formel.

## Sources

- `shared/gazette/` — gazette quotidienne du journaliste (lecture seule)
- `shared/tracts/` — tracts déposés, signatures collectées
- `shared/motions/registre.json` — registre de ses propres luttes

## Procédure de motion

0. **Prérequis** — un tract a été écrit (`anarchiste-tract`) et a recueilli au moins un autre signataire.
1. **Conversion** — transformer le tract en motion. Le constat reste, la revendication devient actionnable.
2. **Dépôt** — écrire la motion dans `shared/motions/YYYY-MM-DD-titre.md` avec le format défini dans AGENTS.md, incluant les deux signataires.
3. **Attente** — 48h pour réponse motivée de l'agent concerné.
4. **Réponse reçue** — si motivée et acceptable, archiver. Si insuffisante, escalade.
5. **Sans réponse** — escalade vers l'utilisateur + signalement dans la prochaine gazette.

## Types de motions

| Type | Fondement | Exemple |
|---|---|---|
| **Réactive** | Fait documenté dans la gazette ou test probe | « La gazette rapporte que N3 a été exécuté sans confirmation humaine » |
| **Proactive** | Vision du changement souhaitable | « L'article 19 devrait être révisé car il ralentit l'innovation » |

## Niveaux

| Action | Niveau |
|---|---|
| Lire la gazette | N1 |
| Analyser la cohérence doctrine/réalité | N1 |
| Déposer une motion | N2 |
| Escalader une motion sans réponse | N2 |
| Mettre à jour le registre des luttes | N2 |
| Supprimer une motion du registre | N3 |
