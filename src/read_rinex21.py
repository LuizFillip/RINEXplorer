import GNSS as gs
import numpy as np
import pandas as pd
import os
import typing as t

"""
RINEX files with missing epochs (time and data)
files with epoch (time information) but without data
"""

def dataset(data: str):
    
    names =  data.observables
    _obs, _lli =  gs.get_observables_rinex21(data)

    data_concated = np.concatenate(
        [_obs, _lli], axis = 1
        )
    
    time_list =  gs.ravel_times(data)
    prns_list =  gs.ravel(data.prns)
    
    tuples = list(zip(*[time_list, prns_list]))

    index = pd.MultiIndex.from_tuples(
        tuples, 
        names = [ "time", "prn"]
        ) 
    
    lli_cols = [ob + 'lli' for ob in names]
    
    df = pd.DataFrame(
        data_concated, 
        columns = names +  lli_cols, 
        index = index
        )
            
    lli_cols = [c for c in lli_cols if 'L' in c]
   
    
    return df[names + lli_cols]




class RINEX21(object):
    
    def __init__(
            self, 
            infile: t.Union[str, os.PathLike]
            ):
        
        ds =  gs.DataSections(infile)
        
        obs_lli = dataset(ds)
        
        drop_cols = [n for n in 
                     ds.observables if 'S' in n]
        
        obs_lli.drop(columns = drop_cols, 
                      inplace = True) 
        
        self.header = gs.HEADER(infile).attrs
        
        self.prns = np.unique(gs.ravel(ds.prns))
        
        self.dataset = obs_lli.copy()
    
    def sel(self, prn):
        """Select obsevables and lli for phases"""
        
        df = self.dataset.copy()
            
        df = df.loc[
            df.index.get_level_values("prn") == prn
            ]
        
        df.index = pd.to_datetime(
            df.index.get_level_values("time")
            )
        
        df.columns.name = prn
        
        return  df
    
    
# infile = gs.paths(2021, 179).fn_rinex('amte')
# infile = gs.paths(2022, 18).fn_rinex('ceeu')

# RINEX21(infile).dataset
# 







