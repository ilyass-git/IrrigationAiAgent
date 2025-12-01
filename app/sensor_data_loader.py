"""
Module de chargement et d'analyse des données de capteurs IoT
"""
import pandas as pd
from typing import Dict, Optional
from pathlib import Path
import datetime
import random


class SensorDataLoader:
    """Charge et analyse les données de capteurs IoT"""
    
    def __init__(self, csv_path: str):
        """
        Initialise le chargeur de données de capteurs
        
        Args:
            csv_path: Chemin vers le fichier CSV contenant les données de capteurs
        """
        self.csv_path = Path(csv_path)
        self.data: Optional[pd.DataFrame] = None
        self.load_data()
    
    def load_data(self) -> None:
        """Charge les données depuis le fichier CSV"""
        if not self.csv_path.exists():
            print(f"[WARNING] Le fichier CSV de capteurs n'existe pas : {self.csv_path}")
            print("[INFO] Le système fonctionnera sans données de capteurs")
            self.data = None
            return
        
        self.data = pd.read_csv(self.csv_path)
        
        # Vérification des colonnes requises
        required_columns = ['humidite_sol', 'temperature_sol', 'niveau_reservoir']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            print(f"[WARNING] Colonnes manquantes dans le CSV de capteurs : {missing_columns}")
    
    def get_current_sensor_data(self) -> Dict:
        """
        Récupère les données de capteurs les plus récentes (simulation d'un capteur en temps réel)
        
        Returns:
            Dictionnaire contenant les données de capteurs actuelles
        """
        if self.data is None or len(self.data) == 0:
            # Retourner des valeurs par défaut si pas de données
            return {
                'humidite_sol': 50.0,
                'temperature_sol': 20.0,
                'niveau_reservoir': 75.0,
                'evapotranspiration': 5.0,
                'profondeur_racines': 30.0,
                'ph_sol': 6.8,
                'conductivite_electrique': 1.0,
                'available': False
            }
        
        # Prendre la dernière ligne (données les plus récentes)
        latest = self.data.iloc[-1]
        
        return {
            'humidite_sol': float(latest.get('humidite_sol', 50.0)),
            'temperature_sol': float(latest.get('temperature_sol', 20.0)),
            'niveau_reservoir': float(latest.get('niveau_reservoir', 75.0)),
            'evapotranspiration': float(latest.get('evapotranspiration', 5.0)),
            'profondeur_racines': float(latest.get('profondeur_racines', 30.0)),
            'ph_sol': float(latest.get('ph_sol', 6.8)),
            'conductivite_electrique': float(latest.get('conductivite_electrique', 1.0)),
            'available': True
        }
    
    def get_sensor_statistics(self) -> Dict:
        """
        Calcule des statistiques sur les données de capteurs
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        if self.data is None or len(self.data) == 0:
            return {}
        
        stats = {
            'total_records': len(self.data),
            'avg_humidite_sol': self.data['humidite_sol'].mean() if 'humidite_sol' in self.data.columns else 0,
            'avg_temperature_sol': self.data['temperature_sol'].mean() if 'temperature_sol' in self.data.columns else 0,
            'avg_niveau_reservoir': self.data['niveau_reservoir'].mean() if 'niveau_reservoir' in self.data.columns else 0,
            'humidite_sol_range': {
                'min': self.data['humidite_sol'].min() if 'humidite_sol' in self.data.columns else 0,
                'max': self.data['humidite_sol'].max() if 'humidite_sol' in self.data.columns else 0
            },
            'temperature_sol_range': {
                'min': self.data['temperature_sol'].min() if 'temperature_sol' in self.data.columns else 0,
                'max': self.data['temperature_sol'].max() if 'temperature_sol' in self.data.columns else 0
            }
        }
        
        if 'evapotranspiration' in self.data.columns:
            stats['avg_evapotranspiration'] = self.data['evapotranspiration'].mean()
        
        return stats
    
    def get_summary_for_llm(self) -> str:
        """
        Génère un résumé textuel des données de capteurs pour l'agent LLM
        
        Returns:
            Chaîne de caractères décrivant les données de capteurs
        """
        current_data = self.get_current_sensor_data()
        
        if not current_data.get('available', False):
            return """
DONNÉES DE CAPTEURS
==================
⚠️ Aucune donnée de capteur disponible. Utilisation de valeurs par défaut.
"""
        
        summary = f"""
DONNÉES DE CAPTEURS IoT (TEMPS RÉEL)
====================================

📊 ÉTAT ACTUEL DES CAPTEURS :

