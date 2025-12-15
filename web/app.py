"""
Interface web Flask pour le système d'irrigation intelligent
"""
from flask import Flask, render_template, jsonify, request
from app.decision_engine import DecisionEngine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'irrigation-ai-secret-key-2024'

# Instance du moteur de décision
decision_engine = DecisionEngine()

# Stockage de la dernière décision
last_decision = {
    'decision': 'NE PAS IRRIGUER',
    'explication': 'Aucune décision prise pour le moment',
    'timestamp': None,
    'metadata': {}
}

# État de la pompe
pump_state = {
    'running': False,
    'started_at': None,
    'stop_at': None,
    'stopped_at': None,
    'duration_minutes': 0,
    'stop_reason': None
}

# Scheduler pour les décisions automatiques
scheduler = BackgroundScheduler()
scheduler.start()


def automatic_decision_task():
    """Tâche automatique pour prendre une décision d'irrigation"""
    global last_decision, pump_state
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
        
        # Gérer la pompe selon la décision (comme pour la décision manuelle)
        if result['decision'] == 'IRRIGUER' and result.get('duration_minutes', 0) > 0:
            start_pump(result['duration_minutes'])
        elif result['decision'] == 'NE PAS IRRIGUER':
            if pump_state['running']:
                _stop_pump_internal('decision_no_irrigate')
        
        print(f"[AUTO] Décision prise à {datetime.datetime.now()}: {result['decision']}")
    except Exception as e:
        print(f"[AUTO] Erreur lors de la prise de décision automatique : {e}")


@app.route('/')
def index():
    """Page principale de l'interface"""
    return render_template('index.html')


@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Démarre le scheduler automatique"""
    try:
        data = request.get_json() or {}
        interval_hours = data.get('interval_hours', 6)
        
        # Supprimer les jobs existants
        scheduler.remove_all_jobs()
        
        # Ajouter le nouveau job
        scheduler.add_job(
            func=automatic_decision_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id='irrigation_decision',
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
        scheduler.remove_all_jobs()
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
    jobs = scheduler.get_jobs()
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


@app.route('/api/reviews', methods=['POST'])
def add_review():
    """Ajoute un review d'expert"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Données manquantes'
            }), 400
        
        # Extraire les données du review
        review_data = {
            'decision_id': data.get('decision_id'),
            'decision': data.get('decision', ''),
            'decision_timestamp': data.get('decision_timestamp'),
            'expert_name': data.get('expert_name', 'Expert anonyme'),
            'stars': int(data.get('stars', 0)),
            'comment': data.get('comment', '')
        }
        
        # Valider les données
        if not review_data['decision_id']:
            return jsonify({
                'success': False,
                'error': 'decision_id est requis'
            }), 400
        
        if review_data['stars'] < 1 or review_data['stars'] > 5:
            return jsonify({
                'success': False,
                'error': 'La note doit être entre 1 et 5'
            }), 400
        
        # Ajouter le review via le decision engine
        review = decision_engine.add_review(review_data)
        
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
    """Récupère les reviews récents"""
    try:
        limit = request.args.get('limit', 10, type=int)
        reviews_data = decision_engine.get_recent_reviews(limit=limit)
        
        return jsonify({
            'success': True,
            'data': reviews_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/pump/stop', methods=['POST'])
def stop_pump():
    """Arrête la pompe manuellement"""
    global pump_state
    try:
        if not pump_state['running']:
            return jsonify({
                'success': False,
                'error': 'La pompe n\'est pas en marche'
            }), 400
        
        # Arrêter la pompe
        _stop_pump_internal('manual_stop')
        
        return jsonify({
            'success': True,
            'data': pump_state,
            'message': 'Pompe arrêtée avec succès'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _stop_pump_internal(reason: str = 'manual_stop'):
    """Fonction interne pour arrêter la pompe"""
    global pump_state
    pump_state['running'] = False
    pump_state['stopped_at'] = datetime.datetime.now().isoformat()
    pump_state['stop_reason'] = reason
    
    # Annuler le job d'arrêt automatique s'il existe
    try:
        scheduler.remove_job('pump_auto_stop')
    except:
        pass


def start_pump(duration_minutes: int):
    """Démarre la pompe pour une durée donnée"""
    global pump_state
    
    # Arrêter la pompe si elle est déjà en marche
    if pump_state['running']:
        _stop_pump_internal('restart')
    
    # Démarrer la pompe
    now = datetime.datetime.now()
    stop_time = now + datetime.timedelta(minutes=duration_minutes)
    
    pump_state = {
        'running': True,
        'started_at': now.isoformat(),
        'stop_at': stop_time.isoformat(),
        'stopped_at': None,
        'duration_minutes': duration_minutes,
        'stop_reason': None
    }
    
    # Programmer l'arrêt automatique
    scheduler.add_job(
        func=stop_pump_auto,
        trigger='date',
        run_date=stop_time,
        id='pump_auto_stop',
        replace_existing=True
    )


def stop_pump_auto():
    """Arrête la pompe automatiquement après la durée programmée"""
    global pump_state
    pump_state['running'] = False
    pump_state['stopped_at'] = datetime.datetime.now().isoformat()
    pump_state['stop_reason'] = 'auto_stop'
    print(f"[PUMP] Pompe arrêtée automatiquement à {pump_state['stopped_at']}")


@app.route('/api/decision', methods=['POST'])
def make_decision():
    """Endpoint pour déclencher manuellement une décision"""
    global last_decision, pump_state
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
        
        # Gérer la pompe selon la décision
        if result['decision'] == 'IRRIGUER' and result.get('duration_minutes', 0) > 0:
            start_pump(result['duration_minutes'])
        elif result['decision'] == 'NE PAS IRRIGUER':
            if pump_state['running']:
                _stop_pump_internal('decision_no_irrigate')
        
        # Ajouter l'état de la pompe à la réponse
        result['pump_state'] = pump_state
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decision/last', methods=['GET'])
def get_last_decision():
    """Récupère la dernière décision prise"""
    # Ajouter l'état de la pompe à la réponse
    response_data = last_decision.copy()
    response_data['pump_state'] = pump_state
    return jsonify({
        'success': True,
        'data': response_data
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Récupère le statut du système"""
    status = decision_engine.get_system_status()
    return jsonify({
        'success': True,
        'data': {
            **status,
            'last_decision': last_decision,
            'auto_scheduler_running': scheduler.running,
            'pump_state': pump_state
        }
    })


if __name__ == '__main__':
    # Prendre une décision initiale au démarrage
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
    except Exception as e:
        print(f"Erreur lors de la décision initiale : {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

