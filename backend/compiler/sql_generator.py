"""
Générateur SQL pour le compilateur NL → SQL
Parcourt l'AST et produit des requêtes SQL valides contre le schéma MySQL existant.
"""

from .ast_nodes import QueryNode


class SQLGeneratorError(Exception):
    """Erreur de génération SQL"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


# ============================================================================
# Mappages entité → colonnes par défaut
# ============================================================================

ENTITY_COLUMNS = {
    'capteur': {
        'select': ['uuid', 'type', 'statut', 'latitude', 'longitude', 'date_installation'],
        'display_name': 'Capteurs',
    },
    'intervention': {
        'select': [
            'id', 'capteur_uuid', 'date_heure', 'nature', 'statut',
            'duree_minutes', 'cout', 'reduction_co2'
        ],
        'display_name': 'Interventions',
    },
    'citoyen': {
        'select': [
            'id', 'identifiant_unique',
            "CONCAT(prenom, ' ', nom) AS nom_complet",
            'email', 'score_engagement', 'preference_mobilite'
        ],
        'display_name': 'Citoyens',
    },
    'trajet': {
        'select': [
            't.id', 'v.plaque', 't.origine', 't.destination',
            't.distance_km', 't.economie_co2', 't.nombre_passagers', 't.statut'
        ],
        'joins': 'JOIN vehicule v ON t.vehicule_id = v.id',
        'alias': 't',
        'display_name': 'Trajets',
    },
    'arrondissement': {
        'select': ['id', 'nom', 'code_postal', 'superficie_km2', 'population'],
        'display_name': 'Zones / Arrondissements',
    },
    'mesure': {
        'select': ['id', 'capteur_uuid', 'timestamp', 'indice_pollution', 'qualite_air'],
        'display_name': 'Mesures',
    },
    'vehicule': {
        'select': ['id', 'plaque', 'type', 'energie', 'statut', 'autonomie_km'],
        'display_name': 'Véhicules',
    },
    'technicien': {
        'select': [
            'id', 'matricule',
            "CONCAT(prenom, ' ', nom) AS nom_complet",
            'specialite', 'type_validation', 'actif'
        ],
        'display_name': 'Techniciens',
    },
}


class SQLGenerator:
    """
    Générateur SQL: parcourt l'AST et produit du SQL valide.
    """

    def __init__(self):
        self.sql = ""
        self.params = []

    def generate(self, ast: QueryNode) -> str:
        """
        Génère une requête SQL à partir de l'AST.
        Retourne la chaîne SQL.
        """
        if not ast.entity:
            raise SQLGeneratorError("Aucune entité cible dans l'AST.")

        table_name = ast.entity.table_name
        entity_config = ENTITY_COLUMNS.get(table_name)

        if not entity_config:
            raise SQLGeneratorError(
                f"Table '{table_name}' non reconnue. "
                f"Tables disponibles: {list(ENTITY_COLUMNS.keys())}"
            )

        # Cas spécial: zones polluées (requiert agrégation sur plusieurs tables)
        if table_name == 'arrondissement' and ast.order and ast.order.column == 'pollution_moyenne':
            return self._generate_zones_polluees(ast)

        # Cas spécial: COUNT
        if ast.query_type == 'COUNT' and ast.aggregate and ast.aggregate.function == 'COUNT':
            return self._generate_count(ast, table_name, entity_config)

        # Cas général: SELECT
        return self._generate_select(ast, table_name, entity_config)

    def _generate_select(self, ast: QueryNode, table_name: str, config: dict) -> str:
        """Génère un SELECT standard"""
        alias = config.get('alias', '')
        table_ref = f"{table_name} {alias}" if alias else table_name

        # Colonnes
        columns = ', '.join(config['select'])

        # Construction du SQL
        parts = [f"SELECT {columns}"]
        parts.append(f"FROM {table_ref}")

        # JOINs
        if 'joins' in config:
            parts.append(config['joins'])

        # WHERE
        where_clauses = self._build_where(ast, table_name, alias)
        if where_clauses:
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        # ORDER BY
        if ast.order:
            col = ast.order.column
            # Qualifier la colonne avec l'alias si nécessaire
            if alias and '.' not in col:
                col = f"{alias}.{col}"
            parts.append(f"ORDER BY {col} {ast.order.direction}")

        # LIMIT
        if ast.limit:
            parts.append(f"LIMIT {ast.limit.count}")

        return '\n'.join(parts)

    def _generate_count(self, ast: QueryNode, table_name: str, config: dict) -> str:
        """Génère un SELECT COUNT(*)"""
        alias = config.get('alias', '')
        table_ref = f"{table_name} {alias}" if alias else table_name

        parts = [f"SELECT COUNT(*) AS total"]
        parts.append(f"FROM {table_ref}")

        # JOINs
        if 'joins' in config:
            parts.append(config['joins'])

        # WHERE
        where_clauses = self._build_where(ast, table_name, alias)
        if where_clauses:
            parts.append(f"WHERE {' AND '.join(where_clauses)}")

        return '\n'.join(parts)

    def _generate_zones_polluees(self, ast: QueryNode) -> str:
        """Génère la requête spéciale pour les zones les plus polluées"""
        sql = """SELECT
    a.nom AS zone,
    a.code_postal,
    ROUND(AVG(m.indice_pollution), 2) AS pollution_moyenne,
    COUNT(m.id) AS nombre_mesures
FROM arrondissement a
JOIN capteur c ON a.id = c.arrondissement_id
JOIN mesure m ON c.uuid = m.capteur_uuid
WHERE c.type = 'AIR'
    AND m.indice_pollution IS NOT NULL
GROUP BY a.id, a.nom, a.code_postal
ORDER BY pollution_moyenne DESC"""

        if ast.limit:
            sql += f"\nLIMIT {ast.limit.count}"

        return sql

    def _build_where(self, ast: QueryNode, table_name: str, alias: str) -> list:
        """Construit les clauses WHERE à partir des filtres de l'AST"""
        clauses = []

        for f in ast.filters:
            col = f.column
            # Qualifier avec alias si nécessaire
            if alias and '.' not in col:
                col = f"{alias}.{col}"

            if f.operator == '=' and isinstance(f.value, str) and not f.value.replace('.', '').isdigit():
                clauses.append(f"{col} = '{f.value}'")
            else:
                clauses.append(f"{col} {f.operator} {f.value}")

        return clauses
