import numpy as np
import datetime as dt
import pandas as pd


def find_missing(ds):
    attrs = ds.attrs

    s = get_datetime(attrs['time'])
    e = get_datetime(attrs['time_end'])
    interval  = int(float(attrs['interval']))
    i = f"{interval}s"

    index  = pd.date_range(s, e, freq = i)

    rest = list(set(index) ^ set(ds.times))
    
    return sorted(rest)


def get_datetime(string_time: str) -> dt.datetime:
    """Convert datetime location into datetime"""
    if isinstance(string_time, str):
        t = string_time.split()
    else:
        t =  string_time
    
    try:
        return dt.datetime(int("20" +  t[0]), 
                       int(t[1]), 
                       int(t[2]), 
                       int(t[3]), 
                       int(t[4]), 
                       int(float(t[5])), 
                       int(t[6]))
    except:
        return dt.datetime(int(t[0]), 
                    int(t[1]), 
                    int(t[2]), 
                    int(t[3]), 
                    int(t[4]), 
                    int(float(t[5])))




def complete_line(obs_line, length = 78):
    
    """
    Complete the line with empty space for avoid
    missing observables values
    
    """
    out = []
    
    for elem in obs_line:
        if len(elem) != length:
            elem += ' ' * (length - len(elem))
        out.append(elem)
        
    return ' '.join(out)



def floatornan(x):
    if x == '' or x[-1] == ' ':
        return np.nan
    else:
        return float(x)

def digitorzero(x):
    if x == ' ' or x == '':
        return 0
    else:
        return int(x)
    

def ravel(prns):
    """like np.ravel"""
    return [item for sublist in prns 
            for item in sublist]

def ravel_times(data):
    
    """
    Multiply times array for lenght of all prns 
    observed in each epoch
    """
    out = []
    for i, prns in enumerate(data.prns):
        out.extend([data.times[i]] * len(prns))
    return out


