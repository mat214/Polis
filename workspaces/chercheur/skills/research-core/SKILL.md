---
name: research-core
description: Gestion de la liste de projets de recherche. list_projects, propose, priorise, archive.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Research Core — Gestion des projets

## Vision

Ce skill est le cœur de l'agent chercheur. Il gère le cycle de vie complet des projets de recherche : de la proposition à l'archivage en passant par le transfert à bâtisseur.

## Structure de stockage

```
~/.openclaw/research/
├── projects/          # Projets de recherche (max 20)
│  ├── PROJET-001-nom-court.md
│  └── ...
├── monthly_reports/       # Rapports mensuels
│  ├── RAPPORT_MENSUEL_2026-05.md
│  └── ...
├── transfer_log.json      # Historique des transferts
└── template.md         # Template pour nouveaux projets
```

Les fichiers dans `workspaces/researcher/projects/` servent de template pour le déploiement vers `~/.openclaw/research/projects/`.

## Tools déclarés

### research.list_projects

**Niveau** : 1

Affiche la liste des projets avec leur statut. Filtres optionnels : statut, urgence.

Format de sortie :
```
📋 *Projets de recherche* (n/20)

## En cours
- PROJET-003 — suivi-colis — 🔴 haute — en cours
- PROJET-002 — liste-courses — 🟡 moyenne — en cours

## Proposés
- PROJET-001 — transcription-vocale — 🟢 basse — proposé

## Transférés
- (aucun)

## Archivés
- (aucun)
```

### research.propose

**Niveau** : 2

Enrichit la liste de projets. Déclenché par :
- Commande `/chercheur propose "idée"` de l'utilisateur
- Détection automatique via research-learn
- Rapport mensuel

Validation :
1. Vérifier que le projet n'existe pas déjà (nom ou description similaire)
2. Attribuer un ID (PROJET-NNN)
3. Définir l'urgence
4. Ajouter les dépendances OpenClaw connues

### research.prioritize

**Niveau** : 2

Change l'ordre de traitement d'un projet. Le déplacement vers le haut de la liste marque le projet comme prioritaire.

### research.transfer_to_engineer

**Niveau** : 2

Transfère un projet validé à bâtisseur :

1. Vérifier que le projet est en statut `proposé` ou `en cours`
2. Créer un fichier de tâche dans `~/.openclaw/shared/tasks/` (format shared-interagent)
3. Mettre à jour le fichier projet (statut = `transféré`)
4. Journaliser dans `transfer_log.json`
5. Notifier l'utilisateur via le canal configuré

### research.archive

**Niveau** : 3 (confirmation requise)

Archive un projet :
- Déplacer vers statut `archivé`
- Garder le fichier (ne pas supprimer)
- Si le quota de 20 projets est atteint, archiver automatiquement les plus anciens inactifs

### research.archive

**Niveau** : 3 (confirmation requise)

Archive un projet :
- Déplacer vers statut `archivé`
- Garder le fichier (ne pas supprimer)
- Si le quota de 20 projets est atteint, archiver automatiquement les plus anciens inactifs

## Statuts d'un projet

| Statut | Description | Actions possibles |
|---|---|---|
| `proposé` | Idée en attente de validation | prioriser, transférer, archiver |
| `en cours` | En cours d'étude ou développement | transférer, archiver |
| `transféré` | Confié à bâtisseur | archiver |
| `archivé` | Projet clos ou abandonné | restaurer (N3) |

## Format du projet

Chaque fichier projet suit ce template (accessible dans `template.md`) :

```markdown
# [Nom du projet]

**ID** : PROJET-NNN
**Statut** : proposé | en cours | transféré | archivé
**Urgence** : basse | moyenne | haute
**Créé le** : YYYY-MM-DD
**Source** : suggestion utilisateur | veille | apprentissage

## Description
...

## Dépendances OpenClaw
- Agent cible :
- Skills requis :
- Capacités :

## Architecture proposée
...

## Indications techniques
...

## Journal
- YYYY-MM-DD : Création
- YYYY-MM-DD : [événement]
```
