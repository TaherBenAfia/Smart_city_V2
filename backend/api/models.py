"""
Models Django pour Smart City Neo-Sousse 2030
Traduction du schéma relationnel MySQL en classes Django ORM
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Arrondissement(models.Model):
    """Zones géographiques de la métropole Neo-Sousse"""
    
    nom = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10, unique=True)
    superficie_km2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'arrondissement'
        ordering = ['nom']
        verbose_name = 'Arrondissement'
        verbose_name_plural = 'Arrondissements'
    
    def __str__(self):
        return f"{self.nom} ({self.code_postal})"


class Proprietaire(models.Model):
    """Propriétaires des capteurs IoT"""
    
    TYPE_CHOICES = [
        ('MUNICIPALITE', 'Municipalité'),
        ('PRIVE', 'Partenaire Privé'),
    ]
    
    nom = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_email = models.EmailField(blank=True, null=True)
    contact_telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proprietaire'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"


class Capteur(models.Model):
    """Capteurs IoT déployés dans la ville"""
    
    TYPE_CHOICES = [
        ('AIR', 'Qualité de l\'air'),
        ('TRAFIC', 'Trafic routier'),
        ('ENERGIE', 'Consommation énergétique'),
        ('DECHETS', 'Gestion des déchets'),
        ('ECLAIRAGE', 'Éclairage public'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('MAINTENANCE', 'En maintenance'),
        ('HORS_SERVICE', 'Hors service'),
    ]
    
    uuid = models.CharField(primary_key=True, max_length=36, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    date_installation = models.DateField()
    description = models.TextField(blank=True, null=True)
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.PROTECT, related_name='capteurs')
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.PROTECT, related_name='capteurs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'capteur'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.arrondissement.nom} ({self.statut})"


class Mesure(models.Model):
    """Mesures collectées par les capteurs"""
    
    QUALITE_CHOICES = [
        ('BON', 'Bon'),
        ('MODERE', 'Modéré'),
        ('MAUVAIS', 'Mauvais'),
        ('TRES_MAUVAIS', 'Très mauvais'),
        ('DANGEREUX', 'Dangereux'),
    ]
    
    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE, related_name='mesures', db_column='capteur_uuid')
    timestamp = models.DateTimeField()
    valeurs = models.JSONField(help_text="Valeurs des mesures selon le type de capteur")
    indice_pollution = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           validators=[MinValueValidator(0), MaxValueValidator(500)])
    qualite_air = models.CharField(max_length=20, choices=QUALITE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mesure'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['capteur', 'timestamp']),
            models.Index(fields=['indice_pollution']),
        ]
    
    def __str__(self):
        return f"Mesure {self.capteur.type} - {self.timestamp}"


class Technicien(models.Model):
    """Techniciens de maintenance"""
    
    TYPE_VALIDATION_CHOICES = [
        ('IA', 'Validation IA'),
        ('HUMAIN', 'Validation Humaine'),
    ]
    
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    type_validation = models.CharField(max_length=10, choices=TYPE_VALIDATION_CHOICES, default='HUMAIN')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'technicien'
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.matricule})"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Intervention(models.Model):
    """
    Interventions de maintenance sur les capteurs
    CONTRAINTE MÉTIER: Chaque intervention nécessite 2 techniciens différents
    """
    
    NATURE_CHOICES = [
        ('PREDICTIVE', 'Maintenance Prédictive'),
        ('CORRECTIVE', 'Maintenance Corrective'),
        ('CURATIVE', 'Maintenance Curative'),
    ]
    
    STATUT_CHOICES = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]
    
    capteur = models.ForeignKey(Capteur, on_delete=models.PROTECT, related_name='interventions', db_column='capteur_uuid')
    date_heure = models.DateTimeField()
    nature = models.CharField(max_length=20, choices=NATURE_CHOICES)
    description = models.TextField(blank=True, null=True)
    duree_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    cout = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reduction_co2 = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True,
                                        help_text="Réduction CO2 en kg")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PLANIFIEE')
    
    # Contrainte: 2 techniciens obligatoires (intervenant + validateur)
    technicien_intervenant = models.ForeignKey(
        Technicien, on_delete=models.PROTECT, 
        related_name='interventions_effectuees',
        help_text="Technicien qui effectue l'intervention"
    )
    technicien_validateur = models.ForeignKey(
        Technicien, on_delete=models.PROTECT,
        related_name='interventions_validees',
        help_text="Technicien qui valide (IA ou Humain)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'intervention'
        ordering = ['-date_heure']
    
    def clean(self):
        """Validation: les deux techniciens doivent être différents"""
        if self.technicien_intervenant_id == self.technicien_validateur_id:
            raise ValidationError({
                'technicien_validateur': "L'intervenant et le validateur doivent être différents."
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Intervention {self.nature} - {self.capteur} ({self.date_heure.date()})"


class Citoyen(models.Model):
    """Citoyens engagés dans la démarche écologique"""
    
    MOBILITE_CHOICES = [
        ('VELO', 'Vélo'),
        ('TRANSPORT_COMMUN', 'Transport en commun'),
        ('COVOITURAGE', 'Covoiturage'),
        ('MARCHE', 'Marche'),
        ('VEHICULE_ELECTRIQUE', 'Véhicule électrique'),
    ]
    
    identifiant_unique = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.TextField(blank=True, null=True)
    score_engagement = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score écologique (0-100)"
    )
    preference_mobilite = models.CharField(
        max_length=30, choices=MOBILITE_CHOICES, default='TRANSPORT_COMMUN'
    )
    notifications_actives = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'citoyen'
        ordering = ['-score_engagement']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} (Score: {self.score_engagement})"


class Consultation(models.Model):
    """Historique des consultations de données par les citoyens"""
    
    SOURCE_CHOICES = [
        ('WEB', 'Application Web'),
        ('MOBILE', 'Application Mobile'),
        ('API', 'API'),
    ]
    
    citoyen = models.ForeignKey(Citoyen, on_delete=models.CASCADE, related_name='consultations')
    timestamp = models.DateTimeField(auto_now_add=True)
    type_donnee = models.CharField(max_length=50, help_text="Type de donnée consultée")
    zone_consultee = models.CharField(max_length=100, blank=True, null=True)
    duree_consultation_secondes = models.IntegerField(null=True, blank=True)
    source_consultation = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='WEB')
    
    class Meta:
        db_table = 'consultation'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.citoyen} - {self.type_donnee} ({self.timestamp})"


class Vehicule(models.Model):
    """Véhicules autonomes municipaux"""
    
    TYPE_CHOICES = [
        ('BUS', 'Bus'),
        ('NAVETTE', 'Navette autonome'),
        ('UTILITAIRE', 'Véhicule utilitaire'),
        ('COLLECTE_DECHETS', 'Collecte des déchets'),
    ]
    
    ENERGIE_CHOICES = [
        ('ELECTRIQUE', 'Électrique'),
        ('HYDROGENE', 'Hydrogène'),
        ('HYBRIDE', 'Hybride'),
    ]
    
    STATUT_CHOICES = [
        ('EN_SERVICE', 'En service'),
        ('MAINTENANCE', 'En maintenance'),
        ('HORS_SERVICE', 'Hors service'),
    ]
    
    plaque = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    energie = models.CharField(max_length=20, choices=ENERGIE_CHOICES)
    marque = models.CharField(max_length=100, blank=True, null=True)
    modele = models.CharField(max_length=100, blank=True, null=True)
    annee_mise_service = models.IntegerField(null=True, blank=True)
    capacite_passagers = models.IntegerField(null=True, blank=True)
    autonomie_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_SERVICE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicule'
        ordering = ['plaque']
    
    def __str__(self):
        return f"{self.plaque} - {self.get_type_display()} ({self.get_energie_display()})"


class Trajet(models.Model):
    """Trajets effectués par les véhicules autonomes"""
    
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    vehicule = models.ForeignKey(Vehicule, on_delete=models.PROTECT, related_name='trajets')
    origine = models.CharField(max_length=255)
    origine_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    origine_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    destination = models.CharField(max_length=255)
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    depart = models.DateTimeField()
    arrivee = models.DateTimeField(null=True, blank=True)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    economie_co2 = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True,
                                       help_text="Économie CO2 en kg vs véhicule thermique")
    nombre_passagers = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trajet'
        ordering = ['-depart']
    
    def __str__(self):
        return f"{self.vehicule.plaque}: {self.origine} → {self.destination}"
    
    @property
    def duree_minutes(self):
        """Calcule la durée du trajet en minutes"""
        if self.arrivee and self.depart:
            delta = self.arrivee - self.depart
            return int(delta.total_seconds() / 60)
        return None
