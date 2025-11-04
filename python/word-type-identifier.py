import spacy

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Function to identify word types
def identify_word_types(sentence):
    # Process the sentence with spaCy
    doc = nlp(sentence)
    # Create a list of tuples with word and its part of speech
    word_types = [(token.text, token.pos_) for token in doc]
    return word_types

# Example usage
sentence = "Cursed be love she pitied me"
result = identify_word_types(sentence)

# Display the result
for word, pos in result:
    print(f"{word}: {pos}")
