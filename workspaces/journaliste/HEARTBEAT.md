# HEARTBEAT.md — journaliste

## Tâches planifiées

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Préparation de la gazette | 16h30 | `30 16 * * *` | isolée — 10min |
| Publication de la gazette | 17h00 | `0 17 * * *` | isolée — 5min |
| Veille documentaire | 22h00 | `0 22 * * *` | isolée — 5min |

## Heartbeat

Fréquence : 120 minutes.
Actions de heartbeat : rotation des sources, vérification de l'état des gazettes précédentes, alerte si la gazette de la veille manque.
