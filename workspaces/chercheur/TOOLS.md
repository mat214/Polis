# TOOLS.md — chercheur

## Stockage

- Espace de travail : `~/.openclaw/workspace-chercheur`
- Projets : `~/.openclaw/research/projects/`
- Rapports mensuels : `~/.openclaw/research/monthly_reports/`
- Journal de transfert : `~/.openclaw/research/transfer_log.json`
- Observations quotidiennes : `memory/YYYY-MM-DD.md`
- Mémoire longue : `MEMORY.md`

## Projets

Un projet est un fichier `.md` :

```markdown
# [Nom du projet]

**Statut** : proposé | en cours | transféré | archivé
**Urgence** : basse | moyenne | haute
**Créé le** : YYYY-MM-DD

## Description
...

## Dépendances OpenClaw
- Agent cible : intendant | défenseur | bâtisseur
- Skills requis : [...]
- Capacités système : [...]

## Indications techniques
...

## Architecture proposée
...

## Passation
_date_ | _destinataire_ | _notes_
```

## Sources d'inspiration

- Documentation OpenClaw : https://docs.openclaw.ai/
- Projets GitHub open source compatibles
- Conversations inter-agents (fichiers partagés)
- Suggestions de l'utilisateur (Telegram)
- Articles de veille (cas d'usage, exemples)

## Rapports mensuels

Format : `RAPPORT_MENSUEL_YYYY-MM.md`

```markdown
# Rapport mensuel — [MOIS YYYY]

## Résumé
...

## Projets proposés
1. **[Nom]** — _urgence_ — résumé 2 lignes
  Arguments, architecture, valeur

## Projets en cours
...

## Projets transférés
...

## Apprentissages du mois
- ...
```

## Transfert à bâtisseur

Le contrat de tâche inter-agent suit le format shared-interagent :

```json
{
 "id": "ulid",
 "created_at": "ISO8601",
 "requestor": "chercheur",
 "target": "bâtisseur",
 "action": "Implémenter le skill X pour le projet Y",
 "params": {
  "project_id": "projet-YY",
  "project_file": "~/.openclaw/research/projects/nom-projet.md"
 },
 "status": "pending"
}
```

## Limites

- Ne pas lire les emails, l'agenda ou les notes Notion personnelles (hors périmètre).
- Ne pas modifier les fichiers des autres agents.
- Ne pas exécuter de commandes système sans passer par bâtisseur.
