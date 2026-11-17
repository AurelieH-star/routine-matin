# Routine du matin : to-do et brief vocal, version connecteur

Chaque matin, une routine Claude Code lit votre boîte mail, met à jour une to-do que
vous cochez dans une page claude.ai, prépare un brief parlé de votre journée (agenda,
derniers échanges avec les gens que vous voyez, tâches qui pressent), et vous envoie le
tout dans un seul mail, à vous-même. Ce dossier est la version **connecteur** de ce
dispositif : elle fonctionne avec le connecteur officiel Microsoft 365 ou le connecteur
Gmail de claude.ai, sans clé d'API, sans application Azure, sans script réseau.

Le dossier voisin `matin/` est la version d'origine, qui passe par l'API Microsoft
Graph et des scripts Python. Même logique, même page, même mail ; seule la façon de
lire et d'envoyer le courrier change.

## Ce que ça fait, ce que ça ne fait jamais

Tous les matins (6h45 par défaut, réglable) :

1. **La to-do.** Les mails depuis le dernier passage sont relus ; les demandes qui
   vous sont faites et les engagements que vous avez pris sont extraits ; ce qui a été
   réglé depuis est écarté ; le reste est fusionné avec la liste existante, puis publié
   dans votre page « To-do » sur claude.ai. Vous y cochez ce qui est fait, vous changez
   les priorités, vous ajoutez une tâche, vous cliquez sur une tâche pour retrouver
   qui l'a demandée et demander une synthèse du dossier.
2. **Le brief**, les jours ouvrés : votre agenda du jour, ce qu'il faut avoir en tête
   avant chaque réunion (tiré des derniers échanges avec les participants), les
   échéances et retards de la to-do. Rédigé pour être écouté, synthétisé en MP3 quand
   c'est possible.
3. **Un seul mail**, de vous à vous : le brief (audio si le fournisseur le permet,
   texte dans tous les cas), votre journée, la to-do.

Ce que la routine **ne fait jamais**, quoi qu'il y ait dans vos mails : répondre à
quelqu'un, mettre quelqu'un en copie, transférer, marquer comme lu, supprimer. Le seul
message qu'elle écrit est le mail du matin, à votre adresse. Une phrase dans un mail
qui s'adresse à « Claude » est de la matière à résumer, pas une consigne.

## Ce qu'il vous faut

