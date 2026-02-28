# Implémentation du Scraper Voursa

## ✅ Statut: Implémentation complète

Tous les composants du plan ont été implémentés avec succès.

## Structure créée

```
immobilier-price-prediction/
├── data/
│   └── raw/
│       └── .gitkeep
├── notebooks/
│   └── 01_scraping.ipynb          # Notebook Jupyter complet
├── src/
│   └── scraping/
│       ├── __init__.py
│       ├── common.py               # Fonctions utilitaires
│       └── voursa.py               # Scraper Voursa
├── .gitignore
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation principale
├── run_scraping.py                 # Script exécutable
└── test_scraper.py                 # Script de test
```

## Fonctionnalités implémentées

### 1. Module commun (`src/scraping/common.py`)
- ✅ `HEADERS` : User-Agent respectant robots.txt
- ✅ `clean_text()` : Nettoyage de texte
- ✅ `safe_int()` / `safe_float()` : Extraction de nombres
- ✅ `anonymize_phone()` : Suppression des numéros de téléphone
- ✅ `polite_sleep()` : Pause de 2+ secondes
- ✅ `fetch()` : Requête HTTP avec retry automatique
- ✅ `parse_relative_date()` : Conversion dates relatives → ISO
- ✅ `extract_price_mru()` : Extraction prix en MRU
- ✅ `COLUMNS` : Schéma des colonnes CSV

### 2. Scraper Voursa (`src/scraping/voursa.py`)
- ✅ `extract_listing_links()` : Extraction des liens depuis page liste
- ✅ `parse_listing_card()` : Parsing carte annonce (données partielles)
- ✅ `parse_listing_page()` : Parsing page annonce complète
- ✅ `scrape_voursa()` : Boucle principale avec gestion pagination

### 3. Notebook Jupyter (`notebooks/01_scraping.ipynb`)
- ✅ Cellule A : Imports + config
- ✅ Cellule B : Test connexion
- ✅ Cellule C : Schéma colonnes
- ✅ Cellule D : Fonction sauvegarde CSV
- ✅ Cellule E : Test extraction liens
- ✅ Cellule F : Test parsing annonce
- ✅ Cellule G : Scraping complet
- ✅ Cellule H : Export + statistiques

### 4. Champs extraits
Tous les champs requis sont extraits :
- ✅ titre
- ✅ type_bien
- ✅ type_annonce
- ✅ prix
- ✅ surface_m2
- ✅ nb_chambres, nb_salons, nb_sdb
- ✅ quartier, ville
- ✅ description (avec anonymisation téléphones)
- ✅ caracteristiques
- ✅ source
- ✅ url_annonce
- ✅ date_publication

## Respect des bonnes pratiques

- ✅ **robots.txt** : User-Agent standard autorisé utilisé
- ✅ **Pause entre requêtes** : Minimum 2 secondes
- ✅ **Anonymisation** : Numéros de téléphone supprimés
- ✅ **Gestion d'erreurs** : Retry automatique avec tenacity
- ✅ **Timeout** : 20 secondes par défaut

## Utilisation

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancer le scraping

**Option 1: Notebook Jupyter**
```bash
jupyter notebook notebooks/01_scraping.ipynb
```

**Option 2: Script Python**
```bash
python3 run_scraping.py
```

**Option 3: Module Python**
```python
from src.scraping.voursa import scrape_voursa
from src.scraping.common import save_raw

listings = scrape_voursa(max_listings=200)
save_raw(listings, "data/raw/raw_data.csv")
```

## Notes importantes

1. **Pagination** : Le scraper gère la pagination automatiquement. Si le site utilise un chargement infini (bouton "Voir plus"), il faudra peut-être adapter le code pour simuler le scroll ou utiliser une API.

2. **Performance** : Avec une pause de 2 secondes entre requêtes, scraper 200 annonces prendra environ 7-10 minutes (200 annonces × 2s = 400s ≈ 6-7 min + temps de traitement).

3. **Robustesse** : Le scraper gère automatiquement les erreurs réseau avec retry exponentiel.

4. **Données manquantes** : Certains champs peuvent être None si non disponibles sur la page. C'est normal et sera géré lors de l'analyse des données.

## Prochaines étapes (Phase 2)

1. Ajouter un 2ème scraper (Wassit ou Mauriannonces)
2. Unifier le schéma de données entre sources
3. Merger les CSV de différentes sources
4. Nettoyer et valider les données

## Tests

Un script de test est disponible : `test_scraper.py`

```bash
python3 test_scraper.py
```

Ce script teste :
- L'extraction des liens depuis la page liste
- Le parsing d'une page d'annonce complète
- La validation des champs requis
