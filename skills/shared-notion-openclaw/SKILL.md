---
name: shared-notion-openclaw
description: Accès carnet Notion OPENCLAW : écriture défenseur, lecture seule intendant.
metadata:
 {
  "openclaw": {
   "requires": { "env": ["NOTION_TOKEN", "NOTION_DB_OPENCLAW_ID"] },
  },
 }
---

# Carnet de notes OpenClaw — Notion

## Base de données

- **Identifiant** : `NOTION_DB_OPENCLAW`
- **Variable** : `$NOTION_DB_OPENCLAW_ID` (lue depuis `~/.openclaw/.env`)
- **Token** : `$NOTION_TOKEN` (commun avec les autres bases Notion)

## Connexion API

- API : Notion API v1 (`https://api.notion.com/v1`)
- Authentification : `Authorization: Bearer $NOTION_TOKEN`
- Version : `Notion-Version: 2022-06-28`

## Usage

Ce carnet est le **registre officiel de l'instance OpenClaw**. Il contient :

- La documentation du système (agents, skills, architecture)
- Les rapports d'audit et de maintenance produits par `défenseur`
- Les rapports d'incident
- Les décisions d'architecture validées
- Les notes de configuration

## Conventions de nommage des pages

| Type de page | Format du titre |
|---|---|
| Rapport d'audit | `[AUDIT] YYYY-MM-DD — <sujet>` |
| Rapport d'incident | `[INCIDENT] YYYY-MM-DD — <sujet>` |
| Rapport de maintenance | `[MAINTENANCE] YYYY-MM-DD — <sujet>` |
| Documentation | `[DOC] <composant> — <sujet>` |
| Décision d'architecture | `[DECISION] YYYY-MM-DD — <sujet>` |
| Note de configuration | `[CONFIG] <composant> — <sujet>` |

## Niveaux d'action

| Action | Niveau |
|---|---|
| Lire, lister, rechercher des pages | 1 |
| Créer une page (rapport, doc, note) | 2 |
| Modifier ou supprimer une page existante | 3 |

## Règles de comportement

- `défenseur` peut créer des pages de type AUDIT, INCIDENT, MAINTENANCE, CONFIG sans confirmation (niveau 2).
- `défenseur` ne peut pas modifier ou supprimer une page existante sans confirmation (niveau 3).
- `intendant` peut lire et rechercher librement (niveau 1). Toute écriture dans ce carnet est réservée à `défenseur`.
- Aucun agent ne supprime une page de documentation sans confirmation explicite.

## Contexte mémoire

Les observations issues de ce carnet ne sont jamais stockées dans `[PERSO]` ou `[SYNDICAL]`.
Elles sont enregistrées dans le segment `[SYSTÈME]` si `int-memory` est chargé.
