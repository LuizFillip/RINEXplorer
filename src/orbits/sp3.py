import datetime as dt
import numpy as np
import pandas as pd

def sp3dt(ln: str) -> dt.datetime:
    """
    some receivers such as ESA Swarm return seconds=60, so let's patch this.
    """

    dt = []

    hour = int(ln[14:16])
    minute = int(ln[17:19])
    second = int(ln[20:22])

    if second == 60:
        dt.append(dt.timedelta(minutes=1))
        second = 0

    if minute == 60:
        dt.append(dt.timedelta(hours=1))
        minute = 0

    if hour == 24:
        dt.append(dt.timedelta(days=1))
        hour = 0

    time = dt.datetime(
        year=int(ln[3:7]),
        month=int(ln[8:10]),
        day=int(ln[11:13]),
        hour=hour,
        minute=minute,
        second=second,
        microsecond=int(ln[23:29]),
    )

    for t in dt:
        time += t

    return time


def sp3(file):
    lines = open(file, "r").readlines()
    
    num_sats = int(lines[2][4:6])    

    ecef = []
    times = []
    prns = []

    for ln in lines:
        if ln[0] == "*":
            times.extend([sp3dt(ln)] * num_sats)
        if ln[0] == "P":
            ecef.append(
                [float(ln[4:18]), 
                 float(ln[18:32]), 
                 float(ln[32:46]), 
                 float(ln[46:60])])
            prns.append(ln[1:4])
            
    ecef = np.array(ecef)
    
    times = pd.to_datetime(times)

    tuples = list(zip(*[times, prns]))

    index = pd.MultiIndex.from_tuples(
        tuples, 
        names = ["time", "prn"]
        )
      
    columns = ["x", "y", "z", "clock"]

    return pd.DataFrame(ecef, 
                        index = index, 
                        columns = columns)


