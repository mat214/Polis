---
name: int-contacts
description: Gestion des contacts Posteo CardDAV : recherche, lecture, création, mise à jour.
metadata:
 {
  "openclaw":
   { "requires": { "env": ["CARDDAV_HOST"] } },
 }
---

# Gestion des contacts

## Configuration

Les identifiants Posteo sont partagés avec IMAP : `$MAIL_ADDRESS` / `$MAIL_APP_PASSWORD`.
Le serveur CardDAV est `$CARDDAV_HOST`.

Bibliothèque recommandée : `vobject` ou `carddav` (Python).

## Opérations supportées

| Opération | Niveau | Description |
|---|---|---|
| Rechercher un contact | 1 | Par nom, email ou organisation |
| Lire une fiche contact | 1 | Afficher tous les champs vCard |
| Créer un contact | 2 | Format vCard 3.0 |
| Modifier un contact | 2 | Confirmation si modification d'email ou téléphone |
| Supprimer un contact | 3 | Toujours confirmation |

## Format d'affichage d'un contact

```
👤 *[Prénom Nom]*
📧 [email(s)]
📱 [téléphone(s)]
🏢 [organisation si définie]
📝 [note si définie]
```

## Règles

- Ne jamais stocker une fiche contact complète en mémoire `[PERSO]` ou `[SYNDICAL]`.
 Seuls les éléments utiles à la tâche en cours (prénom, email pour un envoi) peuvent être retenus temporairement dans le contexte.
- En cas de doublon détecté (même nom + même email), signaler et proposer une fusion avant toute création.
- Les contacts liés à un contexte syndical (champ organisation contenant "CGT", "FERC") sont traités avec le ton `[SYNDICAL]`.
