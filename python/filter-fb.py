import json

# Define a list of texts to filter out
filter_texts = [
    "Ashly Lorenzana played a game on Games on Mindjolt.",
    "Ashly Lorenzana moved up in a game on Games on Mindjolt.",
    "Ashly Lorenzana collected a stack of tokens on Games on Mindjolt."
	"Ashly Lorenzana broke a record in Hex Fill on Games on Mindjolt.",
    "Ashly Lorenzana completed a game on Games on Mindjolt.",
    "Ashly Lorenzana shared a memory."
]

# Load the JSON file
with open("facebook_timeline.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Check if the data is a list
if isinstance(data, list):
    # Filter out entries where 'content' matches any text in the filter list
    filtered_data = [entry for entry in data if entry.get("content") not in filter_texts]
else:
    print("The JSON structure is not a list. Make sure the data format is correct.")
    filtered_data = data

# Save the filtered data back to a new file
with open("facebook_timeline_filtered.json", "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4, ensure_ascii=False)

print("Filtering complete. Saved to 'facebook_timeline_filtered.json'.")
