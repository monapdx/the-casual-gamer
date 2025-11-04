import pandas as pd
from bs4 import BeautifulSoup

# Load HTML file
with open('C:\\Users\\lefeh\\Downloads\\timeline.htm', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Example: Extracting posts and timestamps
# Note: Adjust the selectors based on the actual structure of your Facebook HTML file
posts = soup.find_all('div', class_='comment')  # Replace with actual class name for posts
timestamps = soup.find_all('span', class_='meta')  # Replace with actual class name for timestamps

# Collect data in a list of dictionaries
data = []
for post, timestamp in zip(posts, timestamps):
    data.append({
        'post': post.get_text(strip=True),
        'timestamp': timestamp.get_text(strip=True)
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Save DataFrame to a CSV file for further analysis
df.to_csv('facebook_timeline_data.csv', index=False)
