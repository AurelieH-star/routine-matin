#!/usr/bin/env python3
"""
Rendu HTML de la to-do pour le mail du matin.

Entièrement déterministe : tout est calculé à partir de l'état JSON de l'artefact,
sans que l'agent ait à rédiger quoi que ce soit. C'est ce qui garantit que la liste
a la même tête chaque matin, y compris quand personne ne relit.

Les « mouvements » (nouvelles tâches, tâches soldées) sont déduits des champs
`ajoute_le` et `ferme_le` de l'état — l'agent n'a rien à fournir en plus.

Ce module ne sait pas envoyer. C'est `matin/scripts/envoyer_matin.py` qui l'appelle
et assemble le mail complet (brief vocal + to-do). En ligne de commande il écrit
seulement un aperçu de la partie to-do :

  python3 rendu_todo.py --state state.json --out apercu.html \
      [--artefact-url URL] [--depuis AAAA-MM-JJ] [--today AAAA-MM-JJ]
"""

import argparse, collections, html, json
from datetime import date, timedelta

VERT = "#1c6b4a"       # vert, pour les titres
GRIS = "#5a6570"       # texte secondaire
ROUGE = "#b3261e"      # retard
ENCRE = "#1a1a1a"      # texte courant
TRAIT = "#e3e6e8"      # filets

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def e(s):
    return html.escape(str(s if s is not None else ""))


def date_fr(d, avec_jour=False):
    txt = f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]}"
    return f"{JOURS[d.weekday()]} {txt}" if avec_jour else txt


def iso(s):
    try:
        return date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def pluriel(n, mot, fem=False):
    return f"{n} {mot}{'s' if n > 1 else ''}"


# --- Sélections sur l'état ----------------------------------------------------

def ouvertes(taches):
    return [t for t in taches if t.get("statut") != "fait"]


def echeance_libelle(ech, aujourdhui):
    n = (ech - aujourdhui).days
    if n < 0:
        return f"en retard de {-n} j" if n < -1 else "en retard d'un jour", True
    if n == 0:
        return "aujourd'hui", True
    if n == 1:
        return "demain", True
    if n <= 7:
        return f"dans {n} jours", n <= 3
    return date_fr(ech), False


BANDE = {"haute": 0, "moyenne": 1, "basse": 2}


def cle_tri(t):
    """Même ordre que la page : priorité, puis rang posé à la main, puis échéance.

    Les deux surfaces doivent trier pareil, sinon le mail contredit la page que
    la personne vient d'ordonner.
    """
    rang = t.get("rang")
    return (BANDE.get(t.get("urgence"), 1),
            rang if isinstance(rang, int) else 10 ** 9,
            t.get("echeance") or "9999-99-99",
            t.get("action", ""))


def par_projet(taches):
    """Groupe par projet, du plus fourni au plus léger, Divers en dernier."""
    g = collections.defaultdict(list)
    for t in taches:
        g[(t.get("projet") or "Divers").strip() or "Divers"].append(t)
    for lst in g.values():
        lst.sort(key=cle_tri)
    return sorted(g.items(), key=lambda kv: (kv[0].lower() == "divers", -len(kv[1]), kv[0]))


def compteurs(state, aujourdhui, depuis):
    """Les chiffres de l'en-tête et du sujet, calculés une seule fois."""
    taches = state.get("taches", [])
    ouv = ouvertes(taches)
    nouvelles = [t for t in ouv if (iso(t.get("ajoute_le")) or date.min) >= depuis]
    # Premier mail : tout est « nouveau », le signaler n'apprend rien et noie la page.
    # Au-delà de la moitié des tâches ouvertes, on considère que c'est une amorce.
    if ouv and len(nouvelles) > len(ouv) / 2:
        nouvelles = []
    return {
        "ouvertes": len(ouv),
        "urgentes": sum(1 for t in ouv if t.get("urgence") == "haute"),
        "soldees": sum(1 for t in taches if t.get("statut") == "fait"
                       and (iso(t.get("ferme_le")) or date.min) >= depuis),
        "nouvelles": nouvelles,
    }


