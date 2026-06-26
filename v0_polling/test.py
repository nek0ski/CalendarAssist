from gemini import extract_event

message = """
AI for Income, Productivity & Business – Free Webinar

Date: 20th June 2026
Time: 3:00 PM – 5:00 PM (PKT)
Venue: Google Meet

E-Certificate Included
"""

event = extract_event(message)

print(event)