import datetime as dt
import re
import math


# epoch line RINEX 2: "yy mm dd hh mm ss.sssss  flag nsats ..."
_EPOCH_RNX2_RE = re.compile(r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d")

def is_epoch_line_rinex2(ln: str) -> bool:
    return bool(_EPOCH_RNX2_RE.match(ln))

def get_datetime(string_time):
    if string_time is None:
        raise ValueError("Tempo vazio (None)")
    if isinstance(string_time, str):
        if not string_time.strip():
            raise ValueError("Tempo vazio (string em branco)")
        t = string_time.split()
    else:
        t = list(string_time)
    if len(t) < 6:
        raise ValueError(f"Formato de tempo inválido: {string_time!r}")

    year = int(t[0])
    if year < 100:
        year = 2000 + year if year < 80 else 1900 + year

    month = int(t[1]); day = int(t[2])
    hour = int(t[3]); minute = int(t[4])

    sec_float = float(t[5])
    second = int(sec_float)
 
    return dt.datetime(year, month, day, hour, minute, second)

def _parse_prn_field(field: str):
    """
    Campo de PRNs no RINEX2 vem em blocos de 3 chars: 'G26', 'R15', etc.
    """
    prns = []
    # garante tamanho suficiente
    field = field.ljust(36)
    for j in range(0, 36, 3):
        token = field[j:j+3].strip()
        if token:
            prns.append(token)
    return prns

def join_of_prns(lines, idx_epoch):
    """
    Lê PRNs de um epoch no padrão RINEX2, incluindo linhas de continuação.
    Retorna (lista_prns, n_linhas_usadas_no_prn_list)
    """
    header = lines[idx_epoch]

    # nsats geralmente está em 29:32 (0-index) no RINEX2 (funciona para a maioria dos arquivos)
    raw_nsats = header[29:32].strip()
    if not raw_nsats:
        raise ValueError(f"Não consegui ler nsats em: {header!r}")
    nsats = int(raw_nsats)

    # Cada linha carrega até 12 PRNs (12*3=36 chars)
    lines_needed = int(math.ceil(nsats / 12))

    prns = []
    for k in range(lines_needed):
        ln = lines[idx_epoch + k]
        # Campo típico de PRNs fica após flag+nsats; em muitos arquivos começa na coluna 32
        # Aqui pegamos 32:68 (36 chars)
        field = ln[32:68]
        prns.extend(_parse_prn_field(field))

    prns = prns[:nsats]

    if len(prns) != nsats:
        raise ValueError(
            f"PRNs lidos ({len(prns)}) != nsats ({nsats}). "
            f"Epoch line: {header!r} | PRNs={prns}"
        )

    return prns, lines_needed

# def prn_time_and_data(filepath, encoding="utf-8"):
#     time_prn = {}
#     data_lines = []

#     # 1) Ler bloco de dados após END OF HEADER
#     buffered_lines = []
#     with open(filepath, "r", encoding=encoding, errors="replace") as f:
#         in_data = False
#         for ln in f:
#             if not in_data:
#                 if ln[60:80].strip() == "END OF HEADER" or "END OF HEADER" in ln:
#                     in_data = True
#                 continue
#             buffered_lines.append(ln.rstrip("\n"))

#     current_time = None
#     skip_until = -1   # índice até onde devemos pular (continuação PRNs)

#     # 2) Loop principal usando for
#     for i in range(len(buffered_lines)):

#         # pula linhas de continuação do PRN-list
#         if i <= skip_until:
#             continue

#         ln = buffered_lines[i]

#         if not ln.strip():
#             continue

#         # Epoch
#         if is_epoch_line_rinex2(ln):
#             current_time = get_datetime(ln[:29])

#             prns, span = join_of_prns(buffered_lines, i)
#             time_prn[current_time] = prns

#             # >>> define até onde pular (linhas de continuação do PRN-list)
#             skip_until = i + span - 1
#             continue

#         # Linhas de observação
#         if current_time is not None:
#             line = ln
#             if len(line) < 80:
#                 line = line.ljust(80)
#             elif len(line) > 80:
#                 line = line[:80]

#             data_lines.append(line)

#     return time_prn, data_lines



def lines_per_sat(num_of_obs: int) -> int:
    # 80 chars por linha = 5 campos de 16; logo:
    return int(math.ceil(num_of_obs / 5))


_EPOCH_RE = re.compile(r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d")

def prn_time_and_data_deterministic(filepath, num_of_obs, encoding="utf-8"):
    time_prn = {}
    raw_data = []

    lps = lines_per_sat(num_of_obs)

    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        # pula header
        for ln in f:
            if ln[60:80].strip() == "END OF HEADER" or "END OF HEADER" in ln:
                break

        while True:
            epoch = f.readline()
            if not epoch:
                break

            if not epoch.strip():
                continue

            # garante que é epoch line mesmo
            if not _EPOCH_RE.match(epoch):
                continue

            t = get_datetime(epoch[:29])
            nsats = int(epoch[29:32].strip())  # se necessário, adapte com fallback

            # PRN list: até 12 por linha
            prn_lines = int(math.ceil(nsats / 12))
            prn_block = epoch
            for _ in range(prn_lines - 1):
                cont = f.readline()
                if not cont:
                    raise ValueError("EOF inesperado ao ler continuação de PRNs.")
                prn_block += cont

            prns = split_prns(prn_block)[:nsats]
            if len(prns) != nsats:
                raise ValueError(f"PRNs lidos ({len(prns)}) != nsats ({nsats}) no epoch {t}.")

            time_prn[t] = prns

            # agora lê exatamente as linhas de observação do epoch
            n_obs_lines = nsats * lps
            for _ in range(n_obs_lines):
                obs_ln = f.readline()
                if not obs_ln:
                    raise ValueError(f"EOF inesperado lendo observações no epoch {t}.")
                line = obs_ln.rstrip("\n")
                if len(line) < 80:
                    line = line.ljust(80)
                elif len(line) > 80:
                    line = line[:80]
                raw_data.append(line)

    return time_prn, raw_data



# def test_prn_time_and_data():
#     import GNSS as gs
#     station = 'salu'
    
#     path = gs.paths(2010, 1, root = 'F:\\').fn_rinex(station)
# infile = 'F:\\database\\GNSS\\rinex\\2024\\153\\salu1531.24o' 


# time_prn, data_lines = prn_time_and_data(infile, encoding="utf-8") 


# times = list(time_prn.keys())
# # print(time_prn[times[0]])
    
# # test_prn_time_and_data()

def extend_prns(time_prn):
 

    out = []
    for p in time_prn.values():
        out.extend(p)
    
    return out 

len(extend_prns(time_prn)) 