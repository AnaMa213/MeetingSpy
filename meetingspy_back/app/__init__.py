from flask import Flask    
from .transcribe_controler import api_bp # Importer les routes
import os

def create_app():
    app = Flask(__name__)

    # Créer le dossier temporaire pour stocker les fichiers audio si nécessaire
    if not os.path.exists('temp'):
        os.makedirs('temp')


    app.register_blueprint(api_bp, url_prefix='/api')

    return app
