"""
Moteur de décision principal qui orchestre l'ensemble du processus
"""
from typing import Dict
from app.data_loader import HistoricalDataLoader
from app.weather_api import WeatherAPI
from app.agent import IrrigationAgent
from config import CSV_DATA_PATH
import datetime


class DecisionEngine:
    """Moteur principal de prise de décision d'irrigation"""
    
    def __init__(self):
        """Initialise le moteur de décision avec tous ses composants"""
        self.data_loader = HistoricalDataLoader(CSV_DATA_PATH)
        self.weather_api = WeatherAPI()
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
        # 1. Charger et analyser les données historiques
        historical_summary = self.data_loader.get_summary_for_llm()
        stats = self.data_loader.get_statistics()
        
        # 2. Récupérer les données météo actuelles
        current_weather = self.weather_api.get_current_weather()
        weather_summary = self.weather_api.get_weather_summary_for_llm()
        
        # 3. Trouver des cas similaires dans l'historique
        similar_cases = self.data_loader.get_similar_conditions(
            temperature=current_weather['temperature'],
            humidity=current_weather['humidity'],
            rainfall=current_weather['rainfall']
        )
        
        similar_cases_summary = ""
        if len(similar_cases) > 0:
            irrigation_rate_similar = similar_cases['irrigation'].mean() if 'irrigation' in similar_cases.columns else 0
            similar_cases_summary = f"""
Dans l'historique, {len(similar_cases)} cas présentent des conditions similaires (température: {current_weather['temperature']:.1f}°C, humidité: {current_weather['humidity']:.1f}%, pluie: {current_weather['rainfall']:.1f}mm).
Dans ces cas similaires, le taux d'irrigation était de {irrigation_rate_similar:.1%}.
"""
        
        # 4. Demander à l'agent IA de prendre une décision
        decision_result = self.agent.make_decision(
            historical_summary=historical_summary,
            weather_summary=weather_summary,
            similar_cases=similar_cases_summary
        )
        
        # 5. Construire la réponse complète
        result = {
            'decision': decision_result['decision'],
            'explication': decision_result['explication'],
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': {
                'weather': current_weather,
                'historical_stats': {
                    'total_records': stats.get('total_records', 0),
                    'irrigation_rate': stats.get('irrigation_rate', 0),
                    'similar_cases_found': len(similar_cases)
                }
            }
        }
        
        return result
    
    def get_system_status(self) -> Dict:
        """
        Retourne le statut actuel du système
        
        Returns:
            Dictionnaire contenant les informations de statut
        """
        try:
            weather = self.weather_api.get_current_weather()
            stats = self.data_loader.get_statistics()
            
            return {
                'status': 'operational',
                'weather_available': weather['description'] != 'Données non disponibles',
                'historical_data_loaded': stats.get('total_records', 0) > 0,
                'current_weather': weather,
                'historical_summary': {
                    'total_records': stats.get('total_records', 0),
                    'irrigation_rate': stats.get('irrigation_rate', 0)
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

