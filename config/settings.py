"""
Configuration du système d'irrigation intelligent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'openai' ou 'ollama'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Configuration Ollama (pas de timeout strict - priorité à la qualité)

# Configuration API Météo
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
LATITUDE = os.getenv("LATITUDE", "45.5017")
LONGITUDE = os.getenv("LONGITUDE", "-73.5673")
CITY_NAME = os.getenv("CITY_NAME", "Montreal")

# Configuration Système
AUTO_DECISION_INTERVAL_HOURS = int(os.getenv("AUTO_DECISION_INTERVAL_HOURS", "6"))
CSV_DATA_PATH = os.getenv("CSV_DATA_PATH", "data/historical_data.csv")
SENSOR_CSV_DATA_PATH = os.getenv("SENSOR_CSV_DATA_PATH", "data/sensor_data.csv")
REVIEWS_CSV_DATA_PATH = os.getenv("REVIEWS_CSV_DATA_PATH", "data/reviews.csv")

# Validation
if LLM_PROVIDER == 'openai' and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY doit être défini dans le fichier .env pour le provider 'openai'")
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY doit être défini dans le fichier .env")


