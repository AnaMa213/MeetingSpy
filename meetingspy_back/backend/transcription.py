import spacy

def assign_speaker_name(dialogue):
    """
    Assign a name to each speaker in a dialogue.

    Parameters
    ----------
    dialogue : str
        The dialogue to be processed. It should be a string with each line containing the
        speaker's number and the dialogue. For example:

        SPEAKER 1 00:00:00,000 --> 00:00:00,000
        Hello, how are you?
        SPEAKER 2 00:00:00,000 --> 00:00:00,000
        I am fine, thank you.

    Returns
    -------
    None
    """
    
    nlp = spacy.load('fr_core_news_lg')

    # Split into lines
    lines = dialogue.strip().split("\n")

    # Initialize speaker names dictionary
    speaker_dict = {}

    for i in range(0, len(lines), 2):
        speaker_line = lines[i]
        dialogue_line = lines[i+1]

        # Get speaker number from the speaker line
        speaker_number = speaker_line.split()[1]

        # Perform NER on the dialogue line
        doc = nlp(dialogue_line)
        names = [ent.text for ent in doc.ents if ent.label_ == 'NOM']

        # If there are names in the dialogue line, use the last one as the speaker's name
        if names:
            speaker_dict[speaker_number] = names[-1]

        # Get speaker's name from the dictionary, or use the speaker number if the name is not known
        speaker_name = speaker_dict.get(speaker_number, f"Locuteur {speaker_number}")

        # Print the dialogue line with the speaker's name
        print(f"{speaker_name} {speaker_number} {speaker_line.split()[2]}")
        print(dialogue_line)


def transcript_to_dictionary(dialogue):
    
    """
    Split a dialogue transcript into a dictionary with speaker names as keys and their transcripts as values.

    Parameters
    ----------
    dialogue : str
        The dialogue transcript to split.

    Returns
    -------
    dict
        A dictionary with the speaker names as keys and their transcripts as values.
    """
    
    lines = dialogue.splitlines()

    # Initialize the dictionary
    dictionary = {}

    # Iterate through the lines and construct the dictionary
    for i in range(0, len(lines), 2):
        name_line = lines[i]
        text_line = lines[i + 1]

        # Extract name and text
        name = name_line.split()[0]
        text = text_line

        # Add to the dictionary
        dictionary[name] = text

    return dictionary