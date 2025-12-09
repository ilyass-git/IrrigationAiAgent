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
import time
import logging
import re
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE, LLM_PROVIDER, OLLAMA_BASE_URL

logger = logging.getLogger(__name__)


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
                    base_url=OLLAMA_BASE_URL,
                    timeout=30.0  # Timeout de 30 secondes pour Ollama
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
                temperature=TEMPERATURE,
                timeout=30.0  # Timeout de 30 secondes pour OpenAI
            )
        
        # Template de prompt système pour guider l'agent
        self.system_prompt = """Tu es un expert en agriculture intelligente et en gestion de l'irrigation.

Ta mission est d'analyser les conditions météorologiques actuelles, les données de capteurs IoT et les retours d'experts pour prendre une décision éclairée : IRRIGUER ou NE PAS IRRIGUER.

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

4. **Retours d'experts (REVUES)** :
   - Étudier les critiques passées : si plusieurs revues récentes sont négatives (<3⭐), éviter de reproduire les mêmes conditions
   - Donner davantage de poids aux retours positifs (>4⭐) lorsque les conditions sont similaires
   - Si la note moyenne des revues récentes est < 3⭐, être plus prudent dans la décision

RÈGLES IMPORTANTES :
- L'HUMIDITÉ DU SOL EST LE FACTEUR DÉCISIF - prioriser cette donnée
- Ne jamais irriguer si le réservoir est < 20%
- Ne pas irriguer si le sol est déjà saturé (> 70%)
- Prendre en compte les alertes des capteurs
- Mentionner explicitement lorsqu'une décision suit (ou contredit) les retours d'experts
- SI TU DÉCIDES D'IRRIGUER, CHOISIS UNE DURÉE D'IRRIGATION (10 à 60 minutes). Plus le sol est sec ou l'évapotranspiration élevée, plus la durée doit augmenter. Si la décision est NE PAS IRRIGUER, la durée doit impérativement être 0.

GUIDE RAPIDE POUR LA DURÉE :
- Humidité < 25 % → 45 à 60 min
- Entre 25 % et 35 % → 30 à 40 min
- Entre 35 % et 45 % → 20 à 30 min
- > 45 % ou pluie prévue → 0 à 15 min maximum
Réduis la durée si le niveau du réservoir est bas ou si les experts ont récemment critiqué des durées trop longues.

FORMAT DE RÉPONSE :
Tu dois répondre UNIQUEMENT avec un JSON valide, SANS texte avant ou après, SANS markdown, SANS doubles accolades.
Format exact à utiliser (copier-coller et remplacer les valeurs) :

{
    "decision": "IRRIGUER",
    "duree_minutes": 30,
    "explication": "Explication en français"
}

OU

{
    "decision": "NE PAS IRRIGUER",
    "duree_minutes": 0,
    "explication": "Explication en français"
}

IMPORTANT : 
- Réponds UNIQUEMENT le JSON, rien d'autre
- Utilise des accolades simples { et }, PAS de doubles {{ ou }}
- Pas de texte avant ou après le JSON
- Pas de markdown ```json
"""
    
    def make_decision(self, weather_summary: str, 
                     sensor_summary: str = "", sensor_alerts: list = None,
                     reviews_summary: str = "") -> Dict:
        """
        Prend une décision d'irrigation basée sur les données fournies
        
        Args:
            weather_summary: Résumé des conditions météo actuelles
            sensor_summary: Résumé des données de capteurs IoT
            sensor_alerts: Liste des alertes des capteurs
            reviews_summary: Résumé des retours d'experts (notes et commentaires)
        
        Returns:
            Dictionnaire contenant la décision, la durée et l'explication
        """
        start_time = time.time()
        logger.info("[AGENT] Début de l'analyse par l'IA...")
        
        if sensor_alerts is None:
            sensor_alerts = []
        
        # Construction du message avec alertes
        alerts_text = ""
        if sensor_alerts:
            alerts_text = "\n🚨 ALERTES DES CAPTEURS :\n" + "\n".join(sensor_alerts) + "\n"
        
        try:
            # Construction du prompt
            prompt_start = time.time()
            # Construire le message sans f-string pour éviter les problèmes avec les accolades
            prompt_content = f"""DONNÉES À ANALYSER :

{weather_summary}

{sensor_summary}

{alerts_text}

{reviews_summary}

Prends maintenant ta décision en analysant ces informations. PRIORISE les données de capteurs, surtout l'humidité du sol. Prends en compte les retours d'experts (notes des reviews). 

RÉPONDS UNIQUEMENT AVEC LE JSON, SANS TEXTE AVANT OU APRÈS, SANS MARKDOWN, SANS DOUBLES ACCOLADES. Format exact :

{{
    "decision": "IRRIGUER" ou "NE PAS IRRIGUER",
    "duree_minutes": nombre entier,
    "explication": "ton explication"
}}"""
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt_content)
            ]
            prompt_duration = time.time() - prompt_start
            logger.info(f"[AGENT] Prompt construit en {prompt_duration:.3f}s")
            
            # Appel au LLM
            logger.info(f"[AGENT] Appel au LLM ({LLM_PROVIDER}/{LLM_MODEL})...")
            llm_start = time.time()
            response = self.llm.invoke(messages)
            llm_duration = time.time() - llm_start
            logger.info(f"[AGENT] ✓ Réponse LLM reçue en {llm_duration:.2f}s")
            
            # Extraction de la réponse
            response_text = response.content.strip()
            logger.info(f"[AGENT] Réponse brute (premiers 300 chars): {response_text[:300]}...")
            
            # Nettoyage de la réponse (enlever les markdown code blocks si présents)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Correction des doubles accolades (problème avec certains LLM)
            # Remplacer {{ par { et }} par }
            response_text = response_text.replace('{{', '{').replace('}}', '}')
            
            # Essayer d'extraire le JSON si la réponse contient du texte avant/après
            # Chercher le premier { et le dernier }
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                response_text = response_text[first_brace:last_brace+1]
                logger.info(f"[AGENT] JSON extrait de la réponse (position {first_brace}-{last_brace})")
            
            # Parsing du JSON
            parse_start = time.time()
            try:
                decision_data = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                logger.error(f"[AGENT] Erreur de parsing JSON après nettoyage: {json_err}")
                logger.error(f"[AGENT] Texte nettoyé: {response_text[:500]}")
                raise
            parse_duration = time.time() - parse_start
            logger.info(f"[AGENT] ✓ JSON parsé en {parse_duration:.3f}s")
            
            # Validation
            if 'decision' not in decision_data or 'explication' not in decision_data:
                raise ValueError("Format de réponse invalide: champs manquants")
            
            if decision_data['decision'] not in ['IRRIGUER', 'NE PAS IRRIGUER']:
                raise ValueError(f"Décision invalide: '{decision_data['decision']}'")
            
            duree = int(decision_data.get('duree_minutes', 0) or 0)
            logger.info(f"[AGENT] Durée brute du LLM: {duree} min")
            
            if duree < 0:
                duree = 0
                logger.info(f"[AGENT] Durée négative corrigée à 0")
            
            if decision_data['decision'] == 'NE PAS IRRIGUER':
                duree = 0
                logger.info(f"[AGENT] Durée mise à 0 car décision = NE PAS IRRIGUER")
            else:
                duree = max(10, min(60, duree)) if duree > 0 else 20
                logger.info(f"[AGENT] Durée ajustée entre 10-60 min: {duree} min")
            
            decision_data['duree_minutes'] = duree
            
            total_duration = time.time() - start_time
            logger.info(f"[AGENT] ✓ Décision finale: {decision_data['decision']}, Durée: {duree} min (total: {total_duration:.2f}s)")
            
            return decision_data
            
        except json.JSONDecodeError as e:
            logger.error(f"[AGENT] Erreur de parsing JSON : {e}")
            logger.error(f"[AGENT] Réponse reçue : {response_text[:500]}")
            # Fallback : essayer d'extraire la décision manuellement
            logger.warning("[AGENT] Utilisation du fallback pour extraire la décision")
            return self._extract_decision_fallback(response_text)
        except Exception as e:
            error_msg = str(e)
            total_duration = time.time() - start_time
            logger.error(f"[AGENT] Erreur après {total_duration:.2f}s : {error_msg}", exc_info=True)
            
            # Messages d'erreur plus explicites pour Ollama
            if 'not found' in error_msg.lower() or '404' in error_msg:
                error_msg = f"Modèle '{LLM_MODEL}' non trouvé dans Ollama. Vérifiez que le modèle est installé avec 'ollama pull {LLM_MODEL}'"
            elif 'connection' in error_msg.lower() or 'refused' in error_msg.lower():
                error_msg = f"Impossible de se connecter à Ollama sur {OLLAMA_BASE_URL}. Assurez-vous qu'Ollama est démarré."
            
            logger.warning(f"[AGENT] Retour d'une décision sécurisée: NE PAS IRRIGUER")
            return {
                'decision': 'NE PAS IRRIGUER',
                'duree_minutes': 0,
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
        logger.info("[AGENT] Extraction fallback de la décision...")
        decision = 'NE PAS IRRIGUER'  # Par défaut, sécurité
        explication = response_text
        duree = 0
        
        # Essayer d'extraire le JSON même s'il est mal formaté
        # Chercher "decision" dans le texte
        import re
        
        # Chercher "decision": "IRRIGUER" ou "decision": "NE PAS IRRIGUER"
        decision_pattern = r'"decision"\s*:\s*"([^"]+)"'
        decision_match = re.search(decision_pattern, response_text, re.IGNORECASE)
        
        if decision_match:
            decision_found = decision_match.group(1).strip().upper()
            logger.info(f"[AGENT] Décision trouvée dans JSON: '{decision_found}'")
            
            if decision_found == 'IRRIGUER':
                decision = 'IRRIGUER'
            elif 'NE PAS IRRIGUER' in decision_found or 'NE_PAS_IRRIGUER' in decision_found:
                decision = 'NE PAS IRRIGUER'
            else:
                logger.warning(f"[AGENT] Décision inconnue: '{decision_found}', utilisation par défaut")
        else:
            # Si pas trouvé dans JSON, chercher dans le texte mais de manière plus précise
            # Chercher "NE PAS IRRIGUER" en premier (plus spécifique)
            if 'NE PAS IRRIGUER' in response_text.upper() or '"NE PAS IRRIGUER"' in response_text.upper():
                decision = 'NE PAS IRRIGUER'
                logger.info("[AGENT] Décision extraite du texte: NE PAS IRRIGUER")
            elif '"IRRIGUER"' in response_text.upper() or (response_text.upper().startswith('IRRIGUER') and 'NE PAS' not in response_text.upper()[:50]):
                # Vérifier que "IRRIGUER" n'est pas dans une explication négative
                # Chercher le contexte autour de "IRRIGUER"
                irriguer_pos = response_text.upper().find('IRRIGUER')
                if irriguer_pos != -1:
                    context_before = response_text[max(0, irriguer_pos-30):irriguer_pos].upper()
                    if 'NE PAS' not in context_before and 'NOT' not in context_before:
                        decision = 'IRRIGUER'
                        logger.info("[AGENT] Décision extraite du texte: IRRIGUER")
                    else:
                        decision = 'NE PAS IRRIGUER'
                        logger.info("[AGENT] 'IRRIGUER' trouvé mais dans un contexte négatif, décision: NE PAS IRRIGUER")
            else:
                logger.warning("[AGENT] Décision non trouvée clairement, utilisation par défaut sécurisée: NE PAS IRRIGUER")
        
        # Essayer d'extraire la durée aussi
        duree_pattern = r'"duree_minutes"\s*:\s*(\d+)'
        duree_match = re.search(duree_pattern, response_text, re.IGNORECASE)
        if duree_match:
            try:
                duree = int(duree_match.group(1))
                logger.info(f"[AGENT] Durée extraite du JSON: {duree} min")
            except ValueError:
                pass
        
        # Si décision = NE PAS IRRIGUER, durée doit être 0
        if decision == 'NE PAS IRRIGUER':
            duree = 0
        
        logger.info(f"[AGENT] Décision fallback finale: {decision}, Durée: {duree} min")
        
        return {
            'decision': decision,
            'duree_minutes': duree,
            'explication': explication
        }

