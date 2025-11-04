import PyPDF2
import re

def extract_starred_purchases(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        purchases = []

        # Loop through each page
        for page in pdf_reader.pages:
            # Extract text from the page
            page_text = page.extract_text()
            # Split the text into lines
            lines = page_text.split('\n')
            
            # Loop through each line and check if it contains an asterisk
            for line in lines:
                if '*' in line:
                    purchases.append(line.strip())

    return purchases

# Example usage
pdf_path = 'C:\\Users\\Ash\\Downloads\\Finance\\Bank-Statements\\2024\\2024-08.pdf'
starred_purchases = extract_starred_purchases(pdf_path)

# Print the results
for purchase in starred_purchases:
    print(purchase)
