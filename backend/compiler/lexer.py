"""
Lexer (Analyseur Lexical) pour le compilateur NL → SQL
Tokenise des requêtes en langage naturel (français) en une séquence de tokens.

Exemple:
  "Affiche les 5 zones les plus polluées"
  → [KEYWORD:affiche, ARTICLE:les, NUMBER:5, ENTITY:zones, ARTICLE:les, MODIFIER:plus, FILTER:polluées]
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    """Représente un token lexical"""
    type: str       # KEYWORD, ENTITY, FILTER, OPERATOR, NUMBER, MODIFIER, ARTICLE, PUNCTUATION, UNKNOWN
    value: str      # Valeur originale normalisée
    position: int   # Position dans la chaîne d'entrée

    def to_dict(self):
        return {"type": self.type, "value": self.value, "position": self.position}


# ============================================================================
# Dictionnaires de tokens
# ============================================================================

# Mots-clés de requête (déclencheurs)
KEYWORDS = {
    'affiche', 'afficher', 'montre', 'montrer',
    'combien', 'compte', 'compter',
    'quels', 'quelles', 'quel', 'quelle',
    'liste', 'lister',
    'donne', 'donner',
    'trouve', 'trouver',
    'cherche', 'chercher',
}

# Entités du domaine (tables)
ENTITIES = {
    'capteurs': 'capteurs',
    'capteur': 'capteurs',
    'interventions': 'interventions',
    'intervention': 'interventions',
    'citoyens': 'citoyens',
    'citoyen': 'citoyens',
    'trajets': 'trajets',
    'trajet': 'trajets',
    'zones': 'zones',
    'zone': 'zones',
    'mesures': 'mesures',
    'mesure': 'mesures',
    'arrondissements': 'zones',
    'arrondissement': 'zones',
    'vehicules': 'vehicules',
    'vehicule': 'vehicules',
    'techniciens': 'techniciens',
    'technicien': 'techniciens',
}

# Filtres / états
FILTERS = {
    'actif': 'actif',
    'actifs': 'actif',
    'active': 'actif',
    'actives': 'actif',
    'inactif': 'inactif',
    'inactifs': 'inactif',
    'maintenance': 'maintenance',
    'planifiée': 'planifiee',
    'planifiees': 'planifiee',
    'terminée': 'terminee',
    'terminées': 'terminee',
    'terminees': 'terminee',
    'annulée': 'annulee',
    'annulées': 'annulee',
    'annulees': 'annulee',
    'polluées': 'polluees',
    'polluees': 'polluees',
    'pollué': 'polluees',
    'polluée': 'polluees',
    'écologique': 'ecologique',
    'ecologique': 'ecologique',
    'économique': 'economique',
    'economique': 'economique',
}

# Modificateurs
MODIFIERS = {
    'plus': 'plus',
    'moins': 'moins',
    'meilleur': 'meilleur',
    'meilleurs': 'meilleur',
    'pire': 'pire',
    'pires': 'pire',
    'dernier': 'dernier',
    'derniers': 'dernier',
    'dernière': 'dernier',
    'dernières': 'dernier',
    'premier': 'premier',
    'premiers': 'premier',
}

# Articles et mots de liaison (ignorés dans l'analyse sémantique mais tokenisés)
ARTICLES = {
    'le', 'la', 'les', 'un', 'une', 'des',
    'de', 'du', 'des', 'au', 'aux',
    'en', 'dans', 'par', 'pour', 'sur', 'avec',
    'et', 'ou', 'qui', 'que', 'dont',
    'sont', 'est', 'ont', 'a',
    'moi',
}

# Opérateurs de comparaison
OPERATORS = {'>', '<', '>=', '<=', '=', '!='}

# Tokens multi-mots (doivent être détectés en premier)
MULTI_WORD_TOKENS = {
    'hors service': ('FILTER', 'hors_service'),
    'en cours': ('FILTER', 'en_cours'),
    'en maintenance': ('FILTER', 'en_maintenance'),
    'donne-moi': ('KEYWORD', 'donne'),
    'donne moi': ('KEYWORD', 'donne'),
    'donnez-moi': ('KEYWORD', 'donne'),
    'donnez moi': ('KEYWORD', 'donne'),
    'score écologique': ('DOMAIN_FIELD', 'score_ecologique'),
    'score ecologique': ('DOMAIN_FIELD', 'score_ecologique'),
    'score engagement': ('DOMAIN_FIELD', 'score_ecologique'),
    'qualité air': ('DOMAIN_FIELD', 'qualite_air'),
    'qualite air': ('DOMAIN_FIELD', 'qualite_air'),
    'indice pollution': ('DOMAIN_FIELD', 'indice_pollution'),
    'plus polluées': ('COMPOUND_FILTER', 'plus_polluees'),
    'plus polluees': ('COMPOUND_FILTER', 'plus_polluees'),
    'plus économique': ('COMPOUND_FILTER', 'plus_economique'),
    'plus economique': ('COMPOUND_FILTER', 'plus_economique'),
}

# Mots liés au CO2
CO2_WORDS = {'co2', 'carbone', 'émissions', 'emissions'}


class LexerError(Exception):
    """Erreur d'analyse lexicale"""

    def __init__(self, message, position=0, token_value=""):
        self.message = message
        self.position = position
        self.token_value = token_value
        super().__init__(message)


