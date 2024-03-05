import RINExplorer as rx 
import pandas as pd 
import numpy as np

infile = 'database/GNSS/rinex/areg0170.13o'

    # infile = 'database/GNSS/rinex/iqqe0010.13o'





class rinex2(object):
    
    
    def __init__(self, infile):
        
        self.attrs = rx.headerRINEX2(infile)
        
        self.ob = rx.obs2(self.attrs.lines, self.attrs.num_of_obs)
    
    @property
    def prns(self):
        return np.unique(self.ob.prns_list)
        
    def dataset(self, values = 'obs', drop_ssi = True):
        
        if values == 'obs':
            data = self.ob.obs
        elif values == 'lli':
            data = self.ob.lli
        else:
            data = self.ob.ssi 
            
            
        df =  pd.DataFrame(
                data, 
                index = self.ob.time_list,
                columns = self.attrs.obs_names
            )
        
        df['prn'] = self.ob.prns_list
        
        if drop_ssi:
            columns = [col for col in df.columns 
                       if ('S' in col) or ('D' in col)]
            df = df.drop(columns = columns)
        
        return df
    
    def sel(self, prn, values = 'obs'):
        
        df = self.dataset(values = values)
        
        
        df = df.loc[df["prn"] == prn]
        
        if (prn[0] == 'G') or (prn[0] == 'R'):
            cols = ['L1', 'L2']

        
        return df[cols].dropna()
    
# infile = 'database/GNSS/areg0290.13o'

# rinex2(infile).sel('G01')