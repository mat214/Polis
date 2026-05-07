# Onboarding contacts et réunions (contexte syndical)

**ID** : PROJET-005
**Statut** : proposé
**Urgence** : basse
**Créé le** : 2026-05-06
**Source** : veille — haute-technologie.fr cas #4 + #8, contexte SYNDICAL

## Description

Automatiser l'onboarding d'un nouveau contact ou adhérent syndical : détection de la demande (email ou message Telegram), création du contact CardDAV (via int-contacts), planification de la réunion de bienvenue (via int-calendar), envoi de l'email de bienvenue personnalisé (via int-mail), et création de la page projet dans Notion (via int-notion). Applicable aux contextes ORG-1 et ORG-2.

## Dépendances OpenClaw

- **Agent cible** : intendant
- **Skills requis** : int-mail (existant), int-contacts (existant), int-calendar (existant), int-notion (existant)
- **Skills à créer** : int-onboarding (orchestration des skills existants)

## Architecture proposée

```
Déclencheur : email "nouvel adhérent" ou message Telegram
  │
  ▼
int-onboarding (nouveau skill — orchestre les skills existants)
  ├── 1. Extraction : nom, email, téléphone, secteur
  ├── 2. Création contact CardDAV (int-contacts) — vérification doublon
  ├── 3. Email de bienvenue personnalisé (int-mail) — N3
  ├── 4. Proposition créneaux réunion (int-calendar) — 3 créneaux
  ├── 5. Page projet Notion (int-notion) — objectifs, contacts, calendrier
  ├── 6. Confirmation Telegram
  └── 7. Rappel Slack J-1 (si intégré)
```

## Indications techniques

- Aucun nouveau skill système requis : pure orchestration des skills PA existants
- Particularité ORG-2 : l'email de bienvenue doit partir depuis la bonne boite (EWS Exchange)
- Détection de doublon avant création contact (int-contacts le fait déjà)
- Modèles d'email de bienvenue versionnés dans le dépôt (différents par secteur : juridique, association, établissement)
- Suivi : tâche créée via int-tasks pour suivre la réunion à J+30
- Contexte `[SYNDICAL]` systématique
- Niveaux : extraction N1, création contact N2, envoi email N3

## Journal

- 2026-05-06 : Création — source : article haute-technologie.fr cas #4 + #8, contexte SYNDICAL
