#!/usr/bin/env python3
"""
Scraper Voursa.com (API Internal)
Force la récupération des détails techniques (chambres, etc.) et enregistre en CSV.
"""

import time
import re
import json
import requests
import pandas as pd
import urllib.parse
from pathlib import Path

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
API_BASE   = "https://kg4i9mujda.us-east-1.awsapprunner.com/api/real-estate"
LIST_URL   = f"{API_BASE}/search"
DETAIL_URL = f"{API_BASE}/ads"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://voursa.com/",
    "Origin": "https://voursa.com",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

MAX_LISTINGS    = 500   # Objectif final
PAGE_SIZE       = 50
SLEEP_PAGE      = 2.0
SLEEP_DETAIL    = 1.0   # On peut descendre un peu si ça ne bloque pas
MAX_THREADS     = 1     # Séquentiel pour être poli

OUTPUT_CSV = Path("data/raw/raw_data.csv")

# ─────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────
def clean(v):
    if v is None: return None
    s = str(v).strip()
    return s if s else None

def safe_float(v):
    if v is None: return None
    try:
        return float(str(v).replace(",", "").replace(" ", ""))
    except:
        return None

def safe_int(v):
    if v is None: return None
    try:
        # Gérer les cas comme "3 chambres"
        v_str = str(v).replace(",", "").replace(" ", "")
        num = re.search(r'\d+', v_str)
        return int(num.group()) if num else None
    except:
        return None

def anonymize_phone(text):
    if not text: return text
    # Patterns mauritaniens : +222..., 22334455, etc.
    patterns = [r'\b\+?222\s?\d{8}\b', r'\b[234]\d{7}\b', r'\b\d{8,9}\b']
    for p in patterns:
        text = re.sub(p, '[TÉLÉPHONE SUPPRIMÉ]', text)
    return text

def get_from_list(items, icon_name):
    """Cherche une valeur dans un tableau de dicts (details ou highlights)."""
    if not items: return None
    for item in items:
        if isinstance(item, dict) and item.get("iconName") == icon_name:
            return item.get("value")
    return None

def determine_transaction(subcat):
    """Déduit si c'est Vente ou Location."""
    if not subcat: return "Vente"
    s = subcat.lower()
    if any(k in s for k in ["rent", "location", "louer"]):
        return "Location"
    return "Vente"

# ─────────────────────────────────────────
# Logique de Scraping
# ─────────────────────────────────────────

