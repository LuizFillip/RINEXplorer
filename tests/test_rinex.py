import RINExplorer as rx

PATH = "D:\\database\\GNSS\\rinex\\peru_2\\2012\\230\\lji_2300.12o"

df = rx.RINEX21(PATH)

prn = df.prns[0]
prn = 'G05'
df.sel(prn).sort_index()