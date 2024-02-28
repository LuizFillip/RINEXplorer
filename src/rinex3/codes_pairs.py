channels = {'C': [], 'W': [], 'X': [], 
               'L': [], 'Z': [], 'I': [], 
               'E': [], 'P': [], 'Q': [], 
               'A': [], 'B': [], 'M': [], 
               'N': [], 'Y': []}
   

def observation_codes_pairs(df):
    codes = {'L': [], 'C': []}
    
    for col in df.columns:
        if col == 'prn':
            continue
        
        for code in codes.keys():
            if code == col[0]:
                codes[code].append(col)
                
    return codes 
                



def filter_columns(df, sel = 1):
    
    codes = observation_codes_pairs(df)
    
    comb = combine_pairs(codes)
    
    if sel == 1:
        sel_cols = list(comb[1][0] + comb[2][0])
    else:
        sel_cols = list(comb[1][0] + comb[5][0])
    
    return sel_cols

def combine_pairs(codes):
    
    out = {1: [], 2: [], 5: []}
    
    for l in codes['L']:
        for c in codes['C']:
            if l[1] != c[1]:
                continue
            if l[2] == c[2]:
                for key in out.keys():
                    if key == int(l[1]):
                        out[key].append((l, c))
                        
    return out 

def main():
    import RINExplorer as rx 
    infile = 'G:\\Meu Drive\\Python\\data-analysis\\database\\GNSS\\'
    
    filename = 'AREG00PER_R_20190860000_01D_30S_MO.rnx'
    # filename = 'GLPS00ECU_R_20220010000_01D_30S_MO.rnx'
    
    path_file = infile + filename 
    
    rinex = rx.RINEX3(path_file)
    
    prn = 'G01'
    
    df = rinex.sel(prn)
    
    
    
    codes = observation_codes_pairs(df)
    


