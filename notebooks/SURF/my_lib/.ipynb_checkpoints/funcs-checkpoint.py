import os
import numpy as np
import pandas as pd
import scipy.signal
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

import Tides
import util.coordinate_transforms 

def extract_event_features(events_list, var='x'):
    """
    Processes a list of events to extract pre-slip area and slip severity features for each station.

    Parameters:
        events_list (list of DataFrames): Each event contains time series data from multiple stations.
        derivative (function): A function to compute the derivative (first or second) of station values.
        var (str): Variable passed to `preprocess_events` to select coordinate axis (default 'x').

    Returns:
        new_features (list of DataFrames): One DataFrame per event with features per station.
    """
    # Columns for the features DataFrames
    columns = ["station", "pre-slip_area", "slip_severity", "peak_time", "total_delta", "start_time"]
    
    # Preprocess events, extract displacement
    pre_events = preprocess_events(events_list, var=var)

    # This will hold one feature DataFrame per event
    new_features = []

    # Loop over events
    for i, event in enumerate(pre_events):
        # Initialize an empty DataFrame for this event
        event_features = pd.DataFrame(columns=columns)

        # Get a list of all station columns (excluding the 'time_sec' and start_time column)
        cols = [col for col in event.columns if (col != 'time_sec' and col != 'time_dt')]

        # Loop through each station column
        for col in cols:
            # Compute first and second derivatives of the station's signal
            grad = derivative(event[col].values)
            grad2 = derivative(grad)

            # Identify the peak in the second derivative (maximum acceleration)
            max_idx = np.argmax(np.abs(grad2))
            max_time = event['time_sec'].iloc[max_idx]
            severity = np.abs(grad2[max_idx])

            # compute the pre-slip area (displacement integral up to peak)
            closest_idx = (np.abs(event['time_sec'] - max_time)).idxmin()
            x_segment = event['time_sec'].iloc[:closest_idx + 1].values
            y_segment = event[col].iloc[:closest_idx + 1].values
            integral = np.trapz(y_segment, x_segment)

            # print(f"Adding row for station: {col}, area: {integral}, severity: {severity}")
            
            # Add the extracted features for this station
            event_features.loc[len(event_features)] = {
                "station": col,
                "pre-slip_area": float(integral),
                "slip_severity": severity,
                "peak_time": max_time,
                "total_delta": event[col].iloc[-1],
                "start_time": event['time_dt'].iloc[0]
            }

        # Store the completed features for this event
        new_features.append(event_features)

    return new_features

def derivative(x_col, order=4, crit=.05, spacing=15):
    """
    x_col - col of x values to take derivative of
    order - butterworth filter order
    crit - critical value of butterworth filter
    spacing - spacing of gradient
    """

    y = x_col - np.mean(x_col)

    #1st deriv
    b, a = scipy.signal.butter(order, crit) # butterworth filter 
    filtered = scipy.signal.filtfilt(b, a, y, padlen=50) # applies filter, no phase shift
    grad = np.gradient(filtered, spacing) # computes gradient
    return grad


def preprocess_events(raw_events, var='x'):
    """
    Preprocess a list of event DataFrames by aligning and cleaning displacement data.

    Parameters
    ----------
    raw_events : list of pandas.DataFrame
        raw data uploaded into events_list in this case
    var : str, optional
        which axis you want to focus on (x,y,z)

    Returns
    -------
    list of pandas.DataFrame
        A list of cleaned DataFrames where:
        - 'time_sec' gives time in seconds from the start of each event.
        - Only columns ending in `var` and 'time_sec' are retained.
        - Calculate displacement relative to the start of the event
        - Start time of event
        - x cor
        - y cor
    """
    
    processed_events = [] 

    # loop through full raw data
    for event in raw_events:
        # make copy to not worry about editing raw data
        event_clean = event.copy()

        # parse time and calculate seconds from first timestamp (to_datetime and dt.total_seconds)
        event_clean['time_dt'] = pd.to_datetime(event_clean['time'], format='%Y-%m-%d %H:%M:%S')
        event_clean['time_sec'] = (event_clean['time_dt'] - event_clean['time_dt'].iloc[0]).dt.total_seconds()

        # Keep only columns ending with `var` 
        var_cols = [col for col in event_clean.columns if col.endswith(var)]
        event_clean = event_clean[var_cols + ['time_sec']+ ['time_dt']]   # Keep only var cols and time_sec

        # Drop any remaining NaN columns
        event_clean = event_clean.dropna(axis=1)

        # Recalculate displacement relative to first row for each column
        for col in var_cols: # loop over columns
            if col in event_clean.columns: 
                event_clean[col] = abs(event_clean[col] - event_clean[col].iloc[0])

        processed_events.append(event_clean)

    return processed_events

def load_evt(evts_path):
    """
    Load the events into a list of data frames

    Parameters
    ----------
    evts_path: File path to evts files

    Returns
    -------
    List[pandas DataFrame]
        Raw Data
    
    """
    events_list = [] 

    for evt_path in os.listdir(evts_path):
        full_path = os.path.join(evts_path, evt_path)
        # print(f"Loading {evt_path}")
        event = pd.read_csv(full_path, sep="\t")
        
        events_list.append(event)
    return events_list



def plot_event(event: pd.DataFrame, separated=False, var="x") -> None:
    """
    Plot displacement data for an event.
    
    Parameters
    ----------
    event : pd.DataFrame
        Event to plot
    separated : bool
        If True, plot each station in its own subplot
    var : str
        Coordinate axis to plot ('x', 'y', or 'z')
    """
     # Demean and shift to start at 0 
    def demean_to_zero(col):
       
        mean_val = np.mean(col)
        return (col - mean_val) - (col.iloc[0] - mean_val)

    #Return columns ending in the given suffix with any non-NaN values 
    def valid_plot_cols(df, suffix):
        
        return [col for col in df.columns if str(col).endswith(suffix) and df[col].notna().any()]

    times = pd.to_datetime(event["time"])
    plot_cols = valid_plot_cols(event, var)
    sta_name_len = 4 # excludes direction

    if not separated:
        fig, ax1 = plt.subplots(figsize=(8, 6))
        ax2_dummy = None

        for plot_col in plot_cols:
            col_data = event[plot_col]
            if not np.isnan(col_data.iloc[0]):
                demeaned = demean_to_zero(col_data)
                ax1.plot(times, demeaned, label=str(plot_col)[:sta_name_len])
                if ax2_dummy is None:
                    ax2_dummy = demeaned

        ax1.set_ylabel(f"{var.upper()} Displacement [m]")
        ax1.set_xlim(times.iloc[0], times.iloc[-1])
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax1.legend()

        ax2 = ax1.twiny()
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
        ax2.plot(times, ax2_dummy)
        ax2.set_xlabel("DateTime")
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("outward", 20))
        for label in ax2.xaxis.get_ticklabels()[::2]:
            label.set_visible(False)

        fig.subplots_adjust(bottom=0.10)
        plt.show()

    else:
        n_cols = 3
        n_rows = math.ceil(len(plot_cols) / n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 3), squeeze=False) # always 2d array
        fig.subplots_adjust(hspace=0.5)# spacing

        for i, plot_col in enumerate(plot_cols):
            ax = axes[i // n_cols][i % n_cols] # correct subplot indexing
            demeaned = demean_to_zero(event[plot_col])
            ax.plot(times, demeaned, label=str(plot_col)[:sta_name_len])
            ax.set_title(f"Station {str(plot_col)[:sta_name_len]}")
            ax.set_ylabel(f"{var.upper()} Displacement [m]")
            ax.set_xlim(times.iloc[0], times.iloc[-1])
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.legend()

        # Remove unused subplots
        for j in range(len(plot_cols), n_rows * n_cols):
            fig.delaxes(axes[j // n_cols][j % n_cols])

        fig.suptitle(f"{var.upper()} Displacement per Station", fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()



def get_tide_data(events_list, station, days = 30, spacing = 10, plot = False):
    
        
    # Identify station columns names
    x_col = f"{station}x"
    y_col = f"{station}y"
    
    # loop through events to get first instance station is transmitting
    for i, event in enumerate(events_list):
        if not event[x_col].isna().any():# make sure location is transmitting
            # get first instance of coordinates
            x_cor = event.at[0, x_col] 
            y_cor = event.at[0,y_col]
            print(x_cor, y_cor)
            start_time = event.at[0, 'time']
            start_time_dt = datetime.datetime.fromisoformat(start_time)  # if ISO format
            start_time = str(datetime.datetime(start_time_dt.year, 1, 1))
            break

   
    # print(x_cor, y_cor, start_time)
    # now we need to get tidal data
    ### USER DEFINED PATH TO TIDE MODEL ###
    tide_dir = "/Users/sambrown04/Documents/SURF"
    #######################################

    tide_mod = "CATS2008-v2023"
    
    HR_PER_DAY = 24
    MIN_PER_HR = 60

    # create time series data
    dates_timeseries = []
    initial_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    for i in range(days * HR_PER_DAY * MIN_PER_HR // spacing):  # 30 days * 24 hr/day * 60 min/hr * 1/10 calculations/min
        dates_timeseries.append(initial_time + datetime.timedelta(minutes=spacing * i))

    #convert to lon and lat
    lon, lat = util.coordinate_transforms.xy2ll(x_cor, y_cor)
    print(lon, lat)
    
    tides = Tides.Tide(tide_mod, tide_dir)
    tide_results = tides.tidal_elevation(
        [lon],
        [lat],
        dates_timeseries,
    ).data.T[0]

    if plot:
        fig, ax = plt.subplots(figsize = (10,5))
        ax.plot(dates_timeseries, tide_results, label = f"Station {station}")
        plt.legend()
        ax.set_xlabel("Date")
        ax.set_ylabel("Tide Height [cm]")
        plt.show()

    # print(len(dates_timeseries))
    # print(len(tide_results))
    
    out = pd.DataFrame(columns = ["time", "tide_height"])
    out.loc[:,"time"] = dates_timeseries
    out.loc[:,"tide_height"] = tide_results

    return out
        
