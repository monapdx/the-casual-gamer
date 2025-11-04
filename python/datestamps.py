from datetime import datetime

def convert_ics_dates(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in lines:
                if line.startswith("DTSTART") or line.startswith("DTEND"):
                    # Extract the date-time value
                    dt_str = line.split(":")[1].strip()
                    if dt_str.endswith("Z"):
                        # UTC format with time
                        dt_format = "%Y%m%dT%H%M%SZ"
                    elif "T" in dt_str:
                        # Local time format with time
                        dt_format = "%Y%m%dT%H%M%S"
                    else:
                        # All-day event (no time)
                        dt_format = "%Y%m%d"
                    
                    try:
                        dt = datetime.strptime(dt_str, dt_format)
                        # Format as readable string
                        readable_dt = dt.strftime("%b %d, %Y, %I:%M %p") if "T" in dt_str else dt.strftime("%b %d, %Y")
                        if dt_str.endswith("Z"):
                            readable_dt += " UTC"
                    except ValueError as ve:
                        readable_dt = f"Unrecognized date format: {dt_str}"
                    
                    # Write the converted line
                    outfile.write(f"{line.split(':')[0]}: {readable_dt}\n")
                else:
                    # Write other lines unchanged
                    outfile.write(line)
        
        print(f"Converted file saved as: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace with your file paths
input_file = "C:\\Users\\Ash\\Downloads\\Exported-Data\\Google-Calendar\\mona.ical\\mona.ics"  # Path to your .ics file
output_file = "readable_calendar.ics"  # Path to save the converted file

# Run the function
convert_ics_dates(input_file, output_file)
