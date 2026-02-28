# Projet Prédiction Prix Immobilier - Mauritanie

## Phase 1 : Scraping

Ce projet vise à collecter des données d'annonces immobilières depuis plusieurs sources mauritaniennes pour construire un modèle de prédiction de prix.

### Sources de données
- Voursa.com (https://voursa.com/FR/categories/real_estate)

### Structure du projet

```
immobilier-price-prediction/
├── data/
│   └── raw/
│       └── raw_data.csv          # Données brutes scrapées
├── notebooks/
│   └── 01_scraping.ipynb         # Notebook principal de scraping
├── src/
│   └── scraping/
│       ├── __init__.py
│       ├── common.py             # Fonctions communes
│       └── voursa.py             # Scraper Voursa
├── requirements.txt
└── README.md
```

### Installation

```bash
pip install -r requirements.txt
```

### Utilisation

#### Option 1: Via le notebook Jupyter

Ouvrir le notebook `notebooks/01_scraping.ipynb` et exécuter les cellules dans l'ordre pour scraper les données.

#### Option 2: Via le script Python

```bash
python3 run_scraping.py
```

Le script va scraper jusqu'à 500 annonces (modifiable dans le code) et sauvegarder les résultats dans `data/raw/raw_data.csv`.

#### Option 3: Via le module Python

```python
from src.scraping.voursa import scrape_voursa
from src.scraping.common import save_raw

listings = scrape_voursa(max_listings=200)
save_raw(listings, "data/raw/raw_data.csv")
```

### Respect des bonnes pratiques

- Respect de robots.txt
- Pause de 2+ secondes entre requêtes
- User-Agent clair et identifié
- Anonymisation des numéros de téléphone
