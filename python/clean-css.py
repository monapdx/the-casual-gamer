import cssutils

def clean_css(css_file, output_file):
    # Create a CSSParser instance
    parser = cssutils.CSSParser()
    
    # Parse the CSS file
    with open(css_file, 'r') as file:
        css_content = file.read()
        stylesheet = parser.parseString(css_content)

    # Set the output options for cleaner formatting
    cssutils.ser.prefs.useMinified()  # for minified output, or use:
    cssutils.ser.prefs.useDefaults()  # for readable formatting

    # Save the cleaned CSS to a new file
    with open(output_file, 'w') as file:
        file.write(stylesheet.cssText.decode('utf-8'))

    print(f"CSS has been cleaned and saved to {output_file}")

# Example usage
clean_css('yourfile.css', 'cleaned_output.css')
