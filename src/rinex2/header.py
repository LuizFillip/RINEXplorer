import xrinex as rx
 
def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return x


class HeaderRINEX2:
    """
    Leitor de Header RINEX 2.x (mais completo).

    Atributos principais:
      - num_of_obs: int
      - obs_names: list[str]
      - attrs: dict com campos do header
      - comments: list[str]
      - lines (opcional): lista de linhas do header
    """

    def __init__(self, infile, encoding = "utf-8"):
        self.infile = infile
 
        self.comments = []
        self.attrs = {}

        obs_types_lines = []
        raw_lines = []  
        
        lines = rx.check_input_file(infile, encoding="utf-8")

    
        for ln in lines:
            # if keep_lines:
            raw_lines.append(ln)

            info = ln[:60]
            label = ln[60:80].strip()

            if label == "END OF HEADER":
                break

            # --------- campos comuns do RINEX 2 ----------
            if label == "RINEX VERSION / TYPE":
                
                self.attrs["version"] = info[:9].strip()

            elif label == "MARKER NAME":
                self.attrs["marker_name"] = info.strip() or None

            elif label == "MARKER TYPE":
                self.attrs["marker_type"] = info.strip() or None
 

            elif label == "REC # / TYPE / VERS":
                # self.attrs["receiver_number"] = info[:20].strip() or None
                self.attrs["receiver_type"] = info[20:40].strip() or None
        
            elif label == "APPROX POSITION XYZ":
                parts = info.split()
                if len(parts) >= 3:
                    self.attrs["position"] = [
                        float(parts[0]), float(parts[1]), float(parts[2])]
                else:
                    self.attrs["position"] = parts

            elif label == "INTERVAL":
                # normalmente um float nos primeiros campos
                self.attrs["interval"] = _safe_float(
                    info.strip().split()[0]) if info.strip() else None
            
            elif label == "TIME OF FIRST OBS":
                
                self.attrs["time_first_obs"] = rx.parse_time_of_obs(info) 

            elif label == "TIME OF LAST OBS":
                 
                self.attrs["time_last_obs"] = rx.parse_time_of_obs(info) 

            elif label == "# / TYPES OF OBSERV":
                obs_types_lines.append(info)

            elif label == "COMMENT":
                self.comments.append(info.rstrip())

             
        return None 

def test_HeaderRINEX2():
    infile = 'F:\\database\\GNSS\\rinex\\2010\\001\\alar0011.10o' 
    
    ob = HeaderRINEX2(infile)
    
    print(ob.attrs) 
    