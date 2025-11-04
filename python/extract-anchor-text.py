from bs4 import BeautifulSoup

# Input and output file names
input_file = "C:\\Users\\Ash\\Downloads\\pinboard.html"  # Replace with your actual HTML file
output_file = "extracted_links.txt"

# Read the HTML file
with open(input_file, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Extract anchor text from all <a> tags
anchor_texts = [a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True)]

# Save extracted text to a file
with open(output_file, "w", encoding="utf-8") as file:
    file.write("\n".join(anchor_texts))

print(f"Extracted {len(anchor_texts)} anchor texts and saved to {output_file}")
