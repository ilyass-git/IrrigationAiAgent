"""
Script de test pour lancer une décision et voir les logs
"""
import sys
import logging
from app.decision_engine import DecisionEngine

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("TEST DE DÉCISION D'IRRIGATION")
    logger.info("=" * 80)
    
    try:
        # Créer le moteur de décision
        engine = DecisionEngine()
        
        # Prendre une décision
        logger.info("\n🚀 Lancement de la prise de décision...\n")
        result = engine.make_irrigation_decision()
        
        # Afficher le résultat
        logger.info("\n" + "=" * 80)
        logger.info("RÉSULTAT DE LA DÉCISION")
        logger.info("=" * 80)
        logger.info(f"ID: {result['id']}")
        logger.info(f"Décision: {result['decision']}")
        logger.info(f"Durée: {result['duration_minutes']} minutes")
        logger.info(f"Timestamp: {result['timestamp']}")
        logger.info(f"Explication: {result['explication']}")
        logger.info("=" * 80)
        
        # Vérification de la cohérence
        if result['decision'] == 'NE PAS IRRIGUER' and result['duration_minutes'] > 0:
            logger.error("⚠️ PROBLÈME DÉTECTÉ: Décision = NE PAS IRRIGUER mais durée > 0 !")
            return 1
        elif result['decision'] == 'IRRIGUER' and result['duration_minutes'] == 0:
            logger.warning("⚠️ ATTENTION: Décision = IRRIGUER mais durée = 0")
        
        logger.info("✅ Test terminé avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())


