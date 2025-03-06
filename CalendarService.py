from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import json


class CalendarService:
    def __init__(self, client):
        self.service = build('calendar', 'v3', credentials=client.credentials)

    def add_event(self, json_string):
        event = json.loads(json_string)
        try:
            self.service.events().insert(calendarId='primary', body=event).execute()
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_event_by_summary(self, json_string):
        event = json.loads(json_string)
        event_id = self._find_event_id_by_summary(event['summary'])
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Event with ID {event_id} has been deleted.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_events_on_period(self, time_delta: timedelta):
        try:
            # convert time in rfc format
            now = datetime.now(timezone.utc)
            end_time = now + time_delta
            time_min = now.isoformat()
            time_max = end_time.isoformat()
            #get all events information in the user calendar
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            # get client events information
            events = events_result.get('items', [])
            for event in events:
                # delete by id
                self.service.events().delete(calendarId='primary', eventId=event['id']).execute()

        except Exception as e :
            print(f"An error occurred: {e}")

    def get_events_on_period(self, time_delta: timedelta):
        try:
            # convert time in rfc format
            now = datetime.now(timezone.utc)
            end_time = now + time_delta
            time_min = now.isoformat()
            time_max = end_time.isoformat()

            # get all events information in the user calendar
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            # get client events information
            events = events_result.get('items', [])
            return events

        except Exception as e:
            print(f"An error occurred: {e}")
            return []


    def _find_event_id_by_summary(self, summary):
        try:
            events_result = self.service.events().list(calendarId='primary', maxResults=250).execute()
            events = events_result.get('items', [])
            for event in events:
                if event['summary'] == summary:
                    print(f"Event found! ID: {event['id']}, Summary: {event['summary']}")
                    return event['id']
            print(f"No event found with summary: {summary}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None