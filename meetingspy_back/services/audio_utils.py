import ffmpeg
import os

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

