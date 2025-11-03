from bs4 import BeautifulSoup

# Load your HTML file
with open('C:\\Users\\Ash\\Downloads\\MyActivity.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

search_terms = []

# Find all outer containers
entries = soup.find_all("div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp")

for entry in entries:
    content = entry.find("div", class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1")
    if content and content.text.strip().startswith("Searched for"):
        link = content.find("a")
        if link and link.text:
            search_terms.append(link.text.strip())

# Save results
with open('filtered_search_terms.txt', 'w', encoding='utf-8') as output_file:
    for term in search_terms:
        output_file.write(term + '\n')

print(f"Extracted {len(search_terms)} search terms.")
