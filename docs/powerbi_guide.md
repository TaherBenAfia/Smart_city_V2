# Power BI - Guide d'Intégration

## Smart City Neo-Sousse 2030

Ce guide décrit comment connecter Power BI à la base de données MySQL et créer des visualisations analytiques pour la plateforme Smart City.

---

## 1. Connexion à MySQL

### Prérequis
- Power BI Desktop installé
- Connecteur MySQL ODBC (télécharger depuis [MySQL Connector/ODBC](https://dev.mysql.com/downloads/connector/odbc/))
- Base de données `smart_city_db` accessible

### Étapes de Configuration

1. **Ouvrir Power BI Desktop** → Obtenir les données → MySQL Database

2. **Paramètres de connexion:**
   ```
   Serveur: localhost
   Base de données: smart_city_db
   Mode de connectivité: Import (recommandé)
   ```

3. **Authentification:**
   - Utilisateur: `root` (ou votre utilisateur MySQL)
   - Mot de passe: votre mot de passe MySQL

4. **Tables à importer:**
   - `arrondissement`
   - `capteur`
   - `mesure`
   - `intervention`
   - `technicien`
   - `citoyen`
   - `vehicule`
   - `trajet`

---

## 2. Modèle de Données Power BI

### Relations à configurer

```
arrondissement (1) ─────────────────── (*) capteur
capteur        (1) ─────────────────── (*) mesure
capteur        (1) ─────────────────── (*) intervention
technicien     (1) ── intervenant ──── (*) intervention
technicien     (1) ── validateur ───── (*) intervention
vehicule       (1) ─────────────────── (*) trajet
citoyen        (1) ─────────────────── (*) consultation
```

### Mesures DAX Recommandées

```dax
// Taux de disponibilité global
Taux Disponibilité = 
DIVIDE(
    COUNTROWS(FILTER(capteur, capteur[statut] = "ACTIF")),
    COUNTROWS(capteur)
) * 100

// Total CO2 économisé
Total CO2 Économisé = SUM(trajet[economie_co2])

// Indice pollution moyen (24h)
Pollution Moyenne 24h = 
CALCULATE(
    AVERAGE(mesure[indice_pollution]),
    FILTER(mesure, mesure[timestamp] >= NOW() - 1)
)

// Nombre interventions terminées
Interventions Terminées = 
COUNTROWS(FILTER(intervention, intervention[statut] = "TERMINEE"))
```

---

## 3. Carte Thermique - Pollution/Trafic

### Configuration

1. **Ajouter visuel:** "Carte" (Map) ou "Filled Map"

2. **Champs:**
   - Emplacement: `capteur[latitude]`, `capteur[longitude]`
   - Légende: `capteur[type]`
   - Taille: `mesure[indice_pollution]` (moyenne)
   - Couleur: Échelle de gradient

3. **Format de la carte:**
   ```
   Style: Sombre (pour cohérence avec le thème)
   Bulles: Dégradé du vert au rouge selon pollution
   ```

4. **Filtres:**
   - Type de capteur = "AIR" pour pollution
   - Type de capteur = "TRAFIC" pour trafic
   - Plage temporelle: 24 dernières heures

### Configuration Heatmap personnalisée

Pour une vraie carte thermique, utiliser le visuel "Heatmap" depuis AppSource:

1. **Importer le visuel** depuis Microsoft AppSource > "Heatmap"

2. **Configuration:**
   ```
   Catégorie X: arrondissement[nom]
   Catégorie Y: Heure (extrait de mesure[timestamp])
   Valeur: mesure[indice_pollution] (moyenne)
   ```

---

## 4. Graphiques CO2 - Évolution

### Graphique Linéaire: Économies CO2 dans le temps

1. **Ajouter visuel:** Graphique en courbes

2. **Configuration:**
   ```
   Axe X: trajet[depart] (par jour/semaine/mois)
   Valeurs: SUM(trajet[economie_co2])
   Légende: vehicule[type]
   ```

3. **Mise en forme:**
   - Couleurs par type de véhicule
   - Afficher les points de données
   - Ajouter ligne de tendance

### Graphique à Barres: CO2 par Type de Véhicule

1. **Configuration:**
   ```
   Axe Y: vehicule[type]
   Valeurs: SUM(trajet[economie_co2])
   Tri: Par valeur décroissante
   ```

### KPI Card: Total CO2

1. **Ajouter visuel:** Carte KPI

2. **Configuration:**
   ```
   Valeur: [Total CO2 Économisé]
   Objectif: 10000 (défini selon vos objectifs)
   Format: Nombre avec "kg" comme suffixe
   ```

---

## 5. Dashboard Complet

### Page 1: Vue d'ensemble
- 4x Cartes KPI (Capteurs, Disponibilité, CO2, Interventions)
- Carte géographique des capteurs
- Graphique barres: Capteurs par arrondissement

### Page 2: Qualité de l'Air
- Heatmap pollution par zone/heure
- Graphique: Évolution pollution sur 7 jours
- Tableau: Top zones polluées

### Page 3: Mobilité Durable
- Graphique: Économies CO2 temporelles
- Graphique: Répartition par type de véhicule
- Tableau: Top trajets éco-responsables

### Page 4: Maintenance
- Graphique: Interventions par nature
- Graphique: Coûts de maintenance
- Liste: Interventions récentes

---

## 6. Actualisation des Données

### Configuration Gateway (optionnel pour données en temps réel)

1. Installer **Power BI Gateway** sur le serveur MySQL
2. Configurer la source de données dans le portail Power BI Service
3. Planifier l'actualisation:
   - Fréquence recommandée: Toutes les heures
   - Pour les données critiques: Toutes les 15 minutes

---

## 7. Export et Partage

1. **Publier sur Power BI Service:**
   - Fichier → Publier → Sélectionner l'espace de travail

2. **Créer un tableau de bord:**
   - Épingler les visuels clés au tableau de bord
   - Configurer les alertes sur les KPIs critiques

3. **Partager:**
   - Partager avec les parties prenantes (Municipalité, partenaires)
   - Intégrer dans le portail web Smart City si nécessaire
