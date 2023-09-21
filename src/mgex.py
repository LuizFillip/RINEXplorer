import datetime as dt
import numpy as np
import GNSS as gs
import pandas as pd

def check_if_prns_string(dummy_string):
    
    gnss_constellations = {
        "G", "R", "E", "S", "C", 'J'
        }
    
    if any(constellation in dummy_string for 
           constellation in gnss_constellations):
            
        return True
    else:
        return False

def get_datetime(ln):
    t = [int(i) for i in ln.split()[:-1]]
    return dt.datetime(t[0], t[1], t[2], t[3], t[4])


def fixing_line(a):
    b = []
    for i, ln in enumerate(a):
        if len(ln) > 15:
            b.extend(['-' + i for i in ln.split('-') if i != ''])
            index = i
                
    return a[:index] + b

def get_epochs(string_data):
    
    data_list = []
    time_list = []
    prns_list = []
    header = []
    
    
    for i, ln in enumerate(string_data.readlines()):
        
        if '+' == ln[0]:
            prns_line = ln[1:].split('\n')[0][8:]
    
            if check_if_prns_string(prns_line):
                for prn in gs.split_prns(prns_line):
                    try: 
                        float(prn.strip())
                    except:
                        header.append(prn)
        
        elif 'P' == ln[0]:
            obs_line = ln.split()
            prns_list.append(obs_line[0][1:])
            
            if len(obs_line[1:]) == 4:
                data_list.append(obs_line[1:])
                
            elif len(obs_line[1:]) < 4:
                data_list.append(fixing_line(obs_line)[1:])
             
            else:
                data_list.append(obs_line[1:5])
                
        
        elif '*' == ln[0]:
            obs_time = get_datetime(ln[1:].strip())
            time_list.extend([obs_time] * len(header))
    
    data_list = np.array(data_list, dtype = np.float64)
    
    if len(time_list) == 0:
        raise('No data')
        
    return data_list, time_list, prns_list
        


def build_dataset(data, prns_list, time_list):
    
    tuples = list(zip(*[time_list, prns_list]))
    
    index = pd.MultiIndex.from_tuples(
        tuples, 
        names = ["time", "prn"]
        )
      
    columns = ["x", "y", "z", "clock"]
    
    return pd.DataFrame(data, 
                        index = index, 
                        columns = columns)


def mgex(file):
    
    string_data = open(file, "r")
    
    data_list, time_list, prns_list = get_epochs(string_data)
    
    return build_dataset(data_list, prns_list, time_list)



def test_mgex(infile):
    from tqdm import tqdm 
    import os
    files = os.listdir(infile)

    for fname in tqdm(files):
        try:
            mgex(infile + fname)
        except:
            print(fname)
            continue
        


def test_sata():
    infile = "D:\\database\\GNSS\\orbit\\2022\\cod\\"
    # "D:\database\GNSS\orbit\2022\cod\"
    fname = "cod21906.eph_r"
    fname = 'com22120.eph'
    file = (infile + fname)
    
    string_data = open(file, "r")
    
    data, time, prns = get_epochs(string_data)
    
# mgex(infile + fname)