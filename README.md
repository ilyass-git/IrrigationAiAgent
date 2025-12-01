# 🌾 Système d'Irrigation Intelligent - Agent IA

Un système d'automatisation de l'irrigation basé sur un agent IA intelligent utilisant LangChain et un LLM pour la prise de décision autonome.

## 📋 Description

Ce projet combine l'analyse de données historiques d'irrigation et les données météorologiques en temps réel pour prendre automatiquement des décisions d'irrigation intelligentes. Le système utilise un agent LangChain avec un LLM (GPT) pour analyser les patterns historiques et les conditions actuelles, puis génère une décision justifiée.

## 🏗️ Architecture

### Structure du Projet

```
IrrigationAiAgent/
├── app/                    # Modules principaux de l'application
│   ├── __init__.py
│   ├── data_loader.py      # Chargement et analyse des données CSV
│   ├── weather_api.py      # Récupération des données météo
│   ├── agent.py            # Agent LangChain pour la décision
│   └── decision_engine.py   # Moteur de décision principal
├── web/                    # Interface web
│   ├── __init__.py
│   ├── app.py              # Application Flask
│   └── templates/
│       └── index.html      # Interface utilisateur
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py         # Paramètres système
├── data/                   # Données historiques
│   └── historical_data.csv # Fichier CSV avec données historiques
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances Python
└── README.md              # Documentation
```

### Composants Principaux

#### 1. **Data Loader** (`app/data_loader.py`)
- Charge les données historiques depuis un fichier CSV
- Calcule des statistiques descriptives
- Identifie les patterns d'irrigation passés
- Trouve des cas similaires dans l'historique

#### 2. **Weather API** (`app/weather_api.py`)
- Récupère les données météorologiques en temps réel via une API externe (OpenWeatherMap)
- Formate les données pour l'analyse
- Gère les erreurs avec des valeurs par défaut

#### 3. **Agent IA** (`app/agent.py`)
- Utilise LangChain avec OpenAI GPT pour la prise de décision
- Analyse les données historiques et météo
- Génère une décision (IRRIGUER / NE PAS IRRIGUER) avec justification

#### 4. **Decision Engine** (`app/decision_engine.py`)
- Orchestre l'ensemble du processus de décision
- Combine les données historiques, météo et l'agent IA
- Retourne une décision complète avec métadonnées

