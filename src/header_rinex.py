import typing as T
import os
import RINExplorer as rx
import pandas as pd
import GNSS as gs

def get_time_range(t):
       
    interval = int(float(t['interval']))
            
    return pd.date_range(
        rx.get_datetime(t['time']),
        rx.get_datetime(t['time_end']), 
        freq = f"{interval}s"
        )


def header_lisn(lines):
    
    def get_site(ln, dic):
        if 'Location' in infos:
            dic['site'] = ln[9:60].strip()
    
    def get_obs(name, dic):
        if name == infos_reader:
           dic['obs'].extend(infos.split())
        
    def get_interval(name, dic):
        iname = name.lower()    
        if name == infos_reader:
            dic[iname] = infos[:19].strip()
            
    def get_version(ln, dic):
        if 'RINEX VERSION' in infos_reader:
            dic['version'] = ln[:10].strip()
            
            
    def get_info(name, dic):
        iname = name.lower().replace(' ', '_')
        if name in infos_reader:
            dic[iname] = infos[:47].strip().split()
    
    dic = {'obs': []}
    
    for ln in lines.split("\n"):
       
       infos = ln[:60]
       infos_reader = ln[60:].strip()
       get_version(ln, dic)
       get_info(ln, dic)     
       get_site(ln, dic)
       get_interval('INTERVAL', dic)
       get_info('TIME OF LAST OBS', dic)
       get_info('TIME OF FIRST OBS', dic)
       get_info('APPROX POSITION XYZ', dic)
       get_info('Location:', dic)
       get_obs('# / TYPES OF OBSERV', dic)
    
    
    dic['position'] = dic.pop('approx_position_xyz')
    dic['time_end'] = dic.pop('time_of_last_obs')
    dic['time'] = dic.pop('time_of_first_obs')
    
    if 'interval' not in dic.keys():
        dic['interval'] = '15.0000'
    else:
        pass
    
    return dic

class HEADER(object):
    
    """Get header from Rinex 2 and 3"""
    
    def __init__(self, infile: T.TextIO):
    
        lines = open(infile, "r").read()

        lines = lines[:lines.find("END OF HEADER")]
                    
        station = os.path.split(infile)[-1][:4]
        
        if 'lisn' in lines:
            attrs = {station: self.header_lisn(lines)}
        else:
            attrs = {station: self.header_rinex2(lines)}
        
        self.obs = attrs[station]['obs']
        
        del attrs[station]['obs'] 
        
        self.time = attrs[station]['time'] 
        
        keys = attrs[station].keys()
        
        if 'time_end' in keys:
            pass
        else:
            time_end = self.time[:3] + ['23', '59', '45']
            attrs[station]['time_end'] = time_end
            
        self.time_array = get_time_range( attrs[station])
        
        self.length = len(self.time_array)
       
        self.attrs  = attrs
    

    @staticmethod
    def header_rinex2(lines):
       
        dic = {
           'obs': []
           }
       
        for ln in lines.split("\n"):
           
           infos = ln[:60]
           infos_reader = ln[60:]
           
          
           
           if "RINEX VERSION" in infos_reader:
               dic["version"] = infos[:19].strip()
               
           elif "APPROX POSITION XYZ" in infos_reader:
             
               dic["position"] = infos.split()
               
           elif 'TIME OF FIRST OBS' in infos_reader:
               dic['time'] = infos[:47].strip().split()
               
           elif 'TIME OF LAST OBS' in infos_reader:
               dic['time_end'] = infos[:47].strip().split()
                   
           elif "COMMENT" in  infos_reader:
               
               dic['code'] = infos[:17].replace(
                   'CODIGO:', '').strip()
               dic['site'] = infos[25:].strip()
              
           elif "TYPE / VERS" in infos_reader:
               dic["rxmodel"] = infos[19:38].strip()
               
           elif '# / TYPES OF OBSERV' in ln:
             
               dic['obs'].extend(
                   ln[:ln.find('#')].split()
                                 ) 
        
           if "INTERVAL" == infos_reader.strip():
                dic["interval"] = infos[:19].strip()
           else:
                dic["interval"] = '15.0000'
               
        
        return dic
   
def main():
    path = gs.paths(2021, 1)
    
    
    # infile = path.fn_rinex('alar', index = 1)
    infile = path.fn_rinex('psga', index = 0)
    
    HEADER(infile).attrs
    

   