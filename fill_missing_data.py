#!/usr/bin/env python3
"""
Script pour compléter les données manquantes dans raw_data.csv en scrapant les URLs.
"""

import sys
from pathlib import Path
import pandas as pd
import time
from tqdm import tqdm
import os

# Ajouter src au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

from src.scraping.voursa import parse_listing_page
from src.scraping.common import fetch, polite_sleep, COLUMNS

def main():
    csv_path = "data/raw/raw_data.csv"
    
    if not os.path.exists(csv_path):
        print(f"Fichier non trouvé: {csv_path}")
        return

    print("Chargement des données...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV: {e}")
        return
        
    original_len = len(df)
    print(f"Total lignes: {original_len}")

    # Identifier les lignes avec surface_m2 manquante ET url_annonce valide
    missing_mask = (df['surface_m2'].isna() | (df['surface_m2'] == 0)) & df['url_annonce'].notna()
    rows_to_process = df[missing_mask]
    
    count_missing = len(rows_to_process)
    print(f"Trouvé {count_missing} annonces avec surface_m2 manquante et URL valide.")
    
    if count_missing == 0:
        print("Rien à faire.")
        return

    print("Démarrage du scraping des données manquantes...")
    
    processed_count = 0
    updated_count = 0
    
    try:
        # tqdm for progress bar
        pbar = tqdm(rows_to_process.iterrows(), total=count_missing, desc="Processing")
        for index, row in pbar:
            url = row['url_annonce']
            
            try:
                # Récupérer le HTML
                html = fetch(url, timeout=15)
                
                # Parser la page
                data = parse_listing_page(html, url)
                
                if not data:
                    print(f"  [Warn] Pas de données extraites pour {url}")
                    continue

                updated = False
                
                # Debug info
                # print(f"  [Debug] {url} -> Surface found: {data.get('surface_m2')}")

                # Surface
                current_surface = df.at[index, 'surface_m2']
                if data.get('surface_m2') and (pd.isna(current_surface) or current_surface == 0):
                    df.at[index, 'surface_m2'] = data['surface_m2']
                    updated = True
                    # print(f"    -> Update Surface: {data['surface_m2']}")

                # Chambres
                if data.get('nb_chambres') and (pd.isna(df.at[index, 'nb_chambres']) or df.at[index, 'nb_chambres'] == 0):
                    df.at[index, 'nb_chambres'] = data['nb_chambres']
                    updated = True
                    
                # Salons
                if data.get('nb_salons') and (pd.isna(df.at[index, 'nb_salons']) or df.at[index, 'nb_salons'] == 0):
                    df.at[index, 'nb_salons'] = data['nb_salons']
                    updated = True
                
                # SDB
                if data.get('nb_sdb') and (pd.isna(df.at[index, 'nb_sdb']) or df.at[index, 'nb_sdb'] == 0):
                    df.at[index, 'nb_sdb'] = data['nb_sdb']
                    updated = True

                # Quartier
                if data.get('quartier') and pd.isna(df.at[index, 'quartier']):
                    df.at[index, 'quartier'] = data['quartier']
                    updated = True

                # Description (si elle était manquante, très courte, ou semble être du JSON garbage)
                current_desc = str(df.at[index, 'description']) if pd.notna(df.at[index, 'description']) else ""
                new_desc = data.get('description')
                
                # Detect garbage description (starts with "UTC" or contains "messages":{)
                is_garbage = False
                if '"messages":{' in current_desc or current_desc.strip().startswith('"UTC"'):
                    is_garbage = True
                
                if new_desc and (len(current_desc) < 20 or pd.isna(df.at[index, 'description']) or is_garbage):
                    df.at[index, 'description'] = new_desc
                    updated = True
                    # print("    -> Update Description")

                if updated:
                    updated_count += 1
                    # Update progress bar description
                    pbar.set_postfix({"Updated": updated_count, "Last Surface": data.get('surface_m2')})
                
                processed_count += 1
                
                # Sauvegarder périodiquement toutes les 5 requêtes
                if processed_count % 5 == 0:
                    df.to_csv(csv_path, index=False)
                
                # Pause pour être poli
                polite_sleep(1.0)
                
            except Exception as e:
                # print(f"\nErreur sur {url}: {e}")
                pass
                
    except KeyboardInterrupt:
        print("\nArrêt par l'utilisateur.")
    except Exception as e:
        print(f"\nErreur globale: {e}")
    
    # Sauvegarde finale
    print(f"\nSauvegarde finale dans {csv_path}...")
    df.to_csv(csv_path, index=False)
    
    print(f"Terminé. {updated_count} lignes mises à jour sur {processed_count} traitées.")

if __name__ == "__main__":
    main()
