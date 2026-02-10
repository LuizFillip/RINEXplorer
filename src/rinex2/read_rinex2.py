import RINExplorer as rx 
import pandas as pd 
import numpy as np


def pad_with_nan(arr, target_rows):
    """
    Completa array 2D com linhas NaN até atingir target_rows.
    """
    n_rows, n_cols = arr.shape

    if n_rows >= target_rows:
        return arr

    pad = np.full((target_rows - n_rows, n_cols), np.nan)
    return np.vstack([arr, pad])


class Rinex2:
    """
    Wrapper unificado (novo formato):
      - lê header (rx.HeaderRINEX2)
      - parseia epochs+PRNs e linhas brutas (rx.prn_time_and_data)
      - monta linhas por satélite (rx.get_data_rows)
      - extrai obs/lli/ssi (rx.get_observables)
      - entrega datasets e seleções por PRN
    """

    def __init__(self, infile, drop_ssi_default=True):
        self.infile = infile
        self.drop_ssi_default = drop_ssi_default

        # Header
        self._header = rx.HeaderRINEX2(infile)
        self.header = self._header.attrs
        self.obs_names = list(self._header.obs_names)
        self.num_of_obs = int(self._header.num_of_obs)

        # Dados
        time_prns, raw_data = rx.prn_time_and_data(infile)

        self.time_list, self.prns_list = rx.extend_lists(time_prns)

        data_rows = rx.get_data_rows(raw_data, time_prns, self.num_of_obs)

        self.obs, self.lli, self.ssi = rx.get_observables(data_rows, self.num_of_obs)
        
        n_expected = len(self.time_list)
        n_obs = self.obs.shape[0]
        
        if n_obs != n_expected:
            diff = n_expected - n_obs
            if diff > 0:
                print(f"[WARN] Ajustando {diff} linhas faltantes com NaN")
                self.obs = pad_with_nan(self.obs, n_expected)
                self.lli = pad_with_nan(self.lli, n_expected)
                self.ssi = pad_with_nan(self.ssi, n_expected)

        # Cache para dfs
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
                         if isinstance(c, str) and (c.startswith("S") or c.startswith("D"))]
            df = df.drop(columns=drop_cols, errors="ignore")

        if multiindex:
            df = df.set_index("prn", append=True)
            df.index.names = ["time", "prn"]

        self._cache[key] = df
        return df.copy()

    def dataset(self, values="obs", drop_ssi=None):
        """
        Retorna DataFrame com index=time e coluna 'prn' (compatível com seu estilo antigo).
        """
        return self._make_df(values=values, drop_ssi=drop_ssi, multiindex=False)

    def dataset_mi(self, values="obs", drop_ssi=None):
        """
        Retorna DataFrame com MultiIndex (time, prn).
        """
        return self._make_df(values=values, drop_ssi=drop_ssi, multiindex=True)

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

        cols = [c for c in rx.combine_better_obs(df.assign(prn=prn)) if c != "prn"]
        cols = [c for c in cols if c in df.columns]
        return df[cols]

    def set_prn_lli(self, prn, cols, drop_ssi=None):
        """
        LLI para as colunas selecionadas (mantém só L*).
        """
        lli = self.dataset(values="lli", drop_ssi=drop_ssi)
        lli = lli.loc[lli["prn"] == prn, cols]

        lli = lli[[c for c in lli.columns if isinstance(c, str) and c.startswith("L")]]
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


def test_main():
    infile = 'F:\\database\\GNSS\\rinex\\2010\\001\\alar0011.10o' 
    rnx = Rinex2(infile)
    
    print(rnx.prns)
    
    df = rnx.sel("G26")
    df_all = rnx.dataset_mi(values="obs")
    df 