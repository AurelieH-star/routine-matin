#!/usr/bin/env python3
"""
Transforme le texte du brief en MP3 avec une voix neuronale Microsoft (edge-tts).

edge-tts passe par le service de lecture à voix haute du navigateur Edge : gratuit,
sans clé, mais non officiel. S'il tombe, ce script sort en code 2 et le mail part
quand même, avec le texte seul.

Prérequis : python3 -m pip install edge-tts ; réseau ouvert vers api.msedgeservices.com
(et speech.platform.bing.com, l'ancien hôte, gardé en secours).

Usage :
  python3 synthese.py --texte brief/script.txt --out brief/brief.mp3
"""

import argparse, asyncio, json, os, re, ssl, sys, time

# Henri depuis le 15 octobre 2026 ; avant, fr-FR-VivienneMultilingualNeural, jugée
# peu naturelle. Autres voix françaises : edge-tts --list-voices | grep fr-FR
VOIX = "fr-FR-HenriNeural"
DEBIT = "+5%"
OCTETS_PAR_SECONDE = 6000   # sortie edge-tts : MP3 mono 48 kbit/s


def hotes():
    """Les hôtes à essayer, dans l'ordre. Le 10 octobre 2026, Microsoft a fermé
    speech.platform.bing.com (403 « Invalid response status » pour tout le monde, le
    12 au matin pour la routine) et déplacé la lecture à voix haute d'Edge vers
    api.msedgeservices.com, qui accepte encore l'ancien jeton client (rany2/edge-tts,
    ticket 490). edge-tts 7.2.8 vise toujours l'ancien hôte : on passe par le nouveau
    d'abord, l'ancien ensuite au cas où Microsoft revienne en arrière."""
    from edge_tts.constants import TRUSTED_CLIENT_TOKEN, WSS_URL
    return [
        ("api.msedgeservices.com",
         "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
         f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}"),
        ("speech.platform.bing.com", WSS_URL),
    ]


def indice_proxy(ex, hote):
    """Un refus du proxy du sandbox (domaine absent de la liste blanche) n'a pas les
    en-têtes de Microsoft : on le dit en clair, c'est l'erreur d'installation la plus
    probable chez quelqu'un qui découvre la routine."""
    entetes = getattr(ex, "headers", None) or {}
    de_microsoft = any(k.lower() == "x-msedge-ref" for k in entetes)
    if "allowlist" in str(ex).lower() or (getattr(ex, "status", None) == 403 and not de_microsoft):
        return (f" → {hote} est bloqué par le réseau de l'environnement : l'ajouter à la liste"
                " blanche (réseau Custom), voir SETUP.md ou README.md")
    return ""


def preparer(texte):
    """Retire ce que la voix lirait mal : balises markdown, tirets longs, puces."""
    t = re.sub(r"[*_#>`]", "", texte)
    t = t.replace("—", ", ").replace("–", ", ")
    t = re.sub(r"^\s*[-•]\s+", "", t, flags=re.M)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def contexte_tls():
    """edge-tts ne fait confiance qu'au magasin certifi. Dans le cloud, le proxy de
    sortie présente son propre certificat, que seul le magasin système connaît
    (« self-signed certificate in certificate chain » au premier essai, le 5 octobre
    2026). On charge les deux ; la vérification reste active."""
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_default_certs()
    candidats = [os.environ.get(v) for v in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE",
                                              "CURL_CA_BUNDLE", "NODE_EXTRA_CA_CERTS")]
    candidats += ["/etc/ssl/certs/ca-certificates.crt", "/etc/pki/tls/certs/ca-bundle.crt"]
    for fichier in candidats:
        if fichier and os.path.isfile(fichier):
            try:
                ctx.load_verify_locations(cafile=fichier)
            except ssl.SSLError:
                pass
    return ctx


async def synthetiser(texte, sortie, voix, debit, wss_url):
    import edge_tts
    import edge_tts.communicate
    edge_tts.communicate._SSL_CTX = contexte_tls()
    edge_tts.communicate.WSS_URL = wss_url   # communicate.py lit cette globale
    await edge_tts.Communicate(texte, voix, rate=debit).save(sortie)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--texte", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--voix", default=VOIX)
    p.add_argument("--debit", default=DEBIT)
    args = p.parse_args()

    texte = preparer(open(args.texte, encoding="utf-8").read())
    if len(texte.split()) < 30:
        sys.exit("Texte trop court pour un brief : vérifier script.txt.")
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print(json.dumps({"ok": False, "raison": "module edge-tts absent (pip install bloqué ?)"},
                         ensure_ascii=False))
        sys.exit(2)

    if os.path.exists(args.out):
        os.remove(args.out)    # jamais d'ancien MP3 réutilisé par erreur
    derniere_erreur = None
    hote = None
    tentatives = [(nom, url) for nom, url in hotes() for _ in range(2)]
    for essai, (nom, url) in enumerate(tentatives):
        try:
            asyncio.run(synthetiser(texte, args.out, args.voix, args.debit, url))
            if os.path.getsize(args.out) > 20_000:
                hote = nom
                break
            derniere_erreur = f"{nom} : fichier audio vide ou tronqué"
        except Exception as ex:
            derniere_erreur = f"{nom} : {type(ex).__name__}: {str(ex)[:200]}"
            # Un 403 du proxy cloud (domaine hors liste) se distingue d'un 403 de
            # Microsoft par ses en-têtes : on les garde pour le diagnostic.
            entetes = getattr(ex, "headers", None)
            if entetes:
                derniere_erreur += " | en-têtes : " + json.dumps(dict(entetes), ensure_ascii=False)[:400]
            derniere_erreur += indice_proxy(ex, nom)
            if getattr(ex, "status", None) == 403:
                continue    # refus net : attendre ne changera rien, hôte ou essai suivant
        if essai < len(tentatives) - 1:
            time.sleep(5)
    else:
        if os.path.exists(args.out):
            os.remove(args.out)
        print(json.dumps({"ok": False, "raison": derniere_erreur}, ensure_ascii=False))
        sys.exit(2)

    octets = os.path.getsize(args.out)
    print(json.dumps({"ok": True, "fichier": args.out, "octets": octets,
                      "duree_s": round(octets / OCTETS_PAR_SECONDE), "mots": len(texte.split()),
                      "voix": args.voix, "hote": hote}, ensure_ascii=False))


if __name__ == "__main__":
    main()
