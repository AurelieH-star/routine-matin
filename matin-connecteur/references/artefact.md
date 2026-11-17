# La page « To-do »

La page est à la fois la surface de lecture et la mémoire du dispositif. Ce qu'elle
retient, les cases cochées et les tâches ajoutées à la main, est la seule information
que le scan ne peut pas reconstruire.

## Un seul artefact, une seule URL

Créé au premier lancement (titre `To-do`, icône `📋`, `capabilities: {artifact: {}}`),
épinglé, et son URL écrite dans `profil.md`. Ne jamais en créer un second : republier
avec `url`. Ne jamais repasser d'icône ensuite.

`capabilities: {artifact: {}}` autorise la page à enregistrer de nouvelles versions
d'elle-même quand la personne coche une case. Conséquence : **toujours relire la page
avant de la réécrire**, sinon on écrase des cases cochées depuis le dernier passage.
Publication refusée pour conflit : relire, refusionner, republier ; ne jamais forcer.

## L'état embarqué

Dans la page, un bloc `<script type="application/json" id="todo-state">`. Pour
publier un nouveau scan : remplacer le contenu de ce seul bloc dans
`assets/page-template.html`, rien d'autre.

```json
{
  "version": 1,
  "dernier_scan": "2026-10-12T05:02:00Z",
  "fenetre_depuis": "2026-10-09",
  "fournisseur": "m365",
  "boite": "camille@exemple.fr",
  "taches": [ { "...": "voir ci-dessous" } ],
  "clos": [ { "id": "…", "id_fil": "…", "action": "…", "ferme_le": "…", "ferme_par": "…" } ]
}
```

| Champ d'une tâche | Rôle |
|---|---|
| `id` | Stable d'un scan à l'autre : 10 premiers caractères du sha1 de `id_fil + "|" + action normalisée`. Ajout manuel : `man-<horodatage>`, généré par la page. |
| `action`, `qui`, `date`, `projet`, `fil`, `id_fil` | Le libellé (verbe à l'infinitif, une seule chose, une ligne), le demandeur, la date du dernier message (JJ/MM), le projet (un de ceux du profil, ou Divers), l'objet et l'identifiant du fil. |
| `origine` | `outlook`, `gmail` ou `manuel`. Une tâche manuelle n'est jamais retrouvée par un scan. |
| `statut`, `ferme_par`, `ferme_le`, `preuve` | `ouvert` ou `fait` ; `maxime` (valeur héritée : coché à la main par la personne) ou `scan` ; la date ; la phrase de preuve pour une clôture par le scan. **Une tâche `ferme_par: "maxime"` ne doit jamais être rouverte par un scan.** |
| `urgence`, `urgence_manuelle`, `rang` | `haute`, `moyenne`, `basse` ; `true` dès que la personne a changé la priorité sur la page (le scan n'y touche plus) ; position posée à la main dans sa bande (jamais modifiée par le scan). |
| `echeance` | Date ISO si une date réelle existe, sinon `null`. |
| `ajoute_le` | Date du scan qui a fait apparaître la tâche. Jamais rafraîchie : elle porte l'ancienneté. |
| `contexte` | Deux ou trois phrases posées à la création : qui demande quoi, pour quand, où ça en est. Affiché dans le volet. Jamais réécrit par un scan. |
| `synthese`, `synthese_le`, `synthese_demandee` | La synthèse rédigée à la demande (mode 5 ou A7), sa date, et la date posée par la page quand la personne clique sur « Demander une synthèse ». |

`clos` est le registre des tâches purgées : l'identifiant, le fil et le libellé
tronqué, de quoi reconnaître une tâche qui reviendrait. C'est `scripts/purger_etat.py`
qui y écrit, jamais la page ni la main.

## La page

Partir de `assets/page-template.html`, complet et fonctionnel : CSS, rendu, cases à
cocher, menu de priorité, flèches de rang, filtres par projet, champ d'ajout, volet de
détail, republication. Ne pas le redessiner à chaque scan. Le gabarit est un fragment
(sans `<!doctype>`), l'outil Artifact ajoute le squelette ; quand la page se republie
elle-même, `document4()` reconstruit un document complet. Ne pas toucher à ce
mécanisme.

Au clic :
- cocher → `statut: "fait"`, `ferme_par: "maxime"`, republication ; décocher → retour
  à `ouvert` ;
- changer la priorité → `urgence`, `urgence_manuelle: true`, `rang: null` ;
- flèche → déplacement à l'intérieur de sa bande de priorité, rangs explicites ;
- saisir une tâche → ajout `origine: "manuel"`, republication ;
- cliquer sur le texte d'une tâche (ou une ligne du bandeau d'échéances) → le volet de
  détail : demandé par, dernier message, dans la liste depuis, fil, échéance,
  « En quoi ça consiste » (`contexte`, à défaut `preuve`), « Synthèse de Claude » ;
- « Demander une synthèse à Claude » → `synthese_demandee` = date du jour,
  republication ; la routine rédige au prochain passage, et le volet affiche la
  demande à coller dans Claude (« Synthèse to-do : … ») pour l'avoir tout de suite.
  L'identifiant du volet ouvert vit dans le `sessionStorage` : sans cela la
  republication refermerait le volet sous le clic ;
- lecteur sans droit d'écriture → contrôles désactivés et mention explicite.

Ordre d'affichage : priorité, puis rang, puis échéance, puis alphabet. Le mail trie
pareil. Pas de regroupement par projet dans la liste (les projets sont des filtres),
un bandeau « Échéances » en haut, les tâches faites dans un repli en bas (7 jours
après une coche, 30 après une clôture par le scan, elles passent dans `clos`).

Le texte d'avertissement de la page au-delà de trois jours sans mise à jour est le
garde-fou contre la page périmée qui a l'air fraîche : ne jamais le retirer.
