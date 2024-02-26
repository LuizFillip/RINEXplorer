import RINExplorer as rx
import numpy as np 


infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'

filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'

path = infile + filename 

lines = open(path, "r").readlines()

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




def read_obs_inline(obs_line, n_obs, total_sats):
    
    obs = np.empty((total_sats, n_obs), dtype = np.float64) * np.NaN
    lli = np.zeros((total_sats, n_obs), dtype = np.uint8)
    ssi = np.zeros((total_sats, n_obs), dtype = np.uint8)
    i = 0
    
    for j in range(n_obs):
        
        obs_record = obs_line[3:][16 * j: 16 * (j + 1)]
        
        obs[i, j] = rx.floatornan(obs_record[0:14])
        lli[i, j] = rx.digitorzero(obs_record[14:15].strip())
        ssi[i, j] = rx.digitorzero(obs_record[15:16].strip())
    
    return obs, lli, ssi




def join_epochs(epoch_section):
    
    G = []
    R = []
    E = []
   
    for obs_line in epoch_section:
        prn = obs_line[0]
    
        n_obs = len(obs_types[prn])
        obs, lli, ssi = read_obs_inline(obs_line, n_obs, 1)
        vars()[prn].extend(obs)
    
    return np.array(R), np.array(G), np.array(E)

obs_types = rx.HeaderRINEX3(path).obs_types

number_of_prn, time_sections = epoch_and_prn_count(lines)



rows = list(number_of_prn.keys())

for i, total_sats in enumerate(number_of_prn.values()):
    try:
        epoch_section = lines[rows[i] + 1: rows[i + 1]]
    except:
        epoch_section = lines[rows[-1] + 1:]





gps, glonass, galileu = join_epochs(epoch_section)