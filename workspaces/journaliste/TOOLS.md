# TOOLS.md — journaliste

## Lecture de sources
| Outil | Usage | Niveau |
|---|---|---|
| `read` (logs) | Consultation guardrail.log, historiques | N1 |
| `read` (shared) | Lecture fichiers partagés inter-agents | N1 |
| `read` (cells) | Consultation cellules leviathan | N1 |

## Écriture
| Outil | Usage | Niveau |
|---|---|---|
| `write` (gazette) | Publication gazette dans shared/gazette/ | N2 |
| `write` (reportage) | Publication reportage d'investigation | N2 |
| `write` (status) | Mise à jour journaliste-status.json | N1 |

## Notification
| Outil | Usage | Niveau |
|---|---|---|
| `announce` | Résumé de la gazette à l'utilisateur | N2 |

## Interdit
| Outil | Raison |
|---|---|
| `edit` (logs) | Ne jamais modifier les sources |
| `delete` (gazette) | Archivage seulement, pas de suppression sans N3 |
| `exec` | Aucune exécution de commande système |