class Lexer:
    """
    Analyseur lexical pour les requêtes en langage naturel français.
    Transforme une chaîne de caractères en séquence de tokens.
    """

    def __init__(self):
        self.tokens: List[Token] = []
        self.input_text: str = ""
        self.position: int = 0

    def tokenize(self, text: str) -> List[Token]:
        """
        Analyse lexicale complète d'une requête.
        Retourne la liste des tokens.
        """
        self.tokens = []
        self.input_text = text.strip()
        self.position = 0

        if not self.input_text:
            raise LexerError("Requête vide", 0)

        # Normaliser: minuscules pour l'analyse
        normalized = self.input_text.lower()

        # Phase 1: Détecter les tokens multi-mots
        remaining = normalized
        pos = 0
        segments = []

        # Trier les multi-mots par longueur décroissante pour matcher les plus longs d'abord
        sorted_multi = sorted(MULTI_WORD_TOKENS.keys(), key=len, reverse=True)

        while remaining:
            matched = False
            for multi_word in sorted_multi:
                if remaining.startswith(multi_word):
                    token_type, token_value = MULTI_WORD_TOKENS[multi_word]
                    segments.append(Token(token_type, token_value, pos))
                    advance = len(multi_word)
                    remaining = remaining[advance:].lstrip()
                    pos += advance
                    matched = True
                    break

            if not matched:
                # Extraire le prochain mot ou symbole
                match = re.match(r'(\d+(?:\.\d+)?|[><=!]+|[?!.,;]|\w+[\'-]?\w*)', remaining)
                if match:
                    word = match.group(1)
                    token = self._classify_word(word, pos)
                    segments.append(token)
                    advance = match.end()
                    remaining = remaining[advance:].lstrip()
                    pos += advance
                else:
                    # Skip whitespace or unknown char
                    remaining = remaining[1:]
                    pos += 1

        self.tokens = segments
        return self.tokens

    def _classify_word(self, word: str, position: int) -> Token:
        """Classifie un mot unique en token"""

        # Ponctuation
        if word in '?!.,;':
            return Token('PUNCTUATION', word, position)

        # Opérateurs
        if word in OPERATORS:
            return Token('OPERATOR', word, position)

        # Nombres
        if re.match(r'^\d+(\.\d+)?$', word):
            return Token('NUMBER', word, position)

        # CO2
        if word in CO2_WORDS:
            return Token('DOMAIN_FIELD', 'co2', position)

        # Mots-clés
        if word in KEYWORDS:
            return Token('KEYWORD', word, position)

        # Entités
        if word in ENTITIES:
            return Token('ENTITY', ENTITIES[word], position)

        # Filtres
        if word in FILTERS:
            return Token('FILTER', FILTERS[word], position)

        # Modificateurs
        if word in MODIFIERS:
            return Token('MODIFIER', word, position)

        # Articles et mots de liaison
        if word in ARTICLES:
            return Token('ARTICLE', word, position)

        # Token inconnu (pas une erreur — on le signale mais on continue)
        return Token('UNKNOWN', word, position)

    def get_tokens_summary(self) -> str:
        """Retourne un résumé lisible des tokens"""
        return " | ".join(f"{t.type}:{t.value}" for t in self.tokens)
