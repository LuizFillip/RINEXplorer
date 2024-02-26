def join_obs_types(obs_types):
    
    types_joined = {}
    
    for i, ln in enumerate(obs_types):
        if not ln[0].isalpha():
            index = i
            first_type = obs_types[index - 1].strip()  
            second_type = obs_types[index].strip()    
            joined = ' '.join([first_type, second_type])
        else:
            joined = ln.strip()
            
        types_joined[joined[:7]] = joined[7:].split()
        
    return types_joined
    

def _check_length_of_observables(obs_types_joined):
    
    for key, values in obs_types_joined.items():
        constelation, number_of_obs = tuple(key.split())
        if int(number_of_obs) != len(values):
            raise ValueError('The number of observables doesnt match')
        else:
            return True