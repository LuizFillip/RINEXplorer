
def combine_pairs_phase(codes):
    
    channels = {
        'C': [], 'S': [], 'L': [],
        'W': [], 'X': [], 
        'Z': [], 'I': [], 
        'E': [], 'P': [], 'Q': [], 
        'A': [], 'B': [], 'M': [], 
        'N': [], 'Y': []}
       
    
    for l in codes['L']:
        for key in channels.keys():
            if key == l[2]:
                channels[key].append(l)
            
    return {k: v for k, v in channels.items() if v}
    

def remove_pseudos(comb_list):

    new_list = []
    for elem in comb_list:
        obj = [o[0] == 'L' for o in elem]
        if all(obj):
            new_list.append(elem)
            
    return sorted(new_list) 

def remove_duplicates(data):
    unique_set = set()

    unique_list = []
    
    for sublist in data:
        tuple_sublist = tuple(sublist)
        if tuple_sublist not in unique_set:
            unique_set.add(tuple_sublist)
            unique_list.append(sublist)
    return unique_list

def combine_pairs(df):
    cols = [c for c in df.columns if 'L' in c]
    List = []
    for i in cols:
        out = []
        for j in cols:
            if i[1] != j[1]:
                out.append(sorted([i, j]))
        if out not in List:
            List.append(out[0])
            
    return remove_duplicates(remove_pseudos(List))


def main():
    import RINExplorer as rx 
    infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'
    
    filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
    # filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'
    
    path_file = infile + filename 
    
    rinex = rx.RINEX3(path_file)
    
    prn = 'R01'
    
    df = rinex.sel(prn)
    
    comb_list = combine_pairs(df)
    
    df[comb_list[0]].dropna()
        


