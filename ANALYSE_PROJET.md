# 📊 Analyse Complète du Projet - Système d'Irrigation Intelligent

## 🎯 À QUOI SERT CE PROJET ?

Ce projet est un **système d'automatisation de l'irrigation agricole** basé sur l'intelligence artificielle. Il combine :

1. **Analyse de données historiques** : Utilise un fichier CSV avec l'historique des décisions d'irrigation passées
2. **Données météorologiques en temps réel** : Récupère les conditions météo actuelles via l'API OpenWeatherMap
3. **Agent IA (LangChain + LLM)** : Utilise un modèle de langage (GPT) pour prendre des décisions intelligentes
4. **Interface web** : Une interface Flask moderne pour visualiser et contrôler le système

**Objectif** : Décider automatiquement s'il faut IRRIGUER ou NE PAS IRRIGUER en fonction des conditions actuelles et des patterns historiques.

---

## 🏗️ ARCHITECTURE DU PROJET

### Structure en Couches

```
┌─────────────────────────────────────┐
│   COUCHE PRÉSENTATION (Web)         │
│   - Interface utilisateur Flask    │
│   - API REST                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   COUCHE ORCHESTRATION              │
│   - DecisionEngine                  │
│   - Coordination des composants     │
└──────┬──────────┬──────────┬────────┘
       │          │          │
┌──────▼──┐  ┌───▼───┐  ┌───▼────┐
│ Data    │  │Agent  │  │Weather │
│ Loader  │  │IA     │  │API     │
└─────────┘  └───────┘  └────────┘
```

### Composants Détaillés

#### 1. **`main.py`** - Point d'entrée
- Lance l'application Flask
- Interface accessible sur `http://localhost:5000`

#### 2. **`web/app.py`** - Interface Web Flask
- Routes API REST :
  - `POST /api/decision` : Prendre une décision manuelle
  - `GET /api/decision/last` : Récupérer la dernière décision
  - `GET /api/status` : Statut du système
  - `POST /api/scheduler/start` : Démarrer la planification automatique
  - `POST /api/scheduler/stop` : Arrêter la planification
  - `GET /api/scheduler/status` : Statut du scheduler
- Gère le scheduler automatique (APScheduler)

#### 3. **`app/decision_engine.py`** - Moteur de Décision
- **Classe** : `DecisionEngine`
- **Rôle** : Orchestre tout le processus de décision
- **Méthodes** :
  - `make_irrigation_decision()` : Prend une décision complète
  - `get_system_status()` : Retourne l'état du système

