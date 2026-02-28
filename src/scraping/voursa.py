"""
Scraper pour voursa.com - Annonces immobilières en Mauritanie.
"""

import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .common import (
    fetch, clean_text, safe_int, safe_float, anonymize_phone,
    polite_sleep, parse_relative_date, extract_price_mru, HEADERS
)

BASE_URL = "https://voursa.com"
LISTINGS_URL = "https://voursa.com/FR/categories/real_estate"


def extract_listing_links(html: str) -> List[str]:
    """
    Extrait les liens vers les pages d'annonces depuis la page de liste.
    
    Args:
        html: Contenu HTML de la page de liste
        
    Returns:
        Liste des URLs complètes des annonces
    """
    soup = BeautifulSoup(html, 'lxml')
    links = []
    seen_urls = set()
    
    # Chercher dans les articles (structure observée: <article> contenant <a>)
    articles = soup.find_all('article')
    for article in articles:
        link_elem = article.find('a', href=True)
        if link_elem:
            href = link_elem.get('href', '')
            if '/FR/categories/real_estate/ads/' in href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in seen_urls:
                    links.append(full_url)
                    seen_urls.add(full_url)
    
    # Si pas d'articles trouvés, chercher directement les liens
    if not links:
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/FR/categories/real_estate/ads/' in href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in seen_urls:
                    links.append(full_url)
                    seen_urls.add(full_url)
    
    return links


