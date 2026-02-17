import xrinex as rx 
import pandas as pd 
import numpy as np


def combine_better_obs(df):
    counts = df.count()
    C = counts[counts.index.str.startswith("C")]
    P = counts[counts.index.str.startswith("P")]
    L = counts[counts.index.str.startswith("L")]

    CP = C if not C.empty else P
    cp_pair = CP.nlargest(2).index.tolist()
    l_pair  = L.nlargest(2).index.tolist()

    result = []
    if "prn" in df.columns:
        result.append("prn")
    result.extend(cp_pair)
    result.extend(l_pair)
    return result


 
def pad_with_nan(arr, target_rows):
    """
    Completa array 2D com linhas NaN até atingir target_rows.
    """
    n_rows, n_cols = arr.shape

    if n_rows >= target_rows:
        return arr

    pad = np.full((target_rows - n_rows, n_cols), np.nan)
    return np.vstack([arr, pad])

    


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

def _obs_type_lines(lines):
    obs_types_lines = []
    
    for ln in lines:
        
        info = ln[:60]
        label = ln[60:80].strip()
    
        if label == "END OF HEADER":
            break
        
        if label == "# / TYPES OF OBSERV":
            obs_types_lines.append(info)
            
    return _extend_obs_types(obs_types_lines)





class Rinex2:
    """
    Wrapper unificado (novo formato):
      - lê header (rx.HeaderRINEX2)
      - parseia epochs+PRNs e linhas brutas (rx.prn_time_and_data)
      - monta linhas por satélite (rx.get_data_rows)
      - extrai obs/lli/ssi (rx.get_observables)
      - entrega datasets e seleções por PRN
    """

    def __init__(self, infile, drop_ssi_default=True, ):
        self.infile = infile
        self.drop_ssi_default = drop_ssi_default
        
        lines = rx.check_input_file(infile, encoding="utf-8")
    
        self.obs_names = _obs_type_lines(lines)
 
        self.num_of_obs = len(self.obs_names)

        time_prns, data_list = rx.prn_time_and_data(lines) 

        data = rx.get_data_rows(data_list, time_prns, self.num_of_obs)
       
        self.time_list, self.prns_list = rx.extend_lists(time_prns)

    
        self.obs, self.lli, self.ssi = rx.get_observables(
            data, self.num_of_obs)
        
      
        self._cache = {}

        # Checagem básica de consistência
        n = len(self.prns_list)
        if not ((len(self.time_list) == n == 
                 self.obs.shape[0] == 
                 self.lli.shape[0] == 
                 self.ssi.shape[0])):
            raise ValueError(
                "Inconsistência de tamanhos: "
                f"time={len(self.time_list)}, prn={len(self.prns_list)}, "
                f"obs={self.obs.shape}, lli={self.lli.shape}, ssi={self.ssi.shape}"
            )

    @property
    def prns(self):
        return np.unique(np.asarray(self.prns_list))

    def _make_df(self, values="obs", drop_ssi=None, multiindex=True):
        """
        Cria DataFrame base:
          - index=time (ou MultiIndex time+prn se multiindex=True)
          - colunas = observáveis do header
        """
        if values not in ("obs", "lli", "ssi"):
            raise ValueError("values deve ser 'obs', 'lli' ou 'ssi'.")

        if drop_ssi is None:
            drop_ssi = self.drop_ssi_default

        key = (values, drop_ssi, multiindex)
        if key in self._cache:
            return self._cache[key].copy()

        data = getattr(self, values)

        df = pd.DataFrame(
            data,
            index=pd.to_datetime(self.time_list),
            columns=self.obs_names
        )
        df["prn"] = pd.Index(self.prns_list, dtype="string")

        if drop_ssi:
            # remove S* e D*
            drop_cols = [c for c in df.columns
                         if isinstance(c, str) and 
                         (c.startswith("S") or 
                          c.startswith("D"))]
            df = df.drop(columns=drop_cols, errors="ignore")

        if multiindex:
            df = df.set_index("prn", append=True)
            df.index.names = ["time", "prn"]

        self._cache[key] = df
        return df.copy()

    def dataset(self, values="obs", drop_ssi=None):
        """
        Retorna DataFrame com index=time e coluna 'prn' 
        (compatível com seu estilo antigo).
        """
        return self._make_df(
            values=values, 
            drop_ssi=drop_ssi, 
            multiindex=False)

    def dataset_mi(self, values="obs", drop_ssi=None):
        """
        Retorna DataFrame com MultiIndex (time, prn).
        """
        return self._make_df(
            values=values, 
            drop_ssi=drop_ssi, 
            multiindex=True
            )

    def set_prn_obs(self, prn, drop_ssi=None):
        """
        Observações de um PRN, reduzindo automaticamente para:
          - 2 pseudorange (C* ou P*)
          - 2 fase (L*)
        """
        df = self.dataset(values="obs", drop_ssi=drop_ssi)
        df = df.loc[df["prn"] == prn].drop(columns=["prn"])
        df = df.dropna(axis=1, how="all")

        if df.shape[1] == 4:
            return df

        cols = [c for c in combine_better_obs(df.assign(prn=prn)) 
                if c != "prn"]
        cols = [c for c in cols if c in df.columns]
        return df[cols]

    def set_prn_lli(self, prn, cols, drop_ssi=None):
        """
        LLI para as colunas selecionadas (mantém só L*).
        """
        lli = self.dataset(values="lli", drop_ssi=drop_ssi)
        lli = lli.loc[lli["prn"] == prn, cols]

        lli = lli[[c for c in lli.columns 
                   if isinstance(c, str) and c.startswith("L")]]
        lli.columns = [f"{c}_lli" for c in lli.columns]
        return lli

    def sel(self, prn, drop_ssi=None, dropna=True):
        """
        Dataset final para um PRN:
          - obs selecionadas automaticamente
          - + LLI correspondente
        """
        obs = self.set_prn_obs(prn, drop_ssi=drop_ssi)
        lli = self.set_prn_lli(prn, obs.columns.tolist(), drop_ssi=drop_ssi)

        out = pd.concat([obs, lli], axis=1)
        return out.dropna() if dropna else out





