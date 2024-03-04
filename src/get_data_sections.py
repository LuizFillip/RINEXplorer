import RINExplorer as rx


def fisrt_dn(ds):

    d = ds['time'][:3]
    
    a = int(d[0][2:])
    b = int(d[1])
    c = int(d[2])

    if b >= 10 and c >= 10:
        ls = f'{a} {b} {c}'
    elif b >= 10 and c < 10:
        ls = f'{a} {b}  {c}'
    elif b < 10 and c < 10:
        ls = f'{a}  {b}  {c}'
    else:
        ls = f'{a}  {b} {c}'
    
    return ls
    
    
def get_epochs(data, ds):

    data_list = [] 
    prns_list = []         
    time_list = []
     
    for i, elem in enumerate(data):
        
        if 'other post-header' in elem:
            break
        
        time_epoch = elem[:29]
        prns_epoch = elem[29:]
        
        
        fla = time_epoch[:10].strip()
                
        if rx.check_prns_in_string(prns_epoch):
            
            prns_list.append(prns_epoch.strip())
            
            if fisrt_dn(ds) == fla:
                
                time_list.append(
                    rx.get_datetime(time_epoch)
                    )
                    
        else:
            if fisrt_dn(ds) == fla:
                pass
            else:
                data_list.append(elem)
            
        
    prns_list = rx.join_prns_epochs(prns_list)
    
    if len(time_list) != len(prns_list):
        raise ValueError(
            'Number of observables does not match'
            )
        
    return time_list, prns_list, data_list




class DataSections(object):
    
    
    def __init__(self, infile):
        
        obs = rx.HEADER(infile)
        
        self.number_of_obs = int(obs.obs[0])
        self.observables = obs.obs[1:]
        self.length = obs.length
        self.data = self.raw_string_data(infile)
        
        station = list(obs.attrs.keys())[0]

        self.attrs = obs.attrs[station]
        
        self.times, self.prns, self.epochs = get_epochs(
            self.data, self.attrs
            )
        
            
    @staticmethod         
    def raw_string_data(infile): 
     
        text = open(infile, "r").read()
     
        end_of_header = text.find("END OF HEADER")
         
        return text[end_of_header: 
                    None].split("\n")[1:-1]
    

   