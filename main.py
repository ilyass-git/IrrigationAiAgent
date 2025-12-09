"""
Point d'entrée principal pour l'application d'irrigation intelligente
"""
import sys
import os

# Ajouter le répertoire racine au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.app import app

if __name__ == '__main__':
    print("🌾 Démarrage du Système d'Irrigation Intelligent")
    print("=" * 50)
    print("Interface web disponible sur: http://localhost:5000")
    print("=" * 50)
    # Le code de démarrage est déjà dans web/app.py
    # On importe juste l'app pour que Flask puisse la démarrer
    app.run(debug=True, host='0.0.0.0', port=5000)







