# 🏗️ Architecture du Système d'Irrigation Intelligent

## Vue d'Ensemble

Le système d'irrigation intelligent est conçu selon une architecture modulaire en couches, permettant une séparation claire des responsabilités et une maintenance facilitée.

## Architecture en Couches

```
┌─────────────────────────────────────────────────────────┐
│              COUCHE PRÉSENTATION                        │
│         (Interface Web - Flask + HTML/CSS/JS)          │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│            COUCHE ORCHESTRATION                         │
│         (Decision Engine - Coordination)                │
└─────────────────────────────────────────────────────────┘
         ↕              ↕              ↕
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Data Layer  │  │  Agent Layer │  │ Weather Layer│
│  (CSV Loader)│  │  (LangChain) │  │  (API Météo) │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Composants Détaillés

### 1. Couche Présentation (`web/`)

**Responsabilité** : Interface utilisateur et API REST

**Composants** :
- `web/app.py` : Application Flask principale
  - Routes API pour les décisions
  - Gestion du scheduler automatique
  - Endpoints REST pour l'interface web
  
- `web/templates/index.html` : Interface utilisateur
  - Affichage visuel de la décision (switch ON/OFF)
  - Boutons de contrôle (manuel/automatique)
  - Affichage des informations météo et historiques

**Flux** :
```
Utilisateur → Interface Web → API Flask → Decision Engine → Réponse
```

### 2. Couche Orchestration (`app/decision_engine.py`)

**Responsabilité** : Coordonner tous les composants pour prendre une décision

**Fonctions principales** :
- `make_irrigation_decision()` : Orchestre le processus complet
- `get_system_status()` : Retourne l'état du système

**Flux de décision** :
```
1. Charger données historiques (DataLoader)
2. Récupérer données météo (WeatherAPI)
3. Trouver cas similaires (DataLoader)
4. Envoyer à l'agent IA (IrrigationAgent)
5. Retourner décision complète
```

### 3. Couche Données (`app/data_loader.py`)

**Responsabilité** : Gestion des données historiques

**Classe** : `HistoricalDataLoader`

**Méthodes clés** :
- `load_data()` : Charge le CSV
- `get_statistics()` : Calcule des statistiques descriptives
- `get_similar_conditions()` : Trouve des cas similaires
- `get_summary_for_llm()` : Génère un résumé pour l'agent IA

**Analyse effectuée** :
- Taux d'irrigation moyen
- Conditions moyennes lors d'irrigation vs non-irrigation
- Identification de patterns historiques
- Recherche de similarité avec conditions actuelles

### 4. Couche Météo (`app/weather_api.py`)

**Responsabilité** : Récupération des données météorologiques en temps réel

**Classe** : `WeatherAPI`

**Méthodes clés** :
- `get_current_weather()` : Récupère les données via API
- `get_weather_summary_for_llm()` : Formate pour l'agent IA

**Données récupérées** :
- Température actuelle
- Humidité de l'air
- Pluviométrie (1h et 3h)
- Description des conditions
- Vitesse du vent
- Couverture nuageuse

**Gestion d'erreurs** : Retourne des valeurs par défaut si l'API échoue

### 5. Couche Agent IA (`app/agent.py`)

**Responsabilité** : Prise de décision intelligente via LangChain + LLM

**Classe** : `IrrigationAgent`

**Technologies** :
- LangChain pour l'orchestration
- OpenAI GPT (configurable) pour le raisonnement
- Prompts structurés pour guider la décision

**Processus de décision** :
```
1. Construction du prompt système (règles et critères)
2. Assemblage des données (historique + météo + cas similaires)
3. Appel au LLM avec le prompt
4. Parsing de la réponse JSON
5. Validation et retour de la décision
```

**Critères de décision** (dans le prompt système) :
- Analyse des patterns historiques
- Évaluation des conditions météo actuelles
- Probabilité de pluie
- Humidité de l'air
- Température
- Comparaison avec cas similaires

**Format de réponse** :
```json
{
    "decision": "IRRIGUER" | "NE PAS IRRIGUER",
    "explication": "Explication claire en français"
}
```

## Flux de Données Complet

```
┌─────────────────┐
│  Interface Web  │
└────────┬────────┘
         │ HTTP Request
         ↓
┌─────────────────┐
│   Flask App     │
│  (web/app.py)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Decision Engine │
│ (Orchestration) │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬─────────────┐
    ↓         ↓              ↓             ↓
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  CSV   │ │ Weather  │ │  Agent   │ │ Similar  │
│ Loader │ │   API    │ │   IA     │ │  Cases   │
└────────┘ └──────────┘ └──────────┘ └──────────┘
    │         │              │             │
    │         │              │             │
    └─────────┴──────────────┴─────────────┘
                    │
                    ↓
            ┌───────────────┐
            │   Décision    │
            │  + Explication│
            └───────────────┘
                    │
                    ↓
            ┌───────────────┐
            │  Interface    │
            │     Web       │
            └───────────────┘
```

## Configuration

### Fichier `.env`

Toutes les configurations sont centralisées dans `config/settings.py` qui lit depuis `.env` :

- **LLM** : Modèle, température, clé API
- **Météo** : Clé API, URL, localisation
- **Système** : Intervalle automatique, chemin CSV

### Gestion des Erreurs

Chaque composant gère ses propres erreurs :
- **WeatherAPI** : Valeurs par défaut si API indisponible
- **DataLoader** : Validation des colonnes CSV
- **Agent** : Fallback si JSON mal formaté
- **DecisionEngine** : Try/catch global

## Planification Automatique

Le système utilise `APScheduler` pour les décisions automatiques :

- **Déclenchement** : Intervalle configurable (par défaut 6h)
- **Tâche** : `automatic_decision_task()` dans `web/app.py`
- **Gestion** : Start/Stop via API REST
- **Statut** : Affichage de la prochaine exécution

## Extensibilité

Le système est conçu pour être facilement extensible :

1. **Nouveaux types de données** : Ajouter dans `data_loader.py`
2. **Nouveaux critères de décision** : Modifier le prompt dans `agent.py`
3. **Nouvelles sources météo** : Implémenter dans `weather_api.py`
4. **Nouveaux modèles LLM** : Changer dans `config/settings.py`
5. **Nouvelles fonctionnalités web** : Ajouter routes dans `web/app.py`

## Sécurité

- Clés API stockées dans `.env` (non versionné)
- Validation des entrées utilisateur
- Gestion des erreurs sans exposer d'informations sensibles
- Pas de contrôle de pompe réelle (simulation uniquement)

## Performance

- **Chargement CSV** : Une fois au démarrage
- **API Météo** : Cache possible (non implémenté actuellement)
- **LLM** : Appel synchrone (peut être optimisé avec async)
- **Interface** : Rafraîchissement manuel ou automatique

## Tests Recommandés

1. **Unitaires** : Chaque composant individuellement
2. **Intégration** : Flux complet de décision
3. **End-to-End** : Interface web complète
4. **Edge Cases** : Données manquantes, API indisponible, etc.


