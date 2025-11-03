from bs4 import BeautifulSoup

# Load the HTML file
with open('C:\\Users\\Ash\\Downloads\\MyActivity.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all anchor tags with "Define" in the visible text
define_links = []
for a_tag in soup.find_all('a', string=lambda text: text and 'define' in text.lower()):
    href = a_tag.get('href')
    if href:
        define_links.append(href)

# Output to a text file
with open('define_links.txt', 'w', encoding='utf-8') as output_file:
    for link in define_links:
        output_file.write(link + '\n')

print(f"Extracted {len(define_links)} links containing 'Define'. Saved to define_links.txt.")
