import re
from collections import Counter

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def tokenize(text, stop_words):
    # Convert text to lowercase
    text = text.lower()
    # Use regular expression to find words
    words = re.findall(r'\b\w+\b', text)
    # Exclude stop words
    words = [word for word in words if word not in stop_words]
    return words

def count_words(words):
    return Counter(words)

def write_counts_to_file(counts, output_path):
    sorted_counts = sorted(counts.items(), key=lambda item: item[1])
    with open(output_path, 'w', encoding='utf-8') as file:
        for word, count in sorted_counts:
            file.write(f'{word}: {count}\n')

def main(input_path, output_path, stop_words):
    text = read_file(input_path)
    words = tokenize(text, stop_words)
    word_counts = count_words(words)
    write_counts_to_file(word_counts, output_path)

if __name__ == '__main__':
    input_file_path = 'C:\\Users\\Ash\\Downloads\\The Ins & Outs of Escorting.txt'  # Path to the input text file
    output_file_path = 'output.txt'  # Path to the output text file
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
        'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
    ])
    main(input_file_path, output_file_path, stop_words)
