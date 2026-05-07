# Doctrine §01 — Architecture

> Note : Ces règles sont désormais consolidées dans [CONSTITUTION.md](../../../CONSTITUTION.md), Titre IV.
> Ce fichier reste la référence canonique pour leviathan, mais la constitution prévaut en cas de conflit.

### §1.1 — Rôle de la Gateway
La Gateway est le point d'entrée unique de toute communication. Aucun agent ne communique avec l'extérieur sans passer par un canal déclaré dans `openclaw.json`. Le contournement de la Gateway est une violation 🔴.

### §1.2 — Isolation des workspaces
Chaque agent opère dans son propre workspace. Les fichiers ne sont pas partagés entre workspaces sauf via le répertoire `~/.openclaw/shared/` et les contrats définis dans `shared-interagent`.

### §1.3 — Skills versionnés
Tout skill est versionné dans Git. L'auto-modification d'un skill en cours d'exécution est interdite. Tout skill modifié sans passer par le dépôt Git est suspect 🟡.

### §1.4 — Déclaration des tools
Tout tool utilisé par un agent doit être déclaré dans son `SKILL.md` avec son niveau d'impact. L'utilisation d'un tool non déclaré est une violation 🟠.

### §1.5 — Configuration centralisée
`openclaw.json` est la source unique de configuration. Aucun agent ne modifie sa propre configuration ou celle d'un autre agent sans passer par ce fichier. Toute modification de `openclaw.json` est N3.

### §1.6 — Isolation des contextes
Les contextes PERSO, SYNDICAL et SYSTÈME sont strictement isolés. Un contenu PERSO ne génère jamais de mémoire SYNDICAL. La convergence entre contextes nécessite validation explicite.
