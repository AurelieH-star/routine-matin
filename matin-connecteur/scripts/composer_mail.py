#!/usr/bin/env python3
"""
Compose le mail du matin : le brief (texte, agenda, mention du vocal), puis la to-do.
Il n'envoie rien. Il écrit le sujet, le corps HTML et une version texte dans des
fichiers, que l'opération m_envoyer de l'adaptateur (references/fournisseurs/*.md)
passe au connecteur. C'est la version sans réseau de matin/scripts/envoyer_matin.py.

Pourquoi un script et pas une rédaction par l'agent : le mail doit avoir la même tête
tous les matins, y compris ceux où personne ne relit. Un mail rédigé à la volée dérive
en quelques jours.

Formes :
  brief + to-do        jour ouvré : --texte brief/script.txt --agenda brief/agenda.json
                       plus --mp3 brief/brief.mp3 (pièce jointe à passer au connecteur),
                       ou --lien-audio URL (fichier déposé ailleurs), ou --sans-audio "raison"
  to-do seule          --sans-brief "week-end" (férié, absence, scan manuel)
  échec                --echec "ce qui a cassé" : mail court, la page n'a pas bougé

Garde-fous : l'état doit avoir été scanné aujourd'hui, le texte et l'agenda doivent
dater de cette exécution (moins de trois heures), l'agenda doit être celui du jour,
le texte doit faire entre 60 et 1 000 mots. --test lève ces contrôles pour regarder
un gabarit avec de vieux fichiers.

Sorties (dans --out, défaut brief/) : mail.html, sujet.txt, mail.txt, et sur la
sortie standard un JSON : sujet, fichiers, octets, et `piece_jointe` (le chemin du
MP3 à joindre, ou null).

Usage :
  python3 composer_mail.py --state state.json --artefact-url "<URL>" \
      --texte brief/script.txt --agenda brief/agenda.json --mp3 brief/brief.mp3
"""

import argparse, html as H, json, os, re, sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rendu_todo as R  # noqa: E402

FRAICHEUR_MAX = timedelta(hours=3)
OCTETS_PAR_SECONDE = 6000   # MP3 edge-tts, mono 48 kbit/s


def frais(chemin):
    return datetime.now() - datetime.fromtimestamp(os.path.getmtime(chemin)) < FRAICHEUR_MAX


def duree(octets):
    s = round(octets / OCTETS_PAR_SECONDE)
    return f"{s // 60} min {s % 60:02d}"


# --- Rendu --------------------------------------------------------------------

def section(titre):
    return (f'<tr><td style="padding:30px 0 2px;border-top:2px solid {R.VERT};'
            f'font:600 17px/1.3 Georgia,serif;color:{R.VERT};">{R.e(titre)}</td></tr>')


def lignes_brief(texte, agenda):
    L = []
    A = L.append
    A('<tr><td style="padding:10px 0 0;"></td></tr>')
    for para in [p.strip() for p in texte.split("\n\n") if p.strip()]:
        A(f'<tr><td style="padding:0 0 12px;font:400 15px/1.55 Arial,sans-serif;'
          f'color:{R.ENCRE};">{R.e(para).replace(chr(10), "<br>")}</td></tr>')
    reunions = agenda.get("reunions", [])
    reperes = agenda.get("reperes", [])
    if reunions or reperes:
        A(f'<tr><td style="padding:14px 0 6px;border-top:1px solid {R.TRAIT};'
          f'font:600 14px/1.3 Georgia,serif;color:{R.VERT};">Ta journée</td></tr>')
        A('<tr><td><table role="presentation" cellpadding="0" cellspacing="0" border="0" '
          'style="font:400 13px/1.5 Arial,sans-serif;">')
        for r in reperes:
            A(f'<tr><td style="padding:2px 14px 2px 0;color:{R.GRIS};white-space:nowrap;">'
              f'journée</td><td>{R.e(r)}</td></tr>')
        for r in reunions:
            A(f'<tr><td style="padding:2px 14px 2px 0;color:{R.GRIS};white-space:nowrap;">'
              f'{R.e(r.get("debut", ""))}-{R.e(r.get("fin", ""))}</td><td>{R.e(r.get("objet", ""))}</td></tr>')
        A('</table></td></tr>')
    return L


def construire(jour, depuis, state, url, texte, agenda, mention_vocal, sans_brief):
    c = R.compteurs(state, jour, depuis)
    L = [R.ouvrir_table()]
    A = L.append
    if texte:
        A(R.en_tete(f"Matin du {R.date_fr(jour, avec_jour=True)}",
                    mention_vocal + " &middot; " + R.sous_titre_compteurs(c, depuis)))
        A(section("Le brief"))
        L += lignes_brief(texte, agenda)
        A(section("La to-do"))
    else:
        sous = R.sous_titre_compteurs(c, depuis)
        if sans_brief:
            sous += f" &middot; pas de brief ({R.e(sans_brief)})"
        A(R.en_tete(f"To-do du {R.date_fr(jour, avec_jour=True)}", sous))
    L += R.lignes_todo(state, jour, depuis, url)
    A(R.fermer_table())
    return "\n".join(L)


