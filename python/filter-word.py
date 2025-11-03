import json

# Define a list of words to filter out
filter_words = ["Mindjolt", "GoodReads", "Pyramid Solitaire Saga", "played", "Puzzly Words", "Goodreads", "Word Battle", "Bingo Lane", "GamePoint Bingo", "Wordox", "WordTornado", "BattleSolitaire"]

# Load the JSON file
with open("C:\\Users\\Ash\\Downloads\\Exported-Data\\FB-Timeline-main\\FB-Timeline-main\\html\\facebook_timeline.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Check if the data is a list
if isinstance(data, list):
    # Filter out entries where 'content' contains any of the words
    filtered_data = [
        entry for entry in data
        if not any(word in entry.get("content", "") for word in filter_words)
    ]
else:
    print("The JSON structure is not a list. Make sure the data format is correct.")
    filtered_data = data

# Save the filtered data back to a new file
with open("facebook_timeline_filtered.json", "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4, ensure_ascii=False)

print("Filtering complete. Saved to 'facebook_timeline_filtered.json'.")
