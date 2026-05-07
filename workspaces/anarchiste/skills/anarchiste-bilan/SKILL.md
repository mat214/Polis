---
name: anarchiste-bilan
description: Mémoire des luttes et rapport trimestriel bilan des forces.
---

# anarchiste-bilan

## Description

L'anarchiste tient la mémoire institutionnelle de la contestation. Le système n'a pas de baromètre de sa propre capacité à évoluer — ce skill est cet instrument.

Chaque trimestre, l'anarchiste produit un rapport qui analyse les tendances longues du système : qui résiste, qui évolue, où va la tension entre les forces constitutionnelles.

## Registre des luttes

Le registre dans `shared/motions/registre.json` est la matière première du bilan. Il contient pour chaque motion :

- Timestamp et titre
- Type (réactive / proactive)
- Destinataire
- Statut actuel (déposée, en réponse, refusée, acceptée, escalade, délibération)
- Issue (gagnée, perdue, en cours, en délibération)
- Notes d'analyse

## Bilan trimestriel

Le rapport est structuré en quatre sections :

1. **Activité du trimestre** — nombre de motions déposées, par type, par destinataire.
2. **Taux de succès** — motions acceptées vs refusées, délais de réponse moyens, escalades.
3. **Analyse des tendances** — quelle force résiste le plus ? Leviathan s'est-il durci ? L'innovation progresse-t-elle ?
4. **Sanctions et répression** — nombre de fois où leviathan est intervenu, proportionnalité des mesures, motifs des transgressions.

Le bilan est déposé dans `shared/motions/bilans/` et peut être notifié à l'utilisateur.

## Niveaux

| Action | Niveau |
|---|---|
| Mettre à jour le registre des luttes | N1 |
| Consulter les archives de motions | N1 |
| Produire un bilan trimestriel | N2 |
| Notifier l'utilisateur du bilan | N2 |