#### 4. **`app/data_loader.py`** - Chargement des Données Historiques
- **Classe** : `HistoricalDataLoader`
- **Rôle** : Charge et analyse le fichier CSV
- **Méthodes** :
  - `load_data()` : Charge le CSV
  - `get_statistics()` : Calcule des statistiques (moyennes, taux d'irrigation, etc.)
  - `get_similar_conditions()` : Trouve des cas similaires dans l'historique
  - `get_summary_for_llm()` : Génère un résumé pour l'agent IA

#### 5. **`app/weather_api.py`** - API Météo
- **Classe** : `WeatherAPI`
- **Rôle** : Récupère les données météo en temps réel
- **Méthodes** :
  - `get_current_weather()` : Récupère les données via OpenWeatherMap
  - `get_weather_summary_for_llm()` : Formate pour l'agent IA
- **Gestion d'erreurs** : Retourne des valeurs par défaut si l'API échoue

#### 6. **`app/agent.py`** - Agent IA
- **Classe** : `IrrigationAgent`
- **Rôle** : Prend la décision finale via LangChain + LLM
- **Technologies** :
  - LangChain pour l'orchestration
  - OpenAI GPT (configurable : gpt-4o-mini, gpt-4, etc.)
  - Support Ollama (modèles locaux)
- **Processus** :
  1. Construit un prompt système avec les règles de décision
  2. Assemble les données (historique + météo + cas similaires)
  3. Appelle le LLM
  4. Parse la réponse JSON
  5. Retourne la décision avec explication

#### 7. **`config/settings.py`** - Configuration
- Lit les variables d'environnement depuis `.env`
- Gère toutes les configurations :
  - Clés API (OpenAI, OpenWeatherMap)
  - Modèle LLM et température
  - Localisation (latitude/longitude)
  - Intervalle automatique
  - Chemin du CSV

#### 8. **`web/templates/index.html`** - Interface Utilisateur
- Interface web moderne avec :
  - Switch visuel ON/OFF pour la pompe
  - Affichage de la décision
  - Explication de la décision
  - Informations météo en temps réel
  - Contrôles pour décision manuelle/automatique

---

## 🔄 FLUX DE DÉCISION COMPLET

```
1. Utilisateur clique sur "Lancer la Décision"
   ↓
2. Flask appelle DecisionEngine.make_irrigation_decision()
   ↓
3. DecisionEngine charge les données historiques (DataLoader)
   ↓
4. DecisionEngine récupère les données météo (WeatherAPI)
   ↓
5. DecisionEngine trouve des cas similaires (DataLoader)
   ↓
6. DecisionEngine envoie tout à l'Agent IA
   ↓
7. Agent IA construit le prompt et appelle le LLM
   ↓
8. LLM retourne une décision JSON : {"decision": "IRRIGUER", "explication": "..."}
   ↓
9. DecisionEngine retourne la décision complète avec métadonnées
   ↓
10. Flask affiche la décision dans l'interface web
```

---

## ⚙️ CHOSES À MODIFIER POUR UN BON FONCTIONNEMENT

### 🔴 OBLIGATOIRE - Avant de lancer l'application

#### 1. **Créer le fichier `.env`**
Le fichier `.env` est **absolument nécessaire** et doit contenir :

```env
# OBLIGATOIRE : Clé API OpenAI
OPENAI_API_KEY=votre_cle_openai_ici

# OBLIGATOIRE : Clé API OpenWeatherMap
WEATHER_API_KEY=votre_cle_openweathermap_ici

# Configuration Localisation (à adapter à votre région)
LATITUDE=45.5017
LONGITUDE=-73.5673
CITY_NAME=Montreal

# Configuration LLM (optionnel, valeurs par défaut OK)
LLM_MODEL=gpt-4o-mini
TEMPERATURE=0.3

# Configuration Système (optionnel)
AUTO_DECISION_INTERVAL_HOURS=6
CSV_DATA_PATH=data/historical_data.csv
```

**Comment obtenir les clés ?**
- **OpenAI** : https://platform.openai.com/api-keys (nécessite un compte payant)
- **OpenWeatherMap** : https://openweathermap.org/api (gratuit jusqu'à 1000 appels/jour)

#### 2. **Vérifier le fichier CSV**
Le fichier `data/historical_data.csv` doit exister et contenir ces colonnes :
- `date` : Date (format YYYY-MM-DD)
- `temperature` : Température en °C
- `humidite_air` : Humidité en % (0-100)
- `pluviometrie` : Pluviométrie en mm
- `irrigation` : 1 = irrigué, 0 = non irrigué
- `type_culture` : Optionnel

#### 3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

### 🟡 RECOMMANDÉ - Pour personnaliser le système

#### 1. **Adapter la localisation**
Dans `.env`, modifiez :
```env
LATITUDE=votre_latitude
LONGITUDE=votre_longitude
CITY_NAME=votre_ville
```

#### 2. **Changer le modèle LLM**
Dans `.env` :
```env
LLM_MODEL=gpt-4          # Plus puissant mais plus cher
# ou
LLM_MODEL=gpt-3.5-turbo  # Moins cher
# ou pour utiliser Ollama (local)
LLM_PROVIDER=ollama
LLM_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

#### 3. **Ajuster la température du LLM**
Dans `.env` :
```env
TEMPERATURE=0.3  # 0.0 = très déterministe, 1.0 = très créatif
```

#### 4. **Modifier l'intervalle automatique**
Dans `.env` :
```env
AUTO_DECISION_INTERVAL_HOURS=6  # Intervalle en heures
```

#### 5. **Remplacer les données historiques**
Remplacez `data/historical_data.csv` par vos propres données historiques d'irrigation.

---

### 🟢 OPTIONNEL - Pour améliorer le système

#### 1. **Modifier les critères de décision**
Dans `app/agent.py`, ligne 36-58, vous pouvez modifier le `system_prompt` pour changer les règles de décision de l'agent IA.

#### 2. **Ajouter de nouvelles sources de données**
- Ajoutez des capteurs de sol dans `app/data_loader.py`
- Ajoutez d'autres APIs météo dans `app/weather_api.py`

#### 3. **Améliorer l'interface web**
Modifiez `web/templates/index.html` pour ajouter de nouvelles fonctionnalités visuelles.

#### 4. **Ajouter un système de logging**
Ajoutez un système de logs pour suivre toutes les décisions prises.

#### 5. **Ajouter une base de données**
Remplacez le CSV par une base de données (SQLite, PostgreSQL) pour stocker l'historique.

---

## 🐛 PROBLÈMES COURANTS ET SOLUTIONS

### Erreur : "OPENAI_API_KEY doit être défini"
**Solution** : Créez le fichier `.env` avec votre clé API OpenAI.

### Erreur : "WEATHER_API_KEY doit être défini"
**Solution** : Ajoutez votre clé OpenWeatherMap dans `.env`.

### Erreur : "Le fichier CSV n'existe pas"
**Solution** : Vérifiez que `data/historical_data.csv` existe et que le chemin dans `.env` est correct.

### Les données météo ne se chargent pas
**Solution** : 
- Vérifiez votre clé OpenWeatherMap
- Le système utilisera des valeurs par défaut en cas d'erreur (température: 20°C, humidité: 50%)

### Erreur de parsing JSON de l'agent IA
**Solution** : Le système a un fallback qui extrait la décision même si le JSON est mal formaté.

### Port 5000 déjà utilisé
**Solution** : Modifiez le port dans `main.py` ligne 11 :
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changez 5000 en 5001
```

---

## 📋 CHECKLIST DE DÉMARRAGE

- [ ] Installer Python 3.8+ (recommandé : 3.11 ou 3.12)
- [ ] Installer les dépendances : `pip install -r requirements.txt`
- [ ] Créer le fichier `.env` à partir de `env.example.txt`
- [ ] Remplir `OPENAI_API_KEY` dans `.env`
- [ ] Remplir `WEATHER_API_KEY` dans `.env`
- [ ] Vérifier que `data/historical_data.csv` existe
- [ ] Adapter `LATITUDE` et `LONGITUDE` dans `.env` (optionnel)
- [ ] Lancer l'application : `python main.py`
- [ ] Ouvrir `http://localhost:5000` dans le navigateur
- [ ] Tester avec le bouton "🔄 Lancer la Décision"

---

## 🎓 RÉSUMÉ

**Ce projet est un système complet d'irrigation intelligente qui :**
1. Analyse l'historique d'irrigation
2. Récupère les données météo en temps réel
3. Utilise un agent IA pour prendre des décisions
4. Affiche tout dans une interface web moderne

**Pour le faire fonctionner, vous devez :**
1. Créer le fichier `.env` avec vos clés API
2. Installer les dépendances
3. Lancer `python main.py`

**Pour le personnaliser :**
- Modifiez les coordonnées dans `.env`
- Changez le modèle LLM dans `.env`
- Remplacez le CSV par vos données
- Modifiez les règles de décision dans `app/agent.py`

---

**Bon développement ! 🌾**

