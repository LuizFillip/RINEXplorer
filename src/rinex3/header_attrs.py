import RINExplorer as rx



def convert_to_datetime(dic):
    '''
    Convert into datetime the time of first/end 
    observations
    '''
    for key, value in dic.items():
        dic[key] = rx.get_datetime(dic[key])
    return dic

class HeaderRINEX3:
    
    
    
    def __init__(self, infile):
        
    
        lines = open(infile, "r").readlines()
        
        obs_types = []
        time_of_obs = {}
        geral_infos = {}
        
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
                
                elif 'APPROX POSITION XYZ' in ln:
                    geral_infos['position'] = infos.split()
                
                elif 'VERSION' in ln:
                    geral_infos['version'] = infos[:10].strip()
                    
                elif 'INTERVAL' in ln:
                    geral_infos['interval'] = infos.strip()
                    
                elif 'MARKER NAME' in ln:
                    geral_infos['code'] = infos.strip()
                    
        
        
        geral_infos.update(convert_to_datetime(time_of_obs))
        
        self.obs_types = rx.join_obs_types(obs_types)
        self.header = geral_infos
        


def main():
    infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'
    
    filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
    # filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'
    
    
    path = infile + filename
    he = HeaderRINEX3(path).header 
    
    print(he)
    
# main()