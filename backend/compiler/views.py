"""
API Views pour le module Compilateur NL → SQL
"""

from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .sql_generator import SQLGenerator, SQLGeneratorError


class CompilerQueryView(APIView):
    """
    POST /api/compiler/query/
    Compile une requête en langage naturel français → SQL et l'exécute.

    Body: {"query": "Affiche les 5 zones les plus polluées"}
    Response: {"query": "...", "tokens": [...], "ast": {...}, "sql": "...", "results": [...]}
    """

    # Exemples de requêtes supportées
    EXAMPLE_QUERIES = [
        "Affiche les 5 zones les plus polluées",
        "Combien de capteurs sont hors service ?",
        "Quels citoyens ont un score écologique > 80 ?",
        "Donne-moi le trajet le plus économique en CO2",
        "Quelles interventions sont en cours ?",
    ]

    def post(self, request):
        query_text = request.data.get('query', '').strip()

        if not query_text:
            return Response({
                'error': 'Le champ "query" est requis.',
                'examples': self.EXAMPLE_QUERIES,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Phase 1: Analyse lexicale
            lexer = Lexer()
            tokens = lexer.tokenize(query_text)

            # Phase 2: Analyse syntaxique
            parser = Parser()
            ast = parser.parse(tokens)

            # Phase 3: Génération SQL
            generator = SQLGenerator()
            sql = generator.generate(ast)

            # Phase 4: Exécution (lecture seule)
            results = self._execute_sql(sql)

            return Response({
                'query': query_text,
                'tokens': [t.to_dict() for t in tokens],
                'ast': ast.to_dict(),
                'sql': sql,
                'results': results,
                'results_count': len(results),
            })

        except LexerError as e:
            return Response({
                'error': f'Erreur lexicale: {e.message}',
                'phase': 'lexer',
                'position': e.position,
                'examples': self.EXAMPLE_QUERIES,
            }, status=status.HTTP_400_BAD_REQUEST)

        except ParserError as e:
            return Response({
                'error': f'Erreur syntaxique: {e.message}',
                'phase': 'parser',
                'examples': self.EXAMPLE_QUERIES,
            }, status=status.HTTP_400_BAD_REQUEST)

        except SQLGeneratorError as e:
            return Response({
                'error': f'Erreur de génération SQL: {e.message}',
                'phase': 'sql_generator',
                'examples': self.EXAMPLE_QUERIES,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': f'Erreur d\'exécution: {str(e)}',
                'phase': 'execution',
                'examples': self.EXAMPLE_QUERIES,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _execute_sql(self, sql: str) -> list:
        """
        Exécute la requête SQL en lecture seule et retourne les résultats.
        """
        # Sécurité: on ne permet que les SELECT
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT'):
            raise SQLGeneratorError("Seules les requêtes SELECT sont autorisées.")

        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            # Convertir en liste de dicts
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convertir les types non-sérialisables
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    elif isinstance(value, bytes):
                        value = value.decode('utf-8', errors='replace')
                    elif hasattr(value, '__float__'):
                        value = float(value)
                    row_dict[col] = value
                results.append(row_dict)

            return results

    def get(self, request):
        """GET: retourne les exemples de requêtes supportées"""
        return Response({
            'message': 'Compilateur NL → SQL - Smart City Neo-Sousse 2030',
            'usage': 'POST avec {"query": "votre requête en français"}',
            'examples': self.EXAMPLE_QUERIES,
            'supported_entities': [
                'capteurs', 'interventions', 'citoyens',
                'trajets', 'zones', 'mesures', 'vehicules'
            ],
        })
