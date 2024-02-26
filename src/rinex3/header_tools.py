def join_obs_types(obs_types, only_prn = True):
    
    types_joined = {}
    
    for i, ln in enumerate(obs_types):
        if not ln[0].isalpha():
            index = i
            first_type = obs_types[index - 1].strip()  
            second_type = obs_types[index].strip()    
            joined = ' '.join([first_type, second_type])
        else:
            joined = ln.strip()
        
        if only_prn:
            key = joined[0]
        else:
            key = joined[:7]
            
        types_joined[key] = joined[7:].split()
        
    return types_joined
    

def _check_length_of_observables(obs_types):
    
    obs_types_joined = join_obs_types(obs_types, only_prn = False)
    
    for key, values in obs_types_joined.items():
        constelation, number_of_obs = tuple(key.split())
        if int(number_of_obs) != len(values):
            raise ValueError('The number of observables doesnt match')
        else:
            return True