# --- Rendu --------------------------------------------------------------------

def bloc_titre(txt, compte=None):
    suffixe = f' <span style="color:{GRIS};font-weight:400;">({compte})</span>' if compte else ""
    return (f'<tr><td style="padding:26px 0 8px;border-bottom:1px solid {TRAIT};">'
            f'<span style="font:600 15px/1.3 Georgia,serif;color:{VERT};">'
            f'{e(txt)}{suffixe}</span></td></tr>')


def ligne_tache(t, marqueur=None):
    urg = t.get("urgence")
    puce = "&#9679;" if urg == "haute" else "&#9675;"
    couleur_puce = ROUGE if urg == "haute" else GRIS
    jira = t.get("jira")
    jira_txt = f"{jira} ({t['jira_statut']})" if jira and t.get("jira_statut") else jira
    meta = " &middot; ".join(x for x in [e(t.get("qui")), e(t.get("date")), e(jira_txt)] if x)
    tag = ""
    if marqueur:
        tag = (f'<span style="font:600 10px/1 Arial,sans-serif;color:{VERT};'
               f'letter-spacing:.06em;text-transform:uppercase;">&nbsp;{e(marqueur)}</span>')
    return (f'<tr><td style="padding:7px 0;border-bottom:1px solid #f2f4f5;'
            f'font:400 14px/1.45 Arial,sans-serif;color:{ENCRE};">'
            f'<span style="color:{couleur_puce};">{puce}</span>&nbsp;{e(t.get("action"))}{tag}'
            + (f'<br><span style="font-size:12px;color:{GRIS};">{meta}</span>' if meta else "")
            + "</td></tr>")


def lignes_todo(state, aujourdhui, depuis, url_artefact):
    """Les lignes <tr> de la partie to-do : échéances, nouveautés, liste complète,
    lien vers la page et pied. À insérer dans une table de 640 px."""
    taches = state.get("taches", [])
    ouv = ouvertes(taches)
    c = compteurs(state, aujourdhui, depuis)
    nouvelles = c["nouvelles"]
    ids_nouvelles = {t.get("id") for t in nouvelles}

    datees = sorted([t for t in ouv if iso(t.get("echeance"))],
                    key=lambda t: iso(t["echeance"]))

    L = []
    A = L.append

    # 1. Échéances datées
    if datees:
        A(bloc_titre("Échéances", len(datees)))
        A('<tr><td><table role="presentation" cellpadding="0" cellspacing="0" '
          'border="0" style="width:100%;">')
        for t in datees[:15]:
            libelle, chaud = echeance_libelle(iso(t["echeance"]), aujourdhui)
            couleur = ROUGE if chaud else GRIS
            A(f'<tr><td style="padding:8px 0;border-bottom:1px solid #f2f4f5;'
              f'font:400 14px/1.45 Arial,sans-serif;color:{ENCRE};">'
              f'<span style="font:600 12px/1 Arial,sans-serif;color:{couleur};">'
              f'{e(libelle)}</span><br>{e(t.get("action"))}'
              f'<span style="font-size:12px;color:{GRIS};"> &mdash; {e(t.get("qui"))}</span>'
              f'</td></tr>')
        A('</table></td></tr>')

    # 2. Ce qui est nouveau. Les tâches soldées ne sont plus listées ici : la personne
    # les voit déjà barrées sur la page tant qu'elles y restent, et un rappel par
    # mail n'est qu'une liste de choses à ignorer. Le compteur de l'en-tête suffit.
    if nouvelles:
        A(bloc_titre("Nouveau depuis " + date_fr(depuis)))
        A('<tr><td><table role="presentation" cellpadding="0" cellspacing="0" '
          'border="0" style="width:100%;">')
        for t in nouvelles:
            A(ligne_tache(t, marqueur="nouveau"))
        A('</table></td></tr>')

    # 3. Liste complète
    A(bloc_titre("Toutes les tâches ouvertes", len(ouv)))
    for projet, lst in par_projet(ouv):
        A(f'<tr><td style="padding:16px 0 4px;font:600 13px/1.3 Arial,sans-serif;'
          f'color:{ENCRE};">{e(projet)}'
          f'<span style="color:{GRIS};font-weight:400;"> ({len(lst)})</span></td></tr>')
        A('<tr><td><table role="presentation" cellpadding="0" cellspacing="0" '
          'border="0" style="width:100%;">')
        for t in lst:
            A(ligne_tache(t, marqueur="nouveau" if t.get("id") in ids_nouvelles else None))
        A('</table></td></tr>')

    # 4. Lien et pied
    if url_artefact:
        A(f'<tr><td style="padding:28px 0 6px;">'
          f'<a href="{e(url_artefact)}" style="font:600 14px/1.4 Arial,sans-serif;'
          f'color:{VERT};text-decoration:none;">Ouvrir la to-do pour cocher &rsaquo;</a>'
          f'</td></tr>')
    scan = state.get("dernier_scan", "")
    A(f'<tr><td style="padding:4px 0 24px;font:400 11px/1.5 Arial,sans-serif;color:{GRIS};">'
      f'Scan de la boîte Outlook du {e(scan[:16].replace("T", " à "))} (UTC). '
      f'Les cases cochées dans la to-do ne reviennent jamais.</td></tr>')
    return L


