#!/usr/bin/env python3
"""
Test rapide: scrape 10 annonces avec détails depuis Voursa.com
"""

import sys
import json
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.scraping.common import fetch, polite_sleep
from src.scraping.voursa import extract_listing_links, parse_listing_page

BASE_URL = "https://voursa.com"
LISTINGS_URL = "https://voursa.com/FR/categories/real_estate"
MAX_TO_SCRAPE = 10

def main():
    print("=" * 60)
    print("TEST SCRAPING - 10 annonces avec détails")
    print("=" * 60)
    print()

    # Étape 1 : Récupérer la page principale
    print("📥 Récupération de la page de liste...")
    html = fetch(LISTINGS_URL)
    print(f"  → Page chargée ({len(html)} caractères)")
    polite_sleep(2.0)

    # Étape 2 : Extraire les liens
    links = extract_listing_links(html)
    print(f"  → {len(links)} liens d'annonces trouvés")

    if not links:
        print("❌ Aucun lien trouvé. Vérifier le site ou la structure HTML.")
        return

    # Étape 3 : Scraper les 10 premières annonces avec détails
    results = []
    to_process = links[:MAX_TO_SCRAPE]

    print(f"\n📑 Scraping de {len(to_process)} annonces...\n")

    for i, url in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] {url}")
        try:
            listing_html = fetch(url)
            polite_sleep(2.0)

            data = parse_listing_page(listing_html, url)
            results.append(data)

            # Afficher un résumé propre
            print(f"  ✅ Titre       : {data.get('titre') or '❌ Non trouvé'}")
            print(f"     Type bien   : {data.get('type_bien') or '❌ Non trouvé'}")
            print(f"     Type annonce: {data.get('type_annonce') or '❌ Non trouvé'}")
            print(f"     Prix (MRU)  : {data.get('prix') or '❌ Non trouvé'}")
            print(f"     Surface m²  : {data.get('surface_m2') or '❌ Non trouvé'}")
            print(f"     Chambres    : {data.get('nb_chambres') or '❌ Non trouvé'}")
            print(f"     Ville       : {data.get('ville') or '❌ Non trouvé'}")
            print(f"     Quartier    : {data.get('quartier') or '❌ Non trouvé'}")
            desc = data.get('description')
            if desc:
                print(f"     Description : {desc[:80]}...")
            else:
                print(f"     Description : ❌ Non trouvée")
            print()

        except Exception as e:
            print(f"  ❌ Erreur: {e}\n")

    # Résumé final
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"✅ Annonces scrapées : {len(results)}/{len(to_process)}")
    fields = ['titre', 'type_bien', 'prix', 'surface_m2', 'nb_chambres', 'ville', 'description']
    for field in fields:
        found = sum(1 for r in results if r.get(field) is not None)
        print(f"   {field:<20}: {found}/{len(results)} remplis")

    # Sauvegarder en JSON pour inspection
    output_path = project_root / "data" / "raw" / "test_10.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Données sauvegardées dans: {output_path}")


if __name__ == "__main__":
    main()
