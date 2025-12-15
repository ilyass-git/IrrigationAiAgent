# 🚀 Guide d'Optimisation Ollama pour Réduire le Temps de Réponse

## Problème
Ollama peut prendre beaucoup de temps (plusieurs minutes) pour répondre, ce qui ralentit le système d'irrigation.

## Solutions Implémentées

### 1. ✅ Timeout Réduit
- **Avant** : 30 secondes
- **Maintenant** : 15 secondes (configurable via `OLLAMA_TIMEOUT`)
- Le système abandonne si Ollama ne répond pas dans les 15 secondes

### 2. ✅ Paramètres de Performance Ollama
Les paramètres suivants ont été ajoutés pour accélérer la génération :

- `num_predict=150` : Limite le nombre de tokens générés (réponse plus courte = plus rapide)
- `num_ctx=2048` : Réduit le contexte pour plus de vitesse
- `num_thread=4` : Utilise 4 threads pour le traitement
- `top_k=40` : Réduit les options à considérer
- `top_p=0.9` : Sampling plus déterministe

### 3. ✅ Prompt Optimisé
- Prompt système raccourci de ~50%
- Instructions plus concises
- Moins de tokens à traiter = réponse plus rapide

## Configuration Recommandée

### Modèle Ollama
Pour de meilleures performances, utilisez un modèle plus petit et rapide :

```bash
# Modèles recommandés (du plus rapide au plus lent) :
ollama pull llama3.2:1b      # Très rapide, moins précis
ollama pull llama3.2:3b      # Rapide, bon compromis
ollama pull llama3:8b        # Moyen, bon équilibre
ollama pull llama3:latest    # Plus lent, plus précis (actuel)
```

**Recommandation** : Utilisez `llama3.2:3b` pour un bon équilibre vitesse/précision.

### Variables d'Environnement (.env)

```env
# Provider
LLM_PROVIDER=ollama

# Modèle (recommandé: llama3.2:3b pour vitesse)
LLM_MODEL=llama3.2:3b

# Timeout (secondes) - réduit pour forcer des réponses rapides
OLLAMA_TIMEOUT=15.0

# Paramètres de performance
OLLAMA_NUM_PREDICT=150    # Limite les tokens générés (100-200 recommandé)
OLLAMA_NUM_CTX=2048       # Contexte réduit (1024-4096 selon RAM)

# Température (plus bas = plus déterministe = plus rapide)
TEMPERATURE=0.2
```

## Optimisations Supplémentaires

### 1. Utiliser un Modèle Quantifié
Les modèles quantifiés sont plus rapides :

```bash
# Exemple avec Q4_K_M (quantification moyenne)
ollama pull llama3.2:3b-q4_K_M
```

### 2. Augmenter la RAM Allouée à Ollama
Si vous avez assez de RAM, augmentez le contexte :

```env
OLLAMA_NUM_CTX=4096  # Au lieu de 2048
```

### 3. Utiliser GPU (si disponible)
Ollama utilise automatiquement le GPU s'il est disponible. Vérifiez :

```bash
ollama show llama3.2:3b
# Cherchez "GPU" dans la sortie
```

### 4. Réduire la Température
Une température plus basse = réponses plus déterministes = plus rapides :

```env
TEMPERATURE=0.1  # Au lieu de 0.3
```

## Comparaison des Performances

| Modèle | Temps Moyen | Précision | RAM Requise |
|--------|-------------|-----------|-------------|
| llama3.2:1b | 2-5s | ⭐⭐ | ~1GB |
| llama3.2:3b | 5-10s | ⭐⭐⭐⭐ | ~2GB |
| llama3:8b | 10-20s | ⭐⭐⭐⭐⭐ | ~5GB |
| llama3:latest | 20-60s+ | ⭐⭐⭐⭐⭐ | ~8GB |

## Vérification

Pour tester les performances, regardez les logs :

```
[AGENT] ✓ Réponse LLM reçue en X.XXs
```

Si c'est > 15s, le système utilisera le timeout et retournera une décision sécurisée.

## Dépannage

### Ollama est toujours lent
1. Vérifiez le modèle utilisé : `ollama list`
2. Essayez un modèle plus petit : `ollama pull llama3.2:3b`
3. Réduisez `OLLAMA_NUM_PREDICT` à 100
4. Vérifiez que le GPU est utilisé (si disponible)

### Timeout trop court
Si vous obtenez souvent des timeouts :
1. Augmentez `OLLAMA_TIMEOUT` à 20 ou 25 secondes
2. Utilisez un modèle plus rapide
3. Vérifiez que votre CPU/GPU peut gérer le modèle

### Réponses incomplètes
Si le LLM ne retourne pas tous les champs :
- Le système complète automatiquement avec des valeurs par défaut
- Vérifiez les logs pour voir ce qui manque
- Augmentez légèrement `OLLAMA_NUM_PREDICT` si nécessaire


