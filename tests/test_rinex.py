import RINExplorer as rx
import GNSS as gs 



            
station = 'lji_'

path_in = gs.paths(2013, 3).fn_rinex(
    station, index = 0)

def test_rinex():
    
    return rx.RINEX21(path_in)
     
    

def test_load_receiver():

    obs = gs.load_receiver(path_in)
    
    prn = obs.prns[3]
    
    ds = gs.data_tec(
        obs, 
        prn, 
        station
        )
    
