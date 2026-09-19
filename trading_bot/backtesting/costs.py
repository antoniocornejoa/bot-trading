"""Modelo de costes de ejecución en tres escenarios (§6.2 del marco).

Todo en porcentaje por LADO. El precio de referencia es la apertura de la barra de
ejecución (o el nivel del stop/objetivo). El impacto usa el volumen en USD de la barra
ANTERIOR (conocido en la apertura), nunca el de la barra en curso.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class CostScenario:
    name: str
    fee_pct: float            # comisión por lado
    half_spread_pct: float    # medio spread (se cruza en cada lado)
    slippage_pct: float       # deslizamiento fijo por orden a mercado
    impact_coef: float        # impacto = coef · (nocional / volumen USD barra previa), en %
    stop_slippage_mult: float = 1.0  # multiplicador de slippage en stops (gap-through)

    def _adverse_pct(self, notional: float, prev_quote_volume: float, is_stop: bool) -> float:
        impact = 0.0
        if self.impact_coef > 0 and prev_quote_volume and prev_quote_volume > 0:
            impact = self.impact_coef * (notional / prev_quote_volume) * 100.0
        slip = self.slippage_pct * (self.stop_slippage_mult if is_stop else 1.0)
        return self.half_spread_pct + slip + impact

    def buy_fill(self, ref: float, notional: float, prev_quote_volume: float) -> float:
        return ref * (1 + self._adverse_pct(notional, prev_quote_volume, False) / 100.0)

    def sell_fill(self, ref: float, notional: float, prev_quote_volume: float, is_stop: bool = False) -> float:
        return ref * (1 - self._adverse_pct(notional, prev_quote_volume, is_stop) / 100.0)

    def fee(self, fill: float, qty: float) -> float:
        return fill * qty * self.fee_pct / 100.0

    def round_trip_pct(self) -> float:
        """Coste de ida y vuelta sin impacto, para la tabla coste/movimiento."""
        return 2 * (self.fee_pct + self.half_spread_pct + self.slippage_pct)


_DEFAULT_STOP_MULT = {"optimistic": 1.0, "base": 1.0, "pessimistic": 2.0}


def load_scenarios(path: str | Path | None = None) -> dict[str, CostScenario]:
    path = Path(path) if path else Path(__file__).resolve().parents[1] / "config" / "research.yaml"
    cfg = yaml.safe_load(open(path))["costs"]
    return {k: CostScenario(name=k, stop_slippage_mult=_DEFAULT_STOP_MULT.get(k, 1.0), **v)
            for k, v in cfg.items()}
