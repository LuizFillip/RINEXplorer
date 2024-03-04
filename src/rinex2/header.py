import RINExplorer as rx 

def convert_to_datetime(dic):
    '''
    Convert into datetime the time of first/end 
    observations
    '''
    for key, value in dic.items():
        dic[key] = rx.get_datetime(dic[key])
    return dic

def extend_obs(obs_types):
    extended_list = []
    for f in obs_types:
        extended_list.extend(f[10:].split())
        
    return extended_list

def get_obs_list(obs_types):
    num_of_obs = int(obs_types[0][:10].strip())
    obs_list = extend_obs(obs_types)
    
    if len(obs_list) != num_of_obs:
        raise ValueError('Dont match')
        
    return num_of_obs, obs_list

class headerRINEX2:
    
    
    def __init__(self, infile):
                
        lines = open(infile, 'r').readlines()
        
        
        obs_types = []
        time_of_obs = {}
        geral_infos = {}
        
        for num, ln in enumerate(lines):
            
            infos = ln[:60]
            infos_reader = ln[60:].strip()
            
            if 'END OF HEADER' in ln:
                break
            else:        
                if 'TYPES OF OBSERV' in ln:
                    obs_types.append(infos)
                    
                elif 'TIME' in ln:
                    time_of_obs[infos_reader[8:-4].lower()] = infos.split()
                
                elif 'APPROX POSITION XYZ' in ln:
                    geral_infos['position'] = infos.split()
                
                elif 'VERSION' in ln:
                    geral_infos['version'] = infos[:10].strip()
                    
                elif 'INTERVAL' in ln:
                    geral_infos['interval'] = infos.strip()
                    
                elif 'MARKER NAME' in ln:
                    geral_infos['code'] = infos.strip()
                    
                    
        self.num_of_obs, self.obs_names = get_obs_list(obs_types)
        
        geral_infos.update(convert_to_datetime(time_of_obs))
        self.attrs = geral_infos
        self.lines = lines
        
