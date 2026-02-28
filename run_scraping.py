#!/usr/bin/env python3
"""
Script principal pour lancer le scraping complet des annonces Voursa.
"""

import sys
from pathlib import Path
import pandas as pd
import os

# Ajouter src au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

from src.scraping.voursa import scrape_voursa
from src.scraping.common import COLUMNS

def main():
    """Fonction principale."""
    print("=" * 60)
    print("SCRAPING VOURSA - Annonces Immobilières")
    print("=" * 60)
    print()
    
    # Objectif: ≥ 200 annonces (on vise 500+)
    MAX_LISTINGS = 500
    
    print(f"Objectif: {MAX_LISTINGS} annonces")
    print("Respect de robots.txt: ✓")
    print("Pause entre requêtes: 2+ secondes")
    print()
    
    # Lancer le scraping
    try:
        all_listings = scrape_voursa(max_listings=MAX_LISTINGS)
        
        if len(all_listings) == 0:
            print("\n⚠ Aucune annonce collectée")
            return
        
        # Sauvegarder dans CSV
        output_path = "data/raw/raw_data.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df = pd.DataFrame(all_listings, columns=COLUMNS)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print("\n" + "=" * 60)
        print("RÉSULTATS")
        print("=" * 60)
        print(f"✓ {len(df)} annonces collectées")
        print(f"✓ Données sauvegardées dans: {output_path}")
        print()
        print("Statistiques:")
        print(f"  Annonces avec prix: {df['prix'].notna().sum()}")
        print(f"  Annonces avec surface: {df['surface_m2'].notna().sum()}")
        print(f"  Annonces avec description: {df['description'].notna().sum()}")
        print()
        
        if df['type_bien'].notna().any():
            print("Répartition par type de bien:")
            print(df['type_bien'].value_counts())
            print()
        
        if df['ville'].notna().any():
            print("Répartition par ville:")
            print(df['ville'].value_counts())
            print()
        
        print("✓ Scraping terminé avec succès!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n✗ Erreur lors du scraping: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
