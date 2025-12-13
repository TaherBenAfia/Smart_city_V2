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
│   └── api/                # Application API
│       ├── models.py       # Modèles Django
│       ├── serializers.py  # Serializers DRF
│       ├── views.py        # ViewSets avec analytics
│       ├── urls.py
│       ├── admin.py
│       └── management/commands/run_etl.py
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── App.jsx
│       ├── index.js
│       ├── services/api.js
│       └── components/
│           ├── Dashboard/
│           ├── Interventions/
│           ├── Citizens/
│           └── Layout/
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
