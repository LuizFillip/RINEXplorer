# import RINExplorer as rx

def split_prns(item: str) -> list:
    """Split PRNs string sequence into list"""
    return [item[num - 3: num] for num in 
            range(3, len(item[2:]) + 3, 3)]


def check_prns_in_string(dummy_string):
    
    gnss_constellations = {
        "G", "R", "E", "S", "C"
        }
    
    if any(constellation in dummy_string for 
           constellation in gnss_constellations):
            
        return True
    else:
        return False
    


def get_prns_section(prns_list, num_sats, i):

    num = int(num_sats)
    
    if (num >= 24) and (num < 37):
        element = "".join(
            [prns_list[i], 
             prns_list[i + 1], 
             prns_list[i + 2]]
            )
       
    elif num < 13:
        element = prns_list[i]
        
    elif num >= 37:
        element = "".join(
            [prns_list[i], 
             prns_list[i + 1], 
             prns_list[i + 2],
             prns_list[i + 3]]
            )
        
    else:
        element = "".join(
            [prns_list[i], 
             prns_list[i + 1]]
            )
             
        
    return element


def is_int(num):
    try:
        int(num)
        return True
    except:
        return False
    
    
def check_prns(
        prn_list: list[str], 
        num_sats: list[str]
        ):
    if len(prn_list) != num_sats:
        raise ValueError(
            'Number of PRNs does not match'
            )
    

