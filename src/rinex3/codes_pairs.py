def observation_codes_pairs(df):
    codes = {'L': [], 'C': []}
    
    for col in df.columns:
        if col == 'prn':
            continue
        
        for code in codes.keys():
            if code == col[0]:
                codes[code].append(col)
                
    return codes 
                


def combination_channel_pairs(codes, complete_pairs = True):
    
    channels = {'C': [], 'W': [], 'X': [], 
                'L': [], 'Z': [], 'I': [], 
                'E': [], 'P': [], 'Q': [], 
                'A': [], 'B': [], 'M': [], 
                'N': [], 'Y': []}
    
    
    for l, c in zip(codes['L'], codes['C']):
        if l[2] != c[2]:
            pass 
        else:
            for channel in channels.keys():
                if channel == c[2]:
                    channels[channel].append(c)
                if channel == l[2]:
                    channels[channel].append(l)
                    
                    
    cols = {key: value for key, value in channels.items() if value}

    if complete_pairs:
        cols = {key: value for key, value in 
                channels.items() if len(value) == 4}
        
    return cols


def filter_columns(df):
    
    codes = observation_codes_pairs(df)
    
    pairs = combination_channel_pairs(codes)
        
    return list(pairs.values())