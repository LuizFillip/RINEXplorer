import xrinex as rx
import GNSS as gs 
import zipfile 
import io
import os 

def load_rinex():
    infile = 'E:\\database\\GNSS\\rinex\\2024\\153\\salu1531.24o' 
    rnx = rx.Rinex2(infile)
    
    # print(rnx.prns)
        
    df = rnx.sel("G26")
    df_all = rnx.dataset_mi(values="obs")
    df_all 
    
def open_zip_rinex(infile, file):
    
    z = zipfile.ZipFile(infile)
        
    fbin = z.open(file) 
    
    return io.TextIOWrapper(fbin)

def sel_rinex(files_in):
   
    return [f for f in files_in if f.endswith('o')][0]
 #

path = gs.paths(2009, 2, root = 'F:\\')

zfile = os.listdir(path.rinex)[0]
station_path = path.fn_rinex(zfile, zip_f = True)
files_in = zipfile.ZipFile(station_path).namelist()

fn = sel_rinex(files_in)

path_zip = open_zip_rinex(station_path, fn)

rx.Rinex2(path_zip).dataset()