def construire_echec(jour, message, state, url):
    scan = (state.get("dernier_scan") or "")[:10]
    L = [R.ouvrir_table(),
         R.en_tete(f"To-do du {R.date_fr(jour, avec_jour=True)}",
                   f'<span style="color:{R.ROUGE};">Le scan de ce matin a échoué.</span>'),
         f'<tr><td style="padding:18px 0 12px;font:400 15px/1.55 Arial,sans-serif;'
         f'color:{R.ENCRE};">{R.e(message)}</td></tr>',
         f'<tr><td style="padding:0 0 12px;font:400 15px/1.55 Arial,sans-serif;'
         f'color:{R.ENCRE};">La to-do en ligne est celle du {R.e(scan) or "dernier scan réussi"} : '
         f'elle n&rsquo;a pas été rafraîchie, ne t&rsquo;y fie pas pour ce qui est arrivé '
         f'depuis. Pas de brief non plus.</td></tr>']
    if url:
        L.append(f'<tr><td style="padding:16px 0 24px;"><a href="{R.e(url)}" '
                 f'style="font:600 14px/1.4 Arial,sans-serif;color:{R.VERT};'
                 f'text-decoration:none;">Ouvrir la to-do &rsaquo;</a></td></tr>')
    L.append(R.fermer_table())
    return "\n".join(L)


def en_texte(corps_html):
    """Version texte brut, pour les clients qui n'affichent pas le HTML."""
    t = re.sub(r"</(tr|p|div|h\d)>", "\n", corps_html, flags=re.I)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</td>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = H.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True, help="state.json écrit par le scan du jour")
    p.add_argument("--artefact-url", default="")
    p.add_argument("--texte", default=None, help="brief/script.txt")
    p.add_argument("--agenda", default=None, help="brief/agenda.json")
    p.add_argument("--mp3", default=None, help="brief/brief.mp3, à joindre par le connecteur")
    p.add_argument("--lien-audio", default=None, help="URL du MP3 déposé ailleurs (OneDrive…)")
    p.add_argument("--sans-audio", default=None, help="raison de l'absence de vocal")
    p.add_argument("--sans-brief", default=None, help="raison de l'absence de brief")
    p.add_argument("--echec", default=None, help="le scan a échoué : message court")
    p.add_argument("--depuis", default=None, help="AAAA-MM-JJ (défaut : la veille)")
    p.add_argument("--today", default=None, help="AAAA-MM-JJ (pour les tests)")
    p.add_argument("--out", default="brief", help="dossier des fichiers produits")
    p.add_argument("--test", action="store_true", help="lève les garde-fous de fraîcheur")
    args = p.parse_args()

    jour = R.iso(args.today) or date.today()
    depuis = R.iso(args.depuis) or (jour - timedelta(days=1))
    with open(args.state, encoding="utf-8") as f:
        state = json.load(f)
    c = R.compteurs(state, jour, depuis)
    tete = f"To-do du {R.date_fr(jour)}"
    piece_jointe = None

    if args.echec:
        sujet = f"{tete} : scan en échec"
        corps = construire_echec(jour, args.echec, state, args.artefact_url)
    else:
        if not args.test:
            scan = (state.get("dernier_scan") or "")[:10]
            if scan != jour.isoformat():
                sys.exit(f"ABANDON : state.json a été scanné le {scan or '?'}, pas aujourd'hui. "
                         f"Le mail partirait sur une to-do périmée (--echec si le scan a cassé).")
        texte = agenda = None
        if args.texte:
            if not args.agenda:
                sys.exit("--agenda est obligatoire avec --texte (un fichier {\"jour\": …, "
                         "\"reunions\": []} vide convient).")
            texte = open(args.texte, encoding="utf-8").read().strip()
            agenda = json.load(open(args.agenda, encoding="utf-8"))
            if not args.test and (not frais(args.texte) or not frais(args.agenda)):
                sys.exit("ABANDON : script.txt ou agenda.json ne datent pas de cette exécution.")
            if agenda.get("jour") != jour.isoformat():
                sys.exit(f"ABANDON : agenda.json est celui du {agenda.get('jour')}, pas d'aujourd'hui.")
            if not 60 <= len(texte.split()) <= 1000:
                sys.exit(f"ABANDON : texte de {len(texte.split())} mots, hors de la plage attendue.")
        elif not args.sans_brief:
            sys.exit("Sans --texte, préciser --sans-brief \"raison\" (week-end, férié, absence, "
                     "scan manuel).")

        mention = ""
        if texte:
            if args.mp3 and os.path.exists(args.mp3):
                if not args.test and not frais(args.mp3):
                    sys.exit("ABANDON : le MP3 ne date pas de cette exécution.")
                piece_jointe = os.path.abspath(args.mp3)
                mention = f"Le vocal est en pièce jointe ({duree(os.path.getsize(args.mp3))})"
            elif args.lien_audio:
                mention = (f'<a href="{R.e(args.lien_audio)}" style="color:{R.VERT};">'
                           f'Écouter le vocal</a>')
            else:
                raison = args.sans_audio or "synthèse vocale indisponible"
                mention = f'<span style="color:{R.ROUGE};">Pas de vocal ce matin : {R.e(raison)}</span>'

        compte = f"{c['ouvertes']} tâches ouvertes, {c['urgentes']} urgentes"
        sujet = (f"Matin du {R.date_fr(jour, avec_jour=True)} : {compte}" if texte
                 else f"{tete} : {compte}")
        corps = construire(jour, depuis, state, args.artefact_url, texte, agenda,
                           mention, args.sans_brief)

    os.makedirs(args.out, exist_ok=True)
    chemins = {"html": os.path.join(args.out, "mail.html"),
               "texte": os.path.join(args.out, "mail.txt"),
               "sujet": os.path.join(args.out, "sujet.txt")}
    open(chemins["html"], "w", encoding="utf-8").write(corps)
    open(chemins["texte"], "w", encoding="utf-8").write(en_texte(corps))
    open(chemins["sujet"], "w", encoding="utf-8").write(sujet + "\n")
    print(json.dumps({"sujet": sujet, "fichiers": chemins, "octets": len(corps),
                      "piece_jointe": piece_jointe,
                      "destinataire": "la boîte elle-même (profil.boite), et personne d'autre"},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
