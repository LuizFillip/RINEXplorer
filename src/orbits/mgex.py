# import datetime as dt
# import numpy as np
# import pandas as pd
# import re

# _PRN_RE = re.compile(r"\b[GRECSJ]\d{2}\b")

# def check_if_prns_string(s: str) -> bool:
#     return _PRN_RE.search(s) is not None

# def get_datetime(ln: str) -> dt.datetime:
#     tokens = ln.split()
#     if len(tokens) < 5:
#         raise ValueError(f"Linha de epoch inválida: {ln!r}")

#     year, month, day, hour, minute = map(int, tokens[:5])

#     # se existir segundo e for numérico, usa (opcional)
#     sec = 0
#     if len(tokens) >= 6:
#         try:
#             sec_float = float(tokens[5])
#             sec = int(sec_float)  # truncando
#         except ValueError:
#             sec = 0

#     return dt.datetime(year, month, day, hour, minute, sec)

# def fixing_line(tokens):
#     """
#     tokens: lista resultante de ln.split() incluindo o primeiro campo 'Pxx'
#     Corrige casos onde valores aparecem grudados por '-' sem espaço.
#     """
#     out = []
#     fixed = False

#     for idx, tok in enumerate(tokens):
#         # Mantém o PRN (primeiro token) intacto
#         if idx == 0:
#             out.append(tok)
#             continue

#         if (not fixed) and (len(tok) > 15) and ('-' in tok):
#             # Ex: "12.34-56.78-9.0" -> ["12.34", "-56.78", "-9.0"]
#             parts = tok.split('-')
#             rebuilt = []
#             if parts[0] != '':
#                 rebuilt.append(parts[0])
#             for p in parts[1:]:
#                 if p != '':
#                     rebuilt.append('-' + p)

#             out.extend(rebuilt)
#             fixed = True
#         else:
#             out.append(tok)

#     return out



# def get_epochs(string_data):
#     data_rows = []
#     time_list = []
#     prns_list = []

#     current_time = None
#     epoch_n_obs = 0

#     def finalize_epoch():
#         nonlocal epoch_n_obs, current_time
#         if current_time is not None and epoch_n_obs > 0:
#             time_list.extend([current_time] * epoch_n_obs)
#         epoch_n_obs = 0

#     for ln in string_data:
#         if not ln:
#             continue
#         tag = ln[0]

#         if tag == '*':
#             finalize_epoch()
#             current_time = get_datetime(ln[1:].strip())

#         elif tag == 'P':
#             obs = ln.split()
#             if not obs:
#                 continue

#             prns_list.append(obs[0][1:])

#             vals = obs[1:]
#             if len(vals) < 4:
#                 vals = fixing_line(obs)[1:]

#             vals = vals[:4]
#             if len(vals) != 4:
#                 # se ainda assim não deu 4, preenche com NaN (melhor que quebrar)
#                 vals = (vals + [np.nan] * 4)[:4]

#             data_rows.append(vals)
#             epoch_n_obs += 1

#         elif tag == '+':
#             # opcional: se você usa o header pra algo, mantém;
#             # do jeito original ele não é necessário pra alinhar tempo.
#             pass

#     finalize_epoch()

#     if len(time_list) == 0 or len(data_rows) == 0:
#         raise ValueError("No data: nenhum epoch/observação encontrado.")

#     data_array = np.asarray(data_rows, dtype=np.float64)

#     if not (len(time_list) == len(prns_list) == len(data_array)):
#         raise ValueError(
#             f"Inconsistência no parsing: time={len(time_list)}, "
#             f"prns={len(prns_list)}, data={len(data_array)}."
#         )

#     return data_array, time_list, prns_list


# COLUMNS = ("x", "y", "z", "clock")

# def build_dataset(data, prns_list, time_list, columns=COLUMNS, sort_index=True):
#     # Garantir arrays e consistência
#     data = np.asarray(data, dtype=np.float64)

#     if not (len(time_list) == len(prns_list) == len(data)):
#         raise ValueError(
#             f"Tamanhos inconsistentes: time={len(time_list)}, prn={len(prns_list)}, data={len(data)}"
#         )

#     # MultiIndex mais rápido (sem zip/list de tuples)
#     index = pd.MultiIndex.from_arrays(
#         [pd.to_datetime(time_list), pd.Index(prns_list, dtype="string")],
#         names=["time", "prn"],
#     )

#     df = pd.DataFrame(data, index=index, columns=columns)

#     # útil para slicing e performance (time primeiro)
#     if sort_index:
#         df = df.sort_index()

#     return df


# def mgex(filepath, encoding="utf-8"):
#     # garante fechamento do arquivo
#     with open(filepath, "r", encoding=encoding, errors="replace") as f:
#         data_list, time_list, prns_list = get_epochs(f)

#     return build_dataset(data_list, prns_list, time_list)

# def test_mgex(infile):
#     from tqdm import tqdm 
#     import os
#     files = os.listdir(infile)

#     for fname in tqdm(files):
#         try:
#             mgex(infile + fname)
#         except:
#             print(fname)
#             continue

# file = 'esa15645.sp3'

# prn = 'G02'

# def test_mgex_by_prn(file, prn):
#     df = mgex(file)
    
#     df = df.loc[df.index.get_level_values("prn") == prn]
    
#     df.index = df.index.get_level_values(0)
    
#     print(df)
    
#     string_data = open(file, "r")
    
#     data_list, time_list, prns_list = get_epochs(string_data)
    
#     time_list[:2]
    
# # test_mgex_by_prn(file, prn)

import datetime as dt
import numpy as np
import pandas as pd
import re

_PRN_RE = re.compile(r"\b[GRECSJ]\d{2}\b")

# extrai floats com sinal e expoente, inclusive quando colados
# exemplos que ele extrai:
# "9060.701565-724692.500822" -> ["9060.701565", "-724692.500822"]
_FLOAT_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?")

def check_if_prns_string(s: str) -> bool:
    return _PRN_RE.search(s) is not None

def get_datetime(ln: str) -> dt.datetime:
    tokens = ln.split()
    if len(tokens) < 5:
        raise ValueError(f"Linha de epoch inválida: {ln!r}")

    year, month, day, hour, minute = map(int, tokens[:5])

    sec = 0
    if len(tokens) >= 6:
        sec_float = float(tokens[5])
        sec = int(sec_float)
        micro = int(round((sec_float - sec) * 1_000_000))
        return dt.datetime(year, month, day, hour, minute, sec, micro)

    return dt.datetime(year, month, day, hour, minute, sec)

def parse_p_line(ln: str) -> tuple[str, list[float]]:
    """
    Parse linha tipo:
      PG04  -4309.571446 -24328.122318   9060.701565-724692.500822 10  8  9
    Retorna:
      prn: "G04"
      vals: [x, y, z, clock] (floats/np.nan)
    """
    ln = ln.rstrip("\n")
    if not ln:
        raise ValueError("Linha vazia")

    parts = ln.split(maxsplit=1)
    if len(parts) < 2:
        raise ValueError(f"Linha P inválida: {ln!r}")

    prn_raw, rest = parts[0], parts[1]
    if not prn_raw.startswith("P"):
        raise ValueError(f"Esperado linha iniciando com P: {ln!r}")

    prn = prn_raw[1:]  # "PG04" -> "G04"

    # extrai todos os floats do restante, mesmo colados
    nums = _FLOAT_RE.findall(rest)

    # precisamos de 4 valores (x,y,z,clock); se faltar, completa com NaN
    vals = []
    for k in range(4):
        if k < len(nums):
            try:
                vals.append(float(nums[k]))
            except Exception:
                vals.append(np.nan)
        else:
            vals.append(np.nan)

    return prn, vals

def get_epochs(lines_iter):
    data_rows = []
    time_list = []
    prns_list = []

    current_time = None
    epoch_n_obs = 0

    def finalize_epoch():
        nonlocal epoch_n_obs, current_time
        if current_time is not None and epoch_n_obs > 0:
            time_list.extend([current_time] * epoch_n_obs)
        epoch_n_obs = 0

    for ln in lines_iter:
        if not ln:
            continue

        tag = ln[0]

        if tag == "*":
            finalize_epoch()
            current_time = get_datetime(ln[1:].strip())

        elif tag == "P":
            if current_time is None:
                # achou observação sem epoch → ignora
                continue

            prn, vals = parse_p_line(ln)
            prns_list.append(prn)
            data_rows.append(vals)
            epoch_n_obs += 1

        # "+" pode existir; não é necessário para alinhar tempo aqui
        # demais linhas: ignore

    finalize_epoch()

    if len(time_list) == 0 or len(data_rows) == 0:
        raise ValueError("No data: nenhum epoch/observação encontrado.")

    data_array = np.asarray(data_rows, dtype=np.float64)

    if not (len(time_list) == len(prns_list) == len(data_array)):
        raise ValueError(
            f"Inconsistência no parsing: time={len(time_list)}, "
            f"prns={len(prns_list)}, data={len(data_array)}."
        )

    return data_array, time_list, prns_list

COLUMNS = ("x", "y", "z", "clock")

def build_dataset(data, prns_list, time_list, columns=COLUMNS, sort_index=True):
    data = np.asarray(data, dtype=np.float64)

    if not (len(time_list) == len(prns_list) == len(data)):
        raise ValueError(
            f"Tamanhos inconsistentes: time={len(time_list)}, prn={len(prns_list)}, data={len(data)}"
        )

    index = pd.MultiIndex.from_arrays(
        [pd.to_datetime(time_list), pd.Index(prns_list, dtype="string")],
        names=["time", "prn"],
    )

    df = pd.DataFrame(data, index=index, columns=columns)
    return df.sort_index() if sort_index else df

def mgex(filepath, encoding="utf-8"):
    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        data, time_list, prns_list = get_epochs(f)
    return build_dataset(data, prns_list, time_list)



# file =  'F:\\database\\GNSS\\orbit\\2012\\igv\\igv17072.sp3'

# df = mgex(file)

# df  

