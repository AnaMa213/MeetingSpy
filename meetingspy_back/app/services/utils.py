import os

def clean_temp_directory(directory="temp"):
    """
    Supprime les fichiers dans le dossier 'temp' après utilisation.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
