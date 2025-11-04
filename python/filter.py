
# Read the list of URLs from a file
input_file_path = 'C:\\Users\\lefeh\\Downloads\\urls_2.txt'
output_file_path = 'filtered_urls.txt'

# Function to filter URLs containing "search?q="
def filter_urls(input_file, output_file):
    with open(input_file, 'r') as file:
        urls = file.readlines()

    filtered_urls = [url.strip() for url in urls if "search?q=" in url]

    with open(output_file, 'w') as file:
        for url in filtered_urls:
            file.write(url + '\n')

# Call the function
filter_urls(input_file_path, output_file_path)
