"""
Configuration pour l'enrichissement géographique.
Contient les coordonnées de référence pour les quartiers de Nouakchott
et les points de référence (centre-ville, aéroport, plage).
"""

# Mapping des quartiers de Nouakchott avec leurs coordonnées GPS
QUARTIERS_NOUAKCHOTT = {
    'Tevragh Zeina': (18.1036, -15.9785),
    'Ksar': (18.0866, -15.9750),
    'Arafat': (18.0550, -15.9610),
    'Dar Naim': (18.1200, -15.9450),
    'Toujounine': (18.0680, -15.9350),
    'Sebkha': (18.0730, -15.9870),
    'El Mina': (18.0580, -16.0050),
    'Riyad': (18.0850, -15.9550),
    'Riyadh': (18.0850, -15.9550),  # Variante orthographique
    'Teyarett': (18.0950, -15.9700),
}

# Points de référence pour le calcul des distances
CENTRE_VILLE_KSAR = (18.0866, -15.9750)  # Centre historique (Ksar)

# Aéroport Oumtounsy (Nouakchott)
# Coordonnées approximatives - à vérifier/ajuster si nécessaire
# L'aéroport est situé au nord-est de Nouakchott
AEROPORT_OUMTOUNSY = (18.0981, -15.9481)  # Coordonnées approximatives

# Plage de Nouakchott (coordonnées approximatives)
# La plage principale est située à l'ouest de la ville, près d'El Mina
PLAGE_NOUAKCHOTT = (18.0580, -16.0100)  # Coordonnées approximatives (près d'El Mina)

# Configuration Nominatim
NOMINATIM_USER_AGENT = "Mauritania-Housing-ML/1.0 (academic project)"
NOMINATIM_RATE_LIMIT = 1.1  # secondes entre les requêtes

# Configuration Overpass API
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 25  # secondes

# Rayon pour la recherche de POI (en mètres)
POI_RADIUS_M = 1000  # 1 km