Humidité du sol : {current_data['humidite_sol']:.1f}%
  → Seuil critique : < 30% = sol sec (irrigation nécessaire)
  → Seuil optimal : 40-60% = sol bien hydraté
  → Seuil élevé : > 70% = sol saturé (risque de pourriture)

Température du sol : {current_data['temperature_sol']:.1f}°C
  → Impact sur l'absorption d'eau et la croissance des racines

Niveau du réservoir : {current_data['niveau_reservoir']:.1f}%
  → < 20% = réservoir critique (irrigation impossible)
  → > 50% = réservoir suffisant

Évapotranspiration : {current_data['evapotranspiration']:.1f} mm/jour
  → Besoin en eau réel de la culture

Profondeur des racines : {current_data['profondeur_racines']:.1f} cm
  → Zone d'absorption d'eau

pH du sol : {current_data['ph_sol']:.1f}
  → Optimal : 6.0-7.5 pour la plupart des cultures

Conductivité électrique : {current_data['conductivite_electrique']:.1f} dS/m
  → Indicateur de salinité du sol
"""
        
        return summary
    
    def get_sensor_alerts(self) -> list:
        """
        Génère des alertes basées sur les données de capteurs
        
        Returns:
            Liste d'alertes (chaînes de caractères)
        """
        alerts = []
        current_data = self.get_current_sensor_data()
        
        if not current_data.get('available', False):
            return alerts
        
        # Alerte humidité du sol
        if current_data['humidite_sol'] < 25:
            alerts.append(f"⚠️ ALERTE CRITIQUE : Humidité du sol très faible ({current_data['humidite_sol']:.1f}%) - Irrigation urgente nécessaire")
        elif current_data['humidite_sol'] < 30:
            alerts.append(f"⚠️ ALERTE : Humidité du sol faible ({current_data['humidite_sol']:.1f}%) - Irrigation recommandée")
        elif current_data['humidite_sol'] > 75:
            alerts.append(f"⚠️ ALERTE : Sol saturé ({current_data['humidite_sol']:.1f}%) - Risque de pourriture des racines")
        
        # Alerte niveau réservoir
        if current_data['niveau_reservoir'] < 20:
            alerts.append(f"🚨 ALERTE CRITIQUE : Réservoir presque vide ({current_data['niveau_reservoir']:.1f}%) - Irrigation impossible")
        elif current_data['niveau_reservoir'] < 30:
            alerts.append(f"⚠️ ALERTE : Niveau du réservoir faible ({current_data['niveau_reservoir']:.1f}%)")
        
        # Alerte température du sol
        if current_data['temperature_sol'] < 5:
            alerts.append(f"⚠️ ALERTE : Température du sol très basse ({current_data['temperature_sol']:.1f}°C) - Croissance ralentie")
        elif current_data['temperature_sol'] > 35:
            alerts.append(f"⚠️ ALERTE : Température du sol élevée ({current_data['temperature_sol']:.1f}°C) - Stress hydrique possible")
        
        return alerts
    
    def generate_new_sensor_reading(self, current_weather: Dict, irrigation_decision: str = "NE PAS IRRIGUER") -> Dict:
        """
        Génère une nouvelle lecture de capteurs basée sur les conditions actuelles
        
        Args:
            current_weather: Données météorologiques actuelles
            irrigation_decision: "IRRIGUER" ou "NE PAS IRRIGUER"
        
        Returns:
            Dictionnaire contenant les nouvelles valeurs de capteurs
        """
        # Récupérer les dernières valeurs pour calculer l'évolution
        previous_data = self.get_current_sensor_data()
        
        # Température du sol : proche de la température de l'air mais avec inertie
        temp_air = current_weather.get('temperature', 20.0)
        temp_sol_prev = previous_data.get('temperature_sol', temp_air)
        # Le sol suit l'air avec un décalage (moyenne pondérée)
        temperature_sol = temp_sol_prev * 0.7 + temp_air * 0.3
        # Ajustement selon la saison (variation jour/nuit simulée)
        temperature_sol += random.uniform(-1.0, 1.0)
        
        # Évapotranspiration : dépend de la température et de l'humidité de l'air
        humidity_air = current_weather.get('humidity', 50.0)
        # Formule simplifiée : ET augmente avec la température et diminue avec l'humidité
        evapotranspiration = max(0.5, (temp_air / 10.0) * (1 - humidity_air / 100.0) * 2.0)
        evapotranspiration += random.uniform(-0.5, 0.5)
        
        # Humidité du sol : évolution basée sur plusieurs facteurs
        humidite_sol_prev = previous_data.get('humidite_sol', 50.0)
        rainfall = current_weather.get('rainfall', 0.0) + current_weather.get('rainfall_3h', 0.0) / 3.0
        
        # Calcul de l'évolution de l'humidité
        # 1. Diminution due à l'évapotranspiration (environ 2-5% par jour selon ET)
        loss_et = evapotranspiration * 0.5  # Perte en % par mm d'ET
        
        # 2. Augmentation due à la pluie (environ 1% par mm de pluie)
        gain_rain = rainfall * 1.0
        
        # 3. Augmentation due à l'irrigation (si décision d'irriguer)
        gain_irrigation = 0.0
        if irrigation_decision == "IRRIGUER":
            # Irrigation ajoute environ 15-25% d'humidité
            gain_irrigation = random.uniform(15.0, 25.0)
        
        # Calcul de la nouvelle humidité
        humidite_sol = humidite_sol_prev - loss_et + gain_rain + gain_irrigation
        
        # Limiter entre 0 et 100%
        humidite_sol = max(0.0, min(100.0, humidite_sol))
        
        # Ajouter une petite variation aléatoire pour réalisme
        humidite_sol += random.uniform(-2.0, 2.0)
        humidite_sol = max(0.0, min(100.0, humidite_sol))
        
        # Niveau du réservoir : diminue si irrigation, augmente avec la pluie
        niveau_reservoir_prev = previous_data.get('niveau_reservoir', 75.0)
        if irrigation_decision == "IRRIGUER":
            # Irrigation consomme environ 5-10% du réservoir
            niveau_reservoir = niveau_reservoir_prev - random.uniform(5.0, 10.0)
        else:
            # Recharge naturelle avec la pluie (environ 0.5% par mm de pluie)
            niveau_reservoir = niveau_reservoir_prev + (rainfall * 0.5)
        
        # Limiter entre 0 et 100%
        niveau_reservoir = max(0.0, min(100.0, niveau_reservoir))
        
        # Profondeur des racines : augmente progressivement (simulation de croissance)
        profondeur_racines_prev = previous_data.get('profondeur_racines', 30.0)
        # Croissance très lente (0.1-0.3 cm par jour en moyenne)
        profondeur_racines = profondeur_racines_prev + random.uniform(0.0, 0.3)
        # Limiter entre 10 et 60 cm
        profondeur_racines = max(10.0, min(60.0, profondeur_racines))
        
        # pH du sol : reste relativement stable (légère variation)
        ph_sol_prev = previous_data.get('ph_sol', 6.8)
        ph_sol = ph_sol_prev + random.uniform(-0.05, 0.05)
        ph_sol = max(5.5, min(8.0, ph_sol))
        
        # Conductivité électrique : varie légèrement
        ce_prev = previous_data.get('conductivite_electrique', 1.0)
        conductivite_electrique = ce_prev + random.uniform(-0.05, 0.05)
        conductivite_electrique = max(0.1, min(3.0, conductivite_electrique))
        
        return {
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'humidite_sol': round(humidite_sol, 1),
            'temperature_sol': round(temperature_sol, 1),
            'niveau_reservoir': round(niveau_reservoir, 1),
            'evapotranspiration': round(evapotranspiration, 1),
            'profondeur_racines': round(profondeur_racines, 1),
            'ph_sol': round(ph_sol, 1),
            'conductivite_electrique': round(conductivite_electrique, 1)
        }
    
    def add_sensor_reading(self, sensor_reading: Dict) -> None:
        """
        Ajoute une nouvelle lecture de capteurs au fichier CSV
        
        Args:
            sensor_reading: Dictionnaire contenant les valeurs de capteurs
        """
        try:
            # Créer le DataFrame si le fichier n'existe pas
            if self.data is None or len(self.data) == 0:
                # Créer un DataFrame vide avec les colonnes nécessaires
                columns = ['date', 'humidite_sol', 'temperature_sol', 'niveau_reservoir', 
                          'evapotranspiration', 'profondeur_racines', 'ph_sol', 'conductivite_electrique']
                self.data = pd.DataFrame(columns=columns)
            
            # Créer un nouveau DataFrame avec la nouvelle ligne
            new_row = pd.DataFrame([sensor_reading])
            
            # Ajouter la nouvelle ligne
            self.data = pd.concat([self.data, new_row], ignore_index=True)
            
            # Sauvegarder dans le fichier CSV
            self.data.to_csv(self.csv_path, index=False)
            
            print(f"[INFO] Nouvelle lecture de capteurs ajoutée : {sensor_reading['date']}")
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'ajout de la lecture de capteurs : {e}")
            # Ne pas lever l'exception pour ne pas bloquer le processus de décision