def parse_listing_card(card_html: str, base_url: str = BASE_URL) -> Optional[Dict]:
    """
    Parse une carte d'annonce depuis la page de liste (données partielles).
    
    Args:
        card_html: HTML de la carte d'annonce
        base_url: URL de base du site
        
    Returns:
        Dictionnaire avec les données extraites ou None
    """
    soup = BeautifulSoup(card_html, 'lxml')
    
    # Extraire le lien
    link_elem = soup.find('a', href=True)
    if not link_elem:
        return None
    
    href = link_elem.get('href', '')
    if '/FR/categories/real_estate/ads/' not in href:
        return None
    
    url_annonce = urljoin(base_url, href)
    
    # Titre
    titre_elem = soup.find('h3')
    titre = clean_text(titre_elem.get_text()) if titre_elem else None
    
    # Prix (format: "1,050,000 MRU")
    prix_elem = soup.find(string=re.compile(r'MRU'))
    prix = None
    if prix_elem:
        prix_text = prix_elem.strip()
        prix = extract_price_mru(prix_text)
    
    # Type de bien
    type_bien = None
    type_elem = soup.find(string=re.compile(r'(Immobilier résidentiel|Terrain|Bureau|Entrepôt|Boutique|Immobilier commercial)'))
    if type_elem:
        type_bien = clean_text(type_elem.strip())
    
    # Superficie (dans badge "Superficie · {valeur}")
    surface_m2 = None
    superficie_elem = soup.find(string=re.compile(r'Superficie'))
    if superficie_elem:
        # Chercher le nombre après "Superficie ·"
        match = re.search(r'Superficie\s*·\s*(\d+)', str(superficie_elem))
        if match:
            surface_m2 = safe_int(match.group(1))
    
    # Quartier (dans badge "Point le plus proche · {nom}")
    quartier = None
    quartier_elem = soup.find(string=re.compile(r'Point le plus proche'))
    if quartier_elem:
        match = re.search(r'Point le plus proche\s*·\s*(.+)', str(quartier_elem))
        if match:
            quartier = clean_text(match.group(1))
    
    # Date relative ("il y a X jour(s)")
    date_publication = None
    date_elem = soup.find(string=re.compile(r'il y a'))
    if date_elem:
        date_publication = parse_relative_date(date_elem.strip())
    
    # Ville (peut être dans le texte de localisation)
    ville = None
    ville_elem = soup.find(string=re.compile(r'(Nouakchott|Nouadhibou|Rosso|Atar|Kaédi|Zouérat)'))
    if ville_elem:
        ville = clean_text(ville_elem.strip())
    
    return {
        'titre': titre,
        'type_bien': type_bien,
        'type_annonce': None,  # Sera déterminé depuis la page complète
        'prix': prix,
        'surface_m2': surface_m2,
        'nb_chambres': None,
        'nb_salons': None,
        'nb_sdb': None,
        'quartier': quartier,
        'ville': ville,
        'description': None,  # Sera extrait depuis la page complète
        'caracteristiques': None,
        'source': 'voursa',
        'url_annonce': url_annonce,
        'date_publication': date_publication
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def parse_listing_page(html: str, url: str) -> Dict:
    """
    Parse une page d'annonce complète pour extraire tous les détails.
    
    Args:
        html: Contenu HTML de la page d'annonce
        url: URL de la page d'annonce
        
    Returns:
        Dictionnaire avec toutes les données extraites
    """
    # #region agent log
    import json
    log_data = {"url": url, "html_length": len(html)}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:160", "message": "parse_listing_page entry", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "A"}) + "\n")
    # #endregion
    
    soup = BeautifulSoup(html, 'lxml')
    
    # #region agent log
    # Vérifier si JSON-LD est présent
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    log_data = {"json_ld_count": len(json_ld_scripts), "has_json_ld": len(json_ld_scripts) > 0}
    if json_ld_scripts:
        try:
            json_content = json.loads(json_ld_scripts[0].string) if json_ld_scripts[0].string else None
            log_data["json_ld_type"] = json_content.get("@type") if json_content else None
            log_data["json_ld_category"] = json_content.get("category") if json_content else None
        except:
            log_data["json_ld_parse_error"] = True
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:165", "message": "JSON-LD detection", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "A"}) + "\n")
    # #endregion
    
    data = {
        'titre': None,
        'type_bien': None,
        'type_annonce': None,
        'prix': None,
        'surface_m2': None,
        'nb_chambres': None,
        'nb_salons': None,
        'nb_sdb': None,
        'quartier': None,
        'ville': None,
        'description': None,
        'caracteristiques': None,
        'source': 'voursa',
        'url_annonce': url,
        'date_publication': None
    }
    
    # Titre (généralement dans un h1 ou h2)
    # #region agent log
    titre_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading', re.I))
    if not titre_elem:
        titre_elem = soup.find('title')
    titre_raw = titre_elem.get_text() if titre_elem else None
    log_data = {"titre_raw": titre_raw[:100] if titre_raw else None, "titre_source": "h1/h2/h3" if soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading', re.I)) else "title_tag"}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:181", "message": "Titre extraction", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "C"}) + "\n")
    # #endregion
    if titre_elem:
        titre_text = clean_text(titre_elem.get_text())
        # Supprimer le préfixe "Voursa.com | " si présent
        if titre_text and titre_text.startswith("Voursa.com | "):
            titre_text = titre_text.replace("Voursa.com | ", "", 1).strip()
        data['titre'] = titre_text
    
    # Prix - Utiliser JSON-LD si disponible, sinon HTML
    json_ld_price = None
    if json_ld_scripts and json_ld_scripts[0].string:
        try:
            json_content = json.loads(json_ld_scripts[0].string)
            offers = json_content.get("offers", {})
            if isinstance(offers, dict):
                price_str = offers.get("price")
                if price_str:
                    json_ld_price = safe_float(price_str)
        except:
            pass
    
    if json_ld_price:
        data['prix'] = json_ld_price
    else:
        # Chercher dans le HTML
        prix_elem = soup.find(string=re.compile(r'MRU'))
        if prix_elem:
            prix_text = prix_elem.strip()
            data['prix'] = extract_price_mru(prix_text)
    
    # Type de bien - Utiliser JSON-LD si disponible (plus fiable)
    # #region agent log
    json_ld_category = None
    if json_ld_scripts and json_ld_scripts[0].string:
        try:
            json_content = json.loads(json_ld_scripts[0].string)
            json_ld_category = json_content.get("category")
        except:
            pass
    
    # Sinon, chercher dans le HTML (exclure les balises script)
    type_elem = None
    type_parent_name = None
    if not json_ld_category:
        for elem in soup.find_all(string=re.compile(r'(Immobilier résidentiel|Terrain|Bureau|Entrepôt|Boutique|Immobilier commercial)')):
            # Ignorer le contenu des balises script
            parent = elem.parent if hasattr(elem, 'parent') else None
            if parent and parent.name != 'script':
                type_elem = elem
                type_parent_name = parent.name
                break
    
    log_data = {"json_ld_category": json_ld_category, "type_elem_found": type_elem is not None, "type_elem_parent": type_parent_name, "type_elem_text": clean_text(type_elem.strip())[:50] if type_elem else None}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:194", "message": "Type bien extraction", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "A"}) + "\n")
    # #endregion
    
    # Priorité au JSON-LD, sinon HTML
    if json_ld_category:
        data['type_bien'] = clean_text(json_ld_category)
    elif type_elem:
        data['type_bien'] = clean_text(type_elem.strip())
    
    # Type d'annonce (Vente/Location)
    type_annonce_elem = soup.find(string=re.compile(r'(vente|location|à vendre|à louer)', re.I))
    if type_annonce_elem:
        text = type_annonce_elem.lower()
        if 'location' in text or 'louer' in text:
            data['type_annonce'] = 'Location'
        elif 'vente' in text or 'vendre' in text:
            data['type_annonce'] = 'Vente'
    else:
        # Par défaut, si prix élevé, probablement vente
        data['type_annonce'] = 'Vente'
    
    # Description - Utiliser JSON-LD si disponible, sinon HTML
    # #region agent log
    json_ld_description = None
    if json_ld_scripts and json_ld_scripts[0].string:
        try:
            json_content = json.loads(json_ld_scripts[0].string)
            json_ld_description = json_content.get("description")
        except:
            pass
    
    # Sinon, chercher dans le HTML (exclure les scripts et JSON)
    desc_elem = None
    if not json_ld_description:
        # Chercher dans les divs avec classes spécifiques
        for elem in soup.find_all(['div', 'p', 'section'], class_=re.compile(r'description|content|text|details', re.I)):
            if elem.name != 'script' and not (elem.find_parent('script')):
                text = elem.get_text().strip()
                # Ignorer les textes trop courts ou génériques
                if text and len(text) > 20 and text.lower() not in ['accueil', 'home', 'description']:
                    desc_elem = elem
                    break
        
        # Si pas trouvé, chercher tous les paragraphes et prendre le plus long (mais pas "Accueil")
        if not desc_elem:
            paragraphs = [p for p in soup.find_all('p') if p.name != 'script' and not p.find_parent('script')]
            if paragraphs:
                # Filtrer les paragraphes trop courts ou génériques
                valid_paras = [p for p in paragraphs if len(p.get_text().strip()) > 20 and p.get_text().strip().lower() not in ['accueil', 'home']]
                if valid_paras:
                    longest = max(valid_paras, key=lambda p: len(p.get_text()))
                    desc_elem = longest
    
    desc_raw = json_ld_description or (desc_elem.get_text() if desc_elem else None)
    log_data = {"json_ld_desc": bool(json_ld_description), "desc_found": desc_raw is not None, "desc_length": len(desc_raw) if desc_raw else 0, "desc_preview": desc_raw[:100] if desc_raw else None, "has_phone": bool(re.search(r'\d{8,9}', desc_raw or ''))}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:211", "message": "Description extraction", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "D"}) + "\n")
    # #endregion
    
    if json_ld_description:
        data['description'] = anonymize_phone(clean_text(json_ld_description))
    elif desc_elem:
        data['description'] = anonymize_phone(clean_text(desc_elem.get_text()))
    
    # Caractéristiques (chambres, salons, salles de bain, superficie)
    # Chercher dans les badges, listes, ou textes structurés
    text_content = soup.get_text()
    
    # Nombre de chambres
    chambres_match = re.search(r'(\d+)\s*(chambre|pièce)', text_content, re.I)
    if chambres_match:
        data['nb_chambres'] = safe_int(chambres_match.group(1))
    
    # Nombre de salons
    salons_match = re.search(r'(\d+)\s*salon', text_content, re.I)
    if salons_match:
        data['nb_salons'] = safe_int(salons_match.group(1))
    
    # Nombre de salles de bain
    sdb_match = re.search(r'(\d+)\s*(salle\s*de\s*bain|s\.?d\.?b\.?|bain)', text_content, re.I)
    if sdb_match:
        data['nb_sdb'] = safe_int(sdb_match.group(1))
    
    # Superficie
    superficie_match = re.search(r'(\d+)\s*(m²|m2|mètre|superficie)', text_content, re.I)
    if superficie_match:
        data['surface_m2'] = safe_int(superficie_match.group(1))
    else:
        # Chercher dans badges "Superficie · {valeur}"
        superficie_elem = soup.find(string=re.compile(r'Superficie'))
        if superficie_elem:
            match = re.search(r'Superficie\s*·\s*(\d+)', str(superficie_elem))
            if match:
                data['surface_m2'] = safe_int(match.group(1))
    
    # Quartier
    quartier_elem = soup.find(string=re.compile(r'Point le plus proche|Quartier|Zone'))
    if quartier_elem:
        match = re.search(r'(?:Point le plus proche|Quartier|Zone)\s*[:·]?\s*(.+)', str(quartier_elem), re.I)
        if match:
            data['quartier'] = clean_text(match.group(1))
    
    # Ville
    ville_match = re.search(r'(Nouakchott|Nouadhibou|Rosso|Atar|Kaédi|Zouérat)', text_content, re.I)
    if ville_match:
        data['ville'] = ville_match.group(1)
    
    # Date de publication
    date_elem = soup.find(string=re.compile(r'il y a'))
    if date_elem:
        data['date_publication'] = parse_relative_date(date_elem.strip())
    
    # Caractéristiques supplémentaires (collecter en texte)
    caracteristiques = []
    for elem in soup.find_all(['span', 'div'], class_=re.compile(r'badge|tag|feature', re.I)):
        text = clean_text(elem.get_text())
        if text and len(text) < 50:  # Éviter les textes trop longs
            caracteristiques.append(text)
    
    if caracteristiques:
        data['caracteristiques'] = ' | '.join(caracteristiques)
    
    # #region agent log
    log_data = {"titre": data['titre'][:50] if data['titre'] else None, "type_bien": data['type_bien'][:50] if data['type_bien'] else None, "has_json_in_type": bool(data['type_bien'] and '@context' in str(data['type_bien'])) if data['type_bien'] else False}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "voursa.py:279", "message": "parse_listing_page exit", "data": log_data, "timestamp": __import__("time").time() * 1000, "hypothesisId": "A"}) + "\n")
    # #endregion
    
    return data


