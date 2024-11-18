import whisper


class AudioTranscriber:
    def __init__(self, model_name="small"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, file_path, language="fr"):
        """
        Transcrit un fichier audio en texte.
        :param file_path: Chemin du fichier audio.
        :param language: Langue du fichier audio.
        :return: Texte transcrit.
        """
        try:
            print(f"Transcription du fichier : {file_path}")
            result = self.model.transcribe(file_path, language=language)
            print("Transcription terminée.")
            return result["text"]
        except Exception as e:
            print(f"Erreur lors de la transcription : {e}")
            return None
