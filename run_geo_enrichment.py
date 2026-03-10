#!/usr/bin/env python3
"""
Script pour exécuter l'enrichissement géographique des données immobilières.
Alternative au notebook Jupyter pour une exécution en ligne de commande.
"""

import sys
from pathlib import Path
import pandas as pd
import argparse

# Ajouter le répertoire src au path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'src'))

from src.geo.enrichment import enrich_dataframe


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description='Enrichissement géographique des données immobilières'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/raw/raw_data.csv',
        help='Chemin vers le fichier CSV d\'entrée (défaut: data/raw/raw_data.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/enriched_data.csv',
        help='Chemin vers le fichier CSV de sortie (défaut: data/processed/enriched_data.csv)'
    )
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Nombre de lignes à traiter (pour tester, sinon traite tout le dataset)'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Désactiver la barre de progression'
    )
    
    args = parser.parse_args()
    
    # Vérifier que le fichier d'entrée existe
    input_path = project_root / args.input
    if not input_path.exists():
        print(f"❌ Erreur: Fichier non trouvé: {input_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("ENRICHISSEMENT GÉOGRAPHIQUE - Phase 2")
    print("=" * 60)
    print()
    
    # Charger les données
    print(f"📂 Chargement des données depuis: {input_path}")
    try:
        df = pd.read_csv(input_path)
        print(f"✓ {len(df)} lignes chargées")
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        sys.exit(1)
    
    # Échantillonnage si demandé
    if args.sample:
        print(f"📊 Utilisation d'un échantillon de {args.sample} lignes")
        df = df.head(args.sample).copy()
    
    # Afficher les statistiques
    print(f"\n📊 Statistiques du dataset:")
    print(f"  - Nombre de lignes: {len(df)}")
    print(f"  - Villes uniques: {df['ville'].nunique()}")
    print(f"  - Valeurs manquantes dans 'ville': {df['ville'].isna().sum()}")
    print()
    
    # Enrichissement
    print("🔄 Démarrage de l'enrichissement géographique...")
    print("   ⚠️  Cela peut prendre plusieurs heures pour un grand dataset")
    print("   ⚠️  Nominatim limite à 1 requête/seconde")
    print()
    
    try:
        df_enriched = enrich_dataframe(df, progress_bar=not args.no_progress)
        
        print()
        print("✓ Enrichissement terminé!")
        print()
        print("📊 Statistiques des données enrichies:")
        print(f"  - Lignes avec coordonnées GPS: {df_enriched['latitude'].notna().sum()}")
        print(f"  - Lignes avec distances: {df_enriched['dist_centre_ville_km'].notna().sum()}")
        print(f"  - Lignes avec POI: {(df_enriched['nb_total_pois_1km'] > 0).sum()}")
        print()
        
        # Sauvegarder
        output_path = project_root / args.output
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Sauvegarde dans: {output_path}")
        df_enriched.to_csv(output_path, index=False, encoding='utf-8')
        
        print()
        print("=" * 60)
        print("✅ TERMINÉ!")
        print("=" * 60)
        print(f"✓ {len(df_enriched)} lignes enrichies")
        print(f"✓ Fichier sauvegardé: {output_path}")
        print()
        print("Nouvelles colonnes ajoutées:")
        new_columns = [
            'latitude', 'longitude',
            'dist_centre_ville_km', 'dist_aeroport_km', 'dist_plage_km',
            'nb_ecoles_1km', 'nb_mosquees_1km', 'nb_commerces_1km',
            'nb_hopitaux_1km', 'nb_total_pois_1km'
        ]
        for col in new_columns:
            if col in df_enriched.columns:
                if df_enriched[col].dtype in ['float64', 'float32']:
                    non_null = df_enriched[col].notna().sum()
                else:
                    non_null = (df_enriched[col] > 0).sum()
                print(f"  - {col}: {non_null} valeurs")
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Interruption par l'utilisateur")
        print("💡 Vous pouvez reprendre plus tard - le cache est conservé")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Erreur lors de l'enrichissement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
