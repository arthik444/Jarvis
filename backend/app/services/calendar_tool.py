"""Calendar Tool for fetching and summarizing Google Calendar events using OAuth"""
import json
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Token storage path
TOKEN_FILE = Path("calendar_token.json")


class CalendarTool:
    """Service for interacting with Google Calendar API using OAuth"""

    def __init__(self, calendar_id: str = "primary"):
        """
        Initialize Calendar Tool with OAuth.
        
        Args:
            calendar_id: Calendar ID to use (default: "primary")
        """
        self.calendar_id = calendar_id
        self.service = None
        self._cache = {}  # Session-based cache
        self._cache_timestamp = None
        self._cache_ttl = 300  # Cache for 5 minutes
        
        # Load OAuth credentials
        self.credentials = self._load_credentials()
        
        if self.credentials and self.credentials.valid:
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info(f"✓ Calendar Tool initialized with OAuth for calendar: {calendar_id}")
        else:
            logger.warning("Calendar not authorized. User needs to connect calendar via OAuth.")
            self.service = None

    def _load_credentials(self) -> Credentials | None:
        """
        Load OAuth credentials from token file.
        
        Returns:
            Credentials object or None if not authorized
        """
        if not TOKEN_FILE.exists():
            logger.info("No OAuth token found. User needs to authorize.")
            return None
        
        try:
            # Load token data from file
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
            
            # Create credentials from token data
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                logger.info("Refreshing expired OAuth token...")
                creds.refresh(Request())
                
                # Save refreshed token
                self._save_credentials(creds)
                logger.info("✓ Token refreshed successfully")
            
            return creds
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None
    
    def _save_credentials(self, creds: Credentials):
        """Save credentials to token file"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")

    def get_today_events(self) -> List[Dict[str, Any]]:
        """
        Fetch events from Google Calendar for today.
        
        Returns:
            List of event dictionaries with id, summary, start, end, location
            Returns empty list if not authorized or API fails
        """
        # Check cache first
        if self._is_cache_valid():
            logger.info("Returning cached calendar events")
            return self._cache.get("events", [])
        
        if not self.service:
            logger.warning("Calendar service not available (not authorized)")
            return []
        
        try:
            # Get today's date range (start and end of day)
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + 'Z'
            today_end = datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'
            
            logger.info(f"Fetching events from {today_start} to {today_end}")
            
            # Call Calendar API
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=today_start,
                timeMax=today_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Transform to simplified structure
            simplified_events = []
            for event in events:
                simplified_event = {
                    'id': event.get('id', ''),
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
                    'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
                    'location': event.get('location', ''),
                }
                simplified_events.append(simplified_event)
            
            # Cache the results
            self._cache['events'] = simplified_events
            self._cache_timestamp = datetime.now()
            
            logger.info(f"✓ Fetched {len(simplified_events)} events for today")
            return simplified_events
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            return []

    def summarize_events(self, events: List[Dict[str, Any]]) -> str:
        """
        Create human-readable summary of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Human-readable summary string
        """
        if not events:
            return "You have no events scheduled for today."
        
        event_count = len(events)
        
        # Build summary
        if event_count == 1:
            summary = "You have 1 event today: "
        else:
            summary = f"You have {event_count} events today: "
        
        # Add event details
        event_descriptions = []
        for event in events:
            # Parse start time
            start_str = event.get('start', '')
            if start_str:
                try:
                    # Handle both datetime and date formats
                    if 'T' in start_str:
                        start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                        time_str = start_time.strftime('%I:%M %p').lstrip('0')
                    else:
                        time_str = "all day"
                except Exception:
                    time_str = "unknown time"
            else:
                time_str = "unknown time"
            
            event_name = event.get('summary', 'Untitled')
            event_descriptions.append(f"{event_name} at {time_str}")
        
        summary += ", ".join(event_descriptions) + "."
        
        return summary

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        time_since_cache = (datetime.now() - self._cache_timestamp).total_seconds()
        return time_since_cache < self._cache_ttl


@lru_cache
def get_calendar_tool() -> CalendarTool:
    """
    Get cached Calendar Tool instance.
    
    Returns:
        Configured CalendarTool instance with OAuth
    """
    return CalendarTool(calendar_id="primary")
