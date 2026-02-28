"""
Fonctions communes pour le scraping d'annonces immobilières.
"""

import time
import re
from typing import Optional
import requests
from datetime import datetime, timedelta

# Headers pour les requêtes HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) MauritaniaHousingML/1.0 (academic project)"
}

# Schéma des colonnes pour le CSV
COLUMNS = [
    "titre", "type_bien", "type_annonce",
    "prix", "surface_m2", "nb_chambres", "nb_salons", "nb_sdb",
    "quartier", "ville", "description",
    "caracteristiques",
    "source", "url_annonce", "date_publication"
]


def clean_text(text: Optional[str]) -> Optional[str]:
    """
    Nettoie un texte en supprimant les espaces multiples et en le trimant.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé ou None si l'input est None/vide
    """
    if text is None:
        return None
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if text else None


def safe_int(text: Optional[str]) -> Optional[int]:
    """
    Extrait un entier depuis un texte, en supprimant tous les caractères non-numériques.
    
    Args:
        text: Texte contenant potentiellement un nombre
        
    Returns:
        Entier extrait ou None si aucun nombre trouvé
    """
    if text is None:
        return None
    # Supprimer tous les caractères non-numériques
    digits = re.sub(r"[^\d]", "", str(text))
    return int(digits) if digits else None


def safe_float(text: Optional[str]) -> Optional[float]:
    """
    Extrait un float depuis un texte, en gérant les virgules et points.
    
    Args:
        text: Texte contenant potentiellement un nombre décimal
        
    Returns:
        Float extrait ou None si aucun nombre trouvé
    """
    if text is None:
        return None
    # Remplacer virgules par points et supprimer espaces
    text = str(text).replace(",", ".").replace(" ", "")
    # Extraire nombre avec point décimal
    match = re.search(r"(\d+\.?\d*)", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def anonymize_phone(text: Optional[str]) -> Optional[str]:
    """
    Supprime ou anonymise les numéros de téléphone dans un texte.
    
    Args:
        text: Texte pouvant contenir des numéros de téléphone
        
    Returns:
        Texte avec numéros supprimés/anonymisés ou None
    """
    # #region agent log
    import json
    import time
    log_data = {"input_length": len(text) if text else 0, "input_preview": text[:100] if text else None}
    # #endregion
    
    if text is None:
        return None
    
    # Patterns pour numéros de téléphone (formats mauritaniens)
    patterns = [
        r'\b\d{8,9}\b',  # 8-9 chiffres
        r'\b\+?222\d{8,9}\b',  # Format international
        r'\b0\d{8,9}\b',  # Format local avec 0
    ]
    
    result = str(text)
    phones_found = []
    for pattern in patterns:
        matches = re.findall(pattern, result)
        if matches:
            phones_found.extend(matches)
        result = re.sub(pattern, '[TÉLÉPHONE SUPPRIMÉ]', result)
    
    # #region agent log
    log_data.update({"phones_found": phones_found, "phones_count": len(phones_found), "output_preview": result[:100] if result else None, "still_has_phones": bool(re.search(r'\b\d{8,9}\b', result))})
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "common.py:anonymize_phone", "message": "Phone anonymization", "data": log_data, "timestamp": time.time() * 1000, "hypothesisId": "B"}) + "\n")
    # #endregion
    
    return result if result else None


def polite_sleep(seconds: float = 2.0):
    """
    Pause entre requêtes pour respecter les bonnes pratiques de scraping.
    
    Args:
        seconds: Nombre de secondes à attendre (défaut: 2.0)
    """
    time.sleep(seconds)


def fetch(url: str, timeout: int = 20, max_retries: int = 3) -> str:
    """
    Télécharge le contenu HTML d'une URL avec gestion d'erreurs et retry.
    
    Args:
        url: URL à télécharger
        timeout: Timeout en secondes
        max_retries: Nombre maximum de tentatives
        
    Returns:
        Contenu HTML de la page
        
    Raises:
        requests.RequestException: Si toutes les tentatives échouent
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Backoff exponentiel
    
    raise requests.RequestException("Failed to fetch after retries")


def parse_relative_date(date_text: Optional[str]) -> Optional[str]:
    """
    Convertit une date relative ("il y a X jour(s)") en format ISO.
    
    Args:
        date_text: Texte contenant une date relative
        
    Returns:
        Date au format ISO (YYYY-MM-DD) ou None
    """
    if not date_text:
        return None
    
    date_text = str(date_text).lower().strip()
    
    # Pattern: "il y a X jour(s)" ou "il y a X heure(s)"
    patterns = [
        (r'il y a (\d+)\s*jour', 'days'),
        (r'il y a (\d+)\s*heure', 'hours'),
        (r'il y a (\d+)\s*semaine', 'weeks'),
        (r'il y a (\d+)\s*mois', 'months'),
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, date_text)
        if match:
            value = int(match.group(1))
            now = datetime.now()
            
            if unit == 'days':
                delta = timedelta(days=value)
            elif unit == 'hours':
                delta = timedelta(hours=value)
            elif unit == 'weeks':
                delta = timedelta(weeks=value)
            elif unit == 'months':
                delta = timedelta(days=value * 30)  # Approximation
            else:
                continue
            
            date = now - delta
            return date.strftime('%Y-%m-%d')
    
    return None


def extract_price_mru(price_text: Optional[str]) -> Optional[float]:
    """
    Extrait le prix en MRU depuis un texte.
    
    Args:
        price_text: Texte contenant le prix (ex: "1,050,000 MRU")
        
    Returns:
        Prix en float ou None
    """
    if not price_text:
        return None
    
    # Supprimer "MRU" et espaces, garder chiffres, virgules et points
    cleaned = re.sub(r'[^\d,.]', '', str(price_text))
    # Remplacer virgules par rien (format: 1,050,000)
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None
