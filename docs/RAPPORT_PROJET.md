# Rapport de Projet
## Smart City Analytics Platform - Neo-Sousse 2030

**Module:** Base de Données  
**Année Universitaire:** 2024-2025

---

## 1. Introduction

Ce projet consiste à développer une plateforme de gestion des données urbaines pour la métropole "Neo-Sousse 2030". L'objectif est de collecter, analyser et visualiser les données IoT pour améliorer la qualité de vie et réduire l'empreinte écologique.

### Stack Technique
- **Base de données:** MySQL (SQLite pour développement)
- **Backend:** Python Django + Django REST Framework
- **Frontend:** React.js (interface basique)
- **ETL:** Scripts Python intégrés

---

## 2. Modélisation de la Base de Données

### 2.1 Schéma Entité-Relation

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ARRONDISSEMENT │     │   PROPRIETAIRE  │     │   TECHNICIEN    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ nom             │     │ nom             │     │ matricule (UK)  │
│ code_postal(UK) │     │ type            │     │ nom, prenom     │
│ superficie_km2  │     │ contact_email   │     │ specialite      │
│ population      │     │ contact_tel     │     │ type_validation │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │ 1                     │ 1                     │ 1
         │                       │                       │
         ▼ *                     ▼ *                     ▼ *
┌─────────────────┐                              ┌─────────────────┐
│     CAPTEUR     │                              │  INTERVENTION   │
├─────────────────┤                              ├─────────────────┤
│ uuid (PK)       │◄─────────────────────────────│ capteur_uuid(FK)│
│ type            │                              │ id (PK)         │
│ latitude        │                              │ date_heure      │
│ longitude       │                              │ nature          │
│ statut          │                              │ duree_minutes   │
│ date_install    │                              │ cout            │
│ arrond_id (FK)  │                              │ reduction_co2   │
│ proprio_id (FK) │                              │ tech_interv(FK) │◄── Contrainte:
└────────┬────────┘                              │ tech_valid (FK) │    Différents!
         │                                       └─────────────────┘
         │ 1
         ▼ *
┌─────────────────┐
│     MESURE      │
├─────────────────┤
│ id (PK)         │
│ capteur_uuid(FK)│
│ timestamp       │
│ valeurs (JSON)  │
│ indice_pollut   │
│ qualite_air     │
└─────────────────┘
```

```
┌─────────────────┐     ┌─────────────────┐
│     CITOYEN     │     │    VEHICULE     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ identifiant(UK) │     │ plaque (UK)     │
│ nom, prenom     │     │ type            │
│ email (UK)      │     │ energie         │
│ score_engagem   │     │ marque, modele  │
│ pref_mobilite   │     │ capacite        │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │ 1                     │ 1
         ▼ *                     ▼ *
┌─────────────────┐     ┌─────────────────┐
│  CONSULTATION   │     │     TRAJET      │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ citoyen_id (FK) │     │ vehicule_id(FK) │
│ timestamp       │     │ origine, dest   │
│ type_donnee     │     │ depart, arrivee │
│ zone_consultee  │     │ distance_km     │
└─────────────────┘     │ economie_co2    │
                        └─────────────────┘
```

### 2.2 Liste des Tables

| Table | Description | Clé Primaire | Clés Étrangères |
|-------|-------------|--------------|-----------------|
| `arrondissement` | Zones géographiques | id | - |
| `proprietaire` | Propriétaires des capteurs | id | - |
| `capteur` | Capteurs IoT | uuid | proprietaire_id, arrondissement_id |
| `mesure` | Mesures des capteurs | id | capteur_uuid |
| `technicien` | Techniciens de maintenance | id | - |
| `intervention` | Interventions de maintenance | id | capteur_uuid, tech_intervenant_id, tech_validateur_id |
| `citoyen` | Citoyens engagés | id | - |
| `consultation` | Historique consultations | id | citoyen_id |
| `vehicule` | Véhicules autonomes | id | - |
| `trajet` | Trajets des véhicules | id | vehicule_id |

### 2.3 Justification 3ème Forme Normale (3FN)

**1ère Forme Normale (1FN):**
- Toutes les colonnes contiennent des valeurs atomiques
- Pas de groupes répétitifs
- Exemple: `latitude` et `longitude` sont séparées (pas un seul champ "position")

**2ème Forme Normale (2FN):**
- Respect de 1FN + tous les attributs non-clés dépendent entièrement de la clé primaire
- Exemple: Dans `capteur`, tous les attributs (type, statut, etc.) dépendent uniquement de `uuid`

**3ème Forme Normale (3FN):**
- Respect de 2FN + aucune dépendance transitive
- Exemple: L'adresse du propriétaire est dans `proprietaire`, pas répétée dans `capteur`
- Le nom de l'arrondissement est dans `arrondissement`, pas dans `capteur`

---

## 3. Contraintes d'Intégrité

### 3.1 Clés Primaires
```sql
-- Exemples de clés primaires
CREATE TABLE capteur (
    uuid CHAR(36) PRIMARY KEY,  -- UUID unique
    ...
);

