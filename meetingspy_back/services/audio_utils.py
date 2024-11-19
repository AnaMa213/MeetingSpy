import ffmpeg
import os
from pydub import AudioSegment
def convert_to_wav(audio_path):
    """
    Convert an audio file to a WAV file using FFmpeg.

    Parameters
    ----------
    audio_path : str
        The path to the audio file to be converted.

    Returns
    -------
    str
        The path to the converted WAV file.
    """
    
    wav_path = os.path.splitext(audio_path)[0] + ".wav"
    if not audio_path.endswith(".wav"):
        ffmpeg.input(audio_path).output(wav_path).run()
    else:
        wav_path = audio_path
    return wav_path


def compress_wav(audio_path):
    """
    Compress an audio file by adjusting its sample rate, channels, and sample width.

    Parameters
    ----------
    audio_path : str
        The path to the WAV audio file to be compressed.

    Returns
    -------
    AudioSegment
        The compressed audio segment.
    """
    audio = AudioSegment.from_file(audio_path)

    # Appliquer la compression (modifier la fréquence d'échantillonnage, les canaux, et la largeur d'échantillon)
    compressed_audio = audio.set_frame_rate(22050).set_channels(1).set_sample_width(2)

    # Exporter le fichier compressé avec un débit binaire réduit
    compressed_audio.export(audio_path, format="wav", bitrate="64k")
    
    return audio_path

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

