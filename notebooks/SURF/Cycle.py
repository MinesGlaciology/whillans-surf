class Cycle:
    def __init__(self, dateH = None, dateL = None, h_event= False, l_event = False, full_cyc = False):
        self.dateH = dateH
        self.dateL = dateL
        self.h_event = h_event # boolean whether there is high tide event
        self.l_event = l_event # boolean for low tide
        self.full_cyc = full_cyc # High and low tide event
