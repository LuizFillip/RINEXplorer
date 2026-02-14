# import RINExplorer as rx 
import numpy as np 

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




def get_observables(data, num_of_obs):
    
    total_sats = len(data)
    obs = np.empty((total_sats, num_of_obs), dtype = np.float64) * np.nan
    lli = np.zeros((total_sats, num_of_obs), dtype = np.uint8)
    ssi = np.zeros((total_sats, num_of_obs), dtype = np.uint8)

    for i, obs_line in enumerate(data):
        for j in range(num_of_obs):
            obs_record = obs_line[16 * j: 16 * (j + 1)]
            try:
                obs[i, j] = floatornan(obs_record[0:14])
                lli[i, j] = digitorzero(obs_record[14:15].strip())
                ssi[i, j] = digitorzero(obs_record[15:16].strip())
            except:
                continue
            
    return obs, lli, ssi


def test_lengths(prns_list, time_list, data):
    assert len(prns_list) == len(time_list) == len(data)
    
def test_length_element(data):
    assert list(set([len(ln) for ln in data]))[0] == 80

import re

def normalize_prns(prns):
    """
    Converte PRNs como:
      'G 2' -> 'G02'
      'R 4' -> 'R04'
      'G10' -> 'G10' (mantém)
    """
    out = []

    for p in prns:
        if p is None:
            continue

        # remove espaços laterais
        p = p.strip()

        # separa letra e número
        match = re.match(r"([A-Za-z])\s*(\d+)", p)

        if match:
            const, num = match.groups()
            out.append(f"{const.upper()}{int(num):02d}")
        else:
            out.append(p)

    return out


def extend_lists(time_prns):
    
    time_list = []
    prns_list = []
    for key, value in time_prns.items():
        
        time_list.extend([key] * len(value))
        prns_list.extend(normalize_prns(value))
        
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


def start_data(lines):
    out = []
    for i, ln in enumerate(lines):
        if 'TIME OF FIRST OBS'  in ln:
            out.append(ln[:8].strip())
        elif 'END OF HEADER' in ln:
            out.append(i)
    return tuple(out)

def split_prns(item: str) -> list:
    """Split PRNs string sequence into list"""
    return [item[num - 3: num] for num in 
            range(3, len(item[2:]) + 3, 3)]



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
        
    list_prns = split_prns(element[i:])
    
    if len(list_prns) != int(num):
        raise ValueError('Number of prns doenst match')
        
    return list_prns, u

def check_prns_in_string(dummy_string):
    
    gnss_constellations = {
        "G", "R", "E", "S", "C"
        }
    
    if any(constellation in dummy_string for 
           constellation in gnss_constellations):
            
        return True
    else:
        return False
    

def get_datetime(string_time):
    import datetime as dt 
    if string_time is None:
        raise ValueError("Tempo vazio (None)")
    if isinstance(string_time, str):
        if not string_time.strip():
            raise ValueError("Tempo vazio (string em branco)")
        t = string_time.split()
    else:
        t = list(string_time)
    if len(t) < 6:
        raise ValueError(f"Formato de tempo inválido: {string_time!r}")

    year = int(t[0])
    if year < 100:
        year = 2000 + year if year < 80 else 1900 + year

    month = int(t[1]); day = int(t[2])
    hour = int(t[3]); minute = int(t[4])

    sec_float = float(t[5])
    second = int(sec_float)
 
    return dt.datetime(year, month, day, hour, minute, second)


def prn_time_and_data(lines):
    
    dn, i = start_data(lines)
    year_out = dn[-2:]
    lines = lines[i + 1:]
    time_prn = {}
    data_list = []
  
    
    for i, ln in enumerate(lines):
        year_in = ln[:3].strip()
        
        if 'COMMENT' in ln:
            pass
        else:
            if check_prns_in_string(ln):
                if year_out == year_in:
                     
                    time = get_datetime(ln[:29])
                    
                    prns_out, u = join_of_prns(lines, i)
                    time_prn[time] = prns_out
                    
            else:
                obs_line = ln.replace('\n', '')
                
                
                if len(obs_line) != 80:
                    obs_line += ' ' * abs(80 - len(obs_line))
                
                data_list.append(obs_line)
        
            
    return time_prn, data_list


# # def test():
# # import GNSS as gs
# # station = 'salu'

# # path = gs.paths(2010, 1, root = 'F:\\').fn_rinex(station)

# infile = 'E:\\database\\GNSS\\rinex\\2024\\153\\salu1531.24o' 


# # _header = rx.HeaderRINEX2(infile)

# # num_of_obs = int(_header.num_of_obs)

# lines = open(infile, 'r').readlines()

# time_prns, data_list = prn_time_and_data(lines) 

# # data = get_data_rows(data_list, time_prns, num_of_obs)

# dn, i = start_data(lines)
# # data[0]

# dn, i 

# data_list[0]