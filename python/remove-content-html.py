import re
from bs4 import BeautifulSoup

def remove_visible_text_from_html(file_path, output_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    # Remove all visible text from tags, keeping tag structure and attributes
    for element in soup.find_all(['p', 'h1', 'h2', 'span', 'a', 'li', 'label', 'img', '' ]):
        # Skip script, style, and similar non-visible elements
        if element.name in ["script", "style", "div"]:
            continue
        # Clear only the visible string content
        if element.string and not element.string.isspace():
            element.string.replace_with("")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

    print(f"Processed file saved to: {output_path}")

# Example usage
input_file = "C:\\Users\\Ash\\Downloads\\Code\\the-casual-gamer\\dashboards\\themes\\90s\\90s.html"
output_file = "90s.html"
remove_visible_text_from_html(input_file, output_file)
