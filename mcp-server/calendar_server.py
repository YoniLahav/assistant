import os
import datetime
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from calendar_event import CalendarEvent
from date_parser import extract_date, extract_time

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calendar")

@mcp.tool()
async def get_events(start_date: str, end_date: str) -> list[CalendarEvent]:
    """Get events from the users calendar, within the given start and end dates. This includes any meetings, all-day events, reminder, or anything that might interest the users, within the specified date range."""
    return get_events(start_date_str=start_date, end_date_str=end_date)

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate():
    """Authenticate the user and return the service object."""
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(start_date_str, end_date_str) -> list[CalendarEvent]:
    """
    Retrieve events between start_date and end_date.
    Dates should be in 'YYYY-MM-DD' format.
    """
    service = authenticate()

    # Parse the input dates
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

    # Set timezone to UTC
    timezone = pytz.UTC
    time_min = timezone.localize(start_date).isoformat()
    # Add one day to include events on the end_date
    time_max = timezone.localize(end_date + datetime.timedelta(days=1)).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    calendar_events = [
        CalendarEvent(
            event_name=event.get('summary', 'No Title'),
            event_type=event.get('kind', 'Other'),
            start_date=extract_date(event['start']),
            start_time=extract_time(event['start']),
            end_date=extract_date(event['end']),
            end_time=extract_time(event['end'])
        ) for event in events]

    return calendar_events

if __name__ == "__main__":
    mcp.run(transport="sse")

