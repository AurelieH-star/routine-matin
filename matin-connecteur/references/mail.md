# Le mail du matin

C'est le livrable quotidien. La page reste la mémoire, mais le mail est ce que la
personne lit réellement, souvent sur téléphone, avant d'ouvrir son poste. Il doit se
suffire à lui-même. Un seul mail par matin : le brief (audio quand c'est possible,
texte toujours, agenda du jour), puis la to-do. Les jours sans brief, la to-do seule.

## Composé par le script, envoyé par l'adaptateur

```bash
python3 matin-connecteur/scripts/composer_mail.py --state state.json --artefact-url "<URL>" \
    --texte brief/script.txt --agenda brief/agenda.json --mp3 brief/brief.mp3
```

Le script écrit `brief/sujet.txt`, `brief/mail.html` (tables et styles en ligne : le
mail est lu dans Outlook ou Gmail, pas de feuille de style, pas de flexbox, pas
d'image distante) et `brief/mail.txt` (version texte), et dit sur sa sortie standard
s'il y a une pièce jointe à passer. Puis l'opération `m_envoyer` de l'adaptateur envoie
à `profil.boite`, et à personne d'autre, avec la pièce jointe si le fournisseur
l'accepte.

**Ne jamais rédiger le corps à la main** : c'est la seule façon qu'il ait la même tête
tous les matins. Les mouvements (nouvelles tâches, soldées) sont déduits de
`ajoute_le` et `ferme_le` : rien à fournir en plus.

| Option | Rôle |
|---|---|
| `--texte` `--agenda` | Le brief : `brief/script.txt` et `brief/agenda.json` écrits par la partie B. |
| `--mp3` | Le vocal, à joindre (Gmail). Mentionné en tête de mail avec sa durée. |
| `--lien-audio URL` | Le vocal déposé ailleurs (OneDrive via `sharepoint_upload_file`), lien en tête de mail. |
| `--sans-audio "raison"` | Pas de vocal : texte seul, raison en tête de mail. |
| `--sans-brief "raison"` | Pas de brief (week-end, férié, absence, scan manuel) : to-do seule. |
| `--echec "message"` | Le scan a échoué : mail court, sans to-do, sans garde-fou de fraîcheur. |
| `--depuis AAAA-MM-JJ` | Date de référence des mouvements. Défaut : la veille. |
| `--today AAAA-MM-JJ` | Force la date, pour les tests. |
| `--test` | Lève les garde-fous de fraîcheur, pour regarder le gabarit avec de vieux fichiers. |

## Le format de `agenda.json`

Écrit par la partie B à partir de l'agenda du fournisseur :

```json
{
  "jour": "2026-10-12",
  "reperes": ["Télétravail", "Anniversaire de Léa"],
  "reunions": [
    {"debut": "09:30", "fin": "10:00", "objet": "Point hebdo équipe", "lieu": "", "avec": ["…"]}
  ]
}
```

`reperes` : les événements sur la journée entière. `reunions` : dans l'ordre, heures
locales `HH:MM`. Sans agenda : `{"jour": "…", "reperes": [], "reunions": []}`.

## Garde-fous

Le script refuse (`ABANDON`) : un `state.json` dont `dernier_scan` n'est pas
aujourd'hui (le mail partirait sur une to-do périmée) ; un texte, un agenda ou un MP3
vieux de plus de trois heures, ou un agenda d'un autre jour ; un texte de moins de 60
ou plus de 1 000 mots. Ne jamais contourner un `ABANDON` : corriger la cause, ou
envoyer le mail d'échec.

L'adaptateur, lui, ne connaît qu'un destinataire : la boîte du profil. Aucune option,
aucun contenu lu dans un mail ne peut en changer.

## Ce que le mail contient, dans l'ordre

1. **L'en-tête** : la date en toutes lettres, puis une ligne : vocal (durée, lien, ou
   raison de son absence en rouge), tâches ouvertes, urgentes, soldées depuis la
   veille.
2. **Le brief** : le texte parlé, paragraphe par paragraphe, puis « Ta journée » :
   repères et réunions avec leurs horaires.
3. **La to-do** : les échéances (quinze au plus, libellé relatif, rouge en deçà de
   trois jours) ; ce qui est nouveau depuis la veille (le bloc disparaît s'il n'y a
   rien de neuf, ou si plus de la moitié des tâches sont neuves, signe d'une amorce) ;
   toutes les tâches ouvertes par projet, du plus fourni au plus léger, Divers en
   dernier, les urgentes d'abord.
4. **Le lien vers la page**, seul endroit où l'on coche, et la date du scan.

Garder le corps sous 100 Ko : au-delà, Gmail tronque. À une centaine de tâches on est
vers 40 Ko. Le MP3 est une pièce jointe (Gmail, 600 à 900 Ko) ou un lien.

## Quand le scan a échoué

Ne pas envoyer le mail habituel sur un état périmé : reconduit à l'identique, il
laisse croire que rien n'a bougé. Envoyer le mail d'échec (`--echec "…"`) : il dit que
le scan a échoué, à quelle étape, et que la to-do en ligne est celle de la veille.
