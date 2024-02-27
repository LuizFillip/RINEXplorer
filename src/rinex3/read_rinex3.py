import RINExplorer as rx
import pandas as pd 


class RINEX3(object):
    
    
    def __init__(self, path_file):
        
        
        ep = rx.data_epochs(path_file)
        self.obs_types = ep.obs_types
        self.header = ep.header
        self.prn, self.index, self._obs, self._lli, self._ssi = ep.data_section
        
        
    @staticmethod
    def dataset(values, obs_names, index, prn):
        df = pd.DataFrame(values, columns = obs_names, index = index)
        df['prn'] = prn
        return df

    def obs(self, const = 'G'):
        return self.dataset(
            self._obs[const], 
            self.obs_types[const], 
            self.index[const], 
            self.prn[const])

    def lli(self, const = 'G'):
        return self.dataset(
            self._lli[const], 
            self.obs_types[const], 
            self.index[const], 
            self.prn[const])

    def ssi(self, const = 'G'):
        return self.dataset(
            self._ssi[const], 
            self.obs_types[const], 
            self.index[const], 
            self.prn[const])

    def sel(df, prn):            
        return df.loc[df["prn"] == prn]

 





infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'

filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'

path_file = infile + filename 

df = RINEX3(path_file)

df.obs(const = 'R')