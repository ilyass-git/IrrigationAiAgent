"""
Agent IA LangChain pour la prise de décision d'irrigation
"""
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import os
import json
import requests
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE, LLM_PROVIDER, OLLAMA_BASE_URL


class IrrigationAgent:
    """Agent IA utilisant LangChain pour prendre des décisions d'irrigation"""
    
    def __init__(self):
        """Initialise l'agent avec le modèle LLM"""
        
        if LLM_PROVIDER == 'ollama':
            print(f"Utilisation de Ollama avec le modele {LLM_MODEL}")
            try:
                # Vérifier la disponibilité d'Ollama et des modèles
                import requests
                try:
                    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        if model_names:
                            print(f"[INFO] Modeles Ollama disponibles : {', '.join(model_names)}")
                        else:
                            print("[WARNING] Aucun modele Ollama trouve. Assurez-vous d'avoir telecharge un modele avec 'ollama pull <nom_modele>'")
                        
                        # Vérifier si le modèle existe (avec ou sans tag :latest)
                        model_found = LLM_MODEL in model_names
                        if not model_found:
                            # Essayer avec :latest
                            model_with_latest = f"{LLM_MODEL}:latest"
                            if model_with_latest in model_names:
                                print(f"[INFO] Modele '{LLM_MODEL}' trouve comme '{model_with_latest}'")
                                model_found = True
                        
                        if not model_found:
                            print(f"[WARNING] Attention : Le modele '{LLM_MODEL}' n'est pas dans la liste des modeles disponibles.")
                            if model_names:
                                print(f"[INFO] Suggestion : Utilisez l'un de ces modeles : {', '.join(model_names)}")
                except requests.exceptions.RequestException as e:
                    print(f"[WARNING] Impossible de se connecter a Ollama sur {OLLAMA_BASE_URL}")
                    print(f"   Erreur : {e}")
                    print(f"   Assurez-vous qu'Ollama est demarre : 'ollama serve'")
                
                self.llm = ChatOllama(
                    model=LLM_MODEL,
                    temperature=TEMPERATURE,
                    base_url=OLLAMA_BASE_URL
                )
            except Exception as e:
                print(f"[ERROR] Erreur lors de l'initialisation d'Ollama : {e}")
                raise
        else:
            # S'assurer que la clé API est dans l'environnement pour OpenAI
            if OPENAI_API_KEY:
                os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            
            self.llm = ChatOpenAI(
                model=LLM_MODEL,
                temperature=TEMPERATURE
            )
        
        # Template de prompt système pour guider l'agent
        self.system_prompt = """Tu es un expert en agriculture intelligente et en gestion de l'irrigation.

Ta mission est d'analyser les données historiques d'irrigation, les conditions météorologiques actuelles ET les données de capteurs IoT pour prendre une décision éclairée : IRRIGUER ou NE PAS IRRIGUER.

CRITÈRES DE DÉCISION (par ordre de priorité) :
1. **HUMIDITÉ DU SOL** (CAPTEUR) - LE FACTEUR LE PLUS IMPORTANT :
   - < 25% = ALERTE CRITIQUE → IRRIGUER IMMÉDIATEMENT
   - 25-30% = Sol sec → IRRIGUER
   - 30-40% = Sol légèrement sec → IRRIGUER si autres conditions favorables
   - 40-60% = Sol optimal → NE PAS IRRIGUER sauf si évapotranspiration élevée
   - 60-70% = Sol bien hydraté → NE PAS IRRIGUER
   - > 70% = Sol saturé → NE PAS IRRIGUER (risque de pourriture)

2. **NIVEAU DU RÉSERVOIR** (CAPTEUR) :
   - < 20% = Irrigation impossible → NE PAS IRRIGUER (réservoir vide)
   - 20-30% = Niveau faible → IRRIGUER seulement si sol très sec (< 25%)
   - > 30% = Réservoir suffisant → Peut irriguer si nécessaire

3. **ÉVAPOTRANSPIRATION** (CAPTEUR) :
   - Élevée (> 8 mm/jour) + sol sec → IRRIGUER
   - Faible (< 3 mm/jour) → Besoins réduits

4. **Conditions météorologiques** :
   - Ne pas irriguer si pluviométrie récente ou prévue > 5mm
   - Ne pas irriguer si humidité de l'air > 80%
   - Température élevée → Besoins en eau augmentent

5. **Patterns historiques** :
   - Comparer avec cas similaires dans l'historique

RÈGLES IMPORTANTES :
- L'HUMIDITÉ DU SOL EST LE FACTEUR DÉCISIF - prioriser cette donnée
- Ne jamais irriguer si le réservoir est < 20%
- Ne pas irriguer si le sol est déjà saturé (> 70%)
- Prendre en compte les alertes des capteurs

FORMAT DE RÉPONSE :
Tu dois répondre UNIQUEMENT avec un JSON valide au format suivant :
{{
    "decision": "IRRIGUER" ou "NE PAS IRRIGUER",
    "explication": "Une explication claire et concise en 2-3 phrases expliquant pourquoi cette décision a été prise, en français, adaptée pour un agriculteur. Mentionne spécifiquement l'humidité du sol et le niveau du réservoir si disponibles."
}}
"""
    
    def make_decision(self, historical_summary: str, weather_summary: str, 
                     sensor_summary: str = "", sensor_alerts: list = None,
                     similar_cases: str = "") -> Dict:
        """
        Prend une décision d'irrigation basée sur les données fournies
        
        Args:
            historical_summary: Résumé des données historiques
            weather_summary: Résumé des conditions météo actuelles
            sensor_summary: Résumé des données de capteurs IoT
            sensor_alerts: Liste des alertes des capteurs
            similar_cases: Informations sur les cas similaires (optionnel)
        
        Returns:
            Dictionnaire contenant la décision et l'explication
        """
        if sensor_alerts is None:
            sensor_alerts = []
        
        # Construction du message avec alertes
        alerts_text = ""
        if sensor_alerts:
            alerts_text = "\n🚨 ALERTES DES CAPTEURS :\n" + "\n".join(sensor_alerts) + "\n"
        
        try:
            # Appel au LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
