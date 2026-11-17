#!/usr/bin/env python3
"""
Purge les tâches faites anciennes de l'état, sans jamais permettre leur retour.

Une tâche cochée n'est pas qu'une ligne d'historique : sa présence dans l'état est
ce qui empêche le scan du lendemain de la recréer depuis un fil de mail resté ouvert.
On ne la supprime donc pas — on la remplace par une **pierre tombale** dans `clos`,
qui garde de quoi la reconnaître : l'identifiant, le fil d'origine et le libellé.

L'identifiant seul ne suffirait pas : il dérive du libellé, que le modèle reformule
d'un scan à l'autre. Sans `id_fil` ni `action`, une tâche purgée ressusciterait sous
un identifiant légèrement différent.

Rétentions (fixées le 2026-08-28) :
  - clôture par la personne ("maxime") ->  7 jours   (elle sait ce qu'elle a fait)
  - clôture par le scan -> 30 jours   (une clôture automatique mérite d'être contestable)

L'archive complète vit ailleurs : exports markdown datés et historique Git.

Usage :
  python3 purger_etat.py --state state.json [--today AAAA-MM-JJ] [--dry-run]
"""

import argparse, json, sys
from datetime import date

RETENTION = {"maxime": 7, "scan": 30}
RETENTION_DEFAUT = 30           # ferme_par absent ou inattendu : on est prudent
CLOS_MAX_JOURS = 548            # ~18 mois : au-delà, le fil de mail est mort
ACTION_MAX = 90                 # le libellé sert à reconnaître, pas à tout garder


def iso(s):
    try:
        return date.fromisoformat(s[:10]) if s else None
    except (ValueError, TypeError):
        return None


def tombe(t):
    """La trace minimale qui permet encore de reconnaître la tâche."""
    return {
        "id": t.get("id"),
        "id_fil": t.get("id_fil"),
        "action": (t.get("action") or "")[:ACTION_MAX],
        "ferme_le": t.get("ferme_le"),
        "ferme_par": t.get("ferme_par"),
    }


def purger(etat, aujourdhui):
    taches, gardees, nouvelles_tombes = etat.get("taches", []), [], []
    sans_date = 0

    for t in taches:
        if t.get("statut") != "fait":
            gardees.append(t)
            continue
        d = iso(t.get("ferme_le"))
        if d is None:
            # Pas de date de clôture : on ne peut pas juger de son âge, on garde.
            sans_date += 1
            gardees.append(t)
            continue
        limite = RETENTION.get(t.get("ferme_par"), RETENTION_DEFAUT)
        if (aujourdhui - d).days > limite:
            nouvelles_tombes.append(tombe(t))
        else:
            gardees.append(t)

    clos = etat.get("clos", []) + nouvelles_tombes

    # Les pierres tombales ne s'accumulent pas indéfiniment non plus : passé
    # dix-huit mois, le fil de mail correspondant ne peut plus rien réveiller.
    avant = len(clos)
    clos = [c for c in clos
            if (iso(c.get("ferme_le")) is None
                or (aujourdhui - iso(c["ferme_le"])).days <= CLOS_MAX_JOURS)]
    expirees = avant - len(clos)

    # Dédoublonnage : une tâche ne doit pas avoir deux pierres tombales.
    vus, uniques = set(), []
    for c in clos:
        if c.get("id") in vus:
            continue
        vus.add(c.get("id"))
        uniques.append(c)

    etat["taches"] = gardees
    etat["clos"] = uniques
    return {
        "purgees": len(nouvelles_tombes),
        "faites_gardees": sum(1 for t in gardees if t.get("statut") == "fait"),
        "ouvertes": sum(1 for t in gardees if t.get("statut") != "fait"),
        "clos_total": len(uniques),
        "clos_expirees": expirees,
        "faites_sans_date": sans_date,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--today", default=None, help="AAAA-MM-JJ (pour les tests)")
    p.add_argument("--dry-run", action="store_true",
                   help="Affiche le bilan sans réécrire le fichier")
    args = p.parse_args()

    with open(args.state) as f:
        etat = json.load(f)

    aujourdhui = iso(args.today) or date.today()
    avant = len(json.dumps(etat, ensure_ascii=False))
    bilan = purger(etat, aujourdhui)
    apres = len(json.dumps(etat, ensure_ascii=False))

    bilan["octets_avant"] = avant
    bilan["octets_apres"] = apres
    bilan["mode"] = "dry-run" if args.dry_run else "écrit"

    if not args.dry_run:
        with open(args.state, "w") as f:
            json.dump(etat, f, ensure_ascii=False, indent=1)

    print(json.dumps(bilan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
