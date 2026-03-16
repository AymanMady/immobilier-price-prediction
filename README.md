# Projet Prédiction Prix Immobilier - Mauritanie

Ce projet est une solution de bout en bout pour la collecte, l'analyse et la prédiction des prix de l'immobilier en Mauritanie. Il utilise des techniques avancées de Web Scraping, de Machine Learning et une interface web moderne pour offrir une estimation précise des biens.

## 🚀 État Actuel : Solution Complète (Scraping + ML + Web)

Le projet a évolué d'un simple scraper vers une plateforme complète incluant un modèle prédictif exposé via une API et un tableau de bord interactif.

### ✅ Accomplissements
- **Collecte de données** : 5000+ annonces extraites via l'API interne de Voursa.com.
- **Machine Learning** : Modèles XGBoost et LightGBM avec Feature Engineering avancé (Target Encoding, transformations log, interactions).
- **Interface Utilisateur** : Application Next.js ultra-rapide avec cartographie interactive.

---

## 🛠 Stack Technique

### Backend (Data & API)
- **Langage** : Python 3.12+
- **Framework API** : FastAPI & Uvicorn (Serveur ASGI)
- **Data Science** : Pandas, NumPy, Scikit-learn, XGBoost, LightGBM
- **Scraping** : Requests, BeautifulSoup4

### Frontend (Application Web)
- **Framework** : Next.js 15 (App Router)
- **Langage** : TypeScript
- **Styling** : Tailwind CSS (Design Premium / Dark Mode)
- **Animations** : Framer Motion
- **Cartographie** : Leaflet & React-Leaflet
- **Visualisation** : Recharts

---

## 📂 Structure du Projet

```text
immobilier-price-prediction/
├── api/                    # 🐍 Backend FastAPI
│   ├── app.py              # Script principal de l'API (Régression & Endpoints)
├── frontend/               # ⚛️ Frontend Next.js
│   ├── src/
│   │   ├── app/            # Routes (Home, Predict, Analysis)
│   │   ├── components/     # Composants réutilisables (Navbar, Map)
│   │   └── lib/            # Types et utilitaires
├── model/                  # 🤖 Artefacts du modèle ML
│   ├── housing_model.pkl   # Meilleur modèle entraîné
│   ├── train_params.pkl    # Stats des quartiers & paramètres
│   └── feature_names.pkl   # Liste des variables d'entrée
├── notebooks/              # 📓 Recherche & Expérimentation Jupyter
├── data/                   # 📊 Données CSV (Brutes & Traitées)
├── src/                    # 🛠 Scripts utilitaires (Scraping original)
└── requirements.txt        # Dépendances Python globales
```

---

## ⚙️ Installation et Exécution

### 1. Préparation de l'environnement
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Lancer le Backend (API)
L'API doit être lancée pour que le formulaire de prédiction fonctionne.
```bash
cd api
../venv/bin/python3 app.py
```
*L'API tourne sur `http://localhost:8001`.*

### 3. Lancer le Frontend (App Web)
Dans un nouveau terminal :
```bash
cd frontend
npm install   # Uniquement la première fois
npm run dev
```
*L'application est accessible sur `http://localhost:3000`.*

---

## 📈 Fonctionnalités du Dashboard
- **Prédiction Directe** : Formulaire basé sur la surface, le quartier et les équipements.
- **Visualisation par Quartier** : Carte interactive OpenStreetMap centrée sur la zone choisie.
- **Market Insights** : Statistiques et graphiques comparatifs entre les zones de Nouakchott.
- **Double Devise** : Prix estimé affiché en MRU (Ouguiya) et conversion indicative en EUR.

---

## 🛡 Respect des Bonnes Pratiques
- **Optimisation API** : Temps de réponse < 200ms pour les prédictions.
- **Feature Consistency** : Même pipeline de traitement entre l'entraînement et la production (API).
- **Responsive Design** : Interface parfaitement adaptée aux mobiles et tablettes.
