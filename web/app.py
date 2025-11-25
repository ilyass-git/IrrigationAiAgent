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

# Scheduler pour les décisions automatiques
scheduler = BackgroundScheduler()
scheduler.start()


def automatic_decision_task():
    """Tâche automatique pour prendre une décision d'irrigation"""
    global last_decision
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
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
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
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
    return jsonify({
        'success': True,
        'data': last_decision
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
            'auto_scheduler_running': scheduler.running
        }
    })


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


if __name__ == '__main__':
    # Prendre une décision initiale au démarrage
    try:
        result = decision_engine.make_irrigation_decision()
        last_decision = result
    except Exception as e:
        print(f"Erreur lors de la décision initiale : {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

