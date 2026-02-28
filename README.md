# Projet Prédiction Prix Immobilier - Mauritanie

Ce projet vise à collecter des données d'annonces immobilières depuis plusieurs sources mauritaniennes pour construire un modèle de prédiction de prix (Machine Learning).

## 🚀 État Actuel : Phase 1 - Collecte de Données (Scraping)

Nous avons implémenté un collecteur performant pour le site **Voursa.com**. Contrairement au parsing HTML classique, nous utilisons l'API JSON interne du site pour obtenir toutes les données structurées, y compris les détails techniques (chambres, salons, salles de bain).

### ✅ Accomplissements
- Collecte de **500 annonces** complètes.
- Extraction des détails profonds : nombre de chambres, salles de bain, salons.
- Nettoyage automatique : Anonymisation des numéros de téléphone dans les descriptions.
- Export structuré : Fichier au format CSV compatible Excel.

### 📂 Structure du projet

```
immobilier-price-prediction/
├── data/
│   └── raw/
│       └── raw_data.csv          # 500 annonces brutes scrapées
├── src/
│   └── scraping/
│       ├── common.py             # Fonctions utilitaires (nettoyage, requêtes)
│       └── voursa.py             # Logique originale BeautifulSoup
├── scrape_api.py                 # SCRIPT PRINCIPAL : Scraper API JSON optimisé
├── requirements.txt
├── .gitignore                    # Configuré pour inclure raw_data.csv
└── README.md
```

## 🛠 Installation

1.  Clonez le dépôt.
2.  Créez et activez votre environnement virtuel :
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

## 📈 Utilisation

### Exécuter le Scraping Final
Pour mettre à jour les données ou collecter de nouvelles annonces :

```bash
python3 scrape_api.py
```
*Le script est configuré pour collecter jusqu'à 500 annonces avec une pause de 1 seconde entre les requêtes de détail pour respecter le serveur.*

## 📊 Format des Données (raw_data.csv)

Les champs suivants sont collectés :
- **titre** : Nom de l'annonce.
- **type_bien** : Appartement, Villa, Terrain, etc.
- **prix** : En MRU (converti en float).
- **surface_m2** : Superficie en m².
- **nb_chambres / nb_salons / nb_sdb** : Détails techniques (si disponibles).
- **ville / quartier** : Localisation précise.
- **description** : Texte complet (anonymisé).
- **caracteristiques** : Liste des équipements (Garage, Sécurité, etc.).
- **source / url_annonce** : Origine des données pour vérification.

## 🛡 Respect des Bonnes Pratiques

- **Politesse :** Délai entre les requêtes pour ne pas surcharger le serveur.
- **Identification :** User-Agent personnalisé.
- **Confidentialité :** Suppression automatique de tout numéro de téléphone détecté dans les textes libres.
- **Maintenance :** Utilisation de l'API interne pour une meilleure stabilité face aux changements de design.
