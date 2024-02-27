import RINExplorer as rx
import pandas as pd 


class RINEX3(object):
    
    
    def __init__(self, path_file):
        
        

        const = 'G'
        self.idx, self.obs, self.lli, self.ssi = rx.epochs(path_file)

        # df = rx.dataset(obs[const], obs_types[const], idx[const])
        # pd.MultiIndex.from_tuples(tuples, names =  "time", "prn"]) 
        #  names = [
    @staticmethod
    def dataset(values, obs_names, index):
     
        return pd.DataFrame(values, columns = obs_names, index = list(index))




infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'

filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'

path = infile + filename 
