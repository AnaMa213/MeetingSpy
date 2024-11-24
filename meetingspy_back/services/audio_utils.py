import os
import ffmpeg
import librosa
import torch
import torchaudio
import scipy.signal as signal
from pathlib import Path
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import normalize, high_pass_filter, low_pass_filter
from demucs.pretrained import get_model
from demucs.apply import apply_model


def preprocess_audio(input_path):
    """
    Convertit, prétraite et optimise un fichier audio pour la diarisation.

    La prétraitement implique les étapes suivantes :
    1. Charger et convertir en 16 kHz mono.
    2. Réduction de bruit.
    3. Egalisation et normalisation.
    4. Exporter le fichier final.

    Args:
        input_path (str): Chemin vers le fichier audio d'entrée.
        output_path (str): Chemin vers le fichier audio de sortie.
    """
    # Créer les répertoires temporaires si nécessaires
    temp_dir = "tmp/preprocessed"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "preprocessed_audio.wav")
    output_dir = "tmp/preprocessed/preprocessed_audio.wav"

    # Étape 1 : Charger et convertir en 16 kHz mono
    audio, sr = librosa.load(input_path, sr=16000, mono=True)
    print(f"Chargement et conversion : Taux d'échantillonnage {sr}, Mono")

    # Étape 2 : Réduction de bruit
    print("Réduction de bruit...")
    noise_sample = audio[:sr * 2]  # Prendre les 2 premières secondes pour capturer le bruit
    reduced_audio = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample, prop_decrease=0.8, time_mask_smooth_ms=100)

    # Étape 3 : Sauvegarder l'audio réduit
    sf.write(temp_file, reduced_audio, sr)
    print(f"Réduction de bruit terminée. Fichier sauvegardé temporairement : {temp_file}")

    # # Étape 4 : Charger l'audio pour égalisation et normalisation
    # new_audio, new_sr = librosa.load(temp_file, sr=16000, mono=True)

    # # Étape 5 : Egalisation
    # print("Application de l'égalisation...")
    # boosted_audio = boost_frequencies(new_audio, new_sr, low_cutoff=125, high_cutoff=400, gain=6)
    # sf.write(temp_file, boosted_audio, new_sr)

    # # Étape 6 : Normalisation et filtrage fréquentiel avec PyDub
    # audio_segment = AudioSegment.from_file(temp_file)
    # audio_segment = high_pass_filter(audio_segment, cutoff=85)
    # audio_segment = low_pass_filter(audio_segment, cutoff=3000)
    # audio_segment = normalize(audio_segment)

    # # Étape 7 : Exporter le fichier final
    # audio_segment.export(output_dir, format="wav")
    # print(f"Prétraitement terminé. Fichier sauvegardé : {output_dir}")

    # Afficher les informations du fichier traité
    duration = librosa.get_duration(y=audio, sr=sr)
    channels = 1 if audio.ndim == 1 else audio.shape[0]
    print(f"Taux d'échantillonnage final : {sr} Hz")
    print(f"Durée : {duration:.2f} secondes")
    print(f"Canaux : {channels} (1=mono, >1=stéréo)")

    return output_dir


def separate_vocals(input_audio, output_dir):
    """
    Sépare les voix et la musique d'un fichier audio en utilisant Demucs.
    
    Args:
        input_audio (str): Chemin vers le fichier audio d'entrée.
        output_dir (str): Répertoire de sortie où les fichiers séparés seront sauvegardés.
    """
    # Charger le modèle Demucs
    model = get_model(name="htdemucs")

    # Charger l'audio avec torchaudio
    wav, sr = torchaudio.load(input_audio)

    # Appliquer le modèle pour séparer les voix et la musique
    sources = apply_model(model, wav, device="cuda" if torch.cuda.is_available() else "cpu")

    # Sauvegarder les fichiers séparés
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    torchaudio.save(f"{output_dir}/vocals.wav", sources[0], sample_rate=sr)  # Voix

def convert_to_wav(audio_path):
    """
    Convert an audio file to a WAV file with a sample rate of 16 kHz and mono using FFmpeg.

    Parameters
    ----------
    audio_path : str
        The path to the audio file to be converted.

    Returns
    -------
    str
        The path to the converted WAV file.
    """
    wav_path = os.path.splitext(audio_path)[0] + "_16000_mono.wav"  # Nom du fichier converti
    if not audio_path.endswith(".wav") or not is_16000_mono(audio_path):
        (
            ffmpeg
            .input(audio_path)
            .output(wav_path, ar=16000, ac=1, format="wav")  # Conversion en 16 kHz mono
            .overwrite_output()  # Écrase les fichiers existants sans demander confirmation
            .run()
        )
    else:
        wav_path = audio_path  # Si le fichier est déjà en 16 kHz mono, on le retourne tel quel
    return wav_path

def is_16000_mono(audio_path):
    """
    Check if an audio file is already in 16 kHz and mono.

    Parameters
    ----------
    audio_path : str
        Path to the audio file.

    Returns
    -------
    bool
        True if the audio file is in 16 kHz and mono, False otherwise.
    """
    try:
        probe = ffmpeg.probe(audio_path)
        streams = probe.get('streams', [])
        for stream in streams:
            if stream.get('codec_type') == 'audio':
                sample_rate = int(stream.get('sample_rate', 0))
                channels = int(stream.get('channels', 0))
                return sample_rate == 16000 and channels == 1
        return False
    except ffmpeg.Error as e:
        print(f"Erreur lors de la vérification du fichier audio : {e}")
        return False

def boost_frequencies(audio, sr, low_cutoff=125, high_cutoff=400, gain=6):
    """
    Accentue les fréquences entre `low_cutoff` et `high_cutoff` avec un gain spécifié.
    
    Args:
        audio (numpy.ndarray): Signal audio.
        sr (int): Fréquence d'échantillonnage.
        low_cutoff (float): Fréquence minimale (Hz).
        high_cutoff (float): Fréquence maximale (Hz).
        gain (float): Gain en décibels.
    
    Returns:
        numpy.ndarray: Signal audio avec boost des fréquences.
    """
    # Conception du filtre passe-bande
    nyquist = 0.5 * sr
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist
    b, a = signal.butter(2, [low, high], btype="band")

    # Filtrage du signal
    filtered_audio = signal.lfilter(b, a, audio)

    # Appliquer le gain
    gain_factor = 10 ** (gain / 20)  # Convertir le gain dB en facteur linéaire
    boosted_audio = filtered_audio * gain_factor

    return boosted_audio

def get_audio_segment(diarization):
    """
    Extract audio segments from an audio file based on RTTM file information.

    Parameters
    ----------
    audio_path : str
        The path to the audio file from which segments will be extracted.
    rttm_path : str
        The path to the RTTM file containing segment information.

    Returns
    -------
    list of tuple
        A list of tuples where each tuple contains an audio segment and the corresponding speaker ID.
    """
    segments = []
    try:
        # Construire la liste des segments à partir de la sortie du pipeline
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la diarisation : {e}") from e
    
    return segments

