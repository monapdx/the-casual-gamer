import json
from datetime import datetime

# Load the filtered JSON file
with open("C:\\Users\\Ash\\Downloads\\Exported-Data\\FB-Timeline-main\\FB-Timeline-main\\html\\facebook_timeline_filtered.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Start creating the HTML structure
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Timeline</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .timeline {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
        }
        .post {
            border-bottom: 1px solid #ccc;
            margin-bottom: 20px;
            padding-bottom: 10px;
        }
        .post:last-child {
            border-bottom: none;
        }
        .comment {
            margin: 10px 0;
            white-space: pre-line;
        }
        .meta {
            color: #888;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="timeline">
"""

# Generate HTML for each post
for entry in data:
    content = entry.get("content", "No content provided.")
    raw_date = entry.get("date", "Unknown date")
    
    # Convert ISO 8601 date to a readable format
    try:
        formatted_date = datetime.fromisoformat(raw_date).strftime("%B %d, %Y at %I:%M %p")
    except ValueError:
        formatted_date = "Invalid date"

    html_content += f"""
        <div class="post">
            <div class="comment">{content}</div>
            <div class="meta">{formatted_date}</div>
        </div>
    """

# Close the HTML structure
html_content += """
    </div>
</body>
</html>
"""

# Save the HTML content to a file
with open("facebook_timeline.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML file generated as 'facebook_timeline.html'.")
