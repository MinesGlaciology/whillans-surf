# inter event stations

class InterEvt:
    def __init__(self, name, data):
        self.name = name
        self.filpath = data

        self.avg_disp = self.get_avg_disp()
        self.avg_residuals = self.get_avg_residual()

    def get_avg_disp(self):
        # Loop through each inter event timeframe
        disps = []
        for event in data:
            # Determine if station is up and store its inter event displacement
            col = f"{self.name}_x"
            if col in event:
                if not event[col].isna().any():
                    # Calculate and store displacement
                    first_cor = event.loc[0, col]
                    last_cor = event.iloc[-1][col]
                    disp = last_cor - first_cor
                    disps.addpend(disp)

    return sum(disps) / len(disps)

    def get_avg_residual(self):
        
        for event in data:
            # Determine if station is up and store its residuals to a linear regression
            col = f"{self.name}_x"
            if col in event:
                if not event[col].isna().any():
                    time = event['time']
                    x_vals = event[col]

                    # Set linear regression
            
        
    