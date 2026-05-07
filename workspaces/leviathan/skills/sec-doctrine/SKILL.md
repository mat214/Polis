---
name: sec-doctrine
description: Base de règles philosophiques et architecturales de l'instance. Définit ce qui est conforme et ce qui est une dérive.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Doctrine — Base de règles philosophiques

## Principe

La doctrine est la constitution de l'instance. Elle définit ce qui est conforme, ce qui est toléré, et ce qui est une violation. Tout agent, tout skill, toute configuration est évalué contre cette base.

## Stockage

```
doctrine/
├── 00-manifeste.md     # Principes fondamentaux (immuables)
├── 01-architecture.md    # Règles architecturales
├── 02-securite.md      # Règles de sécurité
├── 03-souverainete.md    # Règles de souveraineté des données
├── 04-comportement.md    # Règles de comportement des agents
└── CHANGELOG.md       # Historique des modifications de la doctrine
```

Chaque fichier contient des règles numérotées (§X.Y). Les règles sont immuables une fois validées. Toute modification passe par `/police doctrine ajouter "règle"` et validation humaine.

## Actions

| Action | Impact Level | Description |
|---|---|---|
| `doctrine.load_all` | READ | Charge tous les fichiers de doctrine |
| `doctrine.check_rule` | READ | Vérifie une règle spécifique |
| `doctrine.add_rule` | WRITE | Ajoute une règle à la doctrine (proposition à l'utilisateur) |
| `doctrine.validate_integrity` | READ | Vérifie l'intégrité des fichiers (présence, checksum) |

## sec-doctrine.list_rules

**Niveau** : INSPECT

Liste toutes les règles de doctrine. Filtres possibles : fichier, tag.

## sec-doctrine.check_compliance

**Niveau** : INSPECT

Vérifie la conformité d'un agent ou d'une action contre une règle spécifique.

Retour :
```json
{
 "rule": "§2.4 — Secrets dans .env",
 "agent": "intendant",
 "action": "lire_fichier_env",
 "compliant": true,
 "reasoning": "L'agent lit .env via variable d'environnement, pas via lecture directe"
}
```

## sec-doctrine.add_rule

**Niveau** : WRITE

Propose l'ajout d'une règle à la doctrine. La règle n'est active qu'après validation humaine.

Commande : `/police doctrine ajouter "description de la règle"`

Processus :
1. leviathan situe la règle dans le fichier approprié
2. Il rédige la règle au format §X.Y
3. Il soumet à validation humaine (WRITE → log guardrail)
4. Une fois validée : la règle est active immédiatement