def ouvrir_table():
    return ('<div style="margin:0;padding:0;background:#ffffff;">'
            '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
            'style="width:100%;max-width:640px;margin:0 auto;padding:0 4px;">')


def fermer_table():
    return "</table></div>"


def en_tete(titre, sous_titre_html):
    return (f'<tr><td style="padding:4px 0 2px;font:600 20px/1.25 Georgia,serif;color:{ENCRE};">'
            f'{e(titre)}</td></tr>'
            f'<tr><td style="padding:2px 0 0;font:400 13px/1.5 Arial,sans-serif;color:{GRIS};">'
            f'{sous_titre_html}</td></tr>')


def sous_titre_compteurs(c, depuis):
    return (f'{pluriel(c["ouvertes"], "tâche")} ouverte{"s" if c["ouvertes"] > 1 else ""}'
            f' &middot; {c["urgentes"]} urgente{"s" if c["urgentes"] > 1 else ""}'
            f' &middot; {c["soldees"]} soldée{"s" if c["soldees"] > 1 else ""} depuis '
            f'{date_fr(depuis)}')


def construire_html(state, aujourdhui, depuis, url_artefact):
    """La to-do seule, telle qu'elle part les jours sans brief."""
    c = compteurs(state, aujourdhui, depuis)
    L = [ouvrir_table(),
         en_tete(f"To-do du {date_fr(aujourdhui, avec_jour=True)}", sous_titre_compteurs(c, depuis))]
    L += lignes_todo(state, aujourdhui, depuis, url_artefact)
    L.append(fermer_table())
    return "\n".join(L)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True, help="Fichier JSON de l'état de l'artefact")
    p.add_argument("--out", required=True, metavar="FICHIER.html")
    p.add_argument("--artefact-url", default="")
    p.add_argument("--depuis", default=None, help="AAAA-MM-JJ (défaut : la veille)")
    p.add_argument("--today", default=None, help="AAAA-MM-JJ (pour les tests)")
    args = p.parse_args()

    with open(args.state, encoding="utf-8") as f:
        state = json.load(f)
    aujourdhui = iso(args.today) or date.today()
    depuis = iso(args.depuis) or (aujourdhui - timedelta(days=1))
    corps = construire_html(state, aujourdhui, depuis, args.artefact_url)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(corps)
    c = compteurs(state, aujourdhui, depuis)
    print(json.dumps({"fichier": args.out, "octets": len(corps),
                      "ouvertes": c["ouvertes"], "urgentes": c["urgentes"],
                      "soldees": c["soldees"], "nouvelles": len(c["nouvelles"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
