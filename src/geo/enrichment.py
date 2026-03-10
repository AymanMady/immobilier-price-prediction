"""
Module d'enrichissement géographique pour les données immobilières.
"""

import time
from typing import Optional, Tuple, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging

from src.geo.config import (
    QUARTIERS_NOUAKCHOTT,
    NOMINATIM_USER_AGENT,
    NOMINATIM_RATE_LIMIT,
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache pour éviter les requêtes redondantes
_geocoding_cache: Dict[str, Optional[Tuple[float, float]]] = {}


def geocode_location(ville: str, use_cache: bool = True) -> Optional[Tuple[float, float]]:
    """
    Géocode une ville pour obtenir ses coordonnées GPS (latitude, longitude).
    
    Stratégie :
    1. Vérifie si la ville correspond à un quartier connu dans le mapping
    2. Si non, utilise Nominatim pour géocoder "ville, Mauritanie"
    3. Utilise un cache pour éviter les requêtes redondantes
    
    Args:
        ville: Nom de la ville à géocoder
        use_cache: Si True, utilise le cache pour éviter les requêtes redondantes
        
    Returns:
        Tuple (latitude, longitude) ou None si le géocodage échoue
    """
    if not ville or str(ville).strip() == '':
        return None
    
    ville = str(ville).strip()
    
    # Vérifier le cache
    if use_cache and ville in _geocoding_cache:
        return _geocoding_cache[ville]
    
    # Étape 1 : Vérifier si la ville correspond à un quartier connu
    if ville in QUARTIERS_NOUAKCHOTT:
        coords = QUARTIERS_NOUAKCHOTT[ville]
        if use_cache:
            _geocoding_cache[ville] = coords
        logger.debug(f"Ville '{ville}' trouvée dans le mapping des quartiers: {coords}")
        return coords
    
    # Étape 2 : Utiliser Nominatim pour géocoder
    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT)
        
        # Construire la requête : "ville, Mauritanie"
        query = f"{ville}, Mauritanie"
        
        # Respecter le rate limiting
        time.sleep(NOMINATIM_RATE_LIMIT)
        
        location = geolocator.geocode(query, timeout=10)
        
        if location:
            coords = (location.latitude, location.longitude)
            if use_cache:
                _geocoding_cache[ville] = coords
            logger.debug(f"Ville '{ville}' géocodée via Nominatim: {coords}")
            return coords
        else:
            logger.warning(f"Ville '{ville}' non trouvée par Nominatim")
            if use_cache:
                _geocoding_cache[ville] = None
            return None
            
    except GeocoderTimedOut:
        logger.error(f"Timeout lors du géocodage de '{ville}'")
        if use_cache:
            _geocoding_cache[ville] = None
        return None
    except GeocoderServiceError as e:
        logger.error(f"Erreur du service de géocodage pour '{ville}': {e}")
        if use_cache:
            _geocoding_cache[ville] = None
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du géocodage de '{ville}': {e}")
        if use_cache:
            _geocoding_cache[ville] = None
        return None


def calculate_distances(
    latitude: float,
    longitude: float
) -> Dict[str, float]:
    """
    Calcule les distances depuis un point GPS vers les points de référence.
    
    Args:
        latitude: Latitude du point
        longitude: Longitude du point
        
    Returns:
        Dictionnaire avec les distances en km :
        - dist_centre_ville_km
        - dist_aeroport_km
        - dist_plage_km
    """
    from geopy.distance import geodesic
    from src.geo.config import (
        CENTRE_VILLE_KSAR,
        AEROPORT_OUMTOUNSY,
        PLAGE_NOUAKCHOTT,
    )
    
    if latitude is None or longitude is None:
        return {
            'dist_centre_ville_km': None,
            'dist_aeroport_km': None,
            'dist_plage_km': None,
        }
    
    point = (latitude, longitude)
    
    distances = {
        'dist_centre_ville_km': geodesic(point, CENTRE_VILLE_KSAR).kilometers,
        'dist_aeroport_km': geodesic(point, AEROPORT_OUMTOUNSY).kilometers,
        'dist_plage_km': geodesic(point, PLAGE_NOUAKCHOTT).kilometers,
    }
    
    return distances


