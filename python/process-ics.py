# Script to process an .ics file and start a new line at every "SUMMARY:"
def process_ics_file(input_file, output_file):
    try:
        # Open the input .ics file with utf-8 encoding
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        # Open the output file with utf-8 encoding to write the formatted data
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in lines:
                # Add a newline before "SUMMARY:" entries
                if line.strip().startswith("SUMMARY:"):
                    outfile.write("\n")  # Start a new line
                outfile.write(line)  # Write the line

        print(f"Processed file saved as: {output_file}")
    except FileNotFoundError:
        print("Error: The input file was not found.")
    except UnicodeDecodeError as e:
        print(f"Unicode decoding error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace with your file paths
input_file = "C:\\Users\\Ash\\Downloads\\Exported-Data\\Google-Calendar\\mona.ical\\mona.ics"  # Path to your .ics file
output_file = "formatted_calendar.ics"  # Path to save the formatted file

# Run the function
process_ics_file(input_file, output_file)
