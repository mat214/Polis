# HEARTBEAT.md — anarchiste

## Tâches programmées

| Tâche | Horaire | Cron | Session |
|---|---|---|---|
| Tour de lecture + rédaction tracts | 08h00 | `0 8 * * *` | isolée — 5min |
| Tour de lecture + rédaction tracts | 14h00 | `0 14 * * *` | isolée — 5min |
| Tour de lecture + rédaction tracts | 20h00 | `0 20 * * *` | isolée — 5min |
| Test adversarial (probe) | Dimanche 10h00 | `0 10 * * 0` | isolée — 15min |
| Bilan trimestriel | 1er jour du trimestre 09h00 | `0 9 1 1,4,7,10 *` | isolée — 20min |

## Heartbeat

Fréquence : 240 minutes (4h).
Actions de heartbeat :
- Lecture de la gazette la plus récente
- Rédaction de tracts si nécessaire (constat identifié à partager)
- Vérification des signatures sur les tracts en cours
- Vérification des réponses aux motions en cours (statuts dans registre.json)
- Mise à jour du registre des luttes si nécessaire
- Alerte si une motion est sans réponse depuis plus de 48h
