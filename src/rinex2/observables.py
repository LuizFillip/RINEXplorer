import RINExplorer as rx 
import numpy as np 

def combine_better_obs(df):
    counts = df.count()
    C = counts[counts.index.str.startswith("C")]
    P = counts[counts.index.str.startswith("P")]
    L = counts[counts.index.str.startswith("L")]

    CP = C if not C.empty else P
    cp_pair = CP.nlargest(2).index.tolist()
    l_pair  = L.nlargest(2).index.tolist()

    result = []
    if "prn" in df.columns:
        result.append("prn")
    result.extend(cp_pair)
    result.extend(l_pair)
    return result



def get_observables(data, num_of_obs):
    
    total_sats = len(data)
    obs = np.empty((total_sats, num_of_obs), dtype = np.float64) * np.nan
    lli = np.zeros((total_sats, num_of_obs), dtype = np.uint8)
    ssi = np.zeros((total_sats, num_of_obs), dtype = np.uint8)

    for i, obs_line in enumerate(data):
        for j in range(num_of_obs):
            obs_record = obs_line[16 * j: 16 * (j + 1)]
            try:
                obs[i, j] = rx.floatornan(obs_record[0:14])
                lli[i, j] = rx.digitorzero(obs_record[14:15].strip())
                ssi[i, j] = rx.digitorzero(obs_record[15:16].strip())
            except:
                continue
            
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










