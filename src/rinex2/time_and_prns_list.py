# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 15:55:11 2026

@author: LuizF
"""

import datetime as dt
import re
import RINExplorer as rx

# Epoch line RINEX 2: "yy mm dd hh mm ss.sssss  flag nsats ...."
_EPOCH_RNX2_RE = re.compile(
    r"^\s*\d{2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d{1,2}\s+\d"
)

# def is_epoch_line_rinex2(ln: str) -> bool:
#     return bool(_EPOCH_RNX2_RE.match(ln))


# def get_datetime(string_time):
#     """
#     Converte 'yy mm dd hh mm ss.sss' ou 'yyyy mm dd hh mm ss.sss' em datetime.
#     Aceita string ou sequência.
#     """
#     if string_time is None:
#         raise ValueError("Tempo vazio (None)")

#     if isinstance(string_time, str):
#         if not string_time.strip():
#             raise ValueError("Tempo vazio (string em branco)")
#         t = string_time.split()
#     else:
#         t = list(string_time)

#     if len(t) < 6:
#         raise ValueError(f"Formato de tempo inválido: {string_time!r}")

#     year = int(t[0])
#     if year < 100:
#         year = 2000 + year if year < 80 else 1900 + year

#     month = int(t[1]); day = int(t[2])
#     hour = int(t[3]); minute = int(t[4])

#     sec_float = float(t[5])
#     second = int(sec_float)
#     micro = int(round((sec_float - second) * 1_000_000))

#     return dt.datetime(year, month, day, hour, minute, second, microsecond=micro)


# def join_of_prns(lines, index):
#     """
#     Lê a lista de PRNs do epoch começando na linha `index`.
#     RINEX2: o número de satélites fica no header do epoch e a lista vem em blocos de 12 PRNs por linha.
#     Aqui usamos a largura típica após a coluna 29 (como no seu código).
#     """
#     header = lines[index]

#     # nsats costuma estar em colunas fixas; mantendo sua abordagem:
#     raw_nsats = header[29:32].strip()
#     if not raw_nsats:
#         raise ValueError(f"Não consegui ler nsats em: {header!r}")

#     nsats = int(raw_nsats)

#     def payload(i):
#         # parte onde ficam os PRNs
#         return lines[i][29:].strip()

#     # cada linha após col 29 costuma comportar ~12 PRNs
#     # (GxxGyy...); então número de linhas necessárias:
#     lines_needed = (nsats + 11) // 12

#     raw = "".join(payload(index + k) for k in range(lines_needed))
#     prns = rx.split_prns(raw)

#     if len(prns) != nsats:
#         raise ValueError(f"Número de PRNs ({len(prns)}) != nsats ({nsats}). Linha: {header!r}")

#     return prns, lines_needed


# def prn_time_and_data(filepath, encoding="utf-8"):
#     """
#     Lê um RINEX2 do disco e retorna:
#       - time_prn: dict {datetime: [prns]}
#       - data_lines: lista de strings (80 chars) com linhas de observação
#     """
#     time_prn = {}
#     data_lines = []
#     current_time = None

#     # 1) Lê apenas o bloco de dados (após END OF HEADER)
#     buffered_lines = []
#     with open(filepath, "r", encoding=encoding, errors="replace") as f:
#         in_data = False
#         for ln in f:
#             if not in_data:
#                 if ln[60:80].strip() == "END OF HEADER" or "END OF HEADER" in ln:
#                     in_data = True
#                 continue
#             if ln:  # mantém até linhas vazias (mas você pode filtrar)
#                 buffered_lines.append(ln.rstrip("\n"))

#     # 2) Parse do bloco de dados
#     for i, ln in enumerate(buffered_lines):
#         if not ln.strip():
#             continue

#         # Epoch só se for uma epoch line válida (regex), NÃO por letras G/R/E/C
#         if is_epoch_line_rinex2(ln):
#             # pega apenas o trecho de tempo (primeiros 29 chars, como seu padrão)
#             current_time = get_datetime(ln[:29])

#             prns, span = join_of_prns(buffered_lines, i)
#             time_prn[current_time] = prns

#             continue

#         # Caso não seja epoch, é linha de observação (desde que já tenhamos current_time)
#         if current_time is None:
#             continue

#         line = ln
#         if len(line) < 80:
#             line = line.ljust(80)
#         elif len(line) > 80:
#             line = line[:80]

#         data_lines.append(line)

#     if not time_prn:
#         raise ValueError("Nenhuma época (epoch) encontrada no bloco de dados. Verifique se é RINEX 2.")

#     return time_prn, data_lines

import datetime as dt
import math
import re

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
    micro = int(round((sec_float - second) * 1_000_000))

    return dt.datetime(year, month, day, hour, minute, second, microsecond=micro)

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

def prn_time_and_data(filepath, encoding="utf-8"):
    """
    Lê RINEX2 do disco e retorna:
      - time_prn: dict {datetime: [PRNs]}
      - data_lines: lista (80 chars) com linhas de observação (somente)
    """
    # 1) pega só bloco de dados
    data_block = []
    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        in_data = False
        for ln in f:
            if not in_data:
                if ln[60:80].strip() == "END OF HEADER" or "END OF HEADER" in ln:
                    in_data = True
                continue
            data_block.append(ln.rstrip("\n"))

    time_prn = {}
    data_lines = []
    current_time = None

    i = 0
    n = len(data_block)
    while i < n:
        ln = data_block[i]

        if not ln.strip():
            i += 1
            continue

        # Epoch
        if is_epoch_line_rinex2(ln):
            # tempo: primeiros 29 chars como você já usa
            current_time = get_datetime(ln[:29])

            prns, span = join_of_prns(data_block, i)
            time_prn[current_time] = prns

            # PULA as linhas de continuação do PRN-list (isso evita cair em "R15R18" como se fosse dado)
            i += span
            continue

        # Linhas de observação (só depois que já existe epoch)
        if current_time is not None:
            line = ln
            if len(line) < 80:
                line = line.ljust(80)
            elif len(line) > 80:
                line = line[:80]
            data_lines.append(line)

        i += 1

    if not time_prn:
        raise ValueError("Nenhuma época encontrada. Verifique se o arquivo é RINEX 2 e se o regex está adequado.")

    return time_prn, data_lines

def test_prn_time_and_data():
    infile = 'F:\\database\\GNSS\\rinex\\2010\\001\\alar0011.10o' 
    
    time_prn, data_lines = prn_time_and_data(infile, encoding="utf-8") 
    
    time_prn