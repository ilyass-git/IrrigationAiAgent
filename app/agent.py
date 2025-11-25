"""
Agent IA LangChain pour la prise de décision d'irrigation
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE


class IrrigationAgent:
    """Agent IA utilisant LangChain pour prendre des décisions d'irrigation"""
    
    def __init__(self):
        """Initialise l'agent avec le modèle LLM"""
        self.llm = ChatOpenAI(
            model_name=LLM_MODEL,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Template de prompt système pour guider l'agent
        self.system_prompt = """Tu es un expert en agriculture intelligente et en gestion de l'irrigation.

Ta mission est d'analyser les données historiques d'irrigation et les conditions météorologiques actuelles pour prendre une décision éclairée : IRRIGUER ou NE PAS IRRIGUER.

CRITÈRES DE DÉCISION :
1. Analyse les patterns historiques : dans quelles conditions a-t-on irrigué dans le passé ?
2. Évalue les conditions météorologiques actuelles (température, humidité, pluviométrie)
3. Prends en compte la probabilité de pluie dans les prochaines heures
4. Considère l'humidité actuelle du sol (déduite des données historiques et météo récentes)

RÈGLES IMPORTANTES :
- Ne pas irriguer si la pluviométrie récente ou prévue est suffisante
- Ne pas irriguer si l'humidité de l'air est très élevée (>80%)
- Irriguer si les conditions sont similaires aux cas historiques où l'irrigation a eu lieu
- Prendre en compte la température : les besoins en eau augmentent avec la chaleur

FORMAT DE RÉPONSE :
Tu dois répondre UNIQUEMENT avec un JSON valide au format suivant :
{{
    "decision": "IRRIGUER" ou "NE PAS IRRIGUER",
    "explication": "Une explication claire et concise en 2-3 phrases expliquant pourquoi cette décision a été prise, en français, adaptée pour un agriculteur"
}}
"""
    
    def make_decision(self, historical_summary: str, weather_summary: str, 
                     similar_cases: str = "") -> Dict:
        """
        Prend une décision d'irrigation basée sur les données fournies
        
        Args:
            historical_summary: Résumé des données historiques
            weather_summary: Résumé des conditions météo actuelles
            similar_cases: Informations sur les cas similaires (optionnel)
        
        Returns:
            Dictionnaire contenant la décision et l'explication
        """
        # Construction du prompt
        prompt = f"""{self.system_prompt}

DONNÉES À ANALYSER :
{historical_summary}

{weather_summary}

{f"CAS SIMILAIRES DANS L'HISTORIQUE :\n{similar_cases}" if similar_cases else ""}

Prends maintenant ta décision en analysant ces informations."""
        
        try:
            # Appel au LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
DONNÉES À ANALYSER :
{historical_summary}

{weather_summary}

{f"CAS SIMILAIRES DANS L'HISTORIQUE :\n{similar_cases}" if similar_cases else ""}

Prends maintenant ta décision en analysant ces informations. Réponds UNIQUEMENT avec un JSON valide au format demandé.""")
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
            import json
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
            print(f"Erreur lors de la prise de décision : {e}")
            return {
                'decision': 'NE PAS IRRIGUER',
                'explication': f'Erreur lors de l\'analyse : {str(e)}. Par précaution, l\'irrigation n\'est pas activée.'
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

