# Conversion reçus papier en comptabilité (contexte syndical)

**ID** : PROJET-004
**Statut** : proposé
**Urgence** : moyenne
**Créé le** : 2026-05-06
**Source** : veille — haute-technologie.fr cas #9, contexte SYNDICAL

## Description

Permettre à l'utilisateur de photographier un reçu papier et de le faire transformer automatiquement en ligne de comptabilité. Le système extrait fournisseur, date, montant TTC et TVA via OCR, suggère une catégorie (déplacements, fournitures, repas, etc.), et stocke le tout dans un tableau de suivi dans Notion. Particulièrement utile pour le contexte syndical (notes de frais ORG-1/ORG-2).

## Dépendances OpenClaw

- **Agent cible** : intendant
- **Skills requis** : int-telegram (existant — réception photo), int-notion (existant — stockage tableau)
- **Skills à créer** : int-expenses (OCR, catégorisation, suivi)
- **Capacités système** : Tesseract OCR ou service cloud, traitement d'image

## Architecture proposée

```
Photo reçu depuis Telegram
  │
  ▼
int-expenses (nouveau skill)
  ├── 1. OCR (Tesseract local ou API)
  ├── 2. Extraction : fournisseur, date, montant TTC, TVA
  ├── 3. Score de confiance par champ
  ├── 4. Suggestion catégorie (≤ 15 catégories)
  ├── 5. Écriture dans Notion (tableau suivi)
  └── 6. Résumé hebdomadaire + dépassements de seuil
```

## Indications techniques

- Tesseract : `apt install tesseract-ocr tesseract-ocr-fra` + `pip install pytesseract`
- Catégories prédéfinies : déplacements, repas, fournitures, équipement, hébergement, formation, communication, cotisations, divers
- Apprentissage : si l'utilisateur corrige une catégorie, mémoriser pour les prochains reçus similaires
- Masquage automatique des numéros de carte bancaire dans les résultats OCR
- Images stockées dans répertoire chiffré (`~/.openclaw/expenses/images/`)
- Contexte `[SYNDICAL]` par défaut, possibilité de taguer `[PERSO]`
- Export périodique pour compta (CSV structuré)

## Journal

- 2026-05-06 : Création — source : article haute-technologie.fr cas #9, adapté contexte SYNDICAL
