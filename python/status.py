from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re

# Step 1: Parse the HTML file to extract text
def extract_statuses(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    statuses = [status.get_text() for status in soup.find_all('div', class_='comment')]
    return statuses

# Step 2: Preprocess the text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove punctuation and special characters
    return text

# Step 3: Group the statuses
def group_statuses(statuses, n_clusters=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(statuses)
    
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X)
    
    groups = {}
    for i, label in enumerate(model.labels_):
        if label not in groups:
            groups[label] = []
        groups[label].append(statuses[i])
    
    return groups

# Step 4: Output the results
def print_groups(groups):
    for group, texts in groups.items():
        print(f"\nGroup {group}:")
        for text in texts:
            print(f" - {text}")

# Example usage:
html_file = 'C:\\Users\\Ash\\Downloads\\timeline.html'
statuses = extract_statuses(html_file)
preprocessed_statuses = [preprocess_text(status) for status in statuses]
groups = group_statuses(preprocessed_statuses, n_clusters=5)
print_groups(groups)
