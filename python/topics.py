import spacy
import yake

# Load spaCy model
nlp = spacy.load('en_core_web_sm')
nlp.max_length = 2000000

def extract_topics(text):
    # Process the text with spaCy to break it into tokens, sentences, etc.
    doc = nlp(text)
    
    # Extract nouns and noun phrases which are often good topic indicators
    topics = set()
    for chunk in doc.noun_chunks:
        topics.add(chunk.text.lower())
    
    return list(topics)

def extract_keywords(text):
    # Initialize YAKE keyword extraction
    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(text)
    
    # Return only the extracted keyword phrases
    return [kw[0] for kw in keywords]

def read_text_file(file_path):
    # Read conversation from a plain text file
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# File path to the conversation text file
file_path = 'C:\\Users\\Ash\\Downloads\\Sex, Drugs & Being an Escort.txt'

# Read the conversation text from the file
conversation = read_text_file(file_path)

# Extract topics and keywords
topics = extract_topics(conversation)
key_words = extract_keywords(conversation)

print("Extracted Topics:", topics)
print("Extracted Keywords:", key_words)