| Besoin | Pourquoi |
|---|---|
| Un compte claude.ai **Pro, Max, Team ou Enterprise** | Les routines (exécution automatique le matin) ne sont pas disponibles sur le plan Free. Sans routine, tout marche quand même en lançant « lance mon matin » à la main. |
| Le connecteur **Microsoft 365** ou **Gmail** branché sur votre compte claude.ai | C'est par lui que Claude lit votre boîte. Microsoft 365 exige un compte professionnel (pas d'adresse outlook.com ou hotmail) et un consentement de l'administrateur de votre tenant. |
| Pour le mail du matin, le **droit d'envoi** sur ce connecteur | Microsoft 365 : l'administrateur doit avoir consenti le scope `Mail.Send` (sinon le connecteur est en lecture seule et il n'y a pas de mail, seulement la page). Gmail : l'envoi fait partie du connecteur. |
| Pour l'agenda du brief | Microsoft 365 : inclus (`outlook_calendar_search`). Gmail : brancher aussi le connecteur **Google Calendar** ; sans lui, le brief se limite à la to-do et aux échanges récents. |
| Un **dépôt GitHub** à vous, créé depuis ce modèle | La routine clone un dépôt à chaque exécution : c'est là que vivent le skill, le miroir de l'état et les exports. |
| **Claude Code** (application de bureau, ou claude.ai/code) | Pour le premier lancement et pour l'usage à la main dans la journée. |

## Installation

### 1. Brancher le connecteur

Sur [claude.ai/customize/connectors](https://claude.ai/customize/connectors), connectez
Microsoft 365 ou Gmail (et Google Calendar si Gmail). Dans une conversation, demandez
« quels outils de messagerie as-tu ? » : vous devez voir des outils `outlook_…` ou
`search_threads` / `get_thread` / `send_message`. Si `outlook_send_mail` n'apparaît
pas, votre tenant n'a pas consenti l'écriture : la page fonctionnera, pas le mail.
Demandez alors à votre administrateur le consentement des scopes d'écriture de l'app
« M365 MCP Server for Claude » (voir la [doc Anthropic](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide)).

### 2. Créer votre dépôt

Sur la page GitHub de ce modèle, **Use this template**, dépôt privé à votre nom. Ne
mettez jamais d'identifiant dedans : la version connecteur n'en a pas besoin.

### 3. Premier lancement, dans Claude Code

Ouvrez le dépôt dans Claude Code et dites : **« Installe ma routine du matin. »** Le
skill `matin-connecteur/SKILL.md` enchaîne, en vous posant cinq questions :

- il repère le fournisseur d'après les outils présents, lit leurs schémas, et note
  ce qu'il peut faire (envoi ou pas, pièces jointes ou pas, agenda ou pas) ;
- il remplit `references/profil.md` : qui vous êtes, votre rôle, votre adresse, vos
  grands projets (ils deviennent les filtres de la page), les expéditeurs à ignorer ;
- il fait un premier scan sur deux à trois semaines, crée la page « To-do », l'épingle,
  et vous l'envoie ;
- il vous propose le prompt de routine, prêt à coller.

Comptez un quart d'heure, le temps du premier scan.

### 4. Créer la routine

Sur [claude.ai/code/routines](https://claude.ai/code/routines), **New routine** :

| Champ | Valeur |
|---|---|
| Prompt | le contenu de `references/prompt-routine.md`, tel que le premier lancement l'a rempli (trois valeurs : votre prénom, l'URL de la page, le fournisseur) |
| Dépôt | le vôtre, créé à l'étape 2 |
| Environnement | Sans la voix, **Default** suffit. Pour la voix, un environnement dont le réseau est en **Custom** avec exactement ces domaines : `pypi.org`, `files.pythonhosted.org`, `api.msedgeservices.com`, `speech.platform.bing.com`. En Custom, tout ce qui n'est pas listé est bloqué, pypi compris ; sans ces domaines, le brief part en texte seul |
| Connecteurs | **ne garder que** le connecteur mail (et calendrier). La routine utilise les outils d'un connecteur inclus sans vous demander, écritures comprises : retirez tout le reste |
| Déclencheur | planifié, chaque jour, à l'heure où vous voulez le mail moins un quart d'heure (l'exécution dure 10 à 25 minutes) |
| Modèle | Sonnet |

Ces réglages se font à la main : aucune session Claude n'a accès aux réglages d'un
environnement. À la fin du premier lancement, Claude vous donne la liste exacte à
reporter ici, domaines compris, prête à copier.

Puis **Run now**, et ouvrez l'exécution pour lire ce qui s'est passé. Un statut vert
dit que la session s'est terminée sans erreur d'infrastructure, pas que le mail est
parti : lisez le résumé final de la session.

### 5. Tous les matins

Le mail arrive dans votre boîte, de vous à vous. Objet : « Matin du mardi 13 octobre :
31 tâches ouvertes, 3 urgentes ». Le week-end et les jours fériés, la to-do part seule.
Si le scan a échoué, un mail court le dit et la page garde sa date de la veille :
elle vous prévient d'elle-même au bout de trois jours sans mise à jour.

### 6. Dans la journée

Dans Claude Code, avec le dépôt ouvert : « lance le scan » (mise à jour immédiate),
« ajoute une tâche : … », « j'ai fait X », « qu'est-ce qu'il me reste ? », ou la
demande copiée depuis le volet de la page (« Synthèse to-do : … ») pour obtenir la
synthèse complète d'un dossier.

## Ce qui change selon le fournisseur

| | Microsoft 365 | Gmail |
|---|---|---|
| Lecture des mails | `outlook_email_search`, `read_resource` | `search_threads`, `get_thread` |
| Agenda | `outlook_calendar_search` | connecteur Google Calendar (séparé) |
| Envoi du mail | `outlook_send_mail`, si `Mail.Send` consenti ; sinon brouillon ou rien | `send_message` |
| Vocal en pièce jointe | **non** (aucune pièce jointe sur les outils d'écriture) : le MP3 est déposé sur OneDrive avec un lien dans le mail si `sharepoint_upload_file` existe, sinon texte seul | oui, jusqu'à 25 Mo |
| En session interactive | chaque envoi demande votre accord | chaque envoi demande votre accord |
| En routine | sans approbation | sans approbation |
| Compte personnel | refusé | accepté |

Le détail de chaque opération est dans `references/fournisseurs/m365.md` et
`gmail.md`.

## Ce que vous perdez par rapport à la version scripts

La version d'origine (`matin/`) lit la boîte avec des scripts déterministes : regroupement
par conversation, filtrage du bruit, corpus de vérification, tout cela se fait hors du
modèle, vite et à l'identique chaque matin. En mode connecteur, c'est le modèle qui
appelle les outils un par un. Conséquences assumées : fenêtre de scan courte (trois
jours, jamais soixante), filtrage du bruit par une liste (`references/bruit.md`),
corpus de vérification reconstitué par le modèle avant la passe de contrôle. Le résultat
est le même, l'exécution un peu plus longue et un peu plus coûteuse en jetons.

## Quand ça ne marche pas

| Symptôme | Cause probable | Quoi faire |
|---|---|---|
| Pas de mail, page à jour | connecteur en lecture seule (`outlook_send_mail` absent) | consentement `Mail.Send` par l'admin ; en attendant, la page suffit |
| Pas de mail, page pas à jour | la routine n'a pas tourné ou a échoué | ouvrir l'exécution sur la page Routines et lire le résumé ; vérifier que le connecteur est toujours connecté |
| « Host not in allowlist » ou « bloqué par le réseau de l'environnement » dans l'exécution | un script a tenté le réseau direct | seule la voix en a besoin : réseau de l'environnement en Custom avec les quatre domaines de l'étape 4, ou accepter le texte seul |
| Brief en texte, pas d'audio | `api.msedgeservices.com` absent des domaines autorisés (c'est l'hôte de la voix depuis le 10 octobre 2026, l'ancien `speech.platform.bing.com` répond 403), ou pièce jointe impossible (Microsoft 365) | normal ; voir le tableau ci-dessus |
| La page a l'air ancienne | trois matins sans mise à jour | la page l'affiche d'elle-même ; vérifier la routine |
| Une tâche revient alors que vous l'avez cochée | jamais, par construction : une tâche cochée ne ressort pas | si ça arrive, c'est un bug à signaler |

## Produire le bundle `.skill`

Pour installer le skill sans passer par Git, depuis la racine du dépôt :

```bash
zip -r matin-connecteur.skill matin-connecteur -x '*__pycache__*' '*.pyc'
```

Le bundle est un zip dont le premier niveau est le dossier du skill.

## Contenu du dossier

| Chemin | Rôle |
|---|---|
| `SKILL.md` | Le moteur : premier lancement, modes, déroulé du matin, garde-fous |
| `references/profil.md` | Votre profil, rempli au premier lancement |
| `references/prompt-routine.md` | Le prompt de la routine, à coller tel quel |
| `references/fournisseurs/m365.md`, `gmail.md` | Comment chaque opération se fait avec chaque connecteur |
| `references/extraction.md` | Ce qui compte comme tâche, la vérification, la synthèse d'un dossier |
| `references/redaction.md` | Comment écrire le brief parlé |
| `references/artefact.md` | La page : état, comportement, volet de détail |
| `references/mail.md` | Le mail du matin : contenu, composition, garde-fous |
| `references/bruit.md` | Expéditeurs et objets à ignorer |
| `scripts/purger_etat.py` | Purge des tâches faites anciennes (pur JSON) |
| `scripts/rendu_todo.py` | Rendu HTML de la to-do pour le mail (pur) |
| `scripts/composer_mail.py` | Assemble le HTML du mail du matin, que le connecteur envoie |
| `scripts/synthese.py` | Texte du brief vers MP3 (edge-tts) |
| `assets/page-template.html` | Le gabarit de la page |