def get_pois_around(
    latitude: float,
    longitude: float,
    radius_m: int = 1000
) -> Dict[str, int]:
    """
    Récupère les Points d'Intérêt (POI) autour d'un point GPS via Overpass API.
    
    Args:
        latitude: Latitude du point
        longitude: Longitude du point
        radius_m: Rayon de recherche en mètres (défaut: 1000m = 1km)
        
    Returns:
        Dictionnaire avec les compteurs de POI :
        - nb_ecoles_1km
        - nb_mosquees_1km
        - nb_commerces_1km
        - nb_hopitaux_1km
        - nb_total_pois_1km
    """
    import overpy
    import inspect
    from src.geo.config import OVERPASS_API_URL, OVERPASS_TIMEOUT
    
    # #region agent log
    import json
    import time as time_module
    log_data = {
        "overpy_version": getattr(overpy, '__version__', 'unknown'),
        "overpass_api_url": OVERPASS_API_URL,
        "overpass_timeout": OVERPASS_TIMEOUT,
        "latitude": latitude,
        "longitude": longitude,
    }
    try:
        overpass_signature = str(inspect.signature(overpy.Overpass.__init__))
        log_data["overpass_init_signature"] = overpass_signature
    except Exception as e:
        log_data["overpass_init_signature_error"] = str(e)
    try:
        overpass_params = list(inspect.signature(overpy.Overpass.__init__).parameters.keys())
        log_data["overpass_init_params"] = overpass_params
    except Exception as e:
        log_data["overpass_init_params_error"] = str(e)
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "enrichment.py:get_pois_around", "message": "Overpass initialization - checking signature", "data": log_data, "timestamp": time_module.time() * 1000, "hypothesisId": "A,B,C,D,E"}) + "\n")
    # #endregion
    
    if latitude is None or longitude is None:
        return {
            'nb_ecoles_1km': 0,
            'nb_mosquees_1km': 0,
            'nb_commerces_1km': 0,
            'nb_hopitaux_1km': 0,
            'nb_total_pois_1km': 0,
        }
    
    # #region agent log
    log_data2 = {"attempting_init": True, "url": OVERPASS_API_URL, "retry_timeout": OVERPASS_TIMEOUT}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "enrichment.py:get_pois_around", "message": "Attempting Overpass init with retry_timeout", "data": log_data2, "timestamp": time_module.time() * 1000, "hypothesisId": "A,C,E", "runId": "post-fix"}) + "\n")
    # #endregion
    
    api = overpy.Overpass(url=OVERPASS_API_URL, retry_timeout=OVERPASS_TIMEOUT)
    # #region agent log
    log_data3 = {"init_success": True, "used_param": "retry_timeout"}
    with open("/home/bechir/Documents/immobilier-price-prediction/.cursor/debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"location": "enrichment.py:get_pois_around", "message": "Overpass init succeeded with retry_timeout", "data": log_data3, "timestamp": time_module.time() * 1000, "hypothesisId": "A,C,E", "runId": "post-fix"}) + "\n")
    # #endregion
    
    try:
        # Requête pour les écoles
        query_ecoles = f"""
        [out:json][timeout:{OVERPASS_TIMEOUT}];
        (
          node["amenity"="school"](around:{radius_m},{latitude},{longitude});
          way["amenity"="school"](around:{radius_m},{latitude},{longitude});
          relation["amenity"="school"](around:{radius_m},{latitude},{longitude});
        );
        out count;
        """
        result_ecoles = api.query(query_ecoles)
        nb_ecoles = len(result_ecoles.nodes) + len(result_ecoles.ways) + len(result_ecoles.relations)
        
        # Requête pour les mosquées
        query_mosquees = f"""
        [out:json][timeout:{OVERPASS_TIMEOUT}];
        (
          node["amenity"="place_of_worship"]["religion"="islam"](around:{radius_m},{latitude},{longitude});
          way["amenity"="place_of_worship"]["religion"="islam"](around:{radius_m},{latitude},{longitude});
          relation["amenity"="place_of_worship"]["religion"="islam"](around:{radius_m},{latitude},{longitude});
        );
        out count;
        """
        result_mosquees = api.query(query_mosquees)
        nb_mosquees = len(result_mosquees.nodes) + len(result_mosquees.ways) + len(result_mosquees.relations)
        
        # Requête pour les commerces
        query_commerces = f"""
        [out:json][timeout:{OVERPASS_TIMEOUT}];
        (
          node["shop"](around:{radius_m},{latitude},{longitude});
          way["shop"](around:{radius_m},{latitude},{longitude});
          relation["shop"](around:{radius_m},{latitude},{longitude});
        );
        out count;
        """
        result_commerces = api.query(query_commerces)
        nb_commerces = len(result_commerces.nodes) + len(result_commerces.ways) + len(result_commerces.relations)
        
        # Requête pour les hôpitaux
        query_hopitaux = f"""
        [out:json][timeout:{OVERPASS_TIMEOUT}];
        (
          node["amenity"~"^(hospital|clinic)$"](around:{radius_m},{latitude},{longitude});
          way["amenity"~"^(hospital|clinic)$"](around:{radius_m},{latitude},{longitude});
          relation["amenity"~"^(hospital|clinic)$"](around:{radius_m},{latitude},{longitude});
        );
        out count;
        """
        result_hopitaux = api.query(query_hopitaux)
        nb_hopitaux = len(result_hopitaux.nodes) + len(result_hopitaux.ways) + len(result_hopitaux.relations)
        
        # Total des POI
        nb_total = nb_ecoles + nb_mosquees + nb_commerces + nb_hopitaux
        
        return {
            'nb_ecoles_1km': nb_ecoles,
            'nb_mosquees_1km': nb_mosquees,
            'nb_commerces_1km': nb_commerces,
            'nb_hopitaux_1km': nb_hopitaux,
            'nb_total_pois_1km': nb_total,
        }
        
    except Exception as e:
        logger.warning(f"Erreur lors de la récupération des POI pour ({latitude}, {longitude}): {e}")
        return {
            'nb_ecoles_1km': 0,
            'nb_mosquees_1km': 0,
            'nb_commerces_1km': 0,
            'nb_hopitaux_1km': 0,
            'nb_total_pois_1km': 0,
        }


def enrich_dataframe(df, progress_bar: bool = True) -> 'pd.DataFrame':
    """
    Enrichit un DataFrame avec des données géographiques.
    
    Ajoute les colonnes suivantes :
    - latitude, longitude
    - dist_centre_ville_km, dist_aeroport_km, dist_plage_km
    - nb_ecoles_1km, nb_mosquees_1km, nb_commerces_1km, nb_hopitaux_1km, nb_total_pois_1km
    
    Args:
        df: DataFrame pandas avec une colonne 'ville'
        progress_bar: Si True, affiche une barre de progression
        
    Returns:
        DataFrame enrichi
    """
    import pandas as pd
    from tqdm import tqdm
    
    # Créer une copie pour éviter de modifier l'original
    df_enriched = df.copy()
    
    # Initialiser les nouvelles colonnes
    df_enriched['latitude'] = None
    df_enriched['longitude'] = None
    df_enriched['dist_centre_ville_km'] = None
    df_enriched['dist_aeroport_km'] = None
    df_enriched['dist_plage_km'] = None
    df_enriched['nb_ecoles_1km'] = 0
    df_enriched['nb_mosquees_1km'] = 0
    df_enriched['nb_commerces_1km'] = 0
    df_enriched['nb_hopitaux_1km'] = 0
    df_enriched['nb_total_pois_1km'] = 0
    
    # Itérer sur les lignes
    iterator = tqdm(df_enriched.iterrows(), total=len(df_enriched), desc="Enrichissement géographique") if progress_bar else df_enriched.iterrows()
    
    for idx, row in iterator:
        ville = row.get('ville')
        
        # Géocodage
        coords = geocode_location(ville)
        
        if coords:
            lat, lon = coords
            df_enriched.at[idx, 'latitude'] = lat
            df_enriched.at[idx, 'longitude'] = lon
            
            # Calcul des distances
            distances = calculate_distances(lat, lon)
            df_enriched.at[idx, 'dist_centre_ville_km'] = distances['dist_centre_ville_km']
            df_enriched.at[idx, 'dist_aeroport_km'] = distances['dist_aeroport_km']
            df_enriched.at[idx, 'dist_plage_km'] = distances['dist_plage_km']
            
            # Récupération des POI
            pois = get_pois_around(lat, lon)
            df_enriched.at[idx, 'nb_ecoles_1km'] = pois['nb_ecoles_1km']
            df_enriched.at[idx, 'nb_mosquees_1km'] = pois['nb_mosquees_1km']
            df_enriched.at[idx, 'nb_commerces_1km'] = pois['nb_commerces_1km']
            df_enriched.at[idx, 'nb_hopitaux_1km'] = pois['nb_hopitaux_1km']
            df_enriched.at[idx, 'nb_total_pois_1km'] = pois['nb_total_pois_1km']
    
    return df_enriched
