import re
from datetime import datetime

# Function to extract the date from a post
def extract_date(post):
    # Regular expression to match the full date format
    # Example: "Saturday, August 12, 2017 at 12:05am PDT"
    date_pattern = r'\*\*Date:\*\* ([A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4} at \d{1,2}:\d{2}[ap]m [A-Z]+)'
    match = re.search(date_pattern, post)
    
    if match:
        # Strip the timezone (PDT, PST, etc.) and parse the rest of the date
        date_str = match.group(1)[:-4]  # Remove the last 4 characters (timezone)
        return datetime.strptime(date_str, '%A, %B %d, %Y at %I:%M%p')
    return None

# Function to sort posts by date
def sort_posts_by_date(posts):
    return sorted(posts, key=lambda post: extract_date(post) or datetime.min)

# Read your Markdown file
with open('C:\\Users\\Ash\\Downloads\\Blog\\content\\fb-posts.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Split the file into individual posts
# Assuming each post starts with a known pattern like "**Date:**"
posts = content.split("\n\n\n\n")  # Splits posts by four newlines between them

# Sort the posts by date
sorted_posts = sort_posts_by_date(posts)

# Write the sorted posts back to a new Markdown file
with open('sorted_facebook_posts.md', 'w', encoding='utf-8') as f:
    f.write("\n\n\n\n".join(sorted_posts))

print("Posts have been sorted and saved to 'sorted_facebook_posts.md'")
