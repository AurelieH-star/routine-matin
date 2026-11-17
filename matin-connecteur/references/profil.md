# Profil

Rempli au premier lancement, relu à chaque exécution. C'est ici, et nulle part
ailleurs, que vit ce qui est propre à la personne : le skill lui-même n'en sait rien.
Tout ce que les prompts d'extraction et de rédaction disent « de vous » vient de ce
fichier.

```yaml
prenom: ""            # ex. Camille — utilisé dans le brief (« Bonjour Camille »)
nom_complet: ""       # ex. Camille Durand
role: ""              # ex. responsable communication, PME de 40 personnes
organisation: ""      # ex. Durand & Fils
boite: ""             # l'adresse lue et destinataire du mail du matin
fournisseur: ""       # m365 | gmail — détecté d'après les outils présents
fuseau: "Europe/Paris"
heure_mail: "07:00"   # heure à laquelle vous voulez lire le mail

# Ce que le connecteur sait faire, constaté au premier lancement (outils présents).
capacites:
  envoi_mail: false        # outlook_send_mail ou send_message présent
  brouillon: false         # outlook_create_draft ou create_draft présent
  piece_jointe: false      # Gmail : oui ; Microsoft 365 : non
  depot_fichier: false     # sharepoint_upload_file présent (lien OneDrive pour le MP3)
  agenda: false            # outlook_calendar_search ou connecteur Google Calendar

# Vos grands projets ou thèmes. Chaque tâche est rangée dans l'un d'eux ; ils
# deviennent les filtres de la page. Cinq à dix, pas plus ; « Divers » est ajouté.
projets:
  - ""
  - ""

# Les personnes que vous côtoyez tous les jours (prénom seul dans le brief) et les
# externes réguliers (prénom + société). Facultatif, améliore le brief.
proches:
  - ""
externes:
  - ""   # ex. Séverine, agence Yumens

# Expéditeurs et objets à ignorer en plus de references/bruit.md.
bruit:
  expediteurs: []
  objets: []

# Jours fériés à respecter (le brief ne part pas) : code pays ou liste de dates.
feries: "FR"

# Page claude.ai de la to-do, créée au premier lancement. Ne change jamais.
artefact_url: ""
```

Règles :

- Le premier lancement pose les questions dans l'ordre et remplit le fichier ; il ne
  demande que ce qu'il ne peut pas constater lui-même.
- `capacites` n'est jamais rempli à la main : c'est le constat des outils présents
  dans la session, refait à chaque premier lancement et à chaque fois qu'une opération
  échoue pour un outil absent.
- `projets` se raffine après le premier scan : le skill propose une liste d'après ce
  qu'il a lu, la personne corrige, la liste est écrite ici.
- Ce fichier est committé dans le dépôt de la personne : il ne contient ni mot de
  passe ni clé, seulement ce qu'un collègue sait déjà.
