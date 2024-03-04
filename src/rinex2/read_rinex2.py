import RINExplorer as rx 
import pandas as pd 


infile = 'database/GNSS/rinex/areg0170.13o'

# infile = 'database/GNSS/rinex/iqqe0010.13o'
# num_of_obs = 7





class rinex2(object):
    
    
    def __init__(self, infile):
        
        self.attrs = rx.headerRINEX2(infile)
        
        self.ob = rx.obs2(self.attrs.lines, self.attrs.num_of_obs)

        
    def dataset(self):
        df =  pd.DataFrame(
            self.ob.obs, 
            index = self.ob.time_list,
            columns = self.attrs.obs_names
            )
        
        df['prn'] = self.ob.prns_list
        
        return df
    
ds = rinex2(infile).dataset()

ds