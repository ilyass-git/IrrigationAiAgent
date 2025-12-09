"""
Moteur de décision principal qui orchestre l'ensemble du processus
"""
from typing import Dict
from app.sensor_data_loader import SensorDataLoader
from app.review_manager import ReviewManager
from app.weather_api import WeatherAPI
from app.agent import IrrigationAgent
from config import SENSOR_CSV_DATA_PATH, REVIEWS_CSV_DATA_PATH
import uuid
import datetime
import time
import logging

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Moteur principal de prise de décision d'irrigation"""
    
    def __init__(self):
        """Initialise le moteur de décision avec tous ses composants"""
        self.sensor_loader = SensorDataLoader(SENSOR_CSV_DATA_PATH)
        self.weather_api = WeatherAPI()
        self.review_manager = ReviewManager(REVIEWS_CSV_DATA_PATH)
        self.agent = IrrigationAgent()
    
    def make_irrigation_decision(self) -> Dict:
        """
        Prend une décision d'irrigation complète
        
        Returns:
            Dictionnaire contenant :
            - decision: "IRRIGUER" ou "NE PAS IRRIGUER"
            - explication: Explication de la décision
            - metadata: Informations supplémentaires (météo, stats, etc.)
        """
        total_start = time.time()
        logger.info("[DECISION_ENGINE] ===== Début de la prise de décision =====")
        
        # 1. Récupérer les données météo actuelles
        logger.info("[DECISION_ENGINE] Étape 1/4: Récupération des données météo...")
        step_start = time.time()
        current_weather = self.weather_api.get_current_weather()
        weather_summary = self.weather_api.get_weather_summary_for_llm()
        step_duration = time.time() - step_start
        logger.info(f"[DECISION_ENGINE] ✓ Données météo récupérées en {step_duration:.2f}s")
        
        # 2. Récupérer les données de capteurs IoT
        logger.info("[DECISION_ENGINE] Étape 2/4: Récupération des données de capteurs...")
        step_start = time.time()
        current_sensor_data = self.sensor_loader.get_current_sensor_data()
        sensor_summary = self.sensor_loader.get_summary_for_llm()
        sensor_alerts = self.sensor_loader.get_sensor_alerts()
        step_duration = time.time() - step_start
        logger.info(f"[DECISION_ENGINE] ✓ Données capteurs récupérées en {step_duration:.2f}s")
        logger.info(f"[DECISION_ENGINE]   - Humidité sol: {current_sensor_data.get('humidite_sol', 'N/A')}%")
        logger.info(f"[DECISION_ENGINE]   - Niveau réservoir: {current_sensor_data.get('niveau_reservoir', 'N/A')}%")
        logger.info(f"[DECISION_ENGINE]   - Alertes: {len(sensor_alerts)}")
        
        # 3. Récupérer le résumé des revues d'expert
        logger.info("[DECISION_ENGINE] Étape 3/4: Récupération des reviews...")
        step_start = time.time()
        reviews_summary = self.review_manager.get_summary_for_llm()
        recent_reviews = self.review_manager.get_recent_reviews(limit=10)
        step_duration = time.time() - step_start
        logger.info(f"[DECISION_ENGINE] ✓ Reviews récupérés en {step_duration:.2f}s")
        
        # 4. Demander à l'agent IA de prendre une décision
        logger.info("[DECISION_ENGINE] Étape 4/4: Appel à l'agent IA...")
        step_start = time.time()
        decision_result = self.agent.make_decision(
            weather_summary=weather_summary,
            sensor_summary=sensor_summary,
            sensor_alerts=sensor_alerts,
            reviews_summary=reviews_summary
        )
        step_duration = time.time() - step_start
        logger.info(f"[DECISION_ENGINE] ✓ Décision IA obtenue en {step_duration:.2f}s")
        logger.info(f"[DECISION_ENGINE]   - Décision: {decision_result.get('decision', 'N/A')}")
        logger.info(f"[DECISION_ENGINE]   - Durée proposée: {decision_result.get('duree_minutes', 0)} min")
        
        decision_id = str(uuid.uuid4())
        duration_minutes = int(decision_result.get('duree_minutes', 0) or 0)
        if duration_minutes < 0:
            duration_minutes = 0
        if decision_result['decision'] == 'NE PAS IRRIGUER':
            duration_minutes = 0
            logger.info(f"[DECISION_ENGINE] Durée mise à 0 car décision = NE PAS IRRIGUER")
        
        logger.info(f"[DECISION_ENGINE] Durée finale validée: {duration_minutes} min")

        # 5. Générer et ajouter une nouvelle lecture de capteurs
        logger.info("[DECISION_ENGINE] Génération nouvelle lecture de capteurs...")
        step_start = time.time()
        new_sensor_reading = self.sensor_loader.generate_new_sensor_reading(
            current_weather=current_weather,
            irrigation_decision=decision_result['decision'],
            irrigation_duration_minutes=duration_minutes
        )
        self.sensor_loader.add_sensor_reading(new_sensor_reading)
        step_duration = time.time() - step_start
        logger.info(f"[DECISION_ENGINE] ✓ Nouvelle lecture générée en {step_duration:.2f}s")
        
        # 6. Récupérer les données de capteurs mises à jour
        updated_sensor_data = self.sensor_loader.get_current_sensor_data()
        
        # 7. Construire la réponse complète
        result = {
            'id': decision_id,
            'decision': decision_result['decision'],
            'duration_minutes': duration_minutes,
            'explication': decision_result['explication'],
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': {
                'weather': current_weather,
                'sensors': updated_sensor_data,
                'sensor_alerts': self.sensor_loader.get_sensor_alerts(),
                'reviews': {
                    'recent': recent_reviews,
                    'summary_text': reviews_summary
                },
                'duration_minutes': duration_minutes
            }
        }
        
        total_duration = time.time() - total_start
        logger.info(f"[DECISION_ENGINE] ===== Décision complète terminée en {total_duration:.2f}s =====")
        logger.info(f"[DECISION_ENGINE] Résultat final: decision={result['decision']}, duration={result['duration_minutes']} min")
        
        return result
    
    def get_system_status(self) -> Dict:
        """
        Retourne le statut actuel du système
        
        Returns:
            Dictionnaire contenant les informations de statut
        """
        try:
            weather = self.weather_api.get_current_weather()
            sensor_data = self.sensor_loader.get_current_sensor_data()
            sensor_stats = self.sensor_loader.get_sensor_statistics()
            review_stats = self.review_manager.get_statistics()
            recent_reviews = self.review_manager.get_recent_reviews(limit=5)
            
            return {
                'status': 'operational',
                'weather_available': weather['description'] != 'Données non disponibles',
                'sensor_data_available': sensor_data.get('available', False),
                'current_weather': weather,
                'current_sensors': sensor_data,
                'sensor_summary': sensor_stats,
                'review_summary': review_stats,
                'recent_reviews': recent_reviews
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def add_review(self, review_data: Dict) -> Dict:
        """
        Ajoute une revue d'expert liée à une décision.
        """
        return self.review_manager.add_review(**review_data)

    def get_recent_reviews(self, limit: int = 5) -> Dict:
        """
        Retourne les revues récentes et statistiques associées.
        """
        return {
            'statistics': self.review_manager.get_statistics(),
            'reviews': self.review_manager.get_recent_reviews(limit=limit),
            'summary_text': self.review_manager.get_summary_for_llm(limit=limit)
        }


