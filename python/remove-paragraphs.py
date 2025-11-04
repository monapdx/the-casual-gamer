from bs4 import BeautifulSoup

def remove_visible_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Iterate through all elements that can have visible content
    for element in soup.find_all(True):  # True matches all tags
        # Remove all child strings that are not other tags
        for child in element.contents:
            if isinstance(child, str):
                child.replace_with('')

    return str(soup)

# Example usage
input_file = 'C:\\Users\\Ash\\Downloads\\Code\\little-red\\index.html'
output_file = 'cleaned_file.html'

with open(input_file, 'r', encoding='utf-8') as f:
    html = f.read()

cleaned_html = remove_visible_content(html)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(cleaned_html)

print(f"Content removed. Cleaned HTML saved to {output_file}")
