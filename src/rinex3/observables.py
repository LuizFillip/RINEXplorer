import RINExplorer as rx
import numpy as np 


class data_epochs(object):
    
    def __init__(self, path_file):
        
        self.header = rx.HeaderRINEX3(path_file)
        self.obs_types = self.header.obs_types

        self.CONSTELLATIONS = self.obs_types.keys()
        self.lines = open(path_file, 'r').readlines()
        
        
    @property
    def empty_list(self):
        return {key: [] for key in self.CONSTELLATIONS}
    
    @staticmethod
    def prn_number_and_time(self, lines):
        
        time_sections = {}
        number_of_prn = {}
        
        for i, ln in enumerate(lines):
            if ln[0] == '>':
             
                time_sections[i] = rx.get_datetime(ln[1:30].split())
                number_of_prn[i] = int(ln[32:35].strip())
        
        if len(number_of_prn) != len(time_sections):
            raise ValueError('The length doenst match')
            
        return number_of_prn, time_sections
    
    @staticmethod
    def empty_arrays(obs_types, total_sats):
        
        out_dict = {}
        for key, values in obs_types.items():
            
            max_obs = len(values)
            obs = np.empty((total_sats, max_obs), dtype = np.float64) * np.NaN
            lli = np.zeros((total_sats, max_obs), dtype = np.uint8)
            ssi = np.zeros((total_sats, max_obs), dtype = np.uint8)
            
            out_dict[key] = (obs, lli, ssi)
            
        return out_dict
    

    def count_and_separate_epochs(self, epoch_section):
        count = {key: 0 for key in self.CONSTELLATIONS}
        sep_epoch = self.empty_list
        
        for i, obs_line in enumerate(epoch_section):
            
            for key in self.CONSTELLATIONS:
                if obs_line[0] == key:
                    sep_epoch[key].append(obs_line)
                    count[key] += 1
                    
        return sep_epoch, count
                
    def get_arrays_in_epoch(self, const, sep_epoch, count):
        
        obs, lli, ssi = self.empty_arrays(self.obs_types, count[const])[const]
        prn_list = []
        for i, obs_line in enumerate(sep_epoch[const]):
            prn_list.append(obs_line[:3])
            for j in range(obs.shape[1]):
                
                obs_record = obs_line[3:][16 * j: 16 * (j + 1)]
                
                obs[i, j] = rx.floatornan(obs_record[0:14])
                lli[i, j] = rx.digitorzero(obs_record[14:15].strip())
                ssi[i, j] = rx.digitorzero(obs_record[15:16].strip())
                
        return obs, lli, ssi, prn_list
    
    @staticmethod
    def concat_values_in_dict(out_obs):
        return {key: np.array(value) for key, value in out_obs.items()}
    
    @staticmethod
    def built_index(time, prn_list):
      
        return list(zip(*[[time] * len(prn_list), prn_list]))

    @property
    def data_section(self):
        number_of_prn, time_sections = self.prn_number_and_time(self.lines)
    
        rows = list(number_of_prn.keys())
            
        out_obs = self.empty_list
        out_lli = self.empty_list
        out_ssi = self.empty_list
        out_idx = self.empty_list
        out_prn = self.empty_list
        
        for i, total_sats in enumerate(number_of_prn.values()):
          
            try:        
                row = rows[i]
                epoch_section = self.lines[row + 1: rows[i + 1]]
            except:
                row = rows[-1]
                epoch_section = self.lines[row + 1:]
                
            time = time_sections[row]
        
            sep_epoch, count = self.count_and_separate_epochs(epoch_section)
            
            for const in self.CONSTELLATIONS:
                
                obs, lli, ssi, prn_list = self.get_arrays_in_epoch(
                    const, sep_epoch, count
                    )
                out_prn[const].extend(prn_list)
                out_idx[const].extend([time] * len(prn_list))
                out_obs[const].extend(obs)
                out_lli[const].extend(lli)
                out_ssi[const].extend(ssi)
        
        
        out_obs = self.concat_values_in_dict(out_obs)
        out_lli = self.concat_values_in_dict(out_lli)
        out_ssi = self.concat_values_in_dict(out_ssi)
        
        return out_prn, out_idx, out_obs, out_lli, out_ssi
        
    