DONNÉES À ANALYSER :
{historical_summary}

{weather_summary}

{sensor_summary}

{alerts_text}

{f"CAS SIMILAIRES DANS L'HISTORIQUE :\n{similar_cases}" if similar_cases else ""}

Prends maintenant ta décision en analysant ces informations. PRIORISE les données de capteurs, surtout l'humidité du sol. Réponds UNIQUEMENT avec un JSON valide au format demandé.""")
            ]
            
            response = self.llm.invoke(messages)
            
            # Extraction de la réponse
            response_text = response.content.strip()
            
            # Nettoyage de la réponse (enlever les markdown code blocks si présents)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parsing du JSON
            decision_data = json.loads(response_text)
            
            # Validation
            if 'decision' not in decision_data or 'explication' not in decision_data:
                raise ValueError("Format de réponse invalide")
            
            if decision_data['decision'] not in ['IRRIGUER', 'NE PAS IRRIGUER']:
                raise ValueError("Décision invalide")
            
            return decision_data
            
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON : {e}")
            print(f"Réponse reçue : {response_text}")
            # Fallback : essayer d'extraire la décision manuellement
            return self._extract_decision_fallback(response_text)
        except Exception as e:
            error_msg = str(e)
            print(f"Erreur lors de la prise de décision : {error_msg}")
            
            # Messages d'erreur plus explicites pour Ollama
            if 'not found' in error_msg.lower() or '404' in error_msg:
                error_msg = f"Modèle '{LLM_MODEL}' non trouvé dans Ollama. Vérifiez que le modèle est installé avec 'ollama pull {LLM_MODEL}'"
            elif 'connection' in error_msg.lower() or 'refused' in error_msg.lower():
                error_msg = f"Impossible de se connecter à Ollama sur {OLLAMA_BASE_URL}. Assurez-vous qu'Ollama est démarré."
            
            return {
                'decision': 'NE PAS IRRIGUER',
                'explication': f'Erreur lors de l\'analyse : {error_msg}. Par précaution, l\'irrigation n\'est pas activée.'
            }
    
    def _extract_decision_fallback(self, response_text: str) -> Dict:
        """
        Méthode de fallback pour extraire la décision si le JSON est mal formaté
        
        Args:
            response_text: Texte de réponse du LLM
        
        Returns:
            Dictionnaire avec la décision extraite
        """
        decision = 'NE PAS IRRIGUER'
        explication = response_text
        
        if 'IRRIGUER' in response_text.upper():
            decision = 'IRRIGUER'
        elif 'NE PAS IRRIGUER' in response_text.upper() or 'NON' in response_text.upper():
            decision = 'NE PAS IRRIGUER'
        
        return {
            'decision': decision,
            'explication': explication
        }