CREATE TABLE intervention (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ...
);
```

### 3.2 Clés Étrangères
```sql
-- Contraintes FK avec règles de cascade
CONSTRAINT fk_capteur_proprietaire 
    FOREIGN KEY (proprietaire_id) REFERENCES proprietaire(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,

CONSTRAINT fk_intervention_capteur 
    FOREIGN KEY (capteur_uuid) REFERENCES capteur(uuid)
    ON DELETE RESTRICT ON UPDATE CASCADE
```

### 3.3 Contrainte Métier: 2 Techniciens par Intervention

**Règle:** Chaque intervention nécessite **deux techniciens différents**:
- Un **intervenant** qui effectue le travail
- Un **validateur** (humain ou IA) qui valide

**Implémentation SQL:**
```sql
-- Deux clés étrangères obligatoires
technicien_intervenant_id INT NOT NULL,
technicien_validateur_id INT NOT NULL,

-- Contrainte CHECK: ils doivent être différents
CONSTRAINT chk_techniciens_differents 
    CHECK (technicien_intervenant_id != technicien_validateur_id)
```

**Implémentation Django (models.py):**
```python
class Intervention(models.Model):
    technicien_intervenant = models.ForeignKey(
        Technicien, on_delete=models.PROTECT,
        related_name='interventions_effectuees'
    )
    technicien_validateur = models.ForeignKey(
        Technicien, on_delete=models.PROTECT,
        related_name='interventions_validees'
    )
    
    def clean(self):
        """Validation: techniciens différents"""
        if self.technicien_intervenant_id == self.technicien_validateur_id:
            raise ValidationError(
                "L'intervenant et le validateur doivent être différents."
            )
```

### 3.4 Contraintes d'Unicité
```sql
UNIQUE KEY uk_citoyen_email (email),
UNIQUE KEY uk_technicien_matricule (matricule),
UNIQUE KEY uk_vehicule_plaque (plaque)
```

### 3.5 Contraintes CHECK
```sql
-- Validation des valeurs ENUM
type ENUM('AIR', 'TRAFIC', 'ENERGIE', 'DECHETS', 'ECLAIRAGE'),
statut ENUM('ACTIF', 'MAINTENANCE', 'HORS_SERVICE'),

-- Validation des plages
score_engagement DECIMAL(5,2) CHECK (score_engagement >= 0 AND score_engagement <= 100)
```

---

## 4. Backend Django

### 4.1 Structure du Projet
```
backend/
├── manage.py
├── requirements.txt
├── smart_city/
│   ├── settings.py      # Configuration Django/MySQL
│   ├── urls.py          # Routes principales
│   └── wsgi.py
└── api/
    ├── models.py        # 10 modèles Django
    ├── serializers.py   # Serializers DRF
    ├── views.py         # ViewSets + endpoints
    ├── urls.py          # Routes API
    ├── admin.py         # Interface admin
    └── management/commands/
        ├── seed_data.py # Données initiales
        └── run_etl.py   # Pipeline ETL
```

### 4.2 Endpoints API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/capteurs/` | Liste tous les capteurs |
| GET | `/api/capteurs/{uuid}/` | Détail d'un capteur |
| POST | `/api/capteurs/` | Créer un capteur |
| PUT | `/api/capteurs/{uuid}/` | Modifier un capteur |
| DELETE | `/api/capteurs/{uuid}/` | Supprimer un capteur |
| GET | `/api/capteurs/zones_polluees_24h/` | **Zones les plus polluées** |
| GET | `/api/capteurs/disponibilite_par_arrondissement/` | **Taux disponibilité** |
| GET | `/api/trajets/top_trajets_co2/` | **Top trajets CO2** |
| GET | `/api/citoyens/top_engages/` | **Top citoyens** |

### 4.3 Exemple d'Endpoint Analytique

```python
# views.py - Zones polluées 24h
@action(detail=False, methods=['get'])
def zones_polluees_24h(self, request):
    depuis = timezone.now() - timedelta(hours=24)
    
    zones = Arrondissement.objects.annotate(
        pollution_moyenne=Avg(
            'capteurs__mesures__indice_pollution',
            filter=Q(
                capteurs__type='AIR',
                capteurs__mesures__timestamp__gte=depuis
            )
        )
    ).filter(pollution_moyenne__isnull=False)
    .order_by('-pollution_moyenne')
    
    return Response({
        'periode': '24 dernières heures',
        'zones': [...]
    })
```

---

## 5. Pipeline ETL

### 5.1 Commandes Disponibles

```bash
# Créer les données initiales
python manage.py seed_data

# Générer mesures, interventions, trajets
python manage.py run_etl --action generate

# Générer les rapports analytiques
python manage.py run_etl --action report
```

### 5.2 Données Générées

| Entité | Quantité |
|--------|----------|
| Arrondissements | 5 |
| Propriétaires | 4 |
| Techniciens | 10 |
| Capteurs | 50 |
| Citoyens | 30 |
| Véhicules | 20 |
| Mesures | 500 |
| Interventions | 100 |
| Trajets | 200 |

---

## 6. Frontend React (Interface Basique)

L'interface utilisateur est volontairement simple pour démontrer que le cœur du travail est le backend.

### Fonctionnalités
- Affichage des KPIs (capteurs, disponibilité, CO2)
- Tableau des interventions avec les 2 techniciens
- Liste des citoyens engagés
- Navigation entre les vues

---

## 7. Conclusion

Ce projet démontre:
1. Une modélisation relationnelle en **3FN**
2. Des contraintes d'intégrité (FK, UK, CHECK)
3. La contrainte métier des **2 techniciens par intervention**
4. Une API REST complète avec Django
5. Des endpoints analytiques pour les KPIs

### Commandes d'Installation

```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py run_etl
python manage.py runserver

# Frontend
cd frontend
npm install
npm start
```
