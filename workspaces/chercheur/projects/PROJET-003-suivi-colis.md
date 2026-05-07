# Suivi de colis et alertes

**ID** : PROJET-003
**Statut** : proposé
**Urgence** : moyenne
**Créé le** : 2026-05-06
**Source** : veille — cas d'usage haute-technologie.fr

## Description

Détecter automatiquement les numéros de suivi de colis dans les emails entrants (via int-mail), interroger les API des transporteurs, et notifier l'utilisateur sur Telegram uniquement pour les événements significatifs : retard, tentative de livraison échouée, passage en douane. Maintenir un tableau de bord dans Notion avec l'état de chaque colis.

## Dépendances OpenClaw

- **Agent cible** : intendant
- **Skills requis** : int-mail (existant — scan emails), int-telegram (existant — alertes), int-notion (existant — tableau de bord)
- **Skills à créer** : int-parcels (extraction, API transporteurs, suivi)

## Architecture proposée

```
Email entrant (int-mail)
  │
  ▼
int-parcels (nouveau skill)
  ├── 1. Regex extraction : numéros de suivi (Colissimo, Chronopost, Mondial Relay, La Poste)
  ├── 2. Interrogation API transporteur
  ├── 3. Harmonisation des statuts
  ├── 4. Écriture tableau de bord Notion (int-notion)
  └── 5. Alerte Telegram si événement significatif
```

## Indications techniques

- Patterns regex courants :
 - Colissimo : `^[0-9]{13}$` ou `^[A-Z]{2}[0-9]{9}FR$`
 - Chronopost : `^[0-9]{13}$`
 - Mondial Relay : `^[A-Z0-9]{8,10}$`
 - La Poste : `^[0-9]{13}$`
- API transporteurs : nécessite clés API ou scraping (mode dégradé)
- Fréquence d'interrogation adaptative : quotidienne si en transit, toutes les heures si livraison prévue dans les 24h
- Alertes uniquement pour : `retard`, `tentative_echouee`, `douane`, `livre`
- Pas de notification nocturne (22h-7h)
- Niveaux : extraction email N1, interrogation API N2, alerte Telegram N2

## Journal

- 2026-05-06 : Création — source : article haute-technologie.fr cas #5
