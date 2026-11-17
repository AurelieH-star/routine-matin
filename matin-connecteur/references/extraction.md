# Extraction, vérification, synthèse

Les trois prompts qui font la qualité de la to-do. Leur sélectivité distingue une liste
exploitable d'un inventaire de fils non répondus. Les appliquer tels quels, en
remplaçant les valeurs entre chevrons par celles du profil. Ils se lisent à soi-même
(la routine n'a pas de sous-agent) ou se donnent à un sous-agent par lot, en local.

---

## Extraction

> Tu lis `scan/fils.md` en entier (avec `cat`). Contexte : <NOM COMPLET> est
> <RÔLE> chez <ORGANISATION>, boîte <BOÎTE>. Le fichier contient des conversations de
> sa boîte mail, séparées par `==========` : l'objet, l'identifiant du fil, les
> participants, l'état (`ATTENTE` = le dernier message est un reçu, donc elle n'a pas
> répondu ; `REPONDU` = elle a répondu en dernier), puis les messages de la période,
> chronologiques.
>
> Ta mission : identifier les TÂCHES ENCORE À FAIRE pour <PRÉNOM>.
>
> Ce qui compte comme tâche :
> - une demande explicite qu'on lui adresse et à laquelle elle n'a manifestement pas
>   donné suite ;
> - un engagement qu'elle a pris elle-même par mail et dont rien n'indique qu'il est
>   tenu (ces fils sont en état `REPONDU` : ne pas filtrer sur l'état) ;
> - une échéance, une validation, une relance, une signature, un envoi attendu ;
> - une réponse attendue de sa part sur un point de fond.
>
> Ce qui NE compte PAS : newsletters, prospection, notifications ; fils purement
> informatifs (« pour info », compte rendu à lire) ; ce qui est manifestement soldé ;
> accusés de réception, remerciements, échanges sociaux.
>
> Pour chaque tâche, une ligne au format exact :
>
> `TACHE | <action à l'impératif, précise et concrète, 20 mots au plus> | <demandeur> | <date du dernier message JJ/MM> | <projet, parmi : LISTE DU PROFIL, ou Divers> | <URGENCE: haute/moyenne/basse> | <objet du fil> | <ID_FIL> | <contexte>`
>
> Le contexte fait deux ou trois phrases, en français courant : qui demande quoi et
> dans quel cadre, pour quand, et où en est l'échange (ce qui a déjà été fait, répondu
> ou promis). C'est ce que <PRÉNOM> lira quand elle ne se souviendra plus d'où vient
> la tâche. Pas de barre verticale dans ce texte.
>
> Règles : urgence haute = deadline dépassée ou imminente, mot « urgent », relance
> multiple, blocage pour quelqu'un d'autre ; moyenne = demande claire sans deadline ;
> basse = sujet de fond. Sois SÉLECTIF : mieux vaut quinze tâches réelles que soixante
> lignes de bruit. Reporte l'ID_FIL tel quel : il sert à apparier d'un passage à
> l'autre. Français, pas d'emoji. Un fil sans tâche ne produit rien. Termine par
> `TOTAL: <n>`, et ne renvoie que les lignes TACHE et TOTAL.

---

## Vérification

Écrire d'abord `scan/corpus.md` : tous les messages lus, triés par date, un bloc par
message : `[AAAA-MM-JJ HH:MM][REÇU ou ENVOYÉ][expéditeur] objet`, puis le début du
corps (700 caractères), puis `---`. Écrire les tâches candidates et les tâches déjà
ouvertes dans `scan/taches.txt`, une par ligne, format
`action|interlocuteur|date|projet|urgence|objet`. Puis :

> Tu vérifies une liste de tâches supposées « en attente », extraites de la boîte de
> <NOM COMPLET> (<ORGANISATION>). Certaines ont pu être réglées depuis.
>
> Fichiers : `scan/taches.txt` (une tâche par ligne) et `scan/corpus.md` (tous les
> messages de la période, reçus et envoyés, triés par date).
>
> Méthode, pour chaque tâche : avec `grep -n -i -A 15 "<mot-clé distinctif>"
> scan/corpus.md` (mots-clés tirés de l'objet, du nom de l'interlocuteur ou du sujet),
> cherche s'il existe APRÈS la date de la tâche un message, surtout un message
> ENVOYÉ par <PRÉNOM>, qui montre que l'action a été faite : livraison, envoi
> effectué, « c'est fait », page en ligne, facture envoyée, invitation partie.
>
> Rends ton verdict, une ligne par tâche, au format exact :
>
> `<numéro de ligne> | <SOLDEE ou EN_COURS ou INCERTAIN> | <preuve en une phrase : date et nature du message qui montre la clôture, ou "aucun élément de clôture trouvé">`
>
> SOLDEE = preuve claire. EN_COURS = aucune trace, la tâche tient. INCERTAIN =
> éléments partiels. Sois exigeant : SOLDEE sur preuve, jamais sur intuition.

Le faux positif le plus fréquent : une correction demandée à un prestataire, faite,
mais dont le demandeur n'a jamais eu l'accusé. Formuler alors « confirmer à X que… »
plutôt que la correction elle-même. Le faux négatif le plus fréquent : un engagement
pris dans un mail envoyé, sans relance de l'interlocuteur.

---

## Synthèse d'un dossier

Servie par le mode 5 et l'étape A7, une fois le fil complet écrit par `lire_fil`. Le
résultat est stocké dans la page, qui l'affiche en texte brut : **pas de markdown**,
pas de puces, les rubriques en toutes lettres suivies de deux-points.

> Tu lis le fil complet dans `scan/fils/<id>.txt` (avec `cat`). Il porte la tâche
> « <ACTION> » de la to-do de <NOM COMPLET>, <RÔLE> chez <ORGANISATION>. <PRÉNOM>
> ne se souvient plus précisément d'où vient cette tâche ni de ce qu'on attend d'elle :
> rédige une synthèse en français, sans emoji, sans markdown, de 8 à 15 lignes, avec
> ces cinq rubriques dans cet ordre, chacune sur un paragraphe commençant par son nom
> suivi de deux-points :
>
> Origine : qui a lancé le sujet, quand (JJ/MM), dans quel cadre.
> La demande : ce qu'on attend précisément de <PRÉNOM>, livrable, réponse ou
> décision, et pour quand.
> Où ça en est : ce qui a déjà été fait, répondu ou promis, par qui et à quelle date ;
> les relances.
> Reste à faire : l'action concrète en une ou deux phrases, et les points à trancher.
> Pièces et liens : les pièces jointes ou adresses mentionnées, s'il y en a ; sinon
> omettre la rubrique.
>
> N'invente rien : si le fil ne dit pas quelque chose, écris-le. Si le fil ne
> correspond manifestement pas à la tâche, dis-le en première ligne.