def scrape_voursa(max_listings: int = 500, start_url: Optional[str] = None) -> List[Dict]:
    """
    Scrape les annonces depuis Voursa.com.
    
    Args:
        max_listings: Nombre maximum d'annonces à scraper
        start_url: URL de départ (optionnel, par défaut la page principale)
        
    Returns:
        Liste de dictionnaires contenant les données des annonces
    """
    if start_url is None:
        start_url = LISTINGS_URL
    
    all_listings = []
    seen_urls = set()
    current_url = start_url
    page_count = 0
    max_pages = 50  # Limite de sécurité
    
    print(f"Démarrage du scraping Voursa (objectif: {max_listings} annonces)")
    
    while len(all_listings) < max_listings and page_count < max_pages:
        try:
            print(f"\nPage {page_count + 1}: {current_url}")
            html = fetch(current_url)
            polite_sleep(2.0)
            
            # Extraire les liens des annonces
            listing_links = extract_listing_links(html)
            print(f"  → {len(listing_links)} annonces trouvées sur cette page")
            
            # Scraper chaque annonce
            for link in listing_links:
                if link in seen_urls:
                    continue
                
                if len(all_listings) >= max_listings:
                    break
                
                try:
                    print(f"  Scraping: {link}")
                    listing_html = fetch(link)
                    polite_sleep(2.0)
                    
                    listing_data = parse_listing_page(listing_html, link)
                    all_listings.append(listing_data)
                    seen_urls.add(link)
                    
                    print(f"    ✓ {listing_data.get('titre', 'Sans titre')[:50]}")
                    
                except Exception as e:
                    print(f"    ✗ Erreur sur {link}: {e}")
                    continue
            
            # Chercher le lien "Voir plus" ou pagination
            soup = BeautifulSoup(html, 'lxml')
            next_link = None
            
            # Chercher bouton "Voir plus" ou lien suivant
            voir_plus = soup.find('button', string=re.compile(r'Voir plus', re.I))
            if voir_plus:
                # Si c'est un chargement infini, on peut simuler un scroll ou chercher une API
                # Pour l'instant, on arrête après la première page si pas de pagination classique
                pass
            
            # Chercher pagination classique
            next_elem = soup.find('a', string=re.compile(r'suivant|next|>', re.I))
            if next_elem and next_elem.get('href'):
                next_link = urljoin(BASE_URL, next_elem['href'])
            
            if not next_link:
                # Si pas de pagination, on peut essayer de modifier l'URL avec un paramètre de page
                # Ou arrêter si on a assez d'annonces
                if len(listing_links) == 0:
                    print("  Aucune annonce trouvée, arrêt du scraping")
                    break
                else:
                    print("  Pas de pagination détectée, arrêt après cette page")
                    break
            
            current_url = next_link
            page_count += 1
            
        except Exception as e:
            print(f"Erreur lors du scraping de la page: {e}")
            break
    
    print(f"\n✓ Scraping terminé: {len(all_listings)} annonces collectées")
    return all_listings
