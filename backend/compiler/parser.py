"""
Parser (Analyseur Syntaxique) pour le compilateur NL → SQL
Construit un AST (Arbre Syntaxique Abstrait) à partir des tokens du lexer.

Grammaire simplifiée:
  Query     → Keyword Entity Filters? Order? Limit?
  Keyword   → KEYWORD
  Entity    → ENTITY
  Filters   → Filter (Filter)*
  Filter    → FILTER | DOMAIN_FIELD OPERATOR NUMBER
  Order     → MODIFIER FILTER
  Limit     → NUMBER
"""

from typing import List, Optional
from .lexer import Token
from .ast_nodes import (
    QueryNode, EntityNode, FilterNode,
    AggregateNode, OrderNode, LimitNode
)


class ParserError(Exception):
    """Erreur d'analyse syntaxique"""

    def __init__(self, message, tokens=None):
        self.message = message
        self.tokens = tokens or []
        super().__init__(message)


class Parser:
    """
    Analyseur syntaxique descendant récursif.
    Transforme une liste de tokens en un AST.
    """

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.query_node: Optional[QueryNode] = None

    def parse(self, tokens: List[Token]) -> QueryNode:
        """
        Point d'entrée principal: parse la liste de tokens et retourne un QueryNode.
        """
        # Filtrer les articles et la ponctuation (les garder dans la liste mais les ignorer)
        self.tokens = tokens
        self.pos = 0

        # Créer le noeud racine
        self.query_node = QueryNode()

        # Analyser la requête
        self._parse_query()

        return self.query_node

    def _current(self) -> Optional[Token]:
        """Retourne le token courant sans avancer"""
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.type in ('ARTICLE', 'PUNCTUATION', 'UNKNOWN'):
                self.pos += 1
                continue
            return t
        return None

    def _peek(self, offset=1) -> Optional[Token]:
        """Regarde le token à pos + offset (en sautant articles/ponctuation)"""
        p = self.pos
        skipped = 0
        while p < len(self.tokens) and skipped <= offset:
            t = self.tokens[p]
            if t.type in ('ARTICLE', 'PUNCTUATION', 'UNKNOWN'):
                p += 1
                continue
            if skipped == offset:
                return t
            skipped += 1
            p += 1
        return None

    def _advance(self) -> Optional[Token]:
        """Retourne le token courant et avance (en sautant articles/ponctuation)"""
        token = self._current()
        if token:
            self.pos += 1
            # Avancer après les articles
            while self.pos < len(self.tokens) and self.tokens[self.pos].type in ('ARTICLE', 'PUNCTUATION', 'UNKNOWN'):
                self.pos += 1
        return token

    def _expect(self, token_type: str) -> Token:
        """Consomme un token du type attendu ou lève une erreur"""
        token = self._current()
        if not token:
            raise ParserError(
                f"Fin de requête inattendue. Token de type '{token_type}' attendu."
            )
        if token.type != token_type:
            raise ParserError(
                f"Token de type '{token_type}' attendu, "
                f"mais '{token.type}:{token.value}' trouvé à la position {token.position}."
            )
        self._advance()
        return token

    def _parse_query(self):
        """Parse la structure complète de la requête"""

        # 1. Détecter le type de requête via le keyword
        self._parse_keyword()

        # 2. Chercher un nombre (limit) avant l'entité
        self._parse_pre_limit()

        # 3. Identifier l'entité cible
        self._parse_entity()

        # 4. Chercher les filtres, modificateurs et compound filters
        self._parse_remainder()

    def _parse_keyword(self):
        """Parse le mot-clé de la requête pour déterminer le type"""
        token = self._current()
        if not token:
            raise ParserError("Requête vide ou sans mot-clé reconnu.")

        if token.type == 'KEYWORD':
            keyword = token.value
            self._advance()

            if keyword in ('combien', 'compte', 'compter'):
                self.query_node.query_type = 'COUNT'
                self.query_node.aggregate = AggregateNode(function='COUNT')
            elif keyword in ('affiche', 'afficher', 'montre', 'montrer',
                             'liste', 'lister', 'donne', 'donner',
                             'trouve', 'trouver', 'cherche', 'chercher'):
                self.query_node.query_type = 'SELECT'
            else:
                self.query_node.query_type = 'SELECT'
        elif token.type == 'ENTITY':
            # Pas de keyword, juste l'entité (ex: "capteurs hors service")
            self.query_node.query_type = 'SELECT'
        else:
            # Essayer de continuer quand même
            self.query_node.query_type = 'SELECT'

    def _parse_pre_limit(self):
        """Détecte un nombre avant l'entité (ex: 'les 5 zones')"""
        token = self._current()
        if token and token.type == 'NUMBER':
            self.query_node.limit = LimitNode(count=int(token.value))
            self._advance()

    def _parse_entity(self):
        """Parse l'entité (table) cible"""
        token = self._current()
        if token and token.type == 'ENTITY':
            entity_name = token.value
            self.query_node.entity = EntityNode(
                entity=entity_name,
                table_name=self._entity_to_table(entity_name)
            )
            self._advance()
        else:
            # Chercher plus loin dans les tokens
            for i in range(self.pos, len(self.tokens)):
                if self.tokens[i].type == 'ENTITY':
                    entity_name = self.tokens[i].value
                    self.query_node.entity = EntityNode(
                        entity=entity_name,
                        table_name=self._entity_to_table(entity_name)
                    )
                    break

            if not self.query_node.entity:
                raise ParserError(
                    "Aucune entité (table) identifiée dans la requête. "
                    "Entités reconnues: capteurs, interventions, citoyens, trajets, zones, mesures"
                )

    def _parse_remainder(self):
        """Parse le reste de la requête pour les filtres, ordres et limites"""
        while self.pos < len(self.tokens):
            token = self._current()
            if not token:
                break

            if token.type == 'FILTER':
                self._handle_filter(token)
                self._advance()

            elif token.type == 'COMPOUND_FILTER':
                self._handle_compound_filter(token)
                self._advance()

            elif token.type == 'DOMAIN_FIELD':
                self._handle_domain_field(token)
                self._advance()

            elif token.type == 'MODIFIER':
                self._handle_modifier(token)
                self._advance()

            elif token.type == 'OPERATOR':
                self._handle_operator(token)
                self._advance()

            elif token.type == 'NUMBER':
                # Nombre non encore consommé — peut être un limit
                if not self.query_node.limit:
                    self.query_node.limit = LimitNode(count=int(token.value))
                self._advance()

            elif token.type == 'ENTITY':
                # Entité secondaire — skip (déjà parsée)
                self._advance()

            elif token.type == 'KEYWORD':
                # Keyword secondaire — skip
                self._advance()

            else:
                self._advance()

    def _handle_filter(self, token):
        """Traite un token FILTER"""
        filter_value = token.value

        if filter_value == 'hors_service':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='HORS_SERVICE')
            )
        elif filter_value == 'en_cours':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='EN_COURS')
            )
        elif filter_value == 'en_maintenance':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='MAINTENANCE')
            )
        elif filter_value == 'actif':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='ACTIF')
            )
        elif filter_value == 'terminee':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='TERMINEE')
            )
        elif filter_value == 'planifiee':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='PLANIFIEE')
            )
        elif filter_value == 'annulee':
            self.query_node.filters.append(
                FilterNode(column='statut', operator='=', value='ANNULEE')
            )
        elif filter_value == 'polluees':
            # "polluées" implique un tri par pollution
            if not self.query_node.order:
                self.query_node.order = OrderNode(
                    column='indice_pollution', direction='DESC'
                )
        elif filter_value == 'ecologique':
            # "écologique" fait référence au score d'engagement
            pass  # Sera géré avec l'opérateur qui suit
        elif filter_value == 'economique':
            # "économique" fait référence au CO2
            if not self.query_node.order:
                self.query_node.order = OrderNode(
                    column='economie_co2', direction='DESC'
                )

    def _handle_compound_filter(self, token):
        """Traite les filtres composés (plus polluées, plus économique)"""
        if token.value == 'plus_polluees':
            self.query_node.order = OrderNode(
                column='indice_pollution', direction='DESC'
            )
            # Pour les zones polluées, on a besoin d'un JOIN et d'agrégation
            if (self.query_node.entity and
                    self.query_node.entity.entity == 'zones'):
                self.query_node.joins = ['mesure', 'capteur']
                self.query_node.aggregate = AggregateNode(
                    function='AVG', column='indice_pollution'
                )
                self.query_node.order = OrderNode(
                    column='pollution_moyenne', direction='DESC'
                )

        elif token.value == 'plus_economique':
            self.query_node.order = OrderNode(
                column='economie_co2', direction='DESC'
            )
            if not self.query_node.limit:
                self.query_node.limit = LimitNode(count=1)

    def _handle_domain_field(self, token):
        """Traite un champ du domaine (score_ecologique, co2, etc.)"""
        if token.value == 'score_ecologique':
            # Regarder s'il y a un opérateur et un nombre ensuite
            next_token = self._peek()
            if next_token and next_token.type == 'OPERATOR':
                pass  # Sera géré par _handle_operator
        elif token.value == 'co2':
            if not self.query_node.order:
                self.query_node.order = OrderNode(
                    column='economie_co2', direction='DESC'
                )

    def _handle_modifier(self, token):
        """Traite un modificateur (plus, moins, etc.)"""
        if token.value == 'plus':
            # "plus" suivi d'un filtre → déjà géré par compound_filter
            pass

    def _handle_operator(self, token):
        """Traite un opérateur de comparaison"""
        operator = token.value

        # Chercher le nombre qui suit
        next_pos = self.pos + 1
        while next_pos < len(self.tokens):
            if self.tokens[next_pos].type == 'NUMBER':
                number_value = self.tokens[next_pos].value
                break
            elif self.tokens[next_pos].type in ('ARTICLE', 'PUNCTUATION'):
                next_pos += 1
                continue
            else:
                return
        else:
            return

        # Déterminer la colonne en fonction du contexte
        # Chercher le dernier DOMAIN_FIELD ou FILTER avant l'opérateur
        column = 'score_engagement'  # Défaut pour les citoyens

        for i in range(self.pos - 1, -1, -1):
            t = self.tokens[i]
            if t.type == 'DOMAIN_FIELD':
                if t.value == 'score_ecologique':
                    column = 'score_engagement'
                elif t.value == 'indice_pollution':
                    column = 'indice_pollution'
                elif t.value == 'co2':
                    column = 'economie_co2'
                break

        self.query_node.filters.append(
            FilterNode(column=column, operator=operator, value=number_value)
        )

    def _entity_to_table(self, entity: str) -> str:
        """Mappe un nom d'entité vers le nom de table MySQL"""
        mapping = {
            'capteurs': 'capteur',
            'interventions': 'intervention',
            'citoyens': 'citoyen',
            'trajets': 'trajet',
            'zones': 'arrondissement',
            'mesures': 'mesure',
            'vehicules': 'vehicule',
            'techniciens': 'technicien',
        }
        return mapping.get(entity, entity)
