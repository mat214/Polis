# Liste de courses partagée via Telegram

**ID** : PROJET-002
**Statut** : proposé
**Urgence** : haute
**Créé le** : 2026-05-06
**Source** : veille — cas d'usage haute-technologie.fr

## Description

Permettre à l'utilisateur d'ajouter des articles à une liste de courses depuis Telegram par une simple phrase : « ajoute du lait demi-écrémé à la liste de courses ». Le système extrait l'article, la quantité et la marque, dédoublonne et catégorise (frais, épicerie, hygiène, etc.). La liste est persistée et accessible depuis Telegram.

## Dépendances OpenClaw

- **Agent cible** : intendant
- **Skills requis** : int-telegram (existant), int-notion (existant)
- **Skills à créer** : int-grocery (gestion liste de courses)

## Architecture proposée

```
Message Telegram : "ajoute du lait bio à la liste de courses"
  │
  ▼
int-telegram ── détection mots-clés "ajoute" / "manque" / "achète"
  │
  ▼
int-grocery (nouveau skill)
  ├── 1. Extraction : article + quantité + marque
  ├── 2. Confirmation : "Ajouter « Lait bio - 1L » à la liste ?" (N2)
  ├── 3. Dédoublonnage et catégorisation
  └── 4. Persistance dans Notion via int-notion
```

## Indications techniques

- Détection par pattern matching simple sur les messages Telegram
- Catégories prédéfinies : `frais`, `épicerie`, `hygiène`, `bébé`, `animaux`, `ménage`
- Dédoublonnage : normalisation (casse, pluriel, marque) avant comparaison
- Stockage : base Notion dédiée (nouvelle DB courses) ou page structurée dans le carnet perso
- Commandes Telegram : `/courses` → affiche la liste, `/courses vide` → efface la liste (N3)
- La liste peut être exportée en texte brut pour impression ou partage

## Journal

- 2026-05-06 : Création — source : article haute-technologie.fr cas #2
