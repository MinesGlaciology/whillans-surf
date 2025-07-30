# inter event stations

class InterEvt:
    def __init__(self, name, data):
        self.name = name
        self.filpath = data

        self.avg disp = self.get_avg_disp()

    def get_avg_disp(self):
        # Loop through each inter event timeframe
        for event in data:
            # Determine if station is up and store its inter event displacement
            col = f"{self.name}_x"
            if col in event:
                if not event[col].isna().any():
                    # Calculate and store displacement
            
        
    