import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Define a set of 100 common stop words
stop_words = set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t',
    'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 
    'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 
    'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 
    'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 
    'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 
    'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 
    'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 
    'when', 'when\'s', 'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 
    'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves', 'just', 'one', 'like', 's', 'said', 'don', 't', 'much', 'something', 'got', 'back', 'know', 'told', 'even', 'marcu', 'really', 'well', 'didn', 't', 'thing', 'still', 'told', 'can', 'get', 'will', 'm', 'd', 'since', 'things', 'get', 'around', 'tell', 'either', 'always', 'made', 'came', 'went', 'anything', 'now', 'way', 'wasn', 'going', 'go', 'll', 'wouldn', 'another', 've', 'hadn', 'everything', 're', 'ever', 'end', 'take', 'someone', 'make', 'take'
])

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def preprocess_text(text, stop_words):
    # Convert text to lowercase
    text = text.lower()
    # Use regular expression to find words
    words = re.findall(r'\b\w+\b', text)
    # Exclude stop words
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)
    
def custom_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "rgb(255, 0, 144)"  


def generate_word_cloud(text):
    wordcloud = WordCloud(color_func=custom_color_func, width=800, height=400, stopwords=stop_words, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def main(input_file_path):
    text = read_file(input_file_path)
    processed_text = preprocess_text(text, stop_words)
    generate_word_cloud(processed_text)

if __name__ == '__main__':
    input_file_path = 'C:\\Users\\Ash\\Downloads\\Sex, Drugs & Being an Escort.txt'  # Path to the input text file
    main(input_file_path)
