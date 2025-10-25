import RINExplorer as rx 
import pandas as pd 
import numpy as np


def combine_better_obs(df):
    
    counts = df.count()

    C = counts[counts.index.str.startswith('C')]
    P = counts[counts.index.str.startswith('P')]
    L = counts[counts.index.str.startswith('L')]
    
    # escolhe grupo primário C, senão P
    CP = C if not C.empty else P
    
    # top-2 de cada grupo
    cp_top2 = CP.nlargest(2)
    l_top2  = L.nlargest(2)
    
    result = ['prn']
    cp_pair = cp_top2.index.tolist()
    l_pair  = l_top2.index.tolist()
    
    result.extend(cp_pair)
    result.extend(l_pair)
    return result



class rinex2(object):
    
    
    def __init__(self, infile):
        
        self.attrs = rx.headerRINEX2(infile)
        
        self.ob = rx.obs2(self.attrs.lines, self.attrs.num_of_obs)
        
        self.header = self.attrs.attrs
        
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
    
    def set_prn_obs(self, prn):
        
        df = self.dataset(values = 'obs')
        
        df = df.loc[df.prn == prn]
    
        df = df.dropna(axis = 1, how = 'all')

        if len(df.columns) == 5:
            return df
        else:
            return df[combine_better_obs(df)]


    def set_prn_lli(self, prn, cols):
        lli = self.dataset(values = 'lli')
        
        lli = lli.loc[lli["prn"] == prn, cols]
        
        lli.columns = [f'{c}lli' for c in lli.columns]
        
        lli = lli[[col for col in lli.columns if 'L' in col]]

        return lli 

    
    def sel(self, prn):
        
        df = self.set_prn_obs(prn)

        lli = self.set_prn_lli(prn, df.columns)

        return pd.concat([df, lli], axis = 1).dropna()
            
# def main():
    
# import GNSS as gs 
# import datetime as dt 

# station  = 'salu'
# dn = dt.date(2025, 1, 1)
# doy = gs.doy_from_date(dn)

# path = gs.paths(dn.year, doy).fn_rinex(station)
    
# ob = rinex2(path)



# prn = 'R06'


# df = ob.sel(prn)


# df 