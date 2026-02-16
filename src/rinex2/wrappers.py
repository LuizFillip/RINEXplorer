import io 
from pathlib import Path
import datetime as dt 
 
import re
_EPOCH_RE_RNX2 = re.compile(r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d")

def parse_first_epoch_rinex2(filepath, encoding="utf-8"):
    """
    Retorna o primeiro datetime encontrado no bloco de dados 
    (RINEX 2) após END OF HEADER.
    Epoch line típica: yy mm dd hh mm ss.ssssssss ...
    """
    in_data = False
    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        for ln in f:
            if not in_data:
                if ln[60:80].strip() == "END OF HEADER":
                    in_data = True
                continue

            if not ln.strip():
                continue

            # RINEX 2 epoch
            if _EPOCH_RE_RNX2.match(ln):
                parts = ln.split()
                yy = int(parts[0])
                year = 2000 + yy if yy < 80 else 1900 + yy  # regra comum p/ RINEX2
                month = int(parts[1]); day = int(parts[2])
                hour = int(parts[3]); minute = int(parts[4])

                sec_float = float(parts[5])
                sec = int(sec_float)
                micro = int(round((sec_float - sec) * 1_000_000))

                return dt.datetime(year, month, day, hour, minute, sec, microsecond=micro)

            # fallback se pegar RINEX 3 por acaso
            if ln.lstrip().startswith(">"):
                parts = ln.split()
                year = int(parts[1]); month = int(parts[2]); day = int(parts[3])
                hour = int(parts[4]); minute = int(parts[5])
                sec_float = float(parts[6])
                sec = int(sec_float)
                micro = int(round((sec_float - sec) * 1_000_000))
                return dt.datetime(year, month, day, hour, minute, sec, microsecond=micro)

    return None

 
def auto_fix_time_of_first_obs(attrs, infile, encoding="utf-8", tolerance_seconds=0.0):
    """
    Compara TIME OF FIRST OBS do header com a primeira época real dos dados.
    Se diferente (maior que tolerância), corrige attrs e registra metadados.
    """
    fmt = '%Y%m%d%H%M%S'
    
    t_data = parse_first_epoch_rinex2(infile, encoding=encoding)
    if t_data is None:
        attrs["time_first_obs_check"] = {"status": "no_data_epoch_found"}
        return attrs

    t_header = None
    if "time_first_obs" in attrs and isinstance(attrs["time_first_obs"], dict):
        t_header = attrs["time_first_obs"].get("datetime")

    # Se não havia no header, preenche
    if t_header is None:
        attrs["time_first_obs"] = t_data.strftime(fmt) #11
        attrs["time_first_obs_check"] = {"status": "filled", "delta_seconds": None}
        return attrs

    # Se havia, compara com tolerância
    delta = abs((t_data - t_header).total_seconds())
    
    
    if delta > float(tolerance_seconds):
        attrs["time_first_obs_original"] = attrs["time_first_obs"].strftime(fmt)
        
        attrs["time_first_obs"] = {
            **attrs["time_first_obs"].strftime(fmt),
            "datetime": t_data.strftime(fmt),
            "fixed_from_data": True}
        
        attrs["time_first_obs_check"] = {"status": "fixed", "delta_seconds": delta}
    else:
        attrs["time_first_obs_check"] = {"status": "ok", "delta_seconds": delta}

    return attrs

def parse_time_of_obs(info60):
    """
    RINEX 2: TIME OF FIRST OBS / TIME OF LAST OBS
    Normalmente: yyyy mm dd hh mm ss.ssssssss [time_system]
    O time system (GPS/UTC/GLO/...) pode aparecer nos últimos campos.
    """
    parts = info60.split()
    if len(parts) < 6:
        return {"raw": parts}

    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    hour = int(parts[3])
    minute = int(parts[4])

    # segundos podem ser float
    sec_float = float(parts[5])
    sec = int(sec_float)
    
    fmt = '%Y%m%d%H%M%S'

    return  dt.datetime(
        year, month, day, hour, minute, sec).strftime(fmt)


def check_input_file(infile, encoding="utf-8"):
    
    if isinstance(infile, (str, Path)):
        with open(infile, "r", 
                  encoding=encoding, 
                  errors="replace") as f:
            lines = f.readlines()
    
    elif hasattr(infile, "read"):
        # já é file-like (TextIOWrapper, ZipExtFile etc.)
        if isinstance(infile, io.TextIOBase):
            lines = infile.readlines()
        else:
            text = io.TextIOWrapper(
                infile, 
                encoding = encoding, errors = "replace"
                )
            lines = text.readlines()
    else:
        raise TypeError("infile must be path or file-like object")
        
    return lines