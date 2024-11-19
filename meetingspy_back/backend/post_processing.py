def merge_close_segments(diarization_result, threshold=0.5):
    """
    Fusionne les segments qui sont suffisamment proches (moins de `threshold` secondes d'intervalle).

    Args:
        diarization_result (list): Liste des segments de type [{'start': ..., 'end': ..., 'speaker': ...}, ...].
        threshold (float): Seuil pour fusionner les segments (en secondes).

    Returns:
        list: Liste des segments fusionnés avec un champ 'ordre' indiquant l'ordre d'apparition, basé sur le temps de début.
    """
    merged_segments = []
    if not diarization_result:
        return merged_segments  # Retourner une liste vide si aucun résultat

    # Trier les segments par temps de début
    diarization_result.sort(key=lambda x: x['start'])

    # Initialiser la fusion avec le premier segment
    current_segment = diarization_result[0]

    for segment in diarization_result[1:]:
        start, end, label = segment['start'], segment['end'], segment['speaker']
        current_start, current_end, current_label = current_segment['start'], current_segment['end'], current_segment['speaker']

        # Si les segments sont suffisamment proches et ont le même label, les fusionner
        if start - current_end <= threshold and current_label == label:
            current_segment = {
                'start': current_start,
                'end': max(current_end, end),
                'speaker': current_label
            }
        else:
            # Ajouter le segment actuel à la liste fusionnée
            merged_segments.append(current_segment)
            current_segment = segment

    # Ajouter le dernier segment
    merged_segments.append(current_segment)

    # Ajouter le champ 'ordre' basé sur le tri par temps de début
    merged_segments.sort(key=lambda x: x['start'])
    for ordre, segment in enumerate(merged_segments, start=1):
        segment['ordre'] = ordre

    # Afficher l'ordre final des valeurs de 'start'
    print("Ordre final des valeurs de 'start':")
    for segment in merged_segments:
        print(f"ordre: {segment['ordre']}, start: {segment['start']}")

    return merged_segments


def generate_combined_transcriptions(transcriptions_list):
    """
    Combine toutes les transcriptions de plusieurs sources et les trie par temps de début.

    Args:
        transcriptions_list (list): Liste contenant les transcriptions de chaque source.
                                    Chaque élément est une liste de segments [{'start': ..., 'end': ..., 'speaker': ..., 'text': ...}, ...]

    Returns:
        str: Le texte du dialogue combiné et ordonné.
    """
    try:
        # Fusionner toutes les transcriptions en une seule liste
        combined_transcriptions = []
        print("Combinaison des transcriptions initiales...")

        # Vérifier le contenu de transcriptions_list
        print("Contenu de transcriptions_list avant combinaison:")
        for idx, transcription in enumerate(transcriptions_list):
            print(f"Transcription {idx}: type: {type(transcription)}, valeur: {transcription}")

        for transcriptions in transcriptions_list:
            if isinstance(transcriptions, list):
                combined_transcriptions.extend(transcriptions)
            else:
                print(f"Erreur: Élément de transcriptions_list n'est pas une liste. Type: {type(transcriptions)}, valeur: {transcriptions}")
                raise TypeError("Chaque élément de transcriptions_list doit être une liste.")

        # Vérifier le contenu après combinaison
        print("Contenu de combined_transcriptions après combinaison:")
        for idx, transcription in enumerate(combined_transcriptions):
            print(f"Segment {idx}: type: {type(transcription)}, valeur: {transcription}")

        # Trier toutes les transcriptions par temps de début
        print("Tri des transcriptions par temps de début...")
        combined_transcriptions.sort(key=lambda x: x['start'])
        
        # Générer le texte ordonné du dialogue
        dialogue_text = []
        print("Génération du texte ordonné...")
        for idx, segment in enumerate(combined_transcriptions):
            try:
                if isinstance(segment, dict) and 'speaker' in segment and 'text' in segment:
                    speaker = segment['speaker']
                    text = segment['text']
                    dialogue_text.append(f"{speaker}: {text}")
                    print(f"Segment ajouté: {speaker}: {text}")
                else:
                    print(f"Erreur: Segment non valide à l'index {idx}. Type: {type(segment)}, valeur: {segment}")
                    raise ValueError("Chaque segment doit être un dictionnaire contenant les clés 'speaker' et 'text'.")
            except Exception as e:
                print(f"Erreur inattendue lors du traitement du segment à l'index {idx}: {e}")
                raise

        # Afficher l'ordre final des valeurs de 'start'
        print("Ordre final des valeurs de 'start' pour toutes les transcriptions combinées:")
        for segment in combined_transcriptions:
            if isinstance(segment, dict) and 'start' in segment:
                print(f"start: {segment['start']}, speaker: {segment['speaker']}")
            else:
                print(f"Erreur: Segment sans clé 'start'. Type: {type(segment)}, valeur: {segment}")

        return "\n".join(dialogue_text)

    except TypeError as e:
        print(f"TypeError: {e}")
        raise
    except KeyError as e:
        print(f"KeyError: Clé manquante {e}")
        raise
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        raise

