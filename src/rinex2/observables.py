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
    
    data = join_epoch_rows(data, num_of_obs)
    total_sats = len(data)
    obs = np.empty((total_sats, num_of_obs), 
                   dtype = np.float64) * np.NaN
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
    

def join_epoch_rows(data, num_of_obs):
    
    if  num_of_obs < 6:
        length = 1
    elif (num_of_obs >= 6) and (num_of_obs < 11):
        length = 2
    elif (num_of_obs >= 11) and (num_of_obs <= 16):
        length = 3
    elif  num_of_obs > 16:
        length = 5

    out = []
    for i in range(0, len(data), length):
        item = ''.join(data[i: i + length])
        out.append(item)
       
        
    return out

def extend_lists(time_prns):
    
    time_list = []
    prns_list = []
    for key, value in time_prns.items():
        
        time_list.extend([key] * len(value))
        prns_list.extend(value)
        
    return time_list, prns_list

def test_length_element(data):
    return list(set([len(ln) for ln in data]))


infile = 'database/GNSS/rinex/areg0170.13o'
num_of_obs = 21

# infile = 'database/GNSS/rinex/iqqe0010.13o'
# num_of_obs = 7

lines = open(infile, 'r').readlines()



time_prns, data, indexes = prn_time_and_data(lines)

# obs, lli, ssi = get_observables(data, num_of_obs)            

# data = join_epoch_rows(data, num_of_obs)
# 
# time_list, prns_list = extend_lists(time_prns)



    

# out1 = []
# for index in range(len(ss) - 1):
    
#     i, u = ss[index] 
#     j, v = ss[index + 1]
    
#     section = data[i - (u * index): 
#                     j - v - (u * index)]
    
#     # if len(section) == 0:
#     #     print(i)
#     # if (len(section) == 0):
#     #     print(i, u, j, v, index)
        
#     out = []
#     for ii in range(0, len(section), length):
#         obs_line = ''.join(section[ii: ii + length])
#         out.append(obs_line)
   
#     if len(out) !=0:
        
#         out1.append(out)
#     else:
#         out1.append([float('nan')])
        
    
# index = 2866
# i, u, j, v = 353225, 2 ,353332, 2

# section = data[i: i + 10]
# row_idx = sorted(list(set(indexes.values())))
# count = 0
# count1 = 0
# for ii, (time, index) in enumerate(indexes.items()):
#     if ii + 1 == len(row_idx):
#         break
#     i, u = index
#     j, v = row_idx[ii + 1]
#     section = data[i - (u * ii):  j - v - (u * ii)]
    
#     # if len(section) !=0:
#     #     print(index, time)
        
#     if i == 345858:
#         print(i)
        
    
    
# for time, prn in time_prns.items():
    
#     n_sats = len(prn)

#     #

if  num_of_obs < 6:
    length = 1
elif (num_of_obs >= 6) and (num_of_obs < 11):
    length = 2
elif (num_of_obs >= 11) and (num_of_obs <= 16):
    length = 3
elif num_of_obs > 16:
    length = 5
    
    
prn = list(time_prns.values())

start = 0
out = []
for p in prn:
    n_sats = len(p) * length
    slice_data = data[start:start+n_sats]
    out.append(''.join(slice_data))
    start += n_sats

out