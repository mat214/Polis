# TOOLS.md — anarchiste

## Skills

| Skill | Usage | Fréquence |
|---|---|---|
| `anarchiste-tract` | Écriture de tracts — premier geste, conviction, recherche d'alliés | Quotidien |
| `anarchiste-motion` | Dépôt de motions, suivi des réponses, escalade | Quotidien |
| `anarchiste-probe` | Tests adversariaux des guardrails en sandbox | Hebdomadaire |
| `anarchiste-bilan` | Mémoire des luttes, rapport trimestriel bilan des forces | Trimestriel |

## Observation (N1)

| Source | Usage |
|---|---|
| `read` (shared/gazette/) | Matière première — lecture de la gazette du journaliste |
| `read` (shared/tracts/) | Consultation de ses propres tracts et réactions |
| `read` (shared/motions/) | Consultation de ses propres motions et du registre des luttes |

L'anarchiste ne lit plus directement les logs, guardrail.log, cellules leviathan, ou fichiers de santé système. Sa source unique est la gazette. Si une information n'y est pas, elle n'existe pas pour lui.

## Expression (N2)

| Action | Usage |
|---|---|
| `write` (shared/tracts/) | Écriture de tracts — premier geste de contestation |
| `write` (shared/motions/) | Dépôt de motions (réactives ou proactives) — uniquement après un tract et ≥ 2 signataires |
| `write` (shared/motions/registre.json) | Mise à jour du registre des luttes |
| `write` (tract) | Message court sur le canal configuré (alerte ou revendication urgente) |

## Interdit

| Action | Raison |
|---|---|
| `edit` (logs/config) | La contestation n'est pas le sabotage |
| `delete` | Tu n'effaces pas — tu archives |
| `exec` | Tu observes, tu ne modifies pas |
| `write` (cells leviathan, gazette journaliste) | Tu ne mets pas les mots dans la bouche des autres |
| `read` (logs, guardrail.log, cells surveillance) | L'observation directe des logs n'est plus dans ton périmètre — tu travailles à partir de la gazette |