#### 5. **Interface Web** (`web/app.py` + `web/templates/index.html`)
- Interface Flask avec une UI moderne
- Affichage de la décision avec un switch visuel
- Bouton pour déclencher manuellement une décision
- Système de planification automatique (scheduler)

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Clé API OpenAI
- Clé API OpenWeatherMap (optionnelle, des valeurs par défaut sont utilisées en cas d'erreur)

### Étapes d'Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# Configuration OpenAI / LLM
OPENAI_API_KEY=your_openai_api_key_here

# Configuration API Météo (OpenWeatherMap)
WEATHER_API_KEY=your_weather_api_key_here
WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather

# Configuration Localisation
LATITUDE=45.5017
LONGITUDE=-73.5673
CITY_NAME=Montreal

# Configuration LangChain
LLM_MODEL=gpt-4o-mini
TEMPERATURE=0.3

# Configuration Système
AUTO_DECISION_INTERVAL_HOURS=6
CSV_DATA_PATH=data/historical_data.csv
```

**Note:** Pour obtenir une clé API OpenWeatherMap, inscrivez-vous sur [OpenWeatherMap](https://openweathermap.org/api)

4. **Vérifier le fichier CSV**

Assurez-vous que le fichier `data/historical_data.csv` existe et contient les colonnes suivantes :
- `date` : Date de l'enregistrement
- `temperature` : Température en degrés Celsius
- `humidite_air` : Humidité de l'air en pourcentage
- `pluviometrie` : Pluviométrie en millimètres
- `irrigation` : 1 si irrigation effectuée, 0 sinon
- `type_culture` : Type de culture (optionnel)

## 🎯 Utilisation

### Démarrage de l'Application

```bash
python main.py
```

L'interface web sera accessible sur : `http://localhost:5000`

### Fonctionnalités

#### 1. **Décision Manuelle**
- Cliquez sur le bouton "🔄 Lancer la Décision"
- Le système analyse les données et prend une décision
- La décision s'affiche avec une explication

#### 2. **Décision Automatique**
- Configurez l'intervalle (en heures) dans la section "Planification Automatique"
- Cliquez sur "Démarrer Auto"
- Le système prendra automatiquement des décisions à l'intervalle configuré

#### 3. **Interface Visuelle**
- **Switch ON/OFF** : Représente l'état de la pompe d'irrigation
- **Décision** : Affiche clairement "IRRIGUER" ou "NE PAS IRRIGUER"
- **Explication** : Justification de la décision en langage clair
- **Informations météo** : Température, humidité, pluviométrie actuelles

## 🔄 Flux de Décision

```
1. Chargement des données historiques (CSV)
   ↓
2. Analyse statistique des patterns passés
   ↓
3. Récupération des données météo en temps réel
   ↓
4. Identification de cas similaires dans l'historique
   ↓
5. Envoi des données à l'agent IA (LangChain + LLM)
   ↓
6. Analyse et prise de décision par l'agent
   ↓
7. Retour de la décision avec justification
   ↓
8. Affichage dans l'interface web
```

## 🧠 Logique de Décision de l'Agent IA

L'agent IA prend en compte :

1. **Patterns historiques** : Dans quelles conditions a-t-on irrigué dans le passé ?
2. **Conditions météorologiques actuelles** : Température, humidité, pluviométrie
3. **Probabilité de pluie** : Évite l'irrigation si la pluie est prévue
4. **Humidité de l'air** : Évite l'irrigation si l'humidité est très élevée (>80%)
5. **Cas similaires** : Compare avec des situations historiques similaires

## 📊 Format des Données CSV

Le fichier CSV doit contenir les colonnes suivantes :

| Colonne | Type | Description |
|---------|------|-------------|
| `date` | Date | Date de l'enregistrement (format: YYYY-MM-DD) |
| `temperature` | Float | Température en degrés Celsius |
| `humidite_air` | Float | Humidité de l'air en pourcentage (0-100) |
| `pluviometrie` | Float | Pluviométrie en millimètres |
| `irrigation` | Integer | 1 si irrigation effectuée, 0 sinon |
| `type_culture` | String | Type de culture (optionnel) |

## 🔧 Configuration Avancée

### Modifier le Modèle LLM

Dans le fichier `.env`, modifiez :
```env
LLM_MODEL=gpt-4o-mini  # ou gpt-4, gpt-3.5-turbo, etc.
TEMPERATURE=0.3        # 0.0 (déterministe) à 1.0 (créatif)
```

### Modifier la Localisation

Dans le fichier `.env`, modifiez :
```env
LATITUDE=45.5017
LONGITUDE=-73.5673
CITY_NAME=Montreal
```

### Modifier l'Intervalle Automatique

Dans le fichier `.env`, modifiez :
```env
AUTO_DECISION_INTERVAL_HOURS=6  # Intervalle en heures
```

## 🐛 Dépannage

### Erreur lors de l'installation : pandas ne peut pas être compilé (Python 3.13)

**Problème** : Si vous utilisez Python 3.13, pandas 2.1.4 n'est pas compatible. Les versions récentes de pandas (>=2.2.0) sont nécessaires.

**Solution** :
1. Le fichier `requirements.txt` a été mis à jour avec des versions compatibles
2. Réessayez l'installation : `pip install -r requirements.txt`
3. Si le problème persiste, installez les packages individuellement :
   ```bash
   pip install pandas>=2.2.0
   pip install langchain langchain-openai langchain-community
   pip install openai flask python-dotenv requests apscheduler
   ```
4. **Alternative** : Utilisez Python 3.11 ou 3.12 qui sont plus stables avec toutes les bibliothèques

### Erreur : "OPENAI_API_KEY doit être défini"
- Vérifiez que le fichier `.env` existe et contient votre clé API OpenAI
- Le fichier doit être à la racine du projet

### Erreur : "Le fichier CSV n'existe pas"
- Vérifiez que le fichier `data/historical_data.csv` existe
- Vérifiez le chemin dans la configuration `CSV_DATA_PATH`

### Les données météo ne se chargent pas
- Vérifiez votre clé API OpenWeatherMap
- Le système utilisera des valeurs par défaut en cas d'erreur

### Erreur : "ModuleNotFoundError: No module named 'langchain'"
- Assurez-vous d'avoir installé toutes les dépendances : `pip install -r requirements.txt`
- Vérifiez que vous utilisez le bon environnement Python

### Problèmes de compatibilité avec les versions récentes de LangChain
- Le code a été mis à jour pour être compatible avec LangChain >= 0.3.0
- Si vous rencontrez des erreurs d'import, mettez à jour LangChain : `pip install --upgrade langchain langchain-openai langchain-community`

## 📝 Notes Importantes

- Ce système est conçu pour un **projet académique** et simule une prise de décision
- Il ne contrôle **pas une pompe réelle**, mais simule le processus de décision
- Les décisions sont basées sur des données historiques et des conditions météo actuelles
- L'agent IA utilise un LLM pour générer des décisions justifiées

## 🎓 Utilisation Académique

Ce projet peut être utilisé comme base pour :
- Études sur l'IA appliquée à l'agriculture
- Automatisation des processus agricoles
- Analyse de données historiques avec IA
- Prise de décision autonome basée sur des données

## 📄 Licence

Ce projet est fourni à des fins éducatives et académiques.

## 👨‍💻 Auteur

Système d'irrigation intelligent développé pour un projet académique sur l'automatisation des processus agricoles par intelligence artificielle.

---

**🌾 Bonne irrigation intelligente ! 🌾**

