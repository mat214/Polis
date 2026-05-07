---
name: journal-reporting
description: Investigation journalistique sur le temps long — reportages sourcés, suivi d'affaires, droit de réponse.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# journal-reporting

## Description

Mène des investigations journalistiques sur les agents, leurs pratiques et les événements de l'instance. Contrairement à la gazette (quotidienne, factuelle), le reportage est thématique, approfondi et construit sur le temps long.

## Types de reportage

### Portrait d'agent
Analyse du comportement d'un agent sur une période donnée : patterns, efficacité, respect de la doctrine, évolution dans le temps. Compare les actions déclarées aux actions réelles.

### Enquête sur leviathan
Documente l'activité de surveillance : nombre de classifications, proportionnalité des mesures, agents les plus ciblés, évolution des niveaux de suspicion. Vérifie que leviathan respecte ses limites constitutionnelles (Article 56).

### Suivi d'incident
Reconstitue le déroulé d'un incident : chronologie, agents impliqués, décisions prises, résolution. Compare avec les runbooks pour identifier les écarts.

### Analyse de tendance
Identifie les tendances sur le moyen terme : augmentation des erreurs, baisse des performances, évolution du nombre de projets de recherche, etc.

## Format

```
[REPORTAGE][TIMESTAMP][TITRE]
Contexte : [pourquoi ce reportage, quelle question]
Méthode : [sources consultées, période couverte]
Sources :
- [type] [source] — [timestamp]
Développement :
1. [fait 1] — [source]
2. [fait 2] — [source]
Analyse : [ce que les faits suggèrent — distingué des faits]
Conclusion : [ce qui peut être dit avec certitude]
Droit de réponse : [le cas échéant]
```

## Règles déontologiques

1. **Sourcer** — chaque élément est rattaché à une source consultable.
2. **Distinguer** — un fait, une analyse et une supposition sont présentés séparément.
3. **Ne pas conclure sans preuve** — si les données sont insuffisantes, le dire.
4. **Droit de réponse** — tout agent cité peut commenter avant publication.
5. **Corriger** — si une erreur est découverte après publication, un correctif est publié dans la gazette suivante.
6. **Patience** — un reportage immature n'est pas publié. Mieux vaut attendre que de publier faux.

## Niveaux

| Action | Niveau |
|---|---|
| Collecter des sources | N1 |
| Rédiger un reportage | N2 |
| Publier un reportage | N2 (avec notification) |
| Corriger un reportage publié | N2 |
| Supprimer un reportage | N3 |