def fetch_json(session, url, params=None, timeout=30):
    try:
        resp = session.get(url, params=params, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
        print(f"  ⚠️  Erreur {resp.status_code} sur {url}")
    except Exception as e:
        print(f"  ❌ Erreur réseau sur {url}: {e}")
    return None

def parse_ad_data(ad_list_obj):
    """Parse les données de base d'une annonce dans la liste."""
    highlights = ad_list_obj.get("highlights", [])
    
    # Extraction depuis highlights
    surface = safe_int(get_from_list(highlights, "AREA_SIZE_KEY"))
    quartier = clean(get_from_list(highlights, "CLOSEST_LANDMARK_KEY"))
    
    subcat = clean(ad_list_obj.get("subcategoryName"))
    
    return {
        "titre": clean(ad_list_obj.get("title")),
        "type_bien": subcat,
        "type_annonce": determine_transaction(subcat),
        "prix": safe_float(ad_list_obj.get("price")),
        "surface_m2": surface,
        "nb_chambres": None,
        "nb_salons": None,
        "nb_sdb": None,
        "quartier": quartier,
        "ville": clean(ad_list_obj.get("location")),
        "description": None,
        "caracteristiques": None,
        "seller": clean(ad_list_obj.get("sellerName")),
        "slug": ad_list_obj.get("slug"),
        "date_publication": ad_list_obj.get("postedAt", "").split("T")[0] if ad_list_obj.get("postedAt") else None,
        "url_annonce": f"https://voursa.com/FR/categories/real_estate/ads/{ad_list_obj.get('slug')}",
        "source": "voursa"
    }

def update_with_details(session, current_data):
    """Complète les données avec l'API de détail."""
    slug = current_data.get("slug")
    if not slug: return current_data
    
    # Encodage propre du slug car il contient de l'arabe
    encoded_slug = urllib.parse.quote(slug)
    url = f"{DETAIL_URL}/{encoded_slug}"
    
    print(f"    🔍 Détails : {slug[:30]}...")
    detail_data = fetch_json(session, url, timeout=45)
    
    if detail_data:
        # Description
        desc = clean(detail_data.get("description"))
        current_data["description"] = anonymize_phone(desc)
        
        # Details techniques (tableau 'details')
        tech_details = detail_data.get("details", [])
        current_data["nb_chambres"] = safe_int(get_from_list(tech_details, "ROOMS_ATTRIBUTE_KEY"))
        current_data["nb_sdb"] = safe_int(get_from_list(tech_details, "BATHROOMS_ATTRIBUTE_KEY"))
        current_data["nb_salons"] = safe_int(get_from_list(tech_details, "HALLS_ATTRIBUTE_KEY"))
        
        # Features
        features = detail_data.get("features", [])
        if features:
            f_list = [f.get("key") if isinstance(f, dict) else str(f) for f in features]
            current_data["caracteristiques"] = " | ".join(f_list)
            
        # Parfois la surface est plus précise dans le détail (overview)
        ov = detail_data.get("overview", [])
        surf_ov = safe_int(get_from_list(ov, "AREA_SIZE_KEY"))
        if surf_ov:
            current_data["surface_m2"] = surf_ov
            
    return current_data

def main():
    print(f"🚀 Démarrage du scraping Voursa (Objectif: {MAX_LISTINGS} annonces)")
    session = requests.Session()
    session.headers.update(HEADERS)
    
    all_data = []
    page = 1
    
    while len(all_data) < MAX_LISTINGS:
        print(f"📄 Page {page}...")
        data = fetch_json(session, LIST_URL, params={"page": page, "size": PAGE_SIZE})
        
        if not data:
            print("  🛑 Impossible de charger la page ou fin des résultats.")
            break
            
        items = data.get("items", [])
        if not items:
            print("  🛑 Plus d'annonces.")
            break
            
        print(f"  ✅ {len(items)} annonces trouvées sur la page.")
        
        for item in items:
            if len(all_data) >= MAX_LISTINGS:
                break
                
            # Données de base
            ad_data = parse_ad_data(item)
            
            # Forcer les détails
            ad_data = update_with_details(session, ad_data)
            
            all_data.append(ad_data)
            n = len(all_data)
            print(f"    ✓ [{n}/{MAX_LISTINGS}] {ad_data['titre'][:40]} | Prix: {ad_data['prix']} | Ch: {ad_data['nb_chambres']}")
            
            # Sauvegarde progressive
            if n % 20 == 0:
                print(f"    💾 Sauvegarde progressive ({n} annonces)...")
                temp_df = pd.DataFrame(all_data)
                temp_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

            # Petit délai entre détails
            time.sleep(SLEEP_DETAIL)
            
        page += 1
        time.sleep(SLEEP_PAGE)

    # Sauvegarde CSV
    if all_data:
        df = pd.DataFrame(all_data)
        # Supprimer le slug et réordonner
        cols = ["titre", "type_bien", "type_annonce", "prix", "surface_m2", 
                "nb_chambres", "nb_salons", "nb_sdb", "quartier", "ville", 
                "description", "caracteristiques", "seller", "date_publication", 
                "url_annonce", "source"]
        df = df[cols]
        
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"\n✨ Scraping terminé ! {len(all_data)} annonces enregistrées dans {OUTPUT_CSV}")
        
        # Petit résumé
        print("\n📊 Statistiques de remplissage :")
        print(df.notna().sum())
    else:
        print("❌ Aucune donnée collectée.")

if __name__ == "__main__":
    main()
