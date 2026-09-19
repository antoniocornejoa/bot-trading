"""Interfaz común de estrategias.

`generate(df)` recibe velas (índice = apertura UTC) y devuelve un DataFrame alineado con
las columnas:
  entry     bool   decidida con el CIERRE de t; el motor la ejecuta en la APERTURA de t+1
  exit      bool   idem, cierra la posición en la apertura de t+1
  stop_dist float  distancia inicial del stop (en precio) para una entrada decidida en t
  tp_dist   float  distancia del objetivo (NaN = sin objetivo)
  trail     float  nivel de stop dinámico calculado en t (NaN = no aplica); el motor lo
                   aplica a partir de t+1 y solo sube, nunca baja

Solo largos: el sistema opera spot. La regla anti look-ahead se verifica con
`backtesting.leakage.check_no_lookahead` sobre cualquier estrategia nueva.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

SIGNAL_COLUMNS = ["entry", "exit", "stop_dist", "tp_dist", "trail"]


class Strategy(ABC):
    name: str = "base"

    def __init__(self, **params):
        self.params = {**self.default_params(), **params}

    @classmethod
    @abstractmethod
    def default_params(cls) -> dict: ...

    @abstractmethod
    def generate(self, df: pd.DataFrame) -> pd.DataFrame: ...

    @staticmethod
    def empty_signals(index: pd.Index) -> pd.DataFrame:
        return pd.DataFrame({
            "entry": np.zeros(len(index), dtype=bool),
            "exit": np.zeros(len(index), dtype=bool),
            "stop_dist": np.full(len(index), np.nan),
            "tp_dist": np.full(len(index), np.nan),
            "trail": np.full(len(index), np.nan),
        }, index=index)

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(f'{k}={v}' for k, v in self.params.items())})"
