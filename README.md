# 🌾 Système d'Irrigation Intelligent avec IA

Système d'irrigation automatisé utilisant l'intelligence artificielle pour prendre des décisions d'irrigation basées sur les données de capteurs IoT, les conditions météorologiques et les retours d'experts.

## 📋 Table des Matières

- [Architecture](#architecture)
- [Fonctionnement](#fonctionnement)
- [Composants](#composants)
- [Flux de Données](#flux-de-données)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)

---

## 🏗️ Architecture

Le système est organisé en plusieurs couches modulaires :

```
┌─────────────────────────────────────────────────────────┐
│                  Interface Web (Flask)                  │
│              web/app.py + templates/index.html           │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Moteur de Décision (Orchestrateur)          │
│              app/decision_engine.py                      │
└───────┬───────────┬───────────┬───────────┬─────────────┘
        │           │           │           │
        ↓           ↓           ↓           ↓
┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Capteurs  │ │ Météo    │ │ Reviews  │ │ Agent IA│
│ IoT       │ │ API      │ │ Experts │ │ LLM     │
└───────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Structure des Répertoires

```
IrrigationAiAgent/
├── app/                    # Modules métier
│   ├── agent.py           # Agent IA (LangChain + LLM)
│   ├── decision_engine.py # Orchestrateur principal
│   ├── sensor_data_loader.py # Gestion des capteurs IoT
│   ├── review_manager.py   # Gestion des avis d'experts
│   └── weather_api.py     # API météorologique
├── web/                    # Interface web
│   ├── app.py             # Application Flask
│   └── templates/
│       └── index.html     # Interface utilisateur
├── config/                 # Configuration
│   └── settings.py        # Paramètres système
├── data/                   # Données persistantes
│   ├── sensor_data.csv    # Données des capteurs
│   └── reviews.csv        # Avis des experts
├── main.py                # Point d'entrée
└── requirements.txt       # Dépendances Python
```

---

## ⚙️ Fonctionnement

### Processus de Décision

Le système prend des décisions d'irrigation en suivant ces étapes :

1. **Collecte des Données**
   - Récupération des données de capteurs IoT (humidité sol, température, réservoir, etc.)
   - Récupération des conditions météorologiques actuelles (OpenWeatherMap)
   - Analyse des retours d'experts (notes et commentaires)

2. **Analyse par l'IA**
   - L'agent IA (LLM) analyse toutes les données collectées
   - Application des critères de décision définis dans le prompt système
   - Génération d'une décision : `IRRIGUER` ou `NE PAS IRRIGUER`
   - Calcul de la durée d'irrigation (10-60 minutes) si irrigation nécessaire

3. **Exécution**
   - Si `IRRIGUER` : démarrage de la pompe pour la durée calculée
   - Si `NE PAS IRRIGUER` : pompe maintenue à l'arrêt
   - Arrêt automatique de la pompe après la durée programmée

4. **Mise à Jour**
   - Génération d'une nouvelle lecture de capteurs (simulation)
   - Enregistrement de la décision avec timestamp
   - Mise à jour de l'interface web

### Critères de Décision

L'IA prend ses décisions en se basant sur :

1. **Humidité du Sol** (priorité absolue)
   - < 25% : ALERTE CRITIQUE → Irrigation immédiate
   - 25-30% : Sol sec → Irrigation
   - 30-40% : Sol légèrement sec → Irrigation si conditions favorables
   - 40-60% : Sol optimal → Pas d'irrigation sauf évapotranspiration élevée
   - 60-70% : Sol bien hydraté → Pas d'irrigation
   - > 70% : Sol saturé → Pas d'irrigation (risque de pourriture)

2. **Niveau du Réservoir**
   - < 20% : Irrigation impossible
   - 20-30% : Irrigation seulement si sol très sec (< 25%)
   - > 30% : Réservoir suffisant

3. **Évapotranspiration**
   - Élevée (> 8 mm/jour) + sol sec → Irrigation
   - Faible (< 3 mm/jour) → Besoins réduits

4. **Conditions Météorologiques**
   - Pas d'irrigation si pluviométrie > 5mm
   - Pas d'irrigation si humidité air > 80%
   - Température élevée → Besoins en eau augmentés

5. **Retours d'Experts (Reviews)**
   - Analyse des notes moyennes (1-5 étoiles)
   - Si note moyenne < 3⭐ : être plus prudent
   - Si note moyenne ≥ 4⭐ : continuer l'approche actuelle
   - Éviter de reproduire les erreurs signalées par les experts

---

## 🔧 Composants

### 1. DecisionEngine (`app/decision_engine.py`)

**Rôle** : Orchestrateur principal qui coordonne tous les composants

**Responsabilités** :
- Collecte des données (capteurs, météo, reviews)
- Appel à l'agent IA pour la décision
- Génération de nouvelles lectures de capteurs
- Construction de la réponse complète avec métadonnées

**Méthodes principales** :
- `make_irrigation_decision()` : Prend une décision complète
- `get_system_status()` : Retourne l'état du système
- `add_review()` : Ajoute un avis d'expert
- `get_recent_reviews()` : Récupère les avis récents

### 2. IrrigationAgent (`app/agent.py`)

**Rôle** : Agent IA utilisant LangChain et un LLM pour la prise de décision

**Technologies** :
- LangChain pour l'orchestration
- OpenAI GPT-4o-mini ou Ollama (configurable)
- Prompts structurés avec règles de décision

**Processus** :
1. Construction du prompt système avec critères de décision
2. Assemblage des données (météo + capteurs + reviews)
3. Appel au LLM avec le prompt
4. Parsing de la réponse JSON
5. Validation et retour de la décision avec durée

**Format de réponse** :
```json
{
    "decision": "IRRIGUER" | "NE PAS IRRIGUER",
    "explication": "Explication détaillée en français",
    "duree_minutes": 30
}
```

### 3. SensorDataLoader (`app/sensor_data_loader.py`)

**Rôle** : Gestion des données de capteurs IoT

**Fonctionnalités** :
- Chargement des données depuis `sensor_data.csv`
- Génération de nouvelles lectures simulées
- Calcul d'alertes basées sur les seuils
- Résumé formaté pour le LLM

**Données gérées** :
- Humidité du sol (%)
- Température du sol (°C)
- Niveau du réservoir (%)
- Évapotranspiration (mm/jour)
- Profondeur des racines (cm)
- pH du sol
- Conductivité électrique (dS/m)

**Simulation** : Génère de nouvelles lectures basées sur :
- Conditions météorologiques actuelles
- Décision d'irrigation prise
- Durée d'irrigation
- Données précédentes

### 4. ReviewManager (`app/review_manager.py`)

**Rôle** : Gestion des avis d'experts

**Fonctionnalités** :
- Stockage des reviews dans `reviews.csv`
- Calcul de statistiques (note moyenne, nombre de reviews)
- Génération de résumés pour le LLM
- Analyse des tendances (reviews négatives/positives)

**Structure d'un review** :
- `review_id` : Identifiant unique
- `decision_id` : ID de la décision évaluée
- `decision` : Type de décision (IRRIGUER / NE PAS IRRIGUER)
- `stars` : Note de 1 à 5
- `comment` : Commentaire de l'expert
- `expert_name` : Nom de l'expert
- `review_timestamp` : Date/heure du review

**Résumé pour LLM** :
- Note moyenne des reviews récentes
- Nombre de reviews négatives (<3⭐) et positives (≥4⭐)
- Règles d'apprentissage basées sur les notes
- Alertes si trop de reviews négatives

### 5. WeatherAPI (`app/weather_api.py`)

**Rôle** : Récupération des données météorologiques

**Source** : OpenWeatherMap API

**Données récupérées** :
- Température actuelle (°C)
- Humidité de l'air (%)
- Pluviométrie (mm)
- Description des conditions
- Vitesse du vent (m/s)
- Couverture nuageuse (%)

**Gestion d'erreurs** : Retourne des valeurs par défaut si l'API échoue

### 6. Flask App (`web/app.py`)

**Rôle** : Interface web et API REST

**Fonctionnalités** :
- Interface web interactive (`/`)
- API REST pour les décisions (`/api/decision/*`)
- API pour les reviews (`/api/reviews/*`)
- Contrôle de la pompe (`/api/pump/*`)
- Planification automatique (APScheduler)

**Endpoints principaux** :
- `GET /` : Interface web
- `POST /api/decision/make` : Prendre une décision manuelle
- `GET /api/decision/last` : Dernière décision
- `GET /api/status` : État du système
- `POST /api/reviews` : Ajouter un review
- `GET /api/reviews/recent` : Reviews récents
- `POST /api/pump/stop` : Arrêter la pompe manuellement
- `POST /api/scheduler/start` : Démarrer la planification automatique
- `POST /api/scheduler/stop` : Arrêter la planification

**Planification automatique** :
- Décisions automatiques à intervalles réguliers (par défaut : 6 heures)
- Arrêt automatique de la pompe après la durée programmée
- Utilisation d'APScheduler pour les tâches en arrière-plan

---

## 📊 Flux de Données

### Flux de Décision

```
┌──────────────┐
│ Interface Web│
│  (Utilisateur)│
└──────┬───────┘
       │
       ↓
┌─────────────────┐
│   Flask App     │
│  web/app.py     │
└──────┬──────────┘
       │
       ↓
┌──────────────────────┐
│  DecisionEngine      │
│  (Orchestration)     │
└──────┬───────────────┘
       │
       ├──────────┬──────────┬──────────┐
       ↓          ↓          ↓          ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Capteurs  │ │ Météo    │ │ Reviews  │ │ Agent IA │
│IoT       │ │ API      │ │ Experts  │ │ (LLM)    │
└──────────┘ └──────────┘ └──────────┘ └────┬─────┘
       │          │          │                │
       └──────────┴──────────┴───────────────┘
                       │
                       ↓
              ┌─────────────────┐
              │   Décision      │
              │  + Durée        │
              └────────┬────────┘
                       │
                       ↓
              ┌─────────────────┐
              │  Contrôle Pompe  │
              │  (Simulation)    │
              └─────────────────┘
```

### Cycle de Vie d'une Décision

1. **Déclenchement** : Manuel (bouton) ou automatique (scheduler)
2. **Collecte** : Capteurs + Météo + Reviews
3. **Analyse** : Agent IA analyse et décide
4. **Exécution** : Démarrage/arrêt de la pompe
5. **Enregistrement** : Nouvelle lecture de capteurs générée
6. **Feedback** : Expert peut évaluer la décision

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- Clé API OpenWeatherMap (optionnelle, valeurs par défaut si absente)
- Clé API OpenAI OU Ollama installé localement

### Étapes

1. **Cloner le projet** (ou télécharger)
   ```bash
   cd IrrigationAiAgent
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement**
   - Créer un fichier `.env` à la racine
   - Copier le contenu de `env.example.txt` et remplir les valeurs

4. **Lancer l'application**
   ```bash
   python main.py
   ```

5. **Accéder à l'interface**
   - Ouvrir un navigateur : `http://localhost:5000`

---

## ⚙️ Configuration

### Variables d'Environnement (`.env`)

```env
# LLM Provider (openai ou ollama)
LLM_PROVIDER=openai
OPENAI_API_KEY=votre_cle_openai
LLM_MODEL=gpt-4o-mini
TEMPERATURE=0.3

# Pour Ollama
OLLAMA_BASE_URL=http://localhost:11434

# API Météo
WEATHER_API_KEY=votre_cle_openweathermap
LATITUDE=45.5017
LONGITUDE=-73.5673
CITY_NAME=Montreal

# Planification automatique
AUTO_DECISION_INTERVAL_HOURS=6
```

### Fichiers de Données

- `data/sensor_data.csv` : Données des capteurs IoT
- `data/reviews.csv` : Avis des experts

Ces fichiers sont créés automatiquement s'ils n'existent pas.

---

## 💻 Utilisation

### Interface Web

1. **Prendre une Décision Manuelle**
   - Cliquer sur le bouton "Prendre une Décision"
   - Attendre l'analyse (quelques secondes)
   - Consulter la décision et l'explication

2. **Planification Automatique**
   - Activer la planification automatique
   - Le système prendra des décisions à intervalles réguliers
   - Désactiver à tout moment

3. **Évaluer une Décision**
   - Après chaque décision, un formulaire apparaît
   - Donner une note (1-5 étoiles)
   - Ajouter un commentaire
   - Valider l'avis

4. **Contrôle de la Pompe**
   - La pompe démarre automatiquement si irrigation décidée
   - Arrêt automatique après la durée programmée
   - Possibilité d'arrêt manuel

### API REST

Exemples avec `curl` :

```bash
# Prendre une décision
curl -X POST http://localhost:5000/api/decision/make

# Obtenir la dernière décision
curl http://localhost:5000/api/decision/last

# Obtenir l'état du système
curl http://localhost:5000/api/status

# Ajouter un review
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "uuid-de-la-decision",
    "decision": "IRRIGUER",
    "decision_timestamp": "2025-12-04T10:00:00",
    "expert_name": "Expert",
    "stars": 5,
    "comment": "Excellente décision"
  }'

# Arrêter la pompe
curl -X POST http://localhost:5000/api/pump/stop
```

---

## 🔄 Amélioration Continue

Le système apprend des retours d'experts :

- **Notes élevées (≥4⭐)** : L'IA continue avec la même approche
- **Notes faibles (<3⭐)** : L'IA ajuste sa stratégie pour éviter les erreurs
- **Tendance négative** : Alertes et changements de comportement

Les reviews influencent directement les prochaines décisions en étant intégrés dans le prompt système de l'agent IA.

---

## 📝 Notes Techniques

- **Simulation de pompe** : La pompe est simulée (pas de matériel réel)
- **Génération de capteurs** : Les nouvelles lectures sont simulées basées sur les conditions
- **Persistance** : Toutes les données sont stockées dans des fichiers CSV
- **Temps réel** : L'interface se met à jour automatiquement toutes les 30 secondes

---

## 🛠️ Technologies Utilisées

- **Python 3.8+**
- **Flask** : Framework web
- **LangChain** : Orchestration LLM
- **OpenAI / Ollama** : Modèles de langage
- **Pandas** : Manipulation de données
- **APScheduler** : Planification de tâches
- **OpenWeatherMap API** : Données météorologiques

---

## 📄 Licence

Ce projet est un système de démonstration pour l'irrigation intelligente avec IA.



