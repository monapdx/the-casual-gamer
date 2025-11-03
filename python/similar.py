import os
from fuzzywuzzy import fuzz

# Function to read terms from a file
def read_terms(file_path):
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        return []
    
    with open(file_path, 'r') as file:
        terms = [line.strip() for line in file]
    return terms

# Function to remove exact duplicates from a list of terms
def remove_duplicates(terms):
    return list(set(terms))

# Function to find similar terms based on fuzzy matching
def find_similar_terms(terms, threshold=90):
    unique_terms = list(set(terms))
    similar_groups = []
    
    while unique_terms:
        term = unique_terms.pop()
        group = [term]
        for other_term in unique_terms[:]:
            if fuzz.ratio(term, other_term) >= threshold:
                group.append(other_term)
                unique_terms.remove(other_term)
        similar_groups.append(group)
    
    return similar_groups

# Main script
def main(file_path):
    # Read terms from the file
    terms = read_terms(file_path)
    
    if not terms:
        print("No terms to process.")
        return
    
    # Remove exact duplicates
    terms = remove_duplicates(terms)
    
    # Find similar terms
    similar_groups = find_similar_terms(terms)
    
    # Print similar groups
    for group in similar_groups:
        print("Group:", group)

# Example usage
if __name__ == "__main__":
    file_path = 'C:\\Users\\Ash\\Downloads\\The Ins & Outs of Escorting.txt'  # Replace with your file path
    main(file_path)
