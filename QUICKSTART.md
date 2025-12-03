# 🚀 Guide de Démarrage Rapide

## Installation en 5 Minutes

### Étape 1 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 2 : Configurer les clés API

1. Créez un fichier `.env` à la racine du projet
2. Copiez le contenu de `env.example.txt` dans `.env`
3. Remplissez vos clés API :

```env
OPENAI_API_KEY=votre_cle_openai_ici
WEATHER_API_KEY=votre_cle_openweathermap_ici
```

**Où obtenir les clés ?**
- **OpenAI** : https://platform.openai.com/api-keys
- **OpenWeatherMap** : https://openweathermap.org/api (gratuit jusqu'à 1000 appels/jour)

### Étape 3 : Vérifier les données

Le fichier `data/historical_data.csv` est déjà fourni avec des données d'exemple. Vous pouvez le remplacer par vos propres données si nécessaire.

### Étape 4 : Lancer l'application

```bash
python main.py
```

### Étape 5 : Accéder à l'interface

Ouvrez votre navigateur sur : **http://localhost:5000**

## Utilisation

### Décision Manuelle

1. Cliquez sur **"🔄 Lancer la Décision"**
2. Attendez quelques secondes (analyse en cours)
3. La décision s'affiche avec une explication

### Décision Automatique

1. Dans la section "Planification Automatique"
2. Choisissez un intervalle (ex: 6 heures)
3. Cliquez sur **"Démarrer Auto"**
4. Le système prendra des décisions automatiquement

## Structure des Données CSV

Votre fichier CSV doit avoir ces colonnes :

```csv
date,temperature,humidite_air,pluviometrie,irrigation,type_culture
2021-01-15,5.2,65.0,0.0,0,Blé
2021-01-16,6.1,68.0,2.5,0,Blé
...
```

- `date` : Format YYYY-MM-DD
- `temperature` : En degrés Celsius
- `humidite_air` : En pourcentage (0-100)
- `pluviometrie` : En millimètres
- `irrigation` : 1 = irrigué, 0 = non irrigué
- `type_culture` : Optionnel

## Dépannage Rapide

### Erreur : "OPENAI_API_KEY doit être défini"
→ Vérifiez que votre fichier `.env` existe et contient la clé

### Erreur : "Le fichier CSV n'existe pas"
→ Vérifiez que `data/historical_data.csv` existe

### L'interface ne se charge pas
→ Vérifiez que le port 5000 n'est pas déjà utilisé

### Les données météo ne se chargent pas
→ Vérifiez votre clé OpenWeatherMap (le système fonctionnera avec des valeurs par défaut)

## Prochaines Étapes

1. **Personnaliser les données** : Remplacez `historical_data.csv` par vos données réelles
2. **Ajuster la localisation** : Modifiez `LATITUDE` et `LONGITUDE` dans `.env`
3. **Tester différents modèles** : Essayez `gpt-4` au lieu de `gpt-4o-mini` dans `.env`
4. **Ajuster la température** : Modifiez `TEMPERATURE` (0.0 = déterministe, 1.0 = créatif)

## Support

Consultez le `README.md` pour la documentation complète et `ARCHITECTURE.md` pour comprendre l'architecture du système.

---

**Bon développement ! 🌾**




