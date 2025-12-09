"""
Interface web Flask pour le système d'irrigation intelligent
"""
from flask import Flask, render_template, jsonify, request
from app.decision_engine import DecisionEngine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from typing import Dict
import datetime
import json
import time
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'irrigation-ai-secret-key-2024'

# Instance du moteur de décision
decision_engine = DecisionEngine()

IRRIGATION_JOB_ID = 'irrigation_decision'
PUMP_STOP_JOB_ID = 'pump_auto_stop'

# Stockage de la dernière décision
last_decision = {
    'id': None,
    'decision': 'NE PAS IRRIGUER',
    'duration_minutes': 0,
    'explication': 'Aucune décision prise pour le moment',
    'timestamp': None,
    'metadata': {}
}

# État simulé de la pompe
pump_state = {
    'running': False,
    'started_at': None,
    'stop_at': None,
    'stopped_at': None,
    'decision_id': None,
    'duration_minutes': 0,
    'stop_reason': None
}

# Scheduler pour les décisions automatiques et les arrêts de pompe
scheduler = BackgroundScheduler()
scheduler.start()


def _cancel_job(job_id: str) -> None:
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        pass


def stop_pump(reason: str = 'manual'):
    global pump_state
    logger.info(f"[POMPE] Arrêt demandé - Raison: {reason}")
    logger.info(f"[POMPE] État avant arrêt: running={pump_state.get('running')}, decision_id={pump_state.get('decision_id')}")
    pump_state.update({
        'running': False,
        'stop_reason': reason,
        'duration_minutes': 0,
        'decision_id': None,
        'started_at': None,
        'stop_at': None,
        'stopped_at': datetime.datetime.now().isoformat()
    })
    _cancel_job(PUMP_STOP_JOB_ID)
    logger.info(f"[POMPE] Arrêt effectué - État final: running={pump_state.get('running')}")


def stop_pump_task():
    stop_pump(reason='auto_stop')


def start_pump(decision_id: str, duration_minutes: int):
    global pump_state
    logger.info(f"[POMPE] Démarrage demandé - Decision ID: {decision_id}, Durée: {duration_minutes} min")
    
    # Arrêter la pompe si elle est déjà en marche
    if pump_state.get('running', False):
        logger.warning(f"[POMPE] Pompe déjà en marche, arrêt avant nouveau démarrage")
        stop_pump(reason='restart')
    
    if duration_minutes <= 0:
        logger.warning(f"[POMPE] Durée invalide ({duration_minutes} min), arrêt de la pompe")
        stop_pump(reason='no_duration')
        return
    
    now = datetime.datetime.now()
    stop_time = now + datetime.timedelta(minutes=duration_minutes)
    pump_state.update({
        'running': True,
        'started_at': now.isoformat(),
        'stop_at': stop_time.isoformat(),
        'stopped_at': None,
        'decision_id': decision_id,
        'duration_minutes': duration_minutes,
        'stop_reason': None
    })
    logger.info(f"[POMPE] Démarrage effectué - Durée: {duration_minutes} min, Arrêt prévu: {stop_time}")
    scheduler.add_job(
        func=stop_pump_task,
        trigger='date',
        run_date=stop_time,
        id=PUMP_STOP_JOB_ID,
        replace_existing=True
    )
    logger.info(f"[POMPE] Job d'arrêt automatique programmé pour {stop_time}")


def apply_pump_state_from_decision(decision: Dict):
    logger.info("=" * 60)
    logger.info("[POMPE] Application de l'état depuis la décision")
    logger.info(f"[POMPE] Décision complète reçue: {json.dumps(decision, indent=2, ensure_ascii=False)}")
    
    if not decision:
        logger.warning("[POMPE] Aucune décision fournie, arrêt de la pompe")
        stop_pump(reason='no_decision')
        return
    
    decision_id = decision.get('id')
    decision_type = decision.get('decision', '')
    duration = int(decision.get('duration_minutes', 0) or 0)
    
    logger.info(f"[POMPE] Analyse - Decision ID: {decision_id}")
    logger.info(f"[POMPE] Analyse - Type de décision: '{decision_type}'")
    logger.info(f"[POMPE] Analyse - Durée: {duration} min")
    logger.info(f"[POMPE] Analyse - État actuel de la pompe: running={pump_state.get('running')}")
    
    # Vérification stricte : IRRIGUER ET durée > 0
    should_start = (decision_type == 'IRRIGUER' and duration > 0)
    logger.info(f"[POMPE] Décision de démarrage: {should_start} (IRRIGUER={decision_type == 'IRRIGUER'}, duration>0={duration > 0})")
    
    if should_start:
        logger.info(f"[POMPE] ✅ DÉMARRAGE de la pompe - Decision: {decision_type}, Durée: {duration} min")
        start_pump(decision_id, duration)
    else:
        logger.info(f"[POMPE] ❌ ARRÊT de la pompe - Raison: decision_type='{decision_type}', duration={duration}")
        stop_pump(reason='decision_stop')
    
    logger.info(f"[POMPE] État final de la pompe: running={pump_state.get('running')}, decision_id={pump_state.get('decision_id')}")
    logger.info("=" * 60)


def automatic_decision_task():
    """Tâche automatique pour prendre une décision d'irrigation"""
    global last_decision
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
        apply_pump_state_from_decision(last_decision)
        print(f"[AUTO] Décision prise à {datetime.datetime.now()}: {result['decision']}")
    except Exception as e:
        print(f"[AUTO] Erreur lors de la prise de décision automatique : {e}")


