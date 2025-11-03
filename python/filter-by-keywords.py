import pandas as pd
import re

# === CONFIGURATION ===
input_file = "C:\\Users\\Ash\\Downloads\\producthunt-2025-10-31.csv"  # your main CSV file
keywords_file = "C:\\Users\\Ash\\Downloads\\Code\\keywords.txt"            # file containing one keyword per line
output_file = "filtered_products.csv"     # results file

# === LOAD KEYWORDS ===
with open(keywords_file, "r", encoding="utf-8") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]

if not keywords:
    raise ValueError("⚠️ No keywords found in keywords.txt — please add one per line.")

print(f"Loaded {len(keywords)} keywords from {keywords_file}")

# === LOAD CSV ===
df = pd.read_csv(input_file)

# Combine all text columns into one string per row
text_columns = df.select_dtypes(include=["object"]).columns
df["combined_text"] = df[text_columns].astype(str).apply(" ".join, axis=1).str.lower()

# === FILTER BY KEYWORDS ===
pattern = r"\b(" + "|".join(map(re.escape, keywords)) + r")\b"

# Extract matches
matches = df["combined_text"].str.extractall(pattern)[0]
match_map = matches.groupby(level=0).apply(lambda x: ", ".join(sorted(set(x))))

# Filter the dataframe to only include matching rows
filtered_df = df.loc[match_map.index].copy()
filtered_df["matched_keywords"] = filtered_df.index.map(match_map)

# Optional: sort by number of matches
filtered_df["match_count"] = filtered_df["matched_keywords"].str.count(",") + 1
filtered_df = filtered_df.sort_values("match_count", ascending=False)

# === SAVE RESULTS ===
filtered_df.to_csv(output_file, index=False)

print(f"✅ Found {len(filtered_df)} matching products.")
print(f"Results saved to {output_file}")
print("Example matches:")
print(filtered_df[['matched_keywords']].head())
