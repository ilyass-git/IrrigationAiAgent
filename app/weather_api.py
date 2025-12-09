"""
Module de récupération des données météorologiques en temps réel
"""
import requests
from typing import Dict, Optional
import time
import logging
from config import WEATHER_API_KEY, WEATHER_API_URL, LATITUDE, LONGITUDE, CITY_NAME

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Récupère les données météorologiques en temps réel"""
    
    def __init__(self):
        """Initialise l'API météo"""
        self.api_key = WEATHER_API_KEY
        self.api_url = WEATHER_API_URL
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        self.city_name = CITY_NAME
    
    def get_current_weather(self) -> Dict:
        """
        Récupère les conditions météorologiques actuelles
        
        Returns:
            Dictionnaire contenant les données météo formatées
        """
        start_time = time.time()
        logger.info("[WEATHER] Récupération des données météo...")
        
        try:
            # Essayer d'abord avec les coordonnées
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'fr'
            }
            
            logger.info(f"[WEATHER] Appel API OpenWeatherMap (timeout: 5s)...")
            response = requests.get(self.api_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Formatage des données
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'rainfall': data.get('rain', {}).get('1h', 0) if 'rain' in data else 0,
                'rainfall_3h': data.get('rain', {}).get('3h', 0) if 'rain' in data else 0,
                'description': data['weather'][0]['description'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'city': data.get('name', self.city_name),
                'timestamp': data.get('dt', None)
            }
            
            duration = time.time() - start_time
            logger.info(f"[WEATHER] ✓ Données météo récupérées en {duration:.2f}s - Temp: {weather_data['temperature']}°C")
            
            return weather_data
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            logger.warning(f"[WEATHER] ⚠ Timeout après {duration:.2f}s, utilisation de valeurs par défaut")
            return self._get_default_weather()
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            logger.warning(f"[WEATHER] ⚠ Erreur après {duration:.2f}s: {e}, utilisation de valeurs par défaut")
            return self._get_default_weather()
    
    def _get_default_weather(self) -> Dict:
        """
        Retourne des données météo par défaut en cas d'erreur API
        
        Returns:
            Dictionnaire avec des valeurs par défaut
        """
        return {
            'temperature': 20.0,
            'humidity': 50.0,
            'pressure': 1013.0,
            'rainfall': 0.0,
            'rainfall_3h': 0.0,
            'description': 'Données non disponibles',
            'wind_speed': 0.0,
            'clouds': 0,
            'city': self.city_name,
            'timestamp': None
        }
    
    def get_weather_summary_for_llm(self) -> str:
        """
        Génère un résumé textuel des conditions météo pour l'agent LLM
        
        Returns:
            Chaîne de caractères décrivant les conditions actuelles
        """
        weather = self.get_current_weather()
        
        summary = f"""
CONDITIONS MÉTÉOROLOGIQUES ACTUELLES
====================================

Localisation : {weather['city']}
Température actuelle : {weather['temperature']:.1f}°C
Humidité de l'air : {weather['humidity']:.1f}%
Pluviométrie (1h) : {weather['rainfall']:.1f}mm
Pluviométrie (3h) : {weather['rainfall_3h']:.1f}mm
Conditions : {weather['description']}
Vitesse du vent : {weather['wind_speed']:.1f} m/s
Couverture nuageuse : {weather['clouds']}%
"""
        
        return summary







