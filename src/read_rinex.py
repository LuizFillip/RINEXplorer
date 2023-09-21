import pandas as pd
import typing as T
import numpy as np
import GNSS as gnss


"""
Verificar o caso de não encontrar nenhum PRN
for i, elem in enumerate(sat_epoch):
    if ' 15  1  1  0 1' in elem:
        print(i)
        
sat_epoch[812]
"""






 
def join_prns_epochs(sat_epoch: list[str]) -> list[str]:

    out = []
    
    sats = sat_epoch.copy()

    for i, ln in enumerate(sats):
     
        if len(ln) == 67:
            num_sats = int(ln[29:][:2].strip())
            
            if num_sats > 24:
                chuck = "".join([sats[i], 
                                 sats[i + 1], 
                                 sats[i + 2]])
            elif num_sats < 13:
                chuck = sats[i]            
            else:
                chuck =  "".join([sats[i], 
                                  sats[i + 1]])
        
            out.append(chuck)

    return out

def get_times_prns(sat_epoch):

    out = join_prns_epochs(sat_epoch)
    
    prns_list = []
    time_list = []  
    
    for epoch in out:
        
        prns = gnss.split_prns(epoch[29:][2:])
        prns_list.extend(prns)
        num_sats = int(epoch[29:][:2].strip())
        
        
        time_list.extend([
            gnss.get_datetime(
                epoch[:29])] * num_sats
            )
        
        if len(prns) != num_sats:
            raise TypeError("Check prns")
            
    return prns_list, time_list


def get_obs(prns_list, obs_epoch, obs_types = 4):
    
     
    """
    Separe string into observables values, 
    lost lock indicators (lli) and
    strength signal indicators (ssi) 
    """
    
   
    # prns list is the total sattelites
    format_types = (len(prns_list), obs_types)
    
    obs = np.empty(format_types, 
                   dtype = np.float64) * np.NaN
    
    lli = np.zeros(format_types, 
                   dtype = np.uint8)
    
    ssi = np.zeros(format_types, 
                   dtype = np.uint8)
    
    for i in range(len(prns_list)):
        
        obs_line = obs_epoch[i]
    
        for j in range(obs_types):
            obs_record = obs_line[16 * j: 16 * (j + 1)]  
            
            try:
                obs[i, j] = gnss.floatornan(obs_record[0:14])
                lli[i, j] =  gnss.digitorzero(obs_record[14:15])
                ssi[i, j] =  gnss.digitorzero(obs_record[15:16])
            except:
                continue
                
    return obs, lli, ssi


def get_epochs(dataSection: list[str]) -> tuple:
    
    """
    Separe epochs with datetime informations
    from data section (observables)
    """
       
    observables_epoch = [] #time
    prns_epoch = [] # prns observaded for each epoch
    
    for elem in dataSection:
        
        #Check gnss constellations
        if any([i in elem.strip() 
                for i in ["G", "R", "E", "S", "C"]]):
            prns_epoch.append(elem.strip())
        else:
            observables_epoch.append(elem)
            
    return prns_epoch, observables_epoch


def data_section(infile):
    
    stringText = open(infile, "r").read()

    start = stringText.find("END OF HEADER")
    
    return stringText[start: None].split("\n")[1:-1]


class RINEX2:
    
    def __init__(self, infile: T.TextIO):
        
        self.header = gnss.HEADER(infile).attrs

        data = data_section(infile)
        
        obs_epoch, sat_epoch = get_epochs(data)
        
        self.prns_list, self.time_list = get_times_prns(obs_epoch)
            
        self._obs, _lli, self._ssi = get_obs(
            self.prns_list, sat_epoch
            )
        
        # Remove "loss lock indicator" for C1 and P2 
        self._lli = np.delete(_lli, slice(1, 3), axis = 1)
        
        self.dat = np.concatenate(
            [self._obs, self._lli], axis = 1
            )
        
        
    def data(self, data, columns):
        
        tuples = list(zip(*[self.time_list, self.prns_list]))

        index = pd.MultiIndex.from_tuples(
            tuples, 
            names = [ "time", "prn"]
            ) 
        
        df = pd.DataFrame(data, 
                          columns = columns, 
                          index = index)
        
        df = df.dropna(subset = ["L1", "C1", "L2", "P2"])
        return df
    

    @property
    def obs(self):
        columns  = ["L1", "C1", "L2", "P2"]
        return self.data(self._obs, columns)
    
    @property
    def prns(self):
        return np.unique(self.prns_list)
    
    @property
    def lli(self):
        columns  = ["L1", "L2"]
        return self.data(self._lli, columns)
    
    @property
    def obs_lli(self):
        columns  = ["L1", "C1", "L2", 
                    "P2", "L1lli", "L2lli"]
        return self.data(self.dat, columns)
    
    @property
    def ssi(self):
        columns  = ["L1", "C1", "L2", "P2"]
        return self.data(self._ssi, columns)
    
         
    def sel(self, prn):
        """Select obsevables and lli for phases"""
        
        df = self.obs_lli
        
        df = df.loc[df.index.get_level_values("prn") == prn]
        
        df.index = pd.to_datetime(
            df.index.get_level_values("time")
            )
        
        df.columns.name = prn
        return df.sort_index()
    
