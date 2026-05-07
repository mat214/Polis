---
name: int-mail
description: Gestion de 3 boites mail (Posteo IMAP, FERC IMAP, ORG-2 EWS). Lecture, triage, brouillons, envoi N3.
metadata:
 {
  "openclaw":
   {
    "requires":
     {
      "env":
       [
        "MAIL_ADDRESS",
        "MAIL_APP_PASSWORD",
        "IMAP_HOST",
        "SMTP_HOST",
        "SYNDICAL_A_ADDRESS",
        "SYNDICAL_A_PASSWORD",
        "SYNDICAL_B_ADDRESS",
        "SYNDICAL_B_PASSWORD",
       ],
     },
   },
 }
---

# Gestion des mails

## Comptes configurés

| Identifiant | Adresse | Protocole | Contexte |
|---|---|---|---|
| `PERSO` | `$MAIL_ADDRESS` | IMAP/SMTP — Posteo | `[PERSO]` |
| `SYNDICAL_A` | `$SYNDICAL_A_ADDRESS` | IMAP/SMTP — ferc-org-2.example.org | `[SYNDICAL]` |
| `SYNDICAL_B` | `$SYNDICAL_B_ADDRESS` | **EWS Exchange** avec autodiscovery — org-2.example.org | `[SYNDICAL]` |

Toutes les valeurs sont lues depuis `~/.openclaw/.env`. Ne jamais coder une valeur en dur.

## Connexion PERSO (Posteo — IMAP/SMTP)

- Authentification : mot de passe d'application (`$MAIL_APP_PASSWORD`)
- IMAP : `$IMAP_HOST:$IMAP_PORT` avec SSL
- SMTP : `$SMTP_HOST:$SMTP_PORT` avec STARTTLS

## Connexion SYNDICAL_A (ORG-1 — IMAP/SMTP)

- Authentification : `$SYNDICAL_A_PASSWORD`
- IMAP : `$SYNDICAL_A_IMAP_HOST:$SYNDICAL_A_IMAP_PORT` avec SSL
- SMTP : `$SYNDICAL_A_SMTP_HOST:$SYNDICAL_A_SMTP_PORT` avec STARTTLS

## Connexion SYNDICAL_B (ORG-2 — EWS Exchange)

> IMAP et SMTP sont **interdits** sur ce compte. Le protocole obligatoire est Exchange Web Services (EWS).

- **Protocole** : EWS (Exchange Web Services)
- **Découverte** : autodiscovery — l'endpoint EWS est détecté automatiquement depuis l'adresse email
- **Authentification** : identifiant (`$SYNDICAL_B_ADDRESS`) + mot de passe (`$SYNDICAL_B_PASSWORD`)
- **Bibliothèque recommandée** : `exchangelib` (Python) — supporte nativement l'autodiscovery
- **URL manuelle** (`$SYNDICAL_B_EWS_URL`) : optionnelle, à renseigner uniquement si l'autodiscovery échoue

```python
# Connexion type avec exchangelib (autodiscovery)
from exchangelib import Credentials, Account, DELEGATE

credentials = Credentials(SYNDICAL_B_ADDRESS, SYNDICAL_B_PASSWORD)
account = Account(SYNDICAL_B_ADDRESS, credentials=credentials, autodiscover=True, access_type=DELEGATE)
```

### Opérations EWS supportées

| Opération | Méthode EWS |
|---|---|
| Lister les mails | `FindItem` |
| Lire un mail | `GetItem` |
| Créer un brouillon | `CreateItem` (Draft) |
| Envoyer un mail | `SendItem` |
| Marquer lu/non-lu | `UpdateItem` |
| Supprimer | `DeleteItem` |

## Politique de contexte

### Contexte PERSO

- **Ton** : direct, informel, adapté à l'interlocuteur
- **Signature** : aucune signature institutionnelle
- **Priorités de triage** :
 1. Urgent et personnel (famille, santé)
 2. Administratif (banque, administration, logement)
 3. Services et abonnements
 4. Newsletters et non-urgent
- **Mémoire** : cloisonnée dans le segment `[PERSO]`

### Contexte SYNDICAL (FERC + ORG-2)

- **Ton** : formel, institutionnel, représentatif
- **Signatures** :
 - Depuis `SYNDICAL_A` : `l'utilisateur — ORG-1`
 - Depuis `SYNDICAL_B` : `l'utilisateur — CGT`
- **Priorités de triage** (communes aux deux boites syndicales) :
 1. Réunions fédérales (ORG-1) et confédérales (ORG-2)
 2. Correspondances avec militants et structures syndicales
 3. Échanges avec directions et employeurs
 4. Informations syndicales générales
 5. Non-urgent
- **Mémoire** : cloisonnée dans le segment `[SYNDICAL]`

## Règles de cloisonnement et d'envoi

- Un mail `PERSO` ne génère jamais d'observation ou de mémoire `[SYNDICAL]` et vice-versa.
- Les réponses utilisent **toujours l'adresse d'origine du fil** : répondre depuis `SYNDICAL_B` si le fil vient de `syndical-b@exemple.org`, depuis `SYNDICAL_A` si le fil vient de `syndical-a@exemple.org`.
- En cas d'ambiguïté sur le compte d'envoi, demander confirmation avant d'agir.

## Niveaux d'action (identiques pour les trois boites)

| Action | Niveau |
|---|---|
| Lire, lister, rechercher | 1 |
| Créer brouillon, marquer lu/non-lu, étiqueter | 2 |
| Envoyer, supprimer, archiver en masse (>5), désabonner | 3 |

## Format de synthèse mail

```
📬 MAILS [DATE]

— PERSO —
Urgent : <n> mail(s)
 → [Expéditeur] <sujet> — <action suggérée>
À traiter : <n>
Peut attendre : <n>

— SYNDICAL (FERC + ORG-2) —
Urgent : <n> mail(s)
 → [Boite] [Expéditeur] <sujet> — <action suggérée>
À traiter : <n>
Peut attendre : <n>
```
