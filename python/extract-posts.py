from bs4 import BeautifulSoup
from datetime import datetime
import json

# Load HTML file
with open('C:\\Users\\Ash\\Downloads\\Exported-Data\\FB-Timeline-main\\FB-Timeline-main\\html\\timeline.htm', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Extract posts
posts = []
for p in soup.find_all('p'):
    meta = p.find('div', class_='meta')
    comment = p.find('div', class_='comment')
    if meta:
        date_text = meta.get_text()
        # Strip the time zone (e.g., PST)
        cleaned_date_text = date_text.rsplit(' ', 1)[0]
        # Parse date
        date = datetime.strptime(cleaned_date_text, "%A, %B %d, %Y at %I:%M%p").isoformat()
        # Extract post content
        content = comment.get_text() if comment else p.get_text().replace(date_text, '').strip()
        # Add to posts list
        posts.append({"date": date, "content": content})

# Save to JSON
with open('facebook_timeline.json', 'w', encoding='utf-8') as json_file:
    json.dump(posts, json_file, indent=4)

print("Posts extracted and saved to 'facebook_timeline.json'")
