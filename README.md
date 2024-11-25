# MeetingSpy

## Description
MeetingSpy est un outil innovant conçu pour analyser et traiter les enregistrements audio de réunions. Grâce à une combinaison de techniques avancées de traitement du signal et de machine learning, il propose des fonctionnalités telles que la diarisation des locuteurs et des services d'analyse audio. MeetingSpy est idéal pour ceux qui souhaitent automatiser la transcription, identifier les locuteurs, et obtenir des informations exploitables à partir de réunions.

## Fonctionnalités
- **Diarisation des locuteurs** : Identification des différents participants dans un enregistrement audio pour comprendre qui parle et quand.
- **Transcription** : Conversion des enregistrements audio en texte, facilitant la documentation et la recherche de contenu spécifique.
- **Analyse audio avancée** : Extraction de caractéristiques audio et analyse des patterns de parole pour générer des insights.
- **Gestion centralisée des logs** : Utilisation d'une configuration standardisée pour le suivi des événements, facilitant le débogage et la maintenance.
- **Services utilitaires** : Outils pour manipuler, nettoyer, et analyser les fichiers audio, tels que la réduction du bruit et l'amélioration de la qualité sonore.

## Prérequis
- Python 3.9+
- `pip` pour la gestion des dépendances

## Installation
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-repo/MeetingSpy.git
   cd MeetingSpy
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv env
   source env/bin/activate  # Sur Windows, utilisez `env\Scripts\activate`
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
1. Lancez le serveur API avec Uvicorn :
   ```bash
   uvicorn app.main:app --reload
   ```
   Cela démarrera le serveur à l'adresse `http://127.0.0.1:8000`, où vous pourrez interagir avec l'API.

2. Accédez à la documentation interactive de l'API (Swagger UI) :
   - Rendez-vous sur `http://127.0.0.1:8000/docs` pour explorer les endpoints disponibles.

## Configuration
- **Fichier `.env`** : Utilisez le fichier `.env` pour spécifier les configurations telles que les clés API ou les paramètres de base de données.
  - Exemple :
    ```
    SECRET_KEY=your_secret_key_here
    DATABASE_URL=your_database_url_here
    ```

## Dépendances
Voici les principales bibliothèques utilisées dans ce projet :
- **FastAPI** : Pour la création de l'API REST.
- **Uvicorn** : Serveur ASGI pour lancer l'application.
- **Pydantic** : Pour la validation des données.
- **Librosa** : Bibliothèque pour l'analyse et le traitement des fichiers audio.
- **Python-dotenv** : Pour charger les variables d'environnement depuis un fichier `.env`.

## Tests
- Les tests unitaires sont gérés avec **pytest**. Pour lancer les tests, utilisez la commande :
  ```bash
  pytest
  ```

## Contribution
Les contributions sont les bienvenues ! Veuillez créer une pull request ou ouvrir une issue pour toute suggestion d'amélioration.

## Licence
Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus de détails.

## Auteur
- Votre Nom - [Votre Profil GitHub](https://github.com/votre-profil)

## Notes supplémentaires
- Assurez-vous que vos enregistrements audio sont de bonne qualité pour obtenir des résultats optimaux lors de l'analyse.
- L'API supporte actuellement les formats audio courants tels que `.wav` et `.mp3`.
