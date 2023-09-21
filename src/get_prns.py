import GNSS as gs


        
        
def get_prns_section(
        prns_list, 
        num_sats, 
        i
        ):
    num = int(num_sats)
    
    if (num > 24) and (num < 37):
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
        prn_list, 
        num_sats
        ):
    if len(prn_list) != num_sats:
        raise ValueError(
            'Number of PRNs does not match'
            )
    

def join_prns_epochs( 
        prns_list: list[str]
        ) -> list[str]:
    
    out = []
    
    for i, ln in enumerate(prns_list):
        
        num_sats = ln[:2]
        if is_int(num_sats):
            
            element = get_prns_section(
                    prns_list, 
                    num_sats, 
                    i
                    )
                
            num_sats = int(element[:2])
            prn_list = gs.split_prns(element[2:])
            out.append(prn_list)
            check_prns(prn_list, num_sats)
            
        else:
            try:
                num_sats = int(ln[:1])
                prn_list = gs.split_prns(ln[1:])
                out.append(prn_list)
                
                check_prns(prn_list, num_sats)
             
            except:
                pass
                

    return out


