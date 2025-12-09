"""
Point d'entrée principal pour l'application d'irrigation intelligente
"""
from web.app import app

if __name__ == '__main__':
    print("🌾 Démarrage du Système d'Irrigation Intelligent")
    print("=" * 50)
    print("Interface web disponible sur: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)







