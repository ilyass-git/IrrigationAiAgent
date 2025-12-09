"""
Module de chargement et d'analyse des données historiques depuis un fichier CSV
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path


class HistoricalDataLoader:
    """Charge et analyse les données historiques d'irrigation"""
    
    def __init__(self, csv_path: str):
        """
        Initialise le chargeur de données
        
        Args:
            csv_path: Chemin vers le fichier CSV contenant les données historiques
        """
        self.csv_path = Path(csv_path)
        self.data: Optional[pd.DataFrame] = None
        self.load_data()
    
    def load_data(self) -> None:
        """Charge les données depuis le fichier CSV"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Le fichier CSV n'existe pas : {self.csv_path}")
        
        self.data = pd.read_csv(self.csv_path)
        
        # Vérification des colonnes requises
        required_columns = ['temperature', 'humidite_air', 'pluviometrie', 'irrigation']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans le CSV : {missing_columns}")
    
    def get_statistics(self) -> Dict:
        """
        Calcule des statistiques descriptives sur les données historiques
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        if self.data is None:
            return {}
        
        stats = {
            'total_records': len(self.data),
            'irrigation_rate': self.data['irrigation'].mean() if 'irrigation' in self.data.columns else 0,
            'avg_temperature': self.data['temperature'].mean(),
            'avg_humidity': self.data['humidite_air'].mean(),
            'avg_rainfall': self.data['pluviometrie'].mean(),
            'temperature_range': {
                'min': self.data['temperature'].min(),
                'max': self.data['temperature'].max()
            },
            'humidity_range': {
                'min': self.data['humidite_air'].min(),
                'max': self.data['humidite_air'].max()
            }
        }
        
        # Statistiques conditionnelles : irrigation vs non-irrigation
        if 'irrigation' in self.data.columns:
            irrigated = self.data[self.data['irrigation'] == 1]
            not_irrigated = self.data[self.data['irrigation'] == 0]
            
            if len(irrigated) > 0:
                stats['when_irrigated'] = {
                    'avg_temperature': irrigated['temperature'].mean(),
                    'avg_humidity': irrigated['humidite_air'].mean(),
                    'avg_rainfall': irrigated['pluviometrie'].mean()
                }
            
            if len(not_irrigated) > 0:
                stats['when_not_irrigated'] = {
                    'avg_temperature': not_irrigated['temperature'].mean(),
                    'avg_humidity': not_irrigated['humidite_air'].mean(),
                    'avg_rainfall': not_irrigated['pluviometrie'].mean()
                }
        
        return stats
    
    def get_recent_patterns(self, days: int = 30) -> Dict:
        """
        Analyse les patterns récents d'irrigation
        
        Args:
            days: Nombre de jours à analyser (si une colonne date existe)
        
        Returns:
            Dictionnaire contenant les patterns récents
        """
        if self.data is None:
            return {}
        
        # Si on a une colonne date, on peut filtrer
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            recent_data = self.data.tail(days)
        else:
            recent_data = self.data.tail(days)
        
        patterns = {
            'recent_irrigation_rate': recent_data['irrigation'].mean() if 'irrigation' in recent_data.columns else 0,
            'recent_avg_temperature': recent_data['temperature'].mean(),
            'recent_avg_humidity': recent_data['humidite_air'].mean(),
            'recent_avg_rainfall': recent_data['pluviometrie'].mean()
        }
        
        return patterns
    
    def get_similar_conditions(self, temperature: float, humidity: float, rainfall: float, 
                               tolerance: float = 2.0) -> pd.DataFrame:
        """
        Trouve les enregistrements historiques avec des conditions similaires
        
        Args:
            temperature: Température actuelle
            humidity: Humidité actuelle
            rainfall: Pluviométrie actuelle
            tolerance: Tolérance pour la similarité (en degrés/pourcentage)
        
        Returns:
            DataFrame contenant les enregistrements similaires
        """
        if self.data is None:
            return pd.DataFrame()
        
        similar = self.data[
            (abs(self.data['temperature'] - temperature) <= tolerance) &
            (abs(self.data['humidite_air'] - humidity) <= tolerance) &
            (abs(self.data['pluviometrie'] - rainfall) <= tolerance)
        ]
        
        return similar
    
    def get_summary_for_llm(self) -> str:
        """
        Génère un résumé textuel des données historiques pour l'agent LLM
        
        Returns:
            Chaîne de caractères décrivant les données historiques
        """
        stats = self.get_statistics()
        
        summary = f"""
ANALYSE DES DONNÉES HISTORIQUES D'IRRIGATION
===========================================

Nombre total d'enregistrements : {stats.get('total_records', 0)}
Taux d'irrigation moyen : {stats.get('irrigation_rate', 0):.1%}

Conditions moyennes générales :
- Température moyenne : {stats.get('avg_temperature', 0):.1f}°C
- Humidité moyenne : {stats.get('avg_humidity', 0):.1f}%
- Pluviométrie moyenne : {stats.get('avg_rainfall', 0):.1f}mm

Conditions moyennes LORS D'UNE IRRIGATION :
"""
        
        if 'when_irrigated' in stats:
            irrig = stats['when_irrigated']
            summary += f"- Température : {irrig.get('avg_temperature', 0):.1f}°C\n"
            summary += f"- Humidité : {irrig.get('avg_humidity', 0):.1f}%\n"
            summary += f"- Pluviométrie : {irrig.get('avg_rainfall', 0):.1f}mm\n"
        
        summary += "\nConditions moyennes LORS D'UNE NON-IRRIGATION :\n"
        if 'when_not_irrigated' in stats:
            not_irrig = stats['when_not_irrigated']
            summary += f"- Température : {not_irrig.get('avg_temperature', 0):.1f}°C\n"
            summary += f"- Humidité : {not_irrig.get('avg_humidity', 0):.1f}%\n"
            summary += f"- Pluviométrie : {not_irrig.get('avg_rainfall', 0):.1f}mm\n"
        
        return summary







