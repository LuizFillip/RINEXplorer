import RINExplorer as rx

infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'

filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'
lines = open(infile + filename, "r").readlines()

obs_types = []
time_of_obs = {}

def convert_to_datetime(dic):
    '''
    Convert into datetime the time of first/end 
    observations
    '''
    for key, value in dic.items():
        dic[key] = rx.get_datetime(dic[key])
    return dic

for num, ln in enumerate(lines):
    
    infos = ln[:60]
    infos_reader = ln[60:].strip()
    
    if 'END OF HEADER' in ln:
        break
    else:        
        if 'OBS TYPES' in ln:
            obs_types.append(infos)
            
        elif 'TIME' in ln:
            time_of_obs[infos_reader[8:-4].lower()] = infos.split()
            



obs_types_joined = rx.join_obs_types(obs_types)




# infos[:47].strip().split()
# obs_types_joined

time_of_obs = convert_time_of_obs_to_datetime(time_of_obs)

