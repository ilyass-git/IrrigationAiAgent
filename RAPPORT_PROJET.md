# 📊 RAPPORT DE PROJET
## Système d'Irrigation Intelligent avec Intelligence Artificielle

---

## 📋 TABLE DES MATIÈRES

1. [Introduction](#1-introduction)
2. [Cahier des Charges](#2-cahier-des-charges)
3. [Architecture et Conception](#3-architecture-et-conception)
4. [Technologies et Outils Utilisés](#4-technologies-et-outils-utilisés)
5. [Étapes de Développement](#5-étapes-de-développement)
6. [Fonctionnalités Détaillées](#6-fonctionnalités-détaillées)
7. [Structure du Projet](#7-structure-du-projet)
8. [Installation et Configuration](#8-installation-et-configuration)
9. [Utilisation du Système](#9-utilisation-du-système)
10. [Flux de Données et Processus](#10-flux-de-données-et-processus)
11. [Système d'Apprentissage et Amélioration Continue](#11-système-dapprentissage-et-amélioration-continue)
12. [Tests et Validation](#12-tests-et-validation)
13. [Limitations et Améliorations Futures](#13-limitations-et-améliorations-futures)
14. [Conclusion](#14-conclusion)

---

## 1. INTRODUCTION

### 1.1 Contexte du Projet

Le projet **IrrigationAiAgent** est un système d'irrigation automatisé et intelligent qui utilise l'intelligence artificielle pour prendre des décisions d'irrigation optimales. Ce système combine les données de capteurs IoT, les conditions météorologiques en temps réel, et les retours d'experts pour optimiser l'utilisation de l'eau dans un contexte agricole.

### 1.2 Objectifs du Projet

L'objectif principal est de créer un système autonome capable de :
- Analyser en temps réel les conditions du sol et de l'environnement
- Prendre des décisions éclairées d'irrigation basées sur l'IA
- Apprendre des retours d'experts pour améliorer continuellement ses décisions
- Optimiser la consommation d'eau tout en maintenant la santé des cultures
- Fournir une interface utilisateur intuitive pour le suivi et le contrôle

### 1.3 Portée du Projet

Le système couvre :
- Collecte et analyse de données multi-sources (capteurs, météo, retours experts)
- Prise de décision automatisée via un agent IA
- Contrôle de pompe d'irrigation (simulé)
- Interface web pour visualisation et contrôle
- Planification automatique des décisions
- Système de feedback et d'apprentissage continu

---

## 2. CAHIER DES CHARGES

### 2.1 Besoins Fonctionnels

#### 2.1.1 Collecte de Données
- **BF1.1** : Récupération des données de capteurs IoT (humidité sol, température, niveau réservoir, etc.)
- **BF1.2** : Récupération des conditions météorologiques en temps réel via API
- **BF1.3** : Stockage et historique des données de capteurs
- **BF1.4** : Gestion des retours d'experts (notes et commentaires)

#### 2.1.2 Prise de Décision
- **BF2.1** : Analyse automatique de toutes les données collectées
- **BF2.2** : Génération de décision binaire : IRRIGUER / NE PAS IRRIGUER
- **BF2.3** : Calcul automatique de la durée d'irrigation (10-60 minutes)
- **BF2.4** : Explication détaillée de chaque décision prise
- **BF2.5** : Prise en compte des retours d'experts dans les décisions futures

#### 2.1.3 Contrôle de l'Irrigation
- **BF3.1** : Démarrage automatique de la pompe si irrigation décidée
- **BF3.2** : Arrêt automatique après la durée programmée
- **BF3.3** : Possibilité d'arrêt manuel de la pompe
- **BF3.4** : Suivi en temps réel de l'état de la pompe

#### 2.1.4 Interface Utilisateur
- **BF4.1** : Interface web responsive et intuitive
- **BF4.2** : Visualisation en temps réel des données (capteurs, météo, pompe)
- **BF4.3** : Déclenchement manuel de décisions
- **BF4.4** : Configuration de la planification automatique
- **BF4.5** : Formulaire d'évaluation des décisions par les experts
- **BF4.6** : Affichage des avis récents et statistiques

#### 2.1.5 Planification Automatique
- **BF5.1** : Prise de décision automatique à intervalles configurables
- **BF5.2** : Activation/désactivation de la planification
- **BF5.3** : Affichage du statut et de la prochaine exécution

### 2.2 Besoins Non-Fonctionnels

#### 2.2.1 Performance
- **BNF1.1** : Temps de réponse < 10 secondes pour une décision
- **BNF1.2** : Mise à jour automatique de l'interface toutes les 30 secondes
- **BNF1.3** : Gestion efficace de la mémoire pour les données historiques

#### 2.2.2 Fiabilité
- **BNF2.1** : Gestion gracieuse des erreurs API (météo, LLM)
- **BNF2.2** : Valeurs par défaut en cas d'indisponibilité des services
- **BNF2.3** : Persistance des données dans des fichiers CSV

#### 2.2.3 Sécurité
- **BNF3.1** : Stockage sécurisé des clés API dans des variables d'environnement
- **BNF3.2** : Validation des entrées utilisateur

#### 2.2.4 Maintenabilité
- **BNF4.1** : Code modulaire et bien structuré
- **BNF4.2** : Documentation complète
- **BNF4.3** : Configuration externalisée

#### 2.2.5 Extensibilité
- **BNF5.1** : Support de multiples providers LLM (OpenAI, Ollama)
- **BNF5.2** : Architecture modulaire permettant l'ajout de nouveaux capteurs
- **BNF5.3** : API REST pour intégrations futures

### 2.3 Critères de Décision

Le système doit prendre des décisions basées sur :

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

5. **Retours d'Experts**
   - Analyse des notes moyennes (1-5 étoiles)
   - Si note moyenne < 3⭐ : être plus prudent
   - Si note moyenne ≥ 4⭐ : continuer l'approche actuelle
   - Éviter de reproduire les erreurs signalées

---

## 3. ARCHITECTURE ET CONCEPTION

### 3.1 Architecture Générale

Le système suit une architecture modulaire en couches :

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
│ Capteurs  │ │ Météo    │ │ Reviews  │ │ Agent IA │
│ IoT       │ │ API      │ │ Experts  │ │ LLM      │
└───────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 3.2 Composants Principaux

#### 3.2.1 DecisionEngine (Orchestrateur)
- **Rôle** : Coordonne tous les composants du système
- **Responsabilités** :
  - Collecte des données depuis toutes les sources
  - Appel à l'agent IA pour la décision
  - Génération de nouvelles lectures de capteurs
  - Construction de la réponse complète avec métadonnées

#### 3.2.2 IrrigationAgent (Agent IA)
- **Rôle** : Prise de décision intelligente via LLM
- **Technologies** : LangChain + OpenAI/Ollama
- **Processus** :
  1. Construction du prompt système avec critères
  2. Assemblage des données (météo + capteurs + reviews)
  3. Appel au LLM avec le prompt
  4. Parsing de la réponse JSON
  5. Validation et retour de la décision

#### 3.2.3 SensorDataLoader
- **Rôle** : Gestion des données de capteurs IoT
- **Fonctionnalités** :
  - Chargement depuis CSV
  - Génération de nouvelles lectures simulées
  - Calcul d'alertes basées sur les seuils
  - Résumé formaté pour le LLM

#### 3.2.4 ReviewManager
- **Rôle** : Gestion des avis d'experts
- **Fonctionnalités** :
  - Stockage des reviews dans CSV
  - Calcul de statistiques (note moyenne, nombre)
  - Génération de résumés pour le LLM
  - Analyse des tendances

#### 3.2.5 WeatherAPI
- **Rôle** : Récupération des données météorologiques
- **Source** : OpenWeatherMap API
- **Gestion d'erreurs** : Valeurs par défaut si API indisponible

#### 3.2.6 Flask App
- **Rôle** : Interface web et API REST
- **Fonctionnalités** :
  - Interface web interactive
  - API REST pour les décisions, reviews, pompe
  - Planification automatique (APScheduler)

### 3.3 Flux de Décision

1. **Déclenchement** : Manuel (bouton) ou automatique (scheduler)
2. **Collecte** : Capteurs + Météo + Reviews
3. **Analyse** : Agent IA analyse et décide
4. **Exécution** : Démarrage/arrêt de la pompe
5. **Enregistrement** : Nouvelle lecture de capteurs générée
6. **Feedback** : Expert peut évaluer la décision

---

## 4. TECHNOLOGIES ET OUTILS UTILISÉS

### 4.1 Langages et Frameworks

#### 4.1.1 Python 3.8+
- **Raison** : Langage principal du projet
- **Utilisation** : Tous les modules backend

#### 4.1.2 Flask 3.0+
- **Raison** : Framework web léger et flexible
- **Utilisation** : Interface web et API REST
- **Avantages** : Simple, extensible, bien documenté

### 4.2 Intelligence Artificielle

#### 4.2.1 LangChain 0.3+
- **Raison** : Framework pour orchestrer les interactions avec les LLM
- **Utilisation** : Gestion des prompts et appels LLM
- **Avantages** : Abstraction des providers, gestion des prompts

#### 4.2.2 OpenAI GPT-4o-mini
- **Raison** : Modèle LLM performant et rapide
- **Utilisation** : Prise de décision d'irrigation
- **Avantages** : Bonne compréhension du contexte, réponses structurées

#### 4.2.3 Ollama (Alternative)
- **Raison** : Solution open-source pour LLM locaux
- **Utilisation** : Alternative à OpenAI pour usage local
- **Avantages** : Pas de coût API, confidentialité des données

### 4.3 Manipulation de Données

#### 4.3.1 Pandas 2.2+
- **Raison** : Manipulation efficace des données tabulaires
- **Utilisation** : Chargement et traitement des CSV (capteurs, reviews)
- **Avantages** : Performance, facilité d'utilisation

#### 4.3.2 NumPy 2.0+
- **Raison** : Calculs numériques
- **Utilisation** : Support pour Pandas et calculs statistiques

### 4.4 Planification et Tâches

#### 4.4.1 APScheduler 3.10+
- **Raison** : Planification de tâches en arrière-plan
- **Utilisation** : Décisions automatiques et arrêt de pompe
- **Avantages** : Flexible, fiable, support des intervalles

### 4.5 APIs Externes

#### 4.5.1 OpenWeatherMap API
- **Raison** : Données météorologiques en temps réel
- **Utilisation** : Conditions météo pour les décisions
- **Données récupérées** : Température, humidité, pluviométrie, vent, nuages

### 4.6 Outils de Développement

#### 4.6.1 python-dotenv 1.0+
- **Raison** : Gestion des variables d'environnement
- **Utilisation** : Configuration sécurisée (clés API)

#### 4.6.2 Requests 2.31+
- **Raison** : Requêtes HTTP
- **Utilisation** : Appels API météo et Ollama

### 4.7 Stockage de Données

#### 4.7.1 Fichiers CSV
- **Raison** : Simplicité et portabilité
- **Fichiers** :
  - `data/sensor_data.csv` : Données de capteurs IoT
  - `data/reviews.csv` : Avis des experts
  - `data/historical_data.csv` : Données historiques (optionnel)

### 4.8 Interface Utilisateur

#### 4.8.1 HTML5 / CSS3 / JavaScript
- **Raison** : Interface web moderne et responsive
- **Utilisation** : Interface utilisateur dans `web/templates/index.html`
- **Caractéristiques** : Design moderne, mise à jour en temps réel

---

## 5. ÉTAPES DE DÉVELOPPEMENT

### 5.1 Phase 1 : Analyse et Conception (Semaine 1)

#### 5.1.1 Analyse des Besoins
- Définition des besoins fonctionnels et non-fonctionnels
- Identification des sources de données (capteurs, météo, experts)
- Définition des critères de décision d'irrigation

#### 5.1.2 Conception Architecturale
- Design de l'architecture modulaire
- Définition des interfaces entre composants
- Choix des technologies et outils

#### 5.1.3 Définition des Formats de Données
- Structure des fichiers CSV
- Format des réponses API
- Format des décisions IA

### 5.2 Phase 2 : Développement des Modules Core (Semaine 2-3)

#### 5.2.1 Module de Configuration
- Création de `config/settings.py`
- Gestion des variables d'environnement
- Validation de la configuration

#### 5.2.2 Module de Données Météo
- Développement de `app/weather_api.py`
- Intégration avec OpenWeatherMap API
- Gestion des erreurs et valeurs par défaut

#### 5.2.3 Module de Capteurs IoT
- Développement de `app/sensor_data_loader.py`
- Chargement et gestion des données CSV
- Génération de nouvelles lectures simulées
- Calcul d'alertes

#### 5.2.4 Module de Gestion des Reviews
- Développement de `app/review_manager.py`
- Stockage et récupération des avis
- Calcul de statistiques
- Génération de résumés pour LLM

### 5.3 Phase 3 : Développement de l'Agent IA (Semaine 4)

#### 5.3.1 Intégration LangChain
- Configuration de LangChain
- Support multi-provider (OpenAI, Ollama)

#### 5.3.2 Développement de l'Agent
- Création de `app/agent.py`
- Définition du prompt système avec critères
- Parsing et validation des réponses JSON
- Gestion des erreurs

#### 5.3.3 Tests de l'Agent
- Tests avec différents scénarios
- Validation des décisions
- Ajustement des prompts

### 5.4 Phase 4 : Moteur de Décision (Semaine 5)

#### 5.4.1 Orchestrateur Principal
- Développement de `app/decision_engine.py`
- Intégration de tous les modules
- Orchestration du flux de décision

#### 5.4.2 Génération de Nouvelles Lectures
- Logique de simulation des capteurs
- Prise en compte de l'irrigation et de la météo

### 5.5 Phase 5 : Interface Web (Semaine 6-7)

#### 5.5.1 Application Flask
- Développement de `web/app.py`
- Définition des routes API REST
- Intégration du scheduler

#### 5.5.2 Interface Utilisateur
- Création de `web/templates/index.html`
- Design responsive et moderne
- JavaScript pour interactions temps réel

#### 5.5.3 Fonctionnalités Web
- Déclenchement manuel de décisions
- Visualisation des données
- Formulaire de reviews
- Contrôle de la pompe
- Planification automatique

### 5.6 Phase 6 : Tests et Optimisation (Semaine 8)

#### 5.6.1 Tests Fonctionnels
- Tests de chaque module
- Tests d'intégration
- Tests de l'interface web

#### 5.6.2 Optimisation
- Amélioration des performances
- Gestion d'erreurs renforcée
- Documentation

### 5.7 Phase 7 : Finalisation (Semaine 9)

#### 5.7.1 Documentation
- README complet
- Documentation du code
- Guide d'installation

#### 5.7.2 Déploiement
- Scripts d'installation
- Configuration des variables d'environnement
- Tests finaux

---

## 6. FONCTIONNALITÉS DÉTAILLÉES

### 6.1 Prise de Décision Automatique

#### 6.1.1 Processus de Décision
1. **Collecte Multi-Sources** :
   - Données de capteurs IoT (humidité sol, température, réservoir, etc.)
   - Conditions météorologiques actuelles (OpenWeatherMap)
   - Retours d'experts (notes et commentaires récents)

2. **Analyse par l'IA** :
   - L'agent IA (LLM) analyse toutes les données
   - Application des critères de décision définis
   - Génération d'une décision : `IRRIGUER` ou `NE PAS IRRIGUER`
   - Calcul de la durée d'irrigation (10-60 minutes) si nécessaire

3. **Exécution** :
   - Si `IRRIGUER` : démarrage de la pompe pour la durée calculée
   - Si `NE PAS IRRIGUER` : pompe maintenue à l'arrêt
   - Arrêt automatique de la pompe après la durée programmée

4. **Mise à Jour** :
   - Génération d'une nouvelle lecture de capteurs (simulation)
   - Enregistrement de la décision avec timestamp
   - Mise à jour de l'interface web

#### 6.1.2 Format de Réponse
```json
{
    "id": "uuid-de-la-decision",
    "decision": "IRRIGUER" | "NE PAS IRRIGUER",
    "duration_minutes": 30,
    "explication": "Explication détaillée en français",
    "timestamp": "2025-12-04T10:00:00",
    "metadata": {
        "weather": {...},
        "sensors": {...},
        "reviews": {...}
    }
}
```

### 6.2 Gestion des Capteurs IoT

#### 6.2.1 Données Collectées
- **Humidité du sol** (%) : Facteur décisif principal
- **Température du sol** (°C) : Impact sur l'absorption d'eau
- **Niveau du réservoir** (%) : Disponibilité de l'eau
- **Évapotranspiration** (mm/jour) : Besoin réel en eau
- **Profondeur des racines** (cm) : Zone d'absorption
- **pH du sol** : Qualité du sol
- **Conductivité électrique** (dS/m) : Salinité du sol

#### 6.2.2 Génération de Nouvelles Lectures
Le système génère automatiquement de nouvelles lectures basées sur :
- Conditions météorologiques actuelles
- Décision d'irrigation prise
- Durée d'irrigation
- Données précédentes

#### 6.2.3 Système d'Alertes
Alertes automatiques générées pour :
- Humidité du sol < 25% (CRITIQUE)
- Humidité du sol < 30% (ALERTE)
- Humidité du sol > 75% (Saturation)
- Niveau réservoir < 20% (CRITIQUE)
- Niveau réservoir < 30% (ALERTE)
- Température sol < 5°C ou > 35°C

### 6.3 Système de Reviews d'Experts

#### 6.3.1 Structure d'un Review
- `review_id` : Identifiant unique
- `decision_id` : ID de la décision évaluée
- `decision` : Type de décision (IRRIGUER / NE PAS IRRIGUER)
- `stars` : Note de 1 à 5 étoiles
- `comment` : Commentaire de l'expert
- `expert_name` : Nom de l'expert
- `review_timestamp` : Date/heure du review

#### 6.3.2 Impact sur les Décisions
- **Note moyenne < 3⭐** : L'IA devient plus prudente
- **Note moyenne ≥ 4⭐** : L'IA continue avec la même approche
- **Plusieurs reviews négatives** : Changement d'approche
- Les reviews sont intégrés dans le prompt système de l'agent IA

### 6.4 Interface Web

#### 6.4.1 Tableau de Bord
- Affichage de la décision actuelle (IRRIGUER / NE PAS IRRIGUER)
- État de la pompe (En marche / Arrêtée)
- Durée planifiée et heure d'arrêt prévue
- Explication de la décision
- Timestamp de la dernière décision

#### 6.4.2 Visualisation des Données
- **Météo** : Température, humidité, pluviométrie
- **Capteurs** : Humidité sol, température sol, réservoir, évapotranspiration
- **Alertes** : Affichage des alertes des capteurs
- **Reviews** : Nombre total et note moyenne

#### 6.4.3 Contrôles
- **Bouton "Lancer la Décision"** : Déclenchement manuel
- **Bouton "Actualiser"** : Mise à jour des données
- **Bouton "Arrêter la Pompe"** : Arrêt manuel
- **Planification automatique** : Activation/désactivation avec intervalle configurable

#### 6.4.4 Formulaire de Review
- Sélection de note (1-5 étoiles)
- Champ commentaire
- Nom de l'expert
- Affichage des reviews récents

### 6.5 Planification Automatique

#### 6.5.1 Configuration
- Intervalle configurable (par défaut : 6 heures)
- Activation/désactivation via interface
- Affichage du statut et de la prochaine exécution

#### 6.5.2 Fonctionnement
- Décisions automatiques à intervalles réguliers
- Arrêt automatique de la pompe après la durée programmée
- Utilisation d'APScheduler pour les tâches en arrière-plan

### 6.6 API REST

#### 6.6.1 Endpoints Disponibles

**Décisions** :
- `POST /api/decision` : Prendre une décision manuelle
- `GET /api/decision/last` : Dernière décision

**Statut** :
- `GET /api/status` : État complet du système

**Reviews** :
- `POST /api/reviews` : Ajouter un review
- `GET /api/reviews/recent` : Reviews récents

**Pompe** :
- `POST /api/pump/stop` : Arrêter la pompe manuellement

**Scheduler** :
- `POST /api/scheduler/start` : Démarrer la planification
- `POST /api/scheduler/stop` : Arrêter la planification
- `GET /api/scheduler/status` : Statut du scheduler

---

## 7. STRUCTURE DU PROJET

```
IrrigationAiAgent/
├── app/                          # Modules métier
│   ├── __init__.py
│   ├── agent.py                  # Agent IA (LangChain + LLM)
│   ├── decision_engine.py        # Orchestrateur principal
│   ├── sensor_data_loader.py     # Gestion des capteurs IoT
│   ├── review_manager.py          # Gestion des avis d'experts
│   └── weather_api.py             # API météorologique
│
├── config/                        # Configuration
│   ├── __init__.py
│   └── settings.py                # Paramètres système
│
├── data/                          # Données persistantes
│   ├── sensor_data.csv           # Données des capteurs
│   ├── reviews.csv                # Avis des experts
│   └── historical_data.csv        # Données historiques (optionnel)
│
├── web/                           # Interface web
│   ├── __init__.py
│   ├── app.py                     # Application Flask
│   └── templates/
│       └── index.html             # Interface utilisateur
│
├── main.py                        # Point d'entrée principal
├── requirements.txt                # Dépendances Python
├── env.example.txt                 # Exemple de fichier .env
├── install.bat                    # Script d'installation (Windows)
├── README.md                      # Documentation principale
└── RAPPORT_PROJET.md              # Ce rapport
```

### 7.1 Description des Modules

#### 7.1.1 Module `app/`
Contient tous les modules métier du système :
- **agent.py** : Agent IA utilisant LangChain pour la prise de décision
- **decision_engine.py** : Orchestrateur qui coordonne tous les composants
- **sensor_data_loader.py** : Gestion des données de capteurs IoT
- **review_manager.py** : Gestion des avis d'experts
- **weather_api.py** : Récupération des données météorologiques

#### 7.1.2 Module `config/`
Configuration centralisée du système :
- **settings.py** : Chargement des variables d'environnement et configuration

#### 7.1.3 Module `data/`
Stockage des données persistantes :
- **sensor_data.csv** : Historique des lectures de capteurs
- **reviews.csv** : Historique des avis d'experts
- **historical_data.csv** : Données historiques (optionnel)

#### 7.1.4 Module `web/`
Interface web et API REST :
- **app.py** : Application Flask avec routes API
- **templates/index.html** : Interface utilisateur HTML/CSS/JS

---

## 8. INSTALLATION ET CONFIGURATION

### 8.1 Prérequis

#### 8.1.1 Logiciels Requis
- **Python 3.8+** : Langage de programmation
- **pip** : Gestionnaire de paquets Python
- **Git** (optionnel) : Pour cloner le dépôt

#### 8.1.2 Services Externes
- **Clé API OpenWeatherMap** (optionnelle, valeurs par défaut si absente)
- **Clé API OpenAI** OU **Ollama installé localement** pour le LLM

### 8.2 Installation

#### 8.2.1 Clonage du Projet
```bash
git clone <url-du-depot>
cd IrrigationAiAgent
```

#### 8.2.2 Installation des Dépendances
```bash
pip install -r requirements.txt
```

#### 8.2.3 Configuration des Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

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

#### 8.2.4 Configuration Ollama (Alternative)

Si utilisation d'Ollama :
```bash
# Installer Ollama
# Télécharger depuis https://ollama.ai

# Démarrer Ollama
ollama serve

# Télécharger un modèle
ollama pull llama2  # ou autre modèle
```

### 8.3 Lancement de l'Application

#### 8.3.1 Démarrage
```bash
python main.py
```

#### 8.3.2 Accès à l'Interface
Ouvrir un navigateur : `http://localhost:5000`

### 8.4 Vérification de l'Installation

#### 8.4.1 Tests de Base
1. Vérifier que l'interface web s'affiche
2. Tester une décision manuelle
3. Vérifier la récupération des données météo
4. Tester l'ajout d'un review

---

## 9. UTILISATION DU SYSTÈME

### 9.1 Prise de Décision Manuelle

1. **Accéder à l'interface** : `http://localhost:5000`
2. **Cliquer sur "Lancer la Décision"**
3. **Attendre l'analyse** (quelques secondes)
4. **Consulter la décision** et l'explication

### 9.2 Planification Automatique

1. **Configurer l'intervalle** (en heures)
2. **Cliquer sur "Démarrer Auto"**
3. Le système prendra des décisions automatiquement
4. **Désactiver** à tout moment avec "Arrêter Auto"

### 9.3 Évaluation d'une Décision

1. **Après chaque décision**, un formulaire apparaît
2. **Sélectionner une note** (1-5 étoiles)
3. **Ajouter un commentaire** (optionnel)
4. **Entrer le nom de l'expert**
5. **Valider l'avis**

### 9.4 Contrôle de la Pompe

- **Démarrage automatique** : Si irrigation décidée
- **Arrêt automatique** : Après la durée programmée
- **Arrêt manuel** : Bouton "Arrêter la Pompe"

### 9.5 Utilisation de l'API REST

#### 9.5.1 Exemples avec curl

**Prendre une décision** :
```bash
curl -X POST http://localhost:5000/api/decision
```

**Obtenir la dernière décision** :
```bash
curl http://localhost:5000/api/decision/last
```

**Obtenir l'état du système** :
```bash
curl http://localhost:5000/api/status
```

**Ajouter un review** :
```bash
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
```

**Arrêter la pompe** :
```bash
curl -X POST http://localhost:5000/api/pump/stop
```

---

## 10. FLUX DE DONNÉES ET PROCESSUS

### 10.1 Flux de Décision Complet

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

### 10.2 Cycle de Vie d'une Décision

1. **Déclenchement** : Manuel (bouton) ou automatique (scheduler)
2. **Collecte** : Capteurs + Météo + Reviews
3. **Analyse** : Agent IA analyse et décide
4. **Exécution** : Démarrage/arrêt de la pompe
5. **Enregistrement** : Nouvelle lecture de capteurs générée
6. **Feedback** : Expert peut évaluer la décision

### 10.3 Format des Données

#### 10.3.1 Données de Capteurs
```csv
date,humidite_sol,temperature_sol,niveau_reservoir,evapotranspiration,profondeur_racines,ph_sol,conductivite_electrique
2025-12-04,45.2,18.5,75.0,5.2,30.0,6.8,1.0
```

#### 10.3.2 Reviews
```csv
review_id,decision_id,decision,decision_timestamp,review_timestamp,expert_name,stars,comment
uuid-1,uuid-decision,IRRIGUER,2025-12-04T10:00:00,2025-12-04T10:05:00,Expert,5,Excellente décision
```

---

## 11. SYSTÈME D'APPRENTISSAGE ET AMÉLIORATION CONTINUE

### 11.1 Mécanisme d'Apprentissage

Le système apprend des retours d'experts de manière continue :

#### 11.1.1 Intégration des Reviews
- Les reviews sont stockés dans `data/reviews.csv`
- Statistiques calculées (note moyenne, nombre de reviews)
- Résumé généré pour le LLM à chaque décision

#### 11.1.2 Impact sur les Décisions
- **Notes élevées (≥4⭐)** : L'IA continue avec la même approche
- **Notes faibles (<3⭐)** : L'IA ajuste sa stratégie pour éviter les erreurs
- **Tendance négative** : Alertes et changements de comportement

#### 11.1.3 Règles d'Apprentissage
Les reviews influencent directement les prochaines décisions en étant intégrés dans le prompt système de l'agent IA :
- Note moyenne des reviews récentes
- Nombre de reviews négatives/positives
- Règles d'apprentissage basées sur les notes
- Alertes si trop de reviews négatives

### 11.2 Amélioration Continue

#### 11.2.1 Feedback Loop
```
Décision → Exécution → Review Expert → Analyse → Ajustement Prompt → Prochaine Décision
```

#### 11.2.2 Métriques de Performance
- Note moyenne des reviews
- Nombre de reviews positifs vs négatifs
- Tendance des notes au fil du temps

---

## 12. TESTS ET VALIDATION

### 12.1 Tests Fonctionnels

#### 12.1.1 Tests des Modules
- **WeatherAPI** : Vérification de la récupération des données météo
- **SensorDataLoader** : Validation du chargement et de la génération de données
- **ReviewManager** : Tests d'ajout et de récupération de reviews
- **IrrigationAgent** : Validation des décisions et du format de réponse

#### 12.1.2 Tests d'Intégration
- **DecisionEngine** : Test du flux complet de décision
- **Flask App** : Tests des endpoints API
- **Interface Web** : Tests des interactions utilisateur

### 12.2 Scénarios de Test

#### 12.2.1 Scénario 1 : Sol Sec
- Humidité sol < 25%
- Réservoir > 30%
- Pas de pluie
- **Résultat attendu** : IRRIGUER avec durée élevée (45-60 min)

#### 12.2.2 Scénario 2 : Sol Optimal
- Humidité sol 45%
- Réservoir > 50%
- Pas de pluie
- **Résultat attendu** : NE PAS IRRIGUER

#### 12.2.3 Scénario 3 : Réservoir Vide
- Humidité sol < 25%
- Réservoir < 20%
- **Résultat attendu** : NE PAS IRRIGUER (réservoir vide)

#### 12.2.4 Scénario 4 : Pluie Récente
- Humidité sol 35%
- Pluviométrie > 5mm
- **Résultat attendu** : NE PAS IRRIGUER (pluie récente)

### 12.3 Validation des Critères

#### 12.3.1 Critères de Décision
- ✅ Priorité à l'humidité du sol
- ✅ Vérification du niveau du réservoir
- ✅ Prise en compte de la pluviométrie
- ✅ Intégration des reviews d'experts

#### 12.3.2 Performance
- ✅ Temps de réponse < 10 secondes
- ✅ Mise à jour automatique toutes les 30 secondes
- ✅ Gestion efficace de la mémoire

---

## 13. LIMITATIONS ET AMÉLIORATIONS FUTURES

### 13.1 Limitations Actuelles

#### 13.1.1 Simulation
- **Pompe simulée** : Pas de matériel réel connecté
- **Capteurs simulés** : Génération de données basée sur des modèles
- **Pas de contrôle physique** : Système en mode démonstration

#### 13.1.2 Données
- **Stockage CSV** : Pas de base de données relationnelle
- **Pas de sauvegarde automatique** : Risque de perte de données
- **Limite de taille** : Fichiers CSV peuvent devenir volumineux

#### 13.1.3 Fonctionnalités
- **Pas de multi-utilisateurs** : Interface pour un seul utilisateur
- **Pas d'authentification** : Accès non sécurisé
- **Pas de notifications** : Pas d'alertes par email/SMS

### 13.2 Améliorations Futures

#### 13.2.1 Intégration Matérielle
- **Connexion de vrais capteurs IoT** : Intégration avec matériel réel
- **Contrôle de pompe physique** : Relais, GPIO, etc.
- **Support de multiples zones** : Gestion de plusieurs parcelles

#### 13.2.2 Base de Données
- **Migration vers PostgreSQL/MySQL** : Stockage relationnel
- **Sauvegarde automatique** : Backups réguliers
- **Requêtes optimisées** : Performance améliorée

#### 13.2.3 Fonctionnalités Avancées
- **Multi-utilisateurs** : Gestion de comptes et permissions
- **Authentification** : Login sécurisé
- **Notifications** : Alertes par email/SMS/Webhook
- **Historique et Analytics** : Graphiques et statistiques avancées
- **Prédictions** : Modèles ML pour prévoir les besoins futurs

#### 13.2.4 Amélioration de l'IA
- **Fine-tuning du modèle** : Adaptation spécifique à l'irrigation
- **Apprentissage par renforcement** : Amélioration continue automatique
- **Multi-modèles** : Comparaison de plusieurs LLM

#### 13.2.5 Interface
- **Application mobile** : iOS/Android
- **Dashboard avancé** : Graphiques interactifs
- **Export de données** : PDF, Excel, etc.

---

## 14. CONCLUSION

### 14.1 Résumé du Projet

Le projet **IrrigationAiAgent** est un système d'irrigation intelligent qui démontre l'utilisation de l'intelligence artificielle pour optimiser la gestion de l'eau en agriculture. Le système combine avec succès :

- **Collecte multi-sources** : Capteurs IoT, données météo, retours d'experts
- **Décision intelligente** : Agent IA basé sur LLM pour l'analyse et la décision
- **Interface moderne** : Interface web intuitive et responsive
- **Apprentissage continu** : Système de feedback pour amélioration progressive

### 14.2 Objectifs Atteints

✅ **Prise de décision automatisée** : Le système prend des décisions éclairées basées sur l'IA  
✅ **Optimisation de l'eau** : Réduction de la consommation grâce à des décisions précises  
✅ **Interface utilisateur** : Interface web moderne et intuitive  
✅ **Apprentissage continu** : Intégration des retours d'experts  
✅ **Planification automatique** : Décisions automatiques à intervalles réguliers  
✅ **API REST** : Intégration possible avec d'autres systèmes  

### 14.3 Contributions Techniques

Le projet démontre l'utilisation efficace de :
- **LangChain** pour l'orchestration LLM
- **Flask** pour l'interface web et API REST
- **APScheduler** pour la planification de tâches
- **Architecture modulaire** pour la maintenabilité
- **Gestion d'erreurs robuste** pour la fiabilité

### 14.4 Impact et Applications

Ce système peut être utilisé pour :
- **Agriculture de précision** : Optimisation de l'irrigation
- **Réduction de la consommation d'eau** : Économies importantes
- **Amélioration des rendements** : Meilleure santé des cultures
- **Démonstration technologique** : Preuve de concept pour l'IA en agriculture

### 14.5 Perspectives

Le projet ouvre la voie à de nombreuses améliorations futures :
- Intégration avec du matériel réel
- Base de données pour un stockage plus robuste
- Fonctionnalités avancées (multi-utilisateurs, notifications, analytics)
- Amélioration continue de l'IA

### 14.6 Remerciements

Ce projet a été développé en utilisant des technologies open-source et des APIs publiques. Il démontre comment l'intelligence artificielle peut être appliquée à des problèmes concrets de l'agriculture moderne.

---

## ANNEXES

### Annexe A : Format des Fichiers CSV

#### A.1 sensor_data.csv
```csv
date,humidite_sol,temperature_sol,niveau_reservoir,evapotranspiration,profondeur_racines,ph_sol,conductivite_electrique
2025-12-04,45.2,18.5,75.0,5.2,30.0,6.8,1.0
```

#### A.2 reviews.csv
```csv
review_id,decision_id,decision,decision_timestamp,review_timestamp,expert_name,stars,comment
uuid-1,uuid-decision,IRRIGUER,2025-12-04T10:00:00,2025-12-04T10:05:00,Expert,5,Excellente décision
```

### Annexe B : Variables d'Environnement

Voir section 8.2.3 pour la liste complète des variables d'environnement.

### Annexe C : Endpoints API

Voir section 6.6 pour la liste complète des endpoints API.

---

**Date du rapport** : Décembre 2024  
**Version du projet** : 1.0  
**Auteur** : Équipe de développement IrrigationAiAgent


