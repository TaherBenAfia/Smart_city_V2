"""
Nœuds AST pour le compilateur NL → SQL
Représentent la structure syntaxique d'une requête analysée
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ASTNode:
    """Noeud de base de l'arbre syntaxique abstrait"""
    node_type: str = "base"

    def to_dict(self):
        """Sérialise le noeud en dictionnaire"""
        return {"type": self.node_type}


@dataclass
class EntityNode(ASTNode):
    """Représente une entité (table) cible"""
    node_type: str = "entity"
    entity: str = ""           # ex: "capteurs", "interventions"
    table_name: str = ""       # ex: "capteur", "intervention"

    def to_dict(self):
        return {
            "type": self.node_type,
            "entity": self.entity,
            "table_name": self.table_name,
        }


@dataclass
class FilterNode(ASTNode):
    """Représente une condition WHERE"""
    node_type: str = "filter"
    column: str = ""
    operator: str = "="
    value: str = ""

    def to_dict(self):
        return {
            "type": self.node_type,
            "column": self.column,
            "operator": self.operator,
            "value": self.value,
        }


@dataclass
class AggregateNode(ASTNode):
    """Représente une fonction d'agrégation (COUNT, AVG, SUM)"""
    node_type: str = "aggregate"
    function: str = ""          # COUNT, AVG, SUM
    column: str = "*"

    def to_dict(self):
        return {
            "type": self.node_type,
            "function": self.function,
            "column": self.column,
        }


@dataclass
class OrderNode(ASTNode):
    """Représente un ORDER BY"""
    node_type: str = "order"
    column: str = ""
    direction: str = "DESC"

    def to_dict(self):
        return {
            "type": self.node_type,
            "column": self.column,
            "direction": self.direction,
        }


@dataclass
class LimitNode(ASTNode):
    """Représente un LIMIT"""
    node_type: str = "limit"
    count: int = 10

    def to_dict(self):
        return {
            "type": self.node_type,
            "count": self.count,
        }


@dataclass
class QueryNode(ASTNode):
    """
    Noeud racine de la requête.
    Contient l'entité, les filtres, agrégations, tri et limite.
    """
    node_type: str = "query"
    query_type: str = "SELECT"   # SELECT, COUNT, etc.
    entity: Optional[EntityNode] = None
    filters: List[FilterNode] = field(default_factory=list)
    aggregate: Optional[AggregateNode] = None
    order: Optional[OrderNode] = None
    limit: Optional[LimitNode] = None
    select_columns: List[str] = field(default_factory=list)
    joins: List[str] = field(default_factory=list)

    def to_dict(self):
        result = {
            "type": self.node_type,
            "query_type": self.query_type,
            "entity": self.entity.to_dict() if self.entity else None,
            "filters": [f.to_dict() for f in self.filters],
            "select_columns": self.select_columns,
        }
        if self.aggregate:
            result["aggregate"] = self.aggregate.to_dict()
        if self.order:
            result["order"] = self.order.to_dict()
        if self.limit:
            result["limit"] = self.limit.to_dict()
        if self.joins:
            result["joins"] = self.joins
        return result
