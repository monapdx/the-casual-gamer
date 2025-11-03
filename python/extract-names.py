import spacy

def extract_proper_nouns(input_file, output_file):
    # Load the spaCy English model
    nlp = spacy.load("en_core_web_sm")
    
    # Read the entire text file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Set to hold unique proper nouns (named entities)
    proper_nouns = set()
    
    # We are interested in:
    # - PERSON: people's names
    # - GPE: countries, cities, states (geo-political entities)
    # - LOC: non-GPE locations (mountains, bodies of water, etc.)
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "GPE", "LOC"):
            proper_nouns.add(ent.text)
    
    # Write the sorted proper nouns to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        for noun in sorted(proper_nouns):
            f.write(noun + "\n")

if __name__ == "__main__":
    # Specify the input and output file paths
    input_path = "C:\\Users\\Ash\\Downloads\\Sex, Drugs & Being an Escort.txt"       # your input text file
    output_path = "proper_nouns.txt"      # the file to store the extracted proper nouns
    
    extract_proper_nouns(input_path, output_path)
    print(f"Extracted proper nouns have been written to {output_path}")
