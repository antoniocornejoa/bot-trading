"""Veredicto del tramo de TEST para H-A2 en BTC+ETH según la regla registrada antes de abrirlo.

    python -m trading_bot.research.test_verdict
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def sym(price: float) -> str:  # el CSV no guarda el símbolo; en el tramo de test los rangos no se solapan
    return "BTC" if price > 20000 else ("ETH" if price > 800 else "SOL")


def slice_metrics(csv: Path, start: str, risk: float = 0.5) -> dict:
    t = pd.read_csv(csv, parse_dates=["entry_time", "exit_time"])
    t["symbol"] = t["entry_price"].map(sym)
    tt = t[(t["entry_time"] >= pd.Timestamp(start, tz="UTC")) & (t["symbol"].isin(["BTC", "ETH"]))].sort_values("exit_time")
    R = tt["r_multiple"].to_numpy(float); pnl = tt["pnl"].to_numpy(float) * risk
    frac = (tt["pnl"] / tt["equity_at_entry"]).to_numpy(float) * risk
    eq = np.concatenate([[500.0], 500 * np.cumprod(1 + frac)])
    dd = (eq / np.maximum.accumulate(eq) - 1).min()
    wins = pnl > 0
    gp, gl = pnl[wins].sum(), -pnl[~wins].sum()
    m = (tt["pnl"] / tt["equity_at_entry"]).groupby(tt["exit_time"].dt.tz_localize(None).dt.to_period("M")).sum()
    return {"ops": len(tt), "BTC": int((tt.symbol == "BTC").sum()), "ETH": int((tt.symbol == "ETH").sum()),
            "win_rate_%": 100 * wins.mean(), "expectancy_R": R.mean(), "t": stats.ttest_1samp(R, 0).statistic,
            "t_mensual": stats.ttest_1samp(m, 0).statistic if len(m) > 2 else np.nan, "meses": len(m),
            "PF": gp / gl if gl else np.inf, f"DD_%_riesgo{risk}": 100 * dd, f"retorno_%_riesgo{risk}": 100 * (eq[-1] / 500 - 1),
            "coste/bruto": (tt.fees.sum() + tt.slippage_cost.sum()) / max((tt.pnl + tt.fees + tt.slippage_cost).sum(), 1e-9),
            "desde": str(tt.entry_time.min().date()), "hasta": str(tt.exit_time.max().date())}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--start", default="2024-11-11", help="inicio del tramo de test de BTC/ETH (80 % del histórico)")
    a = p.parse_args(argv)
    rep = Path(a.root) / "research" / "reports"
    df = pd.DataFrame({sc: slice_metrics(rep / f"trades_H-A2_4h_{sc}_TEST.csv", a.start) for sc in ("base", "pessimistic")}).T
    rule = {"expectancy>0 base y pesimista": bool(df.loc["base", "expectancy_R"] > 0 and df.loc["pessimistic", "expectancy_R"] > 0),
            "PF>=1.3 (base)": bool(df.loc["base", "PF"] >= 1.3), "DD<=20% a 0.5% (base)": bool(df.loc["base", "DD_%_riesgo0.5"] >= -20)}
    L = ["# Veredicto del tramo de TEST · H-A2 (ma_momentum, 4h) · BTC + ETH", "",
         f"Tramo de test: desde {a.start} (20 % final del histórico, nunca usado antes). Regla de decisión escrita antes de abrir el test (ver `trading_bot/research/hypotheses.yaml`).", "",
         "Operaciones del walk-forward cuya entrada cae en el tramo de test, solo BTC y ETH (SOL excluido por no pasar el walk-forward). Riesgo 0,5 % por operación para el drawdown y el retorno.", "",
         df.round(3).to_markdown(), "", "## Regla de decisión", ""] + [f"- {k}: **{'cumple' if v else 'NO cumple'}**" for k, v in rule.items()] + [
         "", f"**Resultado: {'H-A2 pasa el test' if all(rule.values()) else 'H-A2 NO pasa el test'}.**", "",
         "Aviso: el tramo de test tiene menos de dos años y unas 130 operaciones; el t-stat en test por sí solo no alcanza significación. "
         "Lo que se afirma es que la ventaja medida en walk-forward no desapareció fuera de muestra, no que esté demostrada más allá de toda duda. "
         "La siguiente evidencia independiente es el paper trading (Fase 12)."]
    (rep / "05_test_verdict_H-A2.md").write_text("\n".join(L))
    print(df.round(3).to_string()); print(rule)


if __name__ == "__main__":
    main()
