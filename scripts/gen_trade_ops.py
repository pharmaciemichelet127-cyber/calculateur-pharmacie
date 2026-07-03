#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Régénère trade-ops.json depuis la table Notion « 🎁 Operations marketing : TRADE ».
Exécuté par GitHub Actions (nightly) avec le secret NOTION_TOKEN.
Pharmacie Michelet — calculateur-pharmacie.

Sortie : trade-ops.json à la racine du repo, même schéma que la v1 :
{v, date, source, nb, ops:[{promo, labo, debut, fin, type, canal_promo,
 canal_achat, montant, unite, cde_debut, cde_fin, compensation,
 intercomptoir, detail}]}
"""
import json
import os
import sys
import datetime
import urllib.request
import urllib.error

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DATA_SOURCE_ID = "dfadd25e-d3ed-4d96-8e0c-2be4b8fc461a"   # 🎁 Operations marketing : TRADE
DATABASE_ID = "a7f9ab7a-ba55-4a13-8a5f-de6a8ed01894"       # base parente (repli API classique)
OUT_FILE = "trade-ops.json"

if not NOTION_TOKEN:
    print("ERREUR : variable d'environnement NOTION_TOKEN absente.", file=sys.stderr)
    sys.exit(1)


def notion_request(url, payload=None, version="2022-06-28"):
    """Appel API Notion avec gestion d'erreur ; retourne le JSON décodé."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method="POST" if payload is not None else "GET",
        headers={
            "Authorization": "Bearer " + NOTION_TOKEN,
            "Notion-Version": version,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def query_all_pages():
    """Interroge la table des opérations avec pagination.
    Essaie d'abord l'endpoint data_sources (API 2025), replie sur databases (API 2022)."""
    attempts = [
        ("https://api.notion.com/v1/data_sources/%s/query" % DATA_SOURCE_ID, "2025-09-03"),
        ("https://api.notion.com/v1/databases/%s/query" % DATABASE_ID, "2022-06-28"),
    ]
    last_err = None
    for url, version in attempts:
        try:
            pages, cursor = [], None
            while True:
                payload = {"page_size": 100}
                if cursor:
                    payload["start_cursor"] = cursor
                res = notion_request(url, payload, version)
                pages.extend(res.get("results", []))
                if not res.get("has_more"):
                    return pages
                cursor = res.get("next_cursor")
        except urllib.error.HTTPError as e:
            last_err = "%s → HTTP %s : %s" % (url, e.code, e.read().decode("utf-8", "replace")[:300])
            print("Tentative échouée :", last_err, file=sys.stderr)
            continue
    print("ERREUR : impossible d'interroger Notion.\n" + str(last_err), file=sys.stderr)
    sys.exit(1)


# ── Extracteurs de propriétés Notion ──────────────────────────────
def prop(props, name):
    """Trouve une propriété par nom, tolérant sur le type d'apostrophe."""
    if name in props:
        return props[name]
    alt = name.replace("'", "\u2019")
    if alt in props:
        return props[alt]
    alt2 = name.replace("\u2019", "'")
    return props.get(alt2)


def p_title(props, name):
    p = prop(props, name) or {}
    return "".join(t.get("plain_text", "") for t in p.get("title", [])).strip()


def p_rich(props, name):
    p = prop(props, name) or {}
    return "".join(t.get("plain_text", "") for t in p.get("rich_text", [])).strip()


def p_select(props, name):
    p = prop(props, name) or {}
    s = p.get("select")
    return s.get("name") if s else None


def p_number(props, name):
    p = prop(props, name) or {}
    return p.get("number")


def p_checkbox(props, name):
    p = prop(props, name) or {}
    return bool(p.get("checkbox"))


def p_date(props, name):
    p = prop(props, name) or {}
    d = p.get("date") or {}
    start = d.get("start")
    end = d.get("end")
    # tronquer les datetimes en dates simples
    if start:
        start = start[:10]
    if end:
        end = end[:10]
    return start, end


def p_relation_first(props, name):
    p = prop(props, name) or {}
    rels = p.get("relation") or []
    return rels[0].get("id") if rels else None


# ── Résolution des noms de laboratoires (relation → titre de fiche) ─
_labo_cache = {}


def resolve_labo(page_id):
    if not page_id:
        return ""
    if page_id in _labo_cache:
        return _labo_cache[page_id]
    try:
        res = notion_request("https://api.notion.com/v1/pages/" + page_id)
        nom = ""
        for p in (res.get("properties") or {}).values():
            if p.get("type") == "title":
                nom = "".join(t.get("plain_text", "") for t in p.get("title", [])).strip()
                break
    except Exception as e:
        print("Avertissement : fiche labo %s non résolue (%s)" % (page_id, e), file=sys.stderr)
        nom = ""
    _labo_cache[page_id] = nom
    return nom


# ── Génération ────────────────────────────────────────────────────
def main():
    pages = query_all_pages()
    ops = []
    for page in pages:
        props = page.get("properties") or {}
        promo = p_title(props, "Promotion")
        if not promo:
            continue
        debut, _ = p_date(props, "Début")
        fin, _ = p_date(props, "Fin")
        cde_debut, cde_fin = p_date(props, "Période de commande")
        labo = resolve_labo(p_relation_first(props, "Laboratoire"))
        ops.append({
            "promo": promo,
            "labo": labo,
            "debut": debut,
            "fin": fin,
            "type": p_select(props, "Type"),
            "canal_promo": p_select(props, "Canal de promotion"),
            "canal_achat": p_select(props, "Canal d'achat"),
            "montant": p_number(props, "Montant"),
            "unite": p_select(props, "Unité"),
            "cde_debut": cde_debut,
            "cde_fin": cde_fin,
            "compensation": p_number(props, "Compensation labo"),
            "intercomptoir": p_checkbox(props, "Intercomptoir ?"),
            "detail": p_rich(props, "Détail"),
        })

    ops.sort(key=lambda o: ((o["labo"] or "").upper(), o["debut"] or "", o["promo"]))
    out = {
        "v": 1,
        "date": datetime.date.today().isoformat(),
        "source": "Notion — 🎁 Operations marketing : TRADE (GitHub Action)",
        "nb": len(ops),
        "ops": ops,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, allow_nan=False)
    sans_labo = sum(1 for o in ops if not o["labo"])
    print("OK : %d opérations écrites dans %s (%d sans laboratoire)" % (len(ops), OUT_FILE, sans_labo))


if __name__ == "__main__":
    main()
