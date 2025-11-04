import json
from datetime import datetime

# Load your JSON file
with open('C:\\Users\\Ash\\Downloads\\facebook_timeline.json', 'r', encoding='utf-8') as file:
    posts = json.load(file)

# Convert to Timeline.js format
timeline_data = {"events": []}
for post in posts:
    date = datetime.fromisoformat(post['date'])
    timeline_data["events"].append({
        "start_date": {
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "hour": date.hour,
            "minute": date.minute
        },
        "text": {
            "headline": post['content'][:50],  # Truncate for headline
            "text": post['content']
        }
    })

# Save to a new JSON file
with open('timeline_data.json', 'w', encoding='utf-8') as file:
    json.dump(timeline_data, file, indent=4)

print("Converted to Timeline.js format!")
