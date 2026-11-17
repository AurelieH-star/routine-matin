# Ce qui ne porte jamais de tâche

Appliquer cette liste aux résultats de `fils_depuis` **avant** d'extraire. Un fil
écarté à tort reviendra au scan suivant si l'expéditeur relance : la liste peut être
large sans risque.

## Expéditeurs

Écarter tout fil dont le dernier message reçu vient d'une adresse qui contient :

```
noreply  no-reply  notification  notifications  newsletter  mailer  bounce
donotreply  alerte  alert  digest  @mail.  support-site  scanner@  visio@
```

et les plateformes qui n'écrivent qu'en automatique : réseaux sociaux (LinkedIn,
Instagram, Facebook), outils de tickets et de projet quand ils notifient (Jira,
Trello, Notion, Asana), outils de paie et de facturation, transporteurs, billetterie,
hébergeurs, prospection commerciale.

## Objets

Écarter tout fil dont l'objet contient :

```
newsletter  désabonn  webinar  webinaire  votre facture  reçu de paiement
alerte  nouvelle publication  digest  se désinscrire  confirmation d'inscription
bulletin  rapport hebdo
```

et tout objet qui commence par une réponse de calendrier ou une absence :

```
Accepté  Refusé  Provisoire  Annulé  Décliné  Réponse automatique
Absent du bureau  Actuellement en congé  Congés annuels
Accepted  Declined  Tentative  Canceled  Automatic reply  Out of office
```

## Les mails du dispositif lui-même

Les mails du matin que la routine envoie citent toutes les tâches : une recherche par
mots-clés les ramène à chaque fois. Toujours écarter les objets qui commencent par
`Matin du`, `To-do du`, `To-do :`, `Brief du`.

## Ce qui reste malgré tout du bruit

Les fils purement informatifs (« pour info », un compte rendu à lire), les accusés de
réception, les remerciements, les échanges sociaux. Ils passent le filtre : c'est
l'extraction (`extraction.md`) qui les laisse de côté, pas cette liste.

Les expéditeurs et objets propres à la personne s'ajoutent dans `profil.md`, section
`bruit`, jamais ici.
