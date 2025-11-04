from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# STEP 1: Load and parse the HTML file
with open('C:\\Users\\Ash\\Downloads\\MyActivity.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

entries = soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp")

data = []

for entry in entries:
    content = entry.find("div", class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
    if content and content.text.strip().startswith("Searched for"):
        link = content.find("a")
        if link:
            text = link.text.strip()
            # Grab the datetime after the <br> tag
            raw = content.decode_contents()
            match = re.search(r'<br>(.*?)</div>', raw)
            date_str = match.group(1).strip() if match else ''
            try:
                date = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
            except:
                date = None
            data.append((text, date))

df = pd.DataFrame(data, columns=['search_term', 'date'])

# STEP 2: Topic Clustering
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['search_term'])

n_clusters = 20  # tweak this number if needed
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Label clusters with top keywords
def get_top_keywords(n_terms):
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    labels = []
    for i in range(n_clusters):
        top_terms = [terms[ind] for ind in order_centroids[i, :n_terms]]
        labels.append(", ".join(top_terms))
    return labels

cluster_labels = get_top_keywords(5)
df['cluster_label'] = df['cluster'].map(lambda i: cluster_labels[i])

# Save for dashboard use
df.to_csv('search_clusters.csv', index=False)
print("Saved search_clusters.csv with clustered search terms.")
