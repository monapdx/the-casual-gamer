import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def generate_word_cloud(file_path, stopwords_list):
    # Read the text from the file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Define the stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(stopwords_list)
    
    # Generate the word cloud
    wordcloud = WordCloud(stopwords=stopwords, background_color="white", width=1600, height=800).generate(text)
    
    # Display the word cloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    # Path to the text file
    file_path = 'C:\\Users\\Ash\\Downloads\\Sex, Drugs & Being an Escort.txt'
    
    # List of additional stopwords
    stopwords_list = ['John', 'said', 'see', 'now', 'really', 'much', 'one', 'see', 'will', 'don\'t', 'thing', 'even', 'will', 'go', 'say', 'well', 'don', 't', 'know', 'think', 'another', 'away', 'make', 'take', 'must', 'got', 'good', 'around', 'didn', 'behind', 'try', 'trying', 'look', 've', 'm', 'sometimes', 'tell', 've', 'never', 'went', 'made', 's', 'first', 'knew', 'upon', 'open', 'none', 'took', 'within', 'saw', 'told', 'opened', 'every', 'opening', 'done', 'many', 'anything', 'oh', 'kept', 'closed', 'moved', 'ha', 'felt', 'moved']  # Add your stopwords here
    
    generate_word_cloud(file_path, stopwords_list)
