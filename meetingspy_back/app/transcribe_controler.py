from flask import Blueprint, request, jsonify
from .services.diarization_service import diarize_audio
from .services.speech_to_text import transcribe_segments
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Renvoie la transcription d'un fichier audio en texte.
    
    Le fichier audio est attendu en tant que partie de la requête multipart/form-data
    sous le nom de champ `file`. Si le paramètre `num_speakers` est fourni, il est
    utilisé pour diariser le fichier audio avec PyAnnote.
    
    La réponse est un objet JSON contenant la clé `transcription` avec la
    transcription du fichier audio.
    
    Code d'erreur :
        400 : Erreur de format de la requête (par exemple, absence de fichier)
        404 : Fichier introuvable
    """
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Remplacer les espaces par des underscores dans le nom du fichier
    safe_filename = file.filename.replace(" ", "_")
    # Sauvegarder le fichier temporairement
    file_path = f"temp/{safe_filename}"
    os.makedirs("temp", exist_ok=True)  # Crée le dossier temporaire s'il n'existe pas
    file.save(file_path)

    # Récupérer le paramètre `num_speakers` s'il est fourni
    num_speakers = request.form.get('num_speakers')
    if num_speakers is not None:
        try:
            num_speakers = int(num_speakers)
        except ValueError:
            return jsonify({"error": "`num_speakers` must be an integer"}), 400

    try:
        # Étape 1 : Diarisation avec le paramètre num_speakers si disponible
        _, rttm_file_path = diarize_audio(file_path, num_speakers=num_speakers)

        # Étape 2 : Lire le fichier RTTM et transcrire les segments
        transcript = ""
        with open(rttm_file_path, "r", encoding="utf-8") as rttm:
            for line in rttm:
                parts = line.strip().split()
                start_time = float(parts[3])
                duration = float(parts[4])
                speaker = parts[7]
                end_time = start_time + duration

                # Transcrire chaque segment (à adapter avec un vrai modèle)
                segment_text = transcribe_segments(file_path, start_time, end_time)
                transcript += f"{speaker}: {segment_text}\n"

        # Supprimer les fichiers temporaires
        os.remove(file_path)
        os.remove(rttm_file_path)

        return jsonify({"transcription": transcript}), 200

    except FileNotFoundError as e:
        return jsonify({"error": f"File not found: {e}"}), 404
