import datetime as dt
import re

_EPOCH_RE_RNX2 = re.compile(r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d")


def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return x

def _parse_time_of_obs(info60):
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
    micro = int(round((sec_float - sec) * 1_000_000))

    t = dt.datetime(year, month, day, hour, minute, sec, microsecond=micro)

    # time system (se existir)
    time_system = parts[6] if len(parts) >= 7 else None

    return {"datetime": t, "time_system": time_system}

def _extend_obs_types(obs_lines_60):
    """
    Cada linha (60 chars) de '# / TYPES OF OBSERV' contém:
    - nos 10 primeiros chars: N (apenas na primeira linha)
    - depois: até 9 códigos de observáveis por linha
    """
    obs = []
    for i, line60 in enumerate(obs_lines_60):
        tail = line60[10:] if i == 0 else line60
        obs.extend(tail.split())
    return obs

def _parse_types_of_observ(obs_lines_60):
    if not obs_lines_60:
        raise ValueError("Header sem '# / TYPES OF OBSERV'.")

    try:
        n = int(obs_lines_60[0][:10].strip())
    except Exception as e:
        raise ValueError(f"Não consegui ler o número de observáveis em: {obs_lines_60[0]!r}") from e

    obs = _extend_obs_types(obs_lines_60)

    if len(obs) != n:
        # alguns arquivos mal formatados podem ter espaços estranhos; ainda assim, é bom avisar
        raise ValueError(f"N observáveis não bate: esperado {n}, obtido {len(obs)}. Obs={obs}")

    return n, obs

_EPOCH_RE_RNX2 = re.compile(r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d")

def parse_first_epoch_rinex2(filepath, encoding="utf-8"):
    """
    Retorna o primeiro datetime encontrado no bloco de dados (RINEX 2) após END OF HEADER.
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
    t_data = parse_first_epoch_rinex2(infile, encoding=encoding)
    if t_data is None:
        attrs["time_first_obs_check"] = {"status": "no_data_epoch_found"}
        return attrs

    t_header = None
    if "time_first_obs" in attrs and isinstance(attrs["time_first_obs"], dict):
        t_header = attrs["time_first_obs"].get("datetime")

    # Se não havia no header, preenche
    if t_header is None:
        attrs["time_first_obs"] = {
            "datetime": t_data,
            "time_system": attrs.get("time_first_obs", {}).get("time_system") if isinstance(attrs.get("time_first_obs"), dict) else None,
            "filled_from_data": True,
        }
        attrs["time_first_obs_check"] = {"status": "filled", "delta_seconds": None}
        return attrs

    # Se havia, compara com tolerância
    delta = abs((t_data - t_header).total_seconds())
    if delta > float(tolerance_seconds):
        attrs["time_first_obs_original"] = attrs["time_first_obs"]
        attrs["time_first_obs"] = {**attrs["time_first_obs"], "datetime": t_data, "fixed_from_data": True}
        attrs["time_first_obs_check"] = {"status": "fixed", "delta_seconds": delta}
    else:
        attrs["time_first_obs_check"] = {"status": "ok", "delta_seconds": delta}

    return attrs

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

    def __init__(self, infile, encoding="utf-8"):
        self.infile = infile
        # self.keep_lines = keep_lines
        self.comments = []
        self.attrs = {}

        obs_types_lines = []
        raw_lines = []  

        with open(infile, "r", encoding=encoding, errors="replace") as f:
            for ln in f:
                # if keep_lines:
                raw_lines.append(ln)

                info = ln[:60]
                label = ln[60:80].strip()

                if label == "END OF HEADER":
                    break

                # --------- campos comuns do RINEX 2 ----------
                if label == "RINEX VERSION / TYPE":
                    # ex: "2.11           OBSERVATION DATA    G (GPS) ..."
                    self.attrs["version"] = info[:9].strip()
                    self.attrs["file_type"] = info[20:21].strip() or None
                    self.attrs["sat_system_hint"] = info[40:60].strip() or None

                elif label == "PGM / RUN BY / DATE":
                    self.attrs["program"] = info[:20].strip() or None
                    self.attrs["run_by"] = info[20:40].strip() or None
                    self.attrs["date"] = info[40:60].strip() or None

                elif label == "MARKER NAME":
                    self.attrs["marker_name"] = info.strip() or None

                elif label == "MARKER NUMBER":
                    self.attrs["marker_number"] = info.strip() or None

                elif label == "MARKER TYPE":
                    self.attrs["marker_type"] = info.strip() or None

                elif label == "OBSERVER / AGENCY":
                    self.attrs["observer"] = info[:20].strip() or None
                    self.attrs["agency"] = info[20:60].strip() or None

                elif label == "REC # / TYPE / VERS":
                    self.attrs["receiver_number"] = info[:20].strip() or None
                    self.attrs["receiver_type"] = info[20:40].strip() or None
                    self.attrs["receiver_version"] = info[40:60].strip() or None

                elif label == "ANT # / TYPE":
                    self.attrs["antenna_number"] = info[:20].strip() or None
                    self.attrs["antenna_type"] = info[20:40].strip() or None

                elif label == "APPROX POSITION XYZ":
                    parts = info.split()
                    if len(parts) >= 3:
                        self.attrs["position_xyz"] = [float(parts[0]), float(parts[1]), float(parts[2])]
                    else:
                        self.attrs["position_xyz"] = parts

                elif label == "ANTENNA: DELTA H/E/N":
                    parts = info.split()
                    # ordem RINEX: H, E, N
                    if len(parts) >= 3:
                        self.attrs["antenna_delta_hen"] = [float(parts[0]), float(parts[1]), float(parts[2])]
                    else:
                        self.attrs["antenna_delta_hen"] = parts

                elif label == "ANTENNA: DELTA X/Y/Z":
                    parts = info.split()
                    if len(parts) >= 3:
                        self.attrs["antenna_delta_xyz"] = [float(parts[0]), float(parts[1]), float(parts[2])]
                    else:
                        self.attrs["antenna_delta_xyz"] = parts

                elif label == "WAVELENGTH FACT L1/2":
                    parts = info.split()
                    # pode ter 2 ints + lista de PRNs
                    self.attrs["wavelength_fact_l1l2_raw"] = parts

                elif label == "INTERVAL":
                    # normalmente um float nos primeiros campos
                    self.attrs["interval"] = _safe_float(info.strip().split()[0]) if info.strip() else None

                elif label == "LEAP SECONDS":
                    tok = info.strip().split()
                    self.attrs["leap_seconds"] = int(tok[0]) if tok else None

                elif label == "TIME OF FIRST OBS":
                    self.attrs["time_first_obs"] = _parse_time_of_obs(info)

                elif label == "TIME OF LAST OBS":
                    self.attrs["time_last_obs"] = _parse_time_of_obs(info)

                elif label == "# / TYPES OF OBSERV":
                    obs_types_lines.append(info)

                elif label == "COMMENT":
                    self.comments.append(info.rstrip())

                else:
                    # guarda o que não foi tratado (útil para depurar / ampliar)
                    self.attrs.setdefault("unparsed", []).append((label, info.rstrip()))

        # pós-processamento: observáveis
        self.num_of_obs, self.obs_names = _parse_types_of_observ(obs_types_lines)

        self.lines = raw_lines
            
        # ---- Correção opcional: header vs primeira época dos dados ----
        self.attrs = auto_fix_time_of_first_obs(
               self.attrs,
               infile,
               encoding=encoding,
               tolerance_seconds=0.0  # pode pôr 1.0 se quiser tolerar 1s
           )

def test_HeaderRINEX2():
    infile = 'F:\\database\\GNSS\\rinex\\2010\\001\\alar0011.10o' 
    
    ob = HeaderRINEX2(infile)
    
    ob.lines 
