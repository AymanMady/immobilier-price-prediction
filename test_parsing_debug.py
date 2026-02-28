#!/usr/bin/env python3
"""
Script de test pour déboguer le parsing d'une annonce.
"""

import sys
from pathlib import Path

# Ajouter src au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

from src.scraping.common import fetch, polite_sleep
from src.scraping.voursa import parse_listing_page

# URL d'une annonce de test
test_url = "https://voursa.com/FR/categories/real_estate/ads/-جراند-بلازا-grand-plaza-6dc7"

print("Test de parsing d'une annonce...")
print(f"URL: {test_url}")
print()

# Télécharger la page
html = fetch(test_url)
polite_sleep(2.0)

# Parser la page
data = parse_listing_page(html, test_url)

print("\nDonnées extraites:")
print("=" * 60)
for key, value in data.items():
    if value:
        display_value = str(value)
        if len(display_value) > 150:
            display_value = display_value[:150] + "..."
        print(f"{key:20s}: {display_value}")
    else:
        print(f"{key:20s}: None")

print("\n" + "=" * 60)
print("Vérifications:")
print(f"  Titre contient 'Voursa.com': {'Voursa.com' in str(data.get('titre', ''))}")
print(f"  Type_bien contient JSON: {'@context' in str(data.get('type_bien', ''))}")
print(f"  Description contient téléphone: {bool(__import__('re').search(r'\\d{8,9}', str(data.get('description', ''))))}")
print("=" * 60)
print("\n✓ Test terminé. Vérifiez les logs dans .cursor/debug.log")
