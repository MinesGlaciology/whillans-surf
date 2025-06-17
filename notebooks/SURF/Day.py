# Sam Brown
# sam_brown@mines.edu
# June 11 2025
# Goal: Create Day Class that keeps track of high tide and low tide events described in Winburry 2017


# Store whether the day has a high tide event, low-tide event. If event has either, stores relevant numbers regarding the events
# Larger context: Store all of the days in a list, gather relevant information from them, and add a feature to our dataset regarding the sequence of the days

class TideDay:
    def __init__(self, date, h_event= None, l_event = None, h_info = None, l_infor = None):
        self.date = date
        self.h_event = h_event # boolean whether there is high tide event
        self.l_event = l_event # boolean for low tide

        # Only store if events exist
        self.h_info = h_info if h_event is not None else None
        
        self.l_info = l_info if l_event is not None else None