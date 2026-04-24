# Smart City Analytics Platform - Neo-Sousse 2030

Plateforme complète de gestion des données urbaines pour améliorer la qualité de vie et réduire l'empreinte écologique.

## 📁 Structure du Projet

```
ProjetModuleBDD/
├── database/
│   ├── schema.sql          # Script DDL (création tables)
│   └── seed_data.sql       # Script DML (données de test)
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── smart_city/         # Configuration Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                # Application API
│   ├── automata/           # Moteur d'Automates à États Finis (FSM)
│   ├── compiler/           # Compilateur Langage Naturel vers SQL
│   ├── ai_reports/         # Service de Génération de Rapports IA
│   │   ├── models.py       # Modèles Django
│   │   ├── serializers.py  # Serializers DRF
│   │   ├── views.py        # ViewSets avec analytics
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── management/commands/run_etl.py
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── App.jsx
│       ├── index.js
│       ├── services/api.js
│       ├── components/
│       │   ├── Dashboard/
│       │   ├── Interventions/
│       │   ├── Citizens/
│       │   ├── Layout/
│       │   ├── Automata/   # Visualiseur SVG pour FSM
│       │   ├── Compiler/   # Interface pour requêtes NL
│       │   └── AIReports/  # Génération de rapports IA
└── docs/
    └── powerbi_guide.md    # Guide Power BI
```

---

## 🚀 Installation

### 1. Base de données MySQL

```bash
# Créer la base de données
mysql -u root -p < database/schema.sql

# Insérer les données de test
mysql -u root -p smart_city_db < database/seed_data.sql
```

### 2. Backend Django

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données (créer .env si nécessaire)
# DB_NAME=smart_city_db
# DB_USER=root
# DB_PASSWORD=votre_mot_de_passe

# Appliquer les migrations Django
python manage.py migrate

# Créer un superutilisateur admin
python manage.py createsuperuser

# Générer des données avec l'ETL
python manage.py run_etl --action all

# Lancer le serveur
python manage.py runserver
```

L'API sera disponible sur: http://localhost:8000/api/

### 3. Frontend React

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer l'application
npm start
```

L'application sera disponible sur: http://localhost:3000/

---

## 📡 Endpoints API

| Endpoint | Description |
|----------|-------------|
| `/api/capteurs/` | CRUD Capteurs |
| `/api/capteurs/zones_polluees_24h/` | Zones les plus polluées |
| `/api/capteurs/disponibilite_par_arrondissement/` | Taux disponibilité |
| `/api/interventions/` | CRUD Interventions |
| `/api/trajets/top_trajets_co2/` | Top trajets CO2 |
| `/api/citoyens/top_engages/` | Top citoyens engagés |
| `/api/automata/` | Endpoints du Moteur FSM (Transitions & Historique) |
| `/api/compiler/` | Traduction et exécution de requêtes NL |
| `/api/ai/` | Génération de rapports avec LLM (OpenAI / Template) |
| `/api/docs/` | Documentation Swagger |

---

## ⚙️ Commande ETL

```bash
# Générer toutes les données et rapports
python manage.py run_etl --action all

# Générer seulement les données
python manage.py run_etl --action generate --mesures 1000 --interventions 200

# Générer seulement les rapports
python manage.py run_etl --action report
```

---

## 🔒 Contrainte Métier: 2 Techniciens

Chaque intervention nécessite **2 techniciens différents**:
- Un **intervenant** qui effectue le travail
- Un **validateur** (humain ou IA) qui valide

Cette règle est implémentée:
- SQL: Contrainte `CHECK (technicien_intervenant_id != technicien_validateur_id)`
- Django: Validation dans `Intervention.clean()` et `InterventionSerializer.validate()`

---

## 🌟 V2.0 - Modules Académiques Avancés

Dans la version 2.0, la plateforme a été enrichie avec 3 nouveaux modules académiques majeurs basés sur des concepts de compilation et d'intelligence artificielle :

### 1. Compilateur Langage Naturel → SQL (`compiler/`)
- **Lexer & Parser** codés from scratch en Python pur.
- **AST (Abstract Syntax Tree)** générant des requêtes SQL dynamiques compatibles avec l'ORM et la base de données.
- Permet aux utilisateurs d'interroger la base de données avec des phrases comme : *"Affiche les 5 zones les plus polluées"*.

### 2. Moteur d'Automates FSM (`automata/`)
- Moteur d'automates à états finis déterministes codé en Python.
- Gère le cycle de vie complet de trois entités clés de la ville :
  - **Capteurs** (`INACTIF → ACTIF → SIGNALE → EN_MAINTENANCE → HORS_SERVICE`)
  - **Interventions** (`DEMANDE → TECH1_ASSIGNE → TECH2_VALIDE → IA_VALIDE → TERMINE`)
  - **Véhicules** (`STATIONNE → EN_ROUTE → EN_PANNE → ARRIVE`)
- Graphiques SVG générés dynamiquement dans le frontend pour visualiser l'état actuel et l'historique des transitions.

### 3. Service de Rapports IA (`ai_reports/`)
- Intégration de l'API OpenAI pour analyser les données de la ville et proposer des rapports textuels professionnels.
- **Mode Fallback intelligent** (Offline/Template) garantissant le fonctionnement sans clé d'API.
- Fonctionnalité de diagnostic et recommandations pour un équipement donné.

---

## 📊 Power BI

Voir le guide complet: `docs/powerbi_guide.md`

---

## 🧪 Tests

```bash
cd backend
python manage.py test api.tests
```

---

## 📄 Licence

Projet universitaire - Neo-Sousse 2030
