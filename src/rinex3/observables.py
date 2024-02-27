import RINExplorer as rx
import numpy as np 
import pandas as pd


infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'

filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'

path = infile + filename 

obs_types = rx.HeaderRINEX3(path).obs_types

CONSTELLATIONS = obs_types.keys()


def epoch_and_prn_count(lines):
    
    time_sections = {}
    number_of_prn = {}
    
    for i, ln in enumerate(lines):
        if ln[0] == '>':
         
            time_sections[i] = rx.get_datetime(ln[1:30].split())
            number_of_prn[i] = int(ln[32:35].strip())
    
    if len(number_of_prn) != len(time_sections):
        raise ValueError('The length doenst match')
        
    return number_of_prn, time_sections




def empty_arrays(obs_types, total_sats):
    
    out_dict = {}
    for key, values in obs_types.items():
        
        max_obs = len(values)
        obs = np.empty((total_sats, max_obs), dtype = np.float64) * np.NaN
        lli = np.zeros((total_sats, max_obs), dtype = np.uint8)
        ssi = np.zeros((total_sats, max_obs), dtype = np.uint8)
        
        out_dict[key] = (obs, lli, ssi)
        
    return out_dict



def test_length_of_epoch(count, epoch_section):
    
    assert sum(count.values()) == len(epoch_section)
    

def count_and_separate_epochs(epoch_section):
    count = {key: 0 for key in CONSTELLATIONS}
    sep_epoch = {key: [] for key in CONSTELLATIONS}
    
    for i, obs_line in enumerate(epoch_section):
        
        for key in CONSTELLATIONS:
            if obs_line[0] == key:
                sep_epoch[key].append(obs_line)
                count[key] += 1
    return sep_epoch, count
            



def get_arrays_in_epoch(const, sep_epoch, count):
    
    obs, lli, ssi = empty_arrays(obs_types, count[const])[const]
    prn_list = []
    for i, obs_line in enumerate(sep_epoch[const]):
        prn_list.append(obs_line[:3])
        for j in range(obs.shape[1]):
            
            obs_record = obs_line[3:][16 * j: 16 * (j + 1)]
            
            obs[i, j] = rx.floatornan(obs_record[0:14])
            lli[i, j] = rx.digitorzero(obs_record[14:15].strip())
            ssi[i, j] = rx.digitorzero(obs_record[15:16].strip())
            
    return obs, lli, ssi, prn_list

def concat_values_in_dict(out_obs):
    return {key: np.array(value) 
            for key, value in out_obs.items()}

def empty_list():
    return {key: [] for key in CONSTELLATIONS}

def built_index(time, prn_list):
    names = [ "time", "prn"]
    tuples = list(zip(*[[time] * len(prn_list), prn_list]))
    return pd.MultiIndex.from_tuples(tuples, names = names) 


def data_section(lines):
    number_of_prn, time_sections = epoch_and_prn_count(lines)

    rows = list(number_of_prn.keys())
        
    out_obs = empty_list()
    out_lli = empty_list()
    out_ssi = empty_list()
    out_idx = empty_list()
    
    
    for i, total_sats in enumerate(number_of_prn.values()):
      
        try:        
            row = rows[i]
            epoch_section = lines[row + 1: rows[i + 1]]
        except:
            row = rows[-1]
            epoch_section = lines[row + 1:]
            
        time = time_sections[row]
    
        sep_epoch, count = count_and_separate_epochs(epoch_section)
        
        for const in CONSTELLATIONS:
            
            obs, lli, ssi, prn_list = get_arrays_in_epoch(
                const, sep_epoch, count
                )
            
            out_idx[const].extend(built_index(time, prn_list))
            out_obs[const].extend(obs)
            out_lli[const].extend(lli)
            out_ssi[const].extend(ssi)
    
    
    out_obs = concat_values_in_dict(out_obs)
    out_lli = concat_values_in_dict(out_lli)
    out_ssi = concat_values_in_dict(out_ssi)
    
    return out_idx, out_obs, out_lli, out_ssi
    
    
lines = open(path, 'r').readlines()

idx, obs, lli, ssi = data_section(lines)


def dataset(values, obs_names, index):
 
    return pd.DataFrame(values, columns = obs_names, index = list(index))

const = 'G'
df = dataset(obs[const], obs_types[const], idx[const])

df