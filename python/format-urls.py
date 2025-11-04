def format_urls(file_path):
    """Reads plain text URLs from a file, formats them, and writes to a new file."""
    with open(file_path, "r") as file:
        urls = file.readlines()
    
    # Strip newline characters and format
    formatted_urls = ",\n".join(f'"{url.strip()}"' for url in urls)
    
    # Write to output file
    with open("formatted_urls.txt", "w") as output_file:
        output_file.write(formatted_urls)

# Example usage
format_urls("C:\\Users\\Ash\\Downloads\\Exported-Data\\wikipedia-pages.txt")
