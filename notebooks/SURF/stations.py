# sam brown
# sam_brown@mines.edu
# 06/03/2025
# Class for stations to better organize code and possibly allow for more effective standardization


class Station:
    
    def __init__(self, name, evts_path, year):
        self.name = name
        self.chars = name[0:2]
        self.num = name[2:4]
        self.evts_path = evts_path
        self.year = year

        self.slip_size = self.calc_avg_sz()
        self.slip_severity = self.calc_avg_sv()
        self.pre_slip_a = self.calc_area()
        self.data = self.preprocess()
        # average slip size

        # Average slip severity

        # average pre slip area

    def preprocess():
        
        
    
    def calc_avg_sz():
        
        
    # get averages

    # plot station

    # get coordinates

    # get lat, long

    # get tide data



