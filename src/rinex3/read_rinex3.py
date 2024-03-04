import RINExplorer as rx
import pandas as pd 
import numpy as np

class RINEX3(object):
    
    
    def __init__(self, path_file):
        
        
        ep = rx.data_epochs(path_file)
        
        self.types = ep.obs_types
        self.header = ep.header
        self.prn, self.index, self._obs, self._lli, self._ssi = ep.data_section
        
    def prns(self, const = 'G'):
        return np.unique(self.prn[const])
    

    def obs(self, values = 'obs', const = 'G', drop_ssi = True):
        
        if values == 'obs':
            data = self._obs
            
        elif values == 'lli':
            data = self._lli
            
        else:
            data = self._ssi
            
        df = pd.DataFrame(
             data[const], 
             columns = self.types[const], 
             index = self.index[const]
             )
        
        df['prn'] = self.prn[const]
        
        if drop_ssi:
            columns = [col for col in df.columns 
                       if ('S' in col) or ('D' in col)]
            df = df.drop(columns = columns)
        
        
        return df

    
    def sel(self, prn, num = 0, drop_ssi = True):           
        
        
        df = self.obs(
            values = 'obs', 
            const = prn[0], 
            drop_ssi = drop_ssi
            )
        
        df = df.loc[df["prn"] == prn]
        
        columns_with_all_nan = df.columns[
            df.isna().sum() == len(df)]
                        
        df = df.drop(columns = columns_with_all_nan)
        
        comb_list = rx.combine_pairs(df)
    
    
        return df[comb_list[num]].dropna()

        # cols = rx.filter_columns(df, sel = sel)
        
        # lli = self.obs(
        #     values = 'lli', 
        #     const = prn[0], 
        #     drop_ssi = drop_ssi
        #     )
        
        # lli_cols = [f'{c}' for c in cols if 'L' in c]
        
        # lli = lli.loc[lli["prn"] == prn, lli_cols]
        
        # lli.columns = [f'{c}lli' for c in lli.columns]
        
        # return pd.concat([df.loc[:, cols], lli], axis = 1).dropna()
        

 



def main():

    infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'
    
    filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
    # filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'
    
    path_file = infile + filename 
    
    rinex = RINEX3(path_file)
    
    prn = 'G01'
    
    df = rinex.sel(prn)
    df
