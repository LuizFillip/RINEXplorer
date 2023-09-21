import GNSS as gs
import numpy as np



def observables_sections(ds):
    
    epochs = ds.epochs
    num = ds.number_of_obs
    
    
    if num <= 5:
        length = 1
    elif (num > 6) and (num < 11):
        length = 2
    elif (num >= 11) and (num <= 16):
        length = 3
    elif num > 16:
        length = 4
    
    out = []
    for i in range(0, len(epochs), length):
        
        obs_line = gs.complete_line(
            epochs[i: i + length])
        
        if len(obs_line) > 315:
            obs_line = obs_line[1:-3]
        
        out.append(obs_line)
        
    return out

def spurius(obs_record):
    ob = obs_record.split()
    if len(ob) == 2:
        return ob[0], '', ob[-1]
    elif len(ob) == 0:
        return '', '', ''
    else:
        return ob[0][:-2], ob[0][-2], ob[0][-1]

def get_observables_rinex21(ds):

    sections = observables_sections(ds)
    
    shape = (len(gs.ravel(ds.prns)), 
             ds.number_of_obs)
    
    obs = np.empty(shape, dtype = np.float64) * np.NaN
    
    lli = np.zeros(shape, dtype = np.uint8)
    
    #ssi = np.zeros(shape, dtype = np.uint8)
    
 
    for i, obs_line in enumerate(sections):
        
        for j in range(ds.number_of_obs):
            
            obs_record = obs_line[16 * j: 16 * (j + 1)]
                                
            try:
                p1, p2, p3 = spurius(obs_record)
                
            except:
                try:
                    p1, p2, p3 = spurius(obs_record[:-1])
                
                except:
                    p1, p2, p3 = '', '', ''
    
            obs[i, j] = gs.floatornan(p1)
            lli[i, j] = gs.digitorzero(p2)
            #ssi[i, j] = gs.digitorzero(p3)
            
    return obs, lli#, ssi




# ds = gs.DataSections(infile)

# ds

# get_observables_rinex21(ds)