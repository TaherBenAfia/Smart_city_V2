"""
Service LLM pour le module Rapports IA
Abstraction pour la génération de rapports via OpenAI ou mode template (fallback).

- Si OPENAI_API_KEY est défini → utilise OpenAI gpt-3.5-turbo
- Sinon → utilise un générateur de rapports basé sur des templates
"""

import os
import json
from datetime import datetime


def _get_openai_client():
    """Tente de créer un client OpenAI. Retourne None si non disponible."""
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except (ImportError, Exception):
        return None


class LLMService:
    """
    Service de génération de texte par IA.
    Utilise OpenAI si disponible, sinon un mode template déterministe.
    """

    def __init__(self):
        self.client = _get_openai_client()
        self.mode = 'openai' if self.client else 'template'

    def generate_report(self, report_type, data_context):
        """
        Génère un rapport textuel basé sur les données fournies.

        Args:
            report_type: 'air_quality', 'interventions', 'capteurs'
            data_context: dict de données agrégées

        Returns:
            str: Texte du rapport généré
        """
        if self.mode == 'openai':
            return self._generate_with_openai(report_type, data_context)
        return self._generate_with_template(report_type, data_context)

    def generate_suggestion(self, capteur_data):
        """
        Génère une suggestion d'action pour un capteur.

        Args:
            capteur_data: dict avec les détails du capteur

        Returns:
            str: Recommandation d'action
        """
        if self.mode == 'openai':
            return self._suggest_with_openai(capteur_data)
        return self._suggest_with_template(capteur_data)

    # ================================================================
    # Mode OpenAI
    # ================================================================

    def _generate_with_openai(self, report_type, data_context):
        """Génère un rapport via OpenAI"""
        type_labels = {
            'air_quality': "qualité de l'air",
            'interventions': "interventions de maintenance",
            'capteurs': "état des capteurs IoT",
        }

        prompt = f"""Tu es un analyste de données pour la plateforme Smart City Neo-Sousse 2030.
Génère un rapport professionnel et détaillé en français sur {type_labels.get(report_type, report_type)}.

Données actuelles:
{json.dumps(data_context, indent=2, ensure_ascii=False, default=str)}

Le rapport doit:
- Commencer par un titre avec la date
- Résumer les indicateurs clés
- Identifier les points d'attention
- Proposer des recommandations concrètes
- Être formaté proprement avec des sections claires

Génère le rapport:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en gestion urbaine intelligente."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to template if OpenAI fails
            return self._generate_with_template(report_type, data_context)

    def _suggest_with_openai(self, capteur_data):
        """Génère une suggestion via OpenAI"""
        prompt = f"""Tu es un ingénieur de maintenance IoT pour Smart City Neo-Sousse 2030.
Analyse les données suivantes sur un capteur et propose une action:

{json.dumps(capteur_data, indent=2, ensure_ascii=False, default=str)}

Propose une recommandation d'action concrète et détaillée en français (2-3 paragraphes):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en maintenance prédictive IoT."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception:
            return self._suggest_with_template(capteur_data)

    # ================================================================
    # Mode Template (fallback déterministe)
    # ================================================================

    def _generate_with_template(self, report_type, data):
        """Génère un rapport basé sur des templates"""
        now = datetime.now().strftime('%d/%m/%Y à %H:%M')

        if report_type == 'air_quality':
            return self._template_air_quality(data, now)
        elif report_type == 'interventions':
            return self._template_interventions(data, now)
        elif report_type == 'capteurs':
            return self._template_capteurs(data, now)
        else:
            return f"Type de rapport '{report_type}' non reconnu."

    def _template_air_quality(self, data, now):
        """Template pour le rapport qualité de l'air"""
        zones_text = ""
        for z in data.get('zones_polluees', []):
            niveau = "CRITIQUE" if z['pollution'] > 150 else "ÉLEVÉ" if z['pollution'] > 100 else "MODÉRÉ"
            zones_text += f"  • {z['zone']}: indice {z['pollution']} ({niveau}) — {z['mesures']} mesures\n"

        qualite_text = ""
        for q in data.get('qualite_repartition', []):
            qualite_text += f"  • {q.get('qualite_air', 'N/A')}: {q.get('count', 0)} mesures\n"

        capteurs_hs = data.get('capteurs_air_hs', 0)
        total_capteurs = data.get('total_capteurs_air', 0)

        alertes = []
        for z in data.get('zones_polluees', []):
            if z['pollution'] > 150:
                alertes.append(f"⚠️ Zone {z['zone']} dépasse le seuil critique (indice {z['pollution']})")
        if capteurs_hs > 0:
            alertes.append(f"⚠️ {capteurs_hs} capteur(s) air hors service sur {total_capteurs}")

        alertes_text = "\n".join(alertes) if alertes else "  ✅ Aucune alerte critique"

        return f"""═══════════════════════════════════════════════════
📊 RAPPORT QUALITÉ DE L'AIR — Neo-Sousse 2030
   Généré le {now}
   Période: {data.get('periode', 'Dernières 24h')}
═══════════════════════════════════════════════════

📈 INDICATEURS CLÉS
  • Mesures collectées: {data.get('total_mesures', 0)}
  • Capteurs air actifs: {total_capteurs - capteurs_hs}/{total_capteurs}
  • Capteurs hors service: {capteurs_hs}

📊 RÉPARTITION PAR QUALITÉ
{qualite_text}
🗺️ ZONES LES PLUS POLLUÉES
{zones_text}
🚨 ALERTES
{alertes_text}

💡 RECOMMANDATIONS
  1. {"Intervention urgente requise dans les zones critiques." if any(z['pollution'] > 150 for z in data.get('zones_polluees', [])) else "Poursuivre la surveillance régulière."}
  2. {"Réparer les capteurs hors service pour améliorer la couverture." if capteurs_hs > 0 else "Tous les capteurs sont opérationnels."}
  3. Intensifier les mesures dans les zones à indice élevé.
  4. Communiquer les résultats aux citoyens via l'application mobile.

═══════════════════════════════════════════════════
   Rapport généré automatiquement par IA — Mode Template
═══════════════════════════════════════════════════"""

    def _template_interventions(self, data, now):
        """Template pour le rapport interventions"""
        nature_text = ""
        for n in data.get('par_nature', []):
            nature_text += f"  • {n['nature']}: {n['count']} interventions, -{n['co2_kg']} kg CO2, {n['cout_tnd']} TND\n"

        return f"""═══════════════════════════════════════════════════
🔧 RAPPORT MAINTENANCE — Neo-Sousse 2030
   Généré le {now}
═══════════════════════════════════════════════════

📈 INDICATEURS CLÉS
  • Interventions terminées: {data.get('terminees', 0)}
  • En cours: {data.get('en_cours', 0)}
  • Planifiées: {data.get('planifiees', 0)}
  • Réduction CO2 totale: {data.get('reduction_co2_kg', 0)} kg
  • Coût total: {data.get('cout_total_tnd', 0)} TND
  • Durée moyenne: {data.get('duree_moyenne_min', 0)} minutes

📊 PAR TYPE DE MAINTENANCE
{nature_text}
💡 RECOMMANDATIONS
  1. {"Prioriser les interventions planifiées en attente." if data.get('planifiees', 0) > 5 else "Planning d'interventions bien maîtrisé."}
  2. Favoriser la maintenance prédictive pour réduire les coûts.
  3. Optimiser la durée des interventions (objectif < 90 min).
  4. Renforcer la validation IA pour accélérer le processus.

═══════════════════════════════════════════════════
   Rapport généré automatiquement par IA — Mode Template
═══════════════════════════════════════════════════"""

    def _template_capteurs(self, data, now):
        """Template pour le rapport capteurs"""
        statut_text = ""
        for s in data.get('par_statut', []):
            emoji = "✅" if s['statut'] == 'ACTIF' else "🔧" if s['statut'] == 'MAINTENANCE' else "❌"
            statut_text += f"  {emoji} {s['statut']}: {s['count']}\n"

        type_text = ""
        for t in data.get('par_type', []):
            type_text += f"  • {t['type']}: {t['total']} total, {t['actifs']} actifs, {t['hors_service']} HS\n"

        return f"""═══════════════════════════════════════════════════
📡 RAPPORT ÉTAT DES CAPTEURS — Neo-Sousse 2030
   Généré le {now}
═══════════════════════════════════════════════════

📈 INDICATEURS CLÉS
  • Total capteurs: {data.get('total_capteurs', 0)}
  • Taux de disponibilité: {data.get('taux_disponibilite', 0)}%

📊 PAR STATUT
{statut_text}
📊 PAR TYPE
{type_text}
💡 RECOMMANDATIONS
  1. {"⚠️ Taux de disponibilité sous l'objectif de 95%. Actions correctives nécessaires." if data.get('taux_disponibilite', 0) < 95 else "✅ Taux de disponibilité satisfaisant."}
  2. Planifier la maintenance préventive des capteurs vieillissants.
  3. Renforcer le réseau dans les zones à faible couverture.

═══════════════════════════════════════════════════
   Rapport généré automatiquement par IA — Mode Template
═══════════════════════════════════════════════════"""

    def _suggest_with_template(self, data):
        """Template pour les suggestions de maintenance"""
        if not data:
            return "❌ Capteur non trouvé. Veuillez vérifier l'identifiant."

        capteur_id = data.get('capteur_id', 'N/A')
        statut = data.get('statut', 'INCONNU')
        taux_erreur = data.get('taux_erreur', 0)
        nb_interventions = data.get('nb_interventions', 0)
        capteur_type = data.get('type', 'N/A')
        arrondissement = data.get('arrondissement', 'N/A')

        # Déterminer la priorité
        if statut == 'HORS_SERVICE':
            priorite = "🔴 CRITIQUE"
            action = f"Intervention corrective immédiate requise sur le capteur {capteur_id}."
            detail = (
                f"Le capteur de type {capteur_type} situé dans l'arrondissement {arrondissement} "
                f"est actuellement hors service. Avec {nb_interventions} interventions passées "
                f"et un taux d'erreur de {taux_erreur}%, une réparation ou un remplacement "
                f"est fortement recommandé."
            )
        elif statut == 'MAINTENANCE' or taux_erreur > 50:
            priorite = "🟡 ÉLEVÉE"
            action = f"Maintenance préventive recommandée sur le capteur {capteur_id}."
            detail = (
                f"Le capteur présente un taux d'erreur de {taux_erreur}%. "
                f"Il est recommandé de procéder à un diagnostic complet et à une "
                f"recalibration. Vérifier les composants électroniques et les connexions."
            )
        elif taux_erreur > 20:
            priorite = "🟠 MODÉRÉE"
            action = f"Surveillance renforcée conseillée pour le capteur {capteur_id}."
            detail = (
                f"Le capteur fonctionne mais son taux d'erreur ({taux_erreur}%) "
                f"est en hausse. Planifier une inspection dans les 7 prochains jours."
            )
        else:
            priorite = "🟢 FAIBLE"
            action = f"Aucune action immédiate requise pour le capteur {capteur_id}."
            detail = (
                f"Le capteur {capteur_type} dans {arrondissement} fonctionne normalement "
                f"avec un taux d'erreur de {taux_erreur}%. Continuer la surveillance standard."
            )

        return f"""📋 RECOMMANDATION — Capteur {capteur_id}

Priorité: {priorite}
Action: {action}

{detail}

📊 Détails techniques:
  • Type: {capteur_type}
  • Statut: {statut}
  • Zone: {arrondissement}
  • Interventions passées: {nb_interventions}
  • Taux d'erreur estimé: {taux_erreur}%"""
