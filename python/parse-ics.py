from icalendar import Calendar
import json

# Read the .ics file
with open('C:\\Users\\Ash\\Downloads\\Exported-Data\\Google-Calendar\\mona.ical\\mona.ics') as file:
    calendar = Calendar.from_ical(file.read())

events = []

for component in calendar.walk():
    if component.name == "VEVENT":
        start = component.get("dtstart").dt
        end = component.get("dtend")
        summary = component.get("summary")
        location = component.get("location")
        description = component.get("description")

        # Handle cases where dtend is None
        end = end.dt if end else start

        events.append({
            "summary": summary,
            "start": str(start),
            "end": str(end),
            "location": location,
            "description": description,
        })

# Write to a JSON file
with open('events.json', 'w', encoding='utf-8') as json_file:
    json.dump(events, json_file, indent=4, ensure_ascii=False)
