from datetime import date, time

class CalendarEvent:
    def __init__(self, event_type, event_name, start_date, start_time, end_date, end_time):
        """
        Initialize a CalendarEvent object.
        
        Args:
            event_type (str): Type of the event
            event_name (str): Name of the event
            start_date (date): Start date of the event
            start_time (time): Start time of the event
            end_date (date): End date of the event
            end_time (time): End time of the event
        """

        self.event_type = event_type
        self.event_name = event_name
        self.start_date = start_date if isinstance(start_date, date) else None
        self.start_time = start_time if isinstance(start_time, time) else None
        self.end_date = end_date if isinstance(end_date, date) else None
        self.end_time = end_time if isinstance(end_time, time) else None
    
    def __str__(self):
        """Return a string representation of the event."""
        return f"{self.event_name} ({self.event_type}): {self.start_date} - {self.end_date}"
    
    def __repr__(self):
        """Return a detailed string representation of the event."""
        return f"CalendarEvent(event_type='{self.event_type}', event_name='{self.event_name}', " \
               f"start_date={self.start_date}, end_date={self.end_date})"