@app.route('/')
def index():
    """Page principale de l'interface"""
    return render_template('index.html')


@app.route('/api/decision', methods=['POST'])
def make_decision():
    """Endpoint pour déclencher manuellement une décision"""
    global last_decision
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("[API] Début de la prise de décision manuelle")
    
    try:
        logger.info("[API] Appel à decision_engine.make_irrigation_decision()...")
        step_start = time.time()
        result = decision_engine.make_irrigation_decision()
        step_duration = time.time() - step_start
        logger.info(f"[API] Décision prise en {step_duration:.2f} secondes")
        
        logger.info(f"[API] Résultat de la décision: {json.dumps(result, indent=2, ensure_ascii=False)}")
        last_decision = result
        
        logger.info("[API] Application de l'état de la pompe...")
        apply_pump_state_from_decision(last_decision)
        
        total_duration = time.time() - start_time
        logger.info(f"[API] Décision complète terminée en {total_duration:.2f} secondes")
        logger.info("=" * 60)
        
        return jsonify({
            'success': True,
            'data': {
                **result,
                'pump_state': pump_state  # Inclure l'état de la pompe
            }
        })
    except Exception as e:
        total_duration = time.time() - start_time
        logger.error(f"[API] Erreur après {total_duration:.2f} secondes: {str(e)}", exc_info=True)
        logger.info("=" * 60)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decision/last', methods=['GET'])
def get_last_decision():
    """Récupère la dernière décision prise"""
    return jsonify({
        'success': True,
        'data': {
            **last_decision,
            'pump_state': pump_state  # Inclure l'état de la pompe
        }
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Récupère le statut du système"""
    status = decision_engine.get_system_status()
    
    # Ajouter les alertes des capteurs si disponibles
    sensor_alerts = []
    if 'current_sensors' in status and status.get('current_sensors', {}).get('available', False):
        from app.sensor_data_loader import SensorDataLoader
        from config import SENSOR_CSV_DATA_PATH
        sensor_loader = SensorDataLoader(SENSOR_CSV_DATA_PATH)
        sensor_alerts = sensor_loader.get_sensor_alerts()
    recent_reviews = status.get('recent_reviews', [])
    
    return jsonify({
        'success': True,
        'data': {
            **status,
            'last_decision': last_decision,
            'auto_scheduler_running': scheduler.running,
            'sensor_alerts': sensor_alerts,
            'recent_reviews': recent_reviews,
            'pump_state': pump_state
        }
    })


@app.route('/api/reviews', methods=['POST'])
def submit_review():
    """Enregistre un avis d'expert pour la dernière décision."""
    data = request.get_json() or {}
    decision_id = data.get('decision_id') or last_decision.get('id')
    decision_text = data.get('decision') or last_decision.get('decision')
    decision_timestamp = data.get('decision_timestamp') or last_decision.get('timestamp')
    expert_name = data.get('expert_name', '').strip() or 'Expert'
    comment = data.get('comment', '').strip()

    try:
        stars = int(data.get('stars', 0))
    except (TypeError, ValueError):
        stars = 0

    if not decision_id or not decision_timestamp:
        return jsonify({
            'success': False,
            'error': "Aucune décision récente à évaluer."
        }), 400

    if stars < 1 or stars > 5:
        return jsonify({
            'success': False,
            'error': "La note doit être comprise entre 1 et 5 étoiles."
        }), 400

    try:
        review_payload = {
            'decision_id': decision_id,
            'decision': decision_text,
            'decision_timestamp': decision_timestamp,
            'expert_name': expert_name,
            'stars': stars,
            'comment': comment
        }
        review = decision_engine.add_review(review_payload)
        return jsonify({
            'success': True,
            'data': review
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reviews/recent', methods=['GET'])
def get_recent_reviews():
    """Retourne les revues récentes et statistiques."""
    data = decision_engine.get_recent_reviews(limit=5)
    return jsonify({
        'success': True,
        'data': data
    })


@app.route('/api/pump/stop', methods=['POST'])
def api_stop_pump():
    """Arrête manuellement la pompe."""
    stop_pump(reason='manual_api')
    return jsonify({
        'success': True,
        'data': pump_state
    })


@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Démarre le scheduler automatique"""
    try:
        data = request.get_json() or {}
        interval_hours = data.get('interval_hours', 6)
        
        # Supprimer le job automatique précédent
        _cancel_job(IRRIGATION_JOB_ID)
        
        # Ajouter le nouveau job
        scheduler.add_job(
            func=automatic_decision_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id=IRRIGATION_JOB_ID,
            name='Décision d\'irrigation automatique',
            replace_existing=True
        )
        
        return jsonify({
            'success': True,
            'message': f'Scheduler démarré avec un intervalle de {interval_hours} heures'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Arrête le scheduler automatique"""
    try:
        _cancel_job(IRRIGATION_JOB_ID)
        return jsonify({
            'success': True,
            'message': 'Scheduler arrêté'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Récupère le statut du scheduler"""
    jobs = []
    auto_job = scheduler.get_job(IRRIGATION_JOB_ID)
    if auto_job:
        jobs.append(auto_job)
    return jsonify({
        'success': True,
        'data': {
            'running': scheduler.running,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    })


if __name__ == '__main__':
    # Prendre une décision initiale au démarrage
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
        apply_pump_state_from_decision(last_decision)
    except Exception as e:
        print(f"Erreur lors de la décision initiale : {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


