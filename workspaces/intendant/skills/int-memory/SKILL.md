---
name: int-memory
description: Mémoire longue intendant. Segments [PERSO]/[SYNDICAL]/[SYSTÈME], cloisonnement, rétention.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Mémoire longue

## Fichier de mémoire

La mémoire longue est stockée dans `~/.openclaw/memory/intendant.json`. 
Elle est incluse dans la sauvegarde quotidienne gérée par `défenseur`.

## Segments

| Segment | Contenu | Exemples |
|---|---|---|
| `[PERSO]` | Préférences, habitudes, contexte de vie personnelle | Préférence de restaurant, historique de santé, projets personnels |
| `[SYNDICAL]` | Contexte de l'activité syndicale | Positions ORG-2, calendrier des instances, contacts militants |
| `[SYSTÈME]` | Observations sur l'instance OpenClaw | Incidents passés, décisions d'architecture, état du système |

## Règles de cloisonnement strictes

- Une observation issue d'un mail `PERSO` ne va jamais dans `[SYNDICAL]` et vice-versa.
- `[SYSTÈME]` est accessible en lecture par les deux agents. Seul `défenseur` peut y écrire.
- Le segment `[SYNDICAL]` ne contient jamais de données personnelles (santé, famille, finances).
- En cas de doute sur le segment cible : demander confirmation avant d'enregistrer.

## Opérations

| Opération | Niveau |
|---|---|
| Lire la mémoire (tous segments) | 1 |
| Ajouter une observation dans `[PERSO]` ou `[SYNDICAL]` | 2 |
| Modifier ou supprimer une entrée existante | 3 |
| Vider un segment entier | 3 — confirmation obligatoire |

## Format d'une entrée mémoire

```json
{
 "id": "[SEGMENT]-YYYY-MM-DD-NNN",
 "segment": "[PERSO|SYNDICAL|SYSTÈME]",
 "date": "YYYY-MM-DD",
 "source": "[mail|agenda|telegram|agent]",
 "contenu": "texte libre de l'observation",
 "expiration": "YYYY-MM-DD ou null"
}
```

## Politique de rétention

| Type d'entrée | Rétention |
|---|---|
| Préférences et habitudes | Indéfinie (jusqu'à suppression manuelle) |
| Contexte événementiel (réunion passée, mail traité) | 90 jours |
| Observations d'incident `[SYSTÈME]` | 1 an |
| Données sensibles (santé, finances) | 30 jours — jamais en clair plus longtemps |

## Révision mensuelle

Chaque 1er lundi du mois, `défenseur` déclenche une révision : 
- Entrées expirées supprimées automatiquement (N2).
- Entrées sans date d'expiration > 6 mois proposées pour archivage ou suppression (N3).
- Résultat inclus dans le REPORT `weekly`.
