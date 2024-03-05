import RINExplorer as rx 
import numpy as np 

def start_data(lines):
    out = []
    for i, ln in enumerate(lines):
        if 'TIME OF FIRST OBS'  in ln:
            out.append(ln[:8].strip())
        elif 'END OF HEADER' in ln:
            out.append(i)
    return tuple(out)
            
def join_of_prns(LIST, index):
    
    num = int(LIST[index][29:][:3].strip())
    
    if num == 0:
        print(LIST)
    
    def slice_in(i): return LIST[i][29:].strip()
    
    if num < 13:
        element = slice_in(index)
        u = 1
        
    elif (num > 24) and (num < 37):
        element = ''.join([slice_in(index + i) for i in range(3)])
        u = 3
    elif num >= 37:
        element = ''.join([slice_in(index + i) for i in range(4)])
        u = 4
        
    else:
        element = ''.join([slice_in(index + i) for i in range(2)])
        u = 2
    
    if num < 10:
        i = 1
    else:
        i = 2
        
    list_prns = rx.split_prns(element[i:])
    
    if len(list_prns) != int(num):
        raise ValueError('Number of prns doenst match')
        
    return list_prns, u
        
def prn_time_and_data(lines):
    
    dn, i = start_data(lines)
    year_out = dn[-2:]
    lines = lines[i + 1:]
    time_prn = {}
    data_list = []
    indexes = {}
    
    
    for i, ln in enumerate(lines):
        year_in = ln[:3].strip()
        # 
            
        if rx.check_prns_in_string(ln):
            if year_out == year_in:
                index = i
                time = rx.get_datetime(ln[:29])
                
                prns_out, u = join_of_prns(lines, i)
                time_prn[time] = prns_out
                
        else:
           
            obs_line = ln.replace('\n', '')
            indexes[time] = (index, u)
            
            if len(obs_line) != 80:
                obs_line += ' ' * abs(80 - len(obs_line))
            
            data_list.append(obs_line)
            
            
    return time_prn, data_list, indexes


def get_observables(data, num_of_obs):
    
    total_sats = len(data)
    obs = np.empty((total_sats, num_of_obs), dtype = np.float64) * np.NaN
    lli = np.zeros((total_sats, num_of_obs), dtype = np.uint8)
    ssi = np.zeros((total_sats, num_of_obs), dtype = np.uint8)

    for i, obs_line in enumerate(data):
        for j in range(num_of_obs):
            obs_record = obs_line[16 * j: 16 * (j + 1)]
            obs[i, j] = rx.floatornan(obs_record[0:14])
            lli[i, j] = rx.digitorzero(obs_record[14:15].strip())
            ssi[i, j] = rx.digitorzero(obs_record[15:16].strip())
            
    return obs, lli, ssi


def test_lengths(prns_list, time_list, data):
    assert len(prns_list) == len(time_list) == len(data)
    
def test_length_element(data):
    assert list(set([len(ln) for ln in data]))[0] == 80


def extend_lists(time_prns):
    
    time_list = []
    prns_list = []
    for key, value in time_prns.items():
        
        time_list.extend([key] * len(value))
        prns_list.extend(value)
        
    return time_list, prns_list


def get_length(num_of_obs):
    
    if  num_of_obs < 6:
        length = 1
    elif (num_of_obs >= 6) and (num_of_obs < 11):
        length = 2
    elif (num_of_obs >= 11) and (num_of_obs <= 16):
        length = 3
    elif (num_of_obs > 16) and (num_of_obs <= 20):
        length = 4
    else:
        length = 5
        
    return length
        
        

def get_data_rows(data, time_prns, num_of_obs):
    length = get_length(num_of_obs)
    start = 0
    out = []
    
    for p in list(time_prns.values()):
        
        n_sats = len(p) * length
        slice_data = data[start: start + n_sats]
        
        for index in range(0, len(slice_data), length):
            item = ''.join(slice_data[index: index + length])
            out.append(item)
        
        start += n_sats
        
    return out




class obs2:
    
    def __init__(self, lines, num_of_obs):
                
        time_prns, data, indexes = prn_time_and_data(lines)
        
        self.time_list, self.prns_list = extend_lists(time_prns)
        
        data = get_data_rows(data, time_prns, num_of_obs)
        
        self.obs, self.lli, self.ssi = get_observables(data, num_of_obs)            
        
        test_lengths(self.prns_list, self.time_list, data)

