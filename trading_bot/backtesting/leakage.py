"""Test automático de look-ahead (§6.3 del marco).

Perturba los datos POSTERIORES a un corte y comprueba que ninguna señal ANTERIOR o
igual al corte cambia. Si cambia, la estrategia usa información futura. Se aplica a
toda estrategia antes de aceptarla como candidata.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..strategies.base import SIGNAL_COLUMNS, Strategy


def perturb_future(df: pd.DataFrame, cut: int, seed: int = 0, direction: str = "up") -> pd.DataFrame:
    """Reescala todo lo posterior al corte hacia arriba o hacia abajo (ambas direcciones se
    prueban: una sola podría dejar intacta por azar una comparación con la barra siguiente)."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    m = len(df) - cut - 1
    if m <= 0:
        return out
    f = rng.uniform(1.1, 1.5, m) if direction == "up" else rng.uniform(0.5, 0.9, m)
    for col in ("open", "close"):
        out.iloc[cut + 1:, out.columns.get_loc(col)] = df[col].iloc[cut + 1:].to_numpy() * f
    oc = out[["open", "close"]].iloc[cut + 1:]
    out.iloc[cut + 1:, out.columns.get_loc("high")] = oc.max(axis=1).to_numpy() * rng.uniform(1.0, 1.05, m)
    out.iloc[cut + 1:, out.columns.get_loc("low")] = oc.min(axis=1).to_numpy() * rng.uniform(0.95, 1.0, m)
    out.iloc[cut + 1:, out.columns.get_loc("volume")] = df["volume"].iloc[cut + 1:].to_numpy() * rng.uniform(0.2, 5, m)
    return out


def check_no_lookahead(strategy: Strategy, df: pd.DataFrame, cuts: list[int] | None = None, seed: int = 0) -> list[str]:
    """Devuelve la lista de violaciones (vacía si la estrategia es causal)."""
    base = strategy.generate(df)
    n = len(df)
    cuts = cuts or [n // 4, n // 2, 3 * n // 4]
    problems = []
    for k, cut in enumerate(cuts):
      for direction in ("up", "down"):
        pert = strategy.generate(perturb_future(df, cut, seed + k, direction))
        for col in SIGNAL_COLUMNS:
            a = base[col].iloc[:cut + 1]; b = pert[col].iloc[:cut + 1]
            if a.dtype == bool:
                bad = (a != b)
            else:
                bad = ~(np.isclose(a, b, equal_nan=True, rtol=1e-9, atol=1e-12))
            if bad.any():
                first = a.index[np.argmax(bad.to_numpy())]
                problems.append(f"{strategy}: columna '{col}' cambia en {first} al perturbar ({direction}) datos después de {df.index[cut]}")
    return problems
