"""
Script pour vérifier la configuration Ollama
"""
import requests
import sys
import io

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama():
    """Vérifie la disponibilité d'Ollama et liste les modèles"""
    print("🔍 Vérification de la configuration Ollama...")
    print("=" * 50)
    
    # Vérifier si Ollama est accessible
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama est accessible")
        else:
            print(f"❌ Ollama répond avec le code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à Ollama sur {OLLAMA_BASE_URL}")
        print("   Assurez-vous qu'Ollama est démarré : 'ollama serve'")
        return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    # Lister les modèles disponibles
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        data = response.json()
        models = data.get('models', [])
        
        if models:
            print(f"\n📋 Modèles disponibles ({len(models)}) :")
            for model in models:
                name = model.get('name', 'Inconnu')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                print(f"   - {name} ({size_gb:.2f} GB)")
        else:
            print("\n⚠️  Aucun modèle installé")
            print("\n💡 Pour installer un modèle, utilisez :")
            print("   ollama pull llama3")
            print("   ou")
            print("   ollama pull llama2")
            print("   ou")
            print("   ollama pull mistral")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des modèles : {e}")
        return False

def test_model(model_name):
    """Teste un modèle spécifique"""
    print(f"\n🧪 Test du modèle '{model_name}'...")
    try:
        data = {
            'model': model_name,
            'prompt': 'Réponds simplement "OK"',
            'stream': False
        }
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Modèle '{model_name}' fonctionne correctement")
            return True
        else:
            error = response.json().get('error', 'Erreur inconnue')
            print(f"❌ Erreur : {error}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

if __name__ == "__main__":
    if check_ollama():
        # Si un modèle est spécifié en argument, le tester
        if len(sys.argv) > 1:
            model_name = sys.argv[1]
            test_model(model_name)
        else:
            print("\n💡 Pour tester un modèle spécifique :")
            print("   python check_ollama.py <nom_modele>")
    else:
        print("\n❌ Configuration Ollama incomplète")
        sys.exit(1)

