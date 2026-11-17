# Profil

Rempli au premier lancement, relu à chaque exécution. C'est ici, et nulle part
ailleurs, que vit ce qui est propre à la personne : le skill lui-même n'en sait rien.
Tout ce que les prompts d'extraction et de rédaction disent « de vous » vient de ce
fichier.

```yaml
prenom: "Aurélie"
nom_complet: "Aurélie Hennetier"
role: "responsable communication et événementiels"
organisation: "Procivis UES-AP, tête de réseau du réseau coopératif Procivis"
boite: "aurelie.hennetier@procivis.fr"
fournisseur: "m365"
fuseau: "Europe/Paris"
heure_mail: "07:30"

capacites:
  envoi_mail: true         # outlook_send_mail présent, Mail.Send consenti (vérifié le 17/11/2026)
  brouillon: true          # outlook_create_draft présent
  piece_jointe: false      # Microsoft 365 : jamais
  depot_fichier: true      # sharepoint_upload_file présent, Files.ReadWrite.All consenti
  agenda: true             # outlook_calendar_search présent

projets:
  - "Newsletter réseau"
  - "Vœux 2027"
  - "Immolympiades 2027"
  - "Sortie de Noël de l'équipe"
  - "Relations presse et partenariats"
  - "Comité communication PLS"
  - "Baromètre 2027"
  - "Site et marque"

# Interlocuteurs les plus réguliers, d'après les mails envoyés du 27/10 au 17/11/2026.
proches:
  - "Hélène Dürlewanger, directrice logement social et partenariats"
  - "Maxime Taillebois, chef de projets communication"
  - "Danièle Ephestion"
  - "Guillaume Macher, directeur général"
  - "Franck Petit, directeur maîtrise d'ouvrage"
  - "Jérôme Verdin"
  - "Angélique Pouvesle"
  - "Adrien Chaussinand"
externes:
  - "Stéphanie, Papiers de Soi (mise en page de la newsletter)"
  - "Caroline Courteau, Velux (Living Places)"
  - "Marie-Belle Parseghian, AirZen Radio"
  - "Julien Potereau, Toluna Harris Interactive (Baromètre)"
  - "Laura Lerible, Autour des Saveurs (traiteur des vœux)"
  - "Émilie Voegeli, Binéo (partenaire Immolympiades)"
  - "Anne-Flore Telfils, Cision"
  - "Stéphane Sautier, Valrim"

bruit:
  expediteurs: ["lefigaro.fr", "batiactu.com", "immoweek.fr", "newstank.fr", "infopro-digital.com", "strategies.fr", "fpifrance.fr", "clic-cctp.com", "jvweb.fr", "teamresa.com", "airzen.fr/no-reply", "scanner@procivis.fr", "dialog.procivis.fr"]
  objets: ["Synthèse quotidienne des réactions", "Info du jour", "Le 13 H de l'Immobilier", "Les titres du"]

feries: "FR"

artefact_url: "https://claude.ai/artifact/SQnb6Pjy5GfTouu1e3Zxy1"
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

## Notes de l'adaptateur (premier lancement, 17/11/2026)

- `outlook_email_search` avec `folderName: "Sent Items"` + `afterDateTime` : liste les envoyés, 25 par page, pagination par `offset`.
- Boîte de réception très chargée (environ 1 500 mails en trois semaines, surtout des newsletters) : pour les reçus, filtrer avec `sender: "procivis.fr"` + `folderName: "Inbox"` + `afterDateTime`, puis une recherche sans filtre d'expéditeur sur la fenêtre courte de la routine.
- L'agenda renvoie les heures en « Romance Standard Time » (heure de Paris).
