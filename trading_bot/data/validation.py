"""Validación de datos (reglas de §4.3 del marco). Devuelve un informe, no lanza.

La decisión de qué hacer con las barras marcadas la toma el motor: se simulan
(el mercado existió) pero se excluyen del cálculo de métricas si así se configura.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class ValidationReport:
    n_rows: int
    start: pd.Timestamp
    end: pd.Timestamp
    duplicates: int
    gaps: int
    gap_minutes: int
    bad_ohlc: int
    negative_volume: int
    zero_volume: int
    extreme_returns: int
    flagged_index: pd.DatetimeIndex = field(default_factory=lambda: pd.DatetimeIndex([]))

    @property
    def flagged_pct(self) -> float:
        return 100.0 * len(self.flagged_index) / max(self.n_rows, 1)

    def to_markdown(self) -> str:
        lines = [
            f"- Filas: {self.n_rows:,}  ({self.start} → {self.end})",
            f"- Duplicados: {self.duplicates}",
            f"- Huecos: {self.gaps} (minutos ausentes: {self.gap_minutes:,})",
            f"- OHLC incoherentes: {self.bad_ohlc}",
            f"- Volumen negativo: {self.negative_volume}  | volumen cero: {self.zero_volume}",
            f"- Retornos extremos (>|20%| en 1 barra): {self.extreme_returns}",
            f"- Barras marcadas: {len(self.flagged_index):,} ({self.flagged_pct:.3f} %)",
        ]
        return "\n".join(lines)


def validate(df: pd.DataFrame, freq: str = "1min", extreme_ret: float = 0.20) -> ValidationReport:
    df = df.sort_index()
    dup_mask = df.index.duplicated(keep="first")
    duplicates = int(dup_mask.sum())
    d = df[~dup_mask]

    step = pd.Timedelta(freq)
    deltas = pd.Series(d.index[1:] - d.index[:-1])
    gap_mask = deltas > step
    gaps = int(gap_mask.sum())
    gap_minutes = int(((deltas[gap_mask] - step) / pd.Timedelta("1min")).sum()) if gaps else 0

    bad_ohlc_mask = (
        (d["low"] > d[["open", "close"]].min(axis=1))
        | (d["high"] < d[["open", "close"]].max(axis=1))
        | (d["low"] <= 0) | (d["high"] <= 0)
    )
    neg_vol_mask = d["volume"] < 0
    zero_vol_mask = d["volume"] == 0
    ret = d["close"].pct_change().abs()
    extreme_mask = ret > extreme_ret

    flagged = d.index[bad_ohlc_mask | neg_vol_mask | extreme_mask]
    return ValidationReport(
        n_rows=len(df), start=df.index[0], end=df.index[-1], duplicates=duplicates,
        gaps=gaps, gap_minutes=gap_minutes, bad_ohlc=int(bad_ohlc_mask.sum()),
        negative_volume=int(neg_vol_mask.sum()), zero_volume=int(zero_vol_mask.sum()),
        extreme_returns=int(extreme_mask.sum()), flagged_index=flagged,
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina duplicados exactos de índice. No rellena huecos: un hueco es información."""
    df = df.sort_index()
    return df[~df.index.duplicated(keep="first")]


def cross_check(a: pd.DataFrame, b: pd.DataFrame, tol_pct: float = 0.5) -> pd.DataFrame:
    """Compara cierres diarios de dos fuentes; devuelve las fechas con desviación > tol."""
    ca = a["close"].resample("1D").last()
    cb = b["close"].resample("1D").last()
    j = pd.concat({"a": ca, "b": cb}, axis=1).dropna()
    j["dev_pct"] = (j["a"] / j["b"] - 1) * 100
    return j[j["dev_pct"].abs() > tol_pct]
