"""Motor de riesgo (Fase 10): tamaño por operación, escalones por drawdown, límites diario y
semanal, kill switch y gates de capital.

Los escalones se calibraron con el Monte Carlo de H-A2 a 0,5 % de riesgo (research/reports/
04_phase8_9_H-A2.md): drawdown mediano −9 %, percentil 95 −15 %, peor −26 %.
  DD < 8 %        → riesgo normal (dentro de lo esperado la mitad del tiempo)
  8 %  ≤ DD < 12 % → riesgo × 0,5 (zona entre la mediana y el p95)
  12 % ≤ DD < 18 % → riesgo × 0,25 (más allá del p95: el sistema puede estar degradado)
  DD ≥ 18 %       → sin entradas nuevas hasta revisión manual
  DD ≥ 25 %       → kill switch: cierra posiciones y se detiene (riesgo de ruina definido en el marco)
El drawdown se mide sobre el máximo histórico de la equity (incluidas posiciones abiertas).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone


@dataclass
class RiskConfig:
    risk_pct: float = 0.5                 # % de la equity arriesgado por operación
    max_positions: int = 2                # BTC y ETH
    max_total_risk_pct: float = 1.0       # riesgo abierto total (suma de riesgos iniciales)
    daily_loss_limit_pct: float = 2.0     # pérdida realizada en el día que bloquea nuevas entradas
    weekly_loss_limit_pct: float = 4.0
    dd_tiers: tuple = ((0.08, 1.0), (0.12, 0.5), (0.18, 0.25))  # (umbral superior de DD, multiplicador)
    dd_halt: float = 0.18                 # sin entradas nuevas
    dd_kill: float = 0.25                 # kill switch
    max_consecutive_errors: int = 5
    max_spread_pct: float = 0.15          # spread anormal (BTC/ETH spot suele ser < 0,02 %)
    max_bar_move_pct: float = 15.0        # vela fuera de rango histórico (4h): no operar


@dataclass
class RiskState:
    peak_equity: float
    start_of_day: date | None = None
    day_realized_pnl: float = 0.0
    week_start: date | None = None
    week_realized_pnl: float = 0.0
    consecutive_errors: int = 0
    killed: bool = False
    kill_reason: str = ""
    halted_manual: bool = False
    events: list = field(default_factory=list)


class RiskEngine:
    def __init__(self, cfg: RiskConfig, initial_equity: float, state: RiskState | None = None):
        self.cfg = cfg
        self.state = state or RiskState(peak_equity=initial_equity)

    # --- contabilidad temporal -------------------------------------------------
    def _roll_calendar(self, now: datetime) -> None:
        d = now.date()
        if self.state.start_of_day != d:
            self.state.start_of_day = d
            self.state.day_realized_pnl = 0.0
        monday = d - timedelta(days=d.weekday())
        if self.state.week_start != monday:
            self.state.week_start = monday
            self.state.week_realized_pnl = 0.0

    def record_close(self, pnl: float, now: datetime) -> None:
        self._roll_calendar(now)
        self.state.day_realized_pnl += pnl
        self.state.week_realized_pnl += pnl

    def record_error(self, msg: str) -> None:
        self.state.consecutive_errors += 1
        self.state.events.append(("error", msg))
        if self.state.consecutive_errors >= self.cfg.max_consecutive_errors:
            self.kill(f"{self.state.consecutive_errors} errores consecutivos: {msg}")

    def record_ok(self) -> None:
        self.state.consecutive_errors = 0

    def kill(self, reason: str) -> None:
        if not self.state.killed:
            self.state.killed = True
            self.state.kill_reason = reason
            self.state.events.append(("kill", reason))

    # --- evaluación -------------------------------------------------------------
    def drawdown(self, equity: float) -> float:
        self.state.peak_equity = max(self.state.peak_equity, equity)
        return 1.0 - equity / self.state.peak_equity if self.state.peak_equity > 0 else 0.0

    def risk_multiplier(self, equity: float) -> float:
        dd = self.drawdown(equity)
        if dd >= self.cfg.dd_kill:
            self.kill(f"drawdown {dd:.1%} ≥ {self.cfg.dd_kill:.0%}")
            return 0.0
        if dd >= self.cfg.dd_halt:
            return 0.0
        for upper, mult in self.cfg.dd_tiers:
            if dd < upper:
                return mult
        return 0.0

    def check_market(self, spread_pct: float | None, last_bar_move_pct: float | None) -> str | None:
        if spread_pct is not None and spread_pct > self.cfg.max_spread_pct:
            return f"spread anormal {spread_pct:.3f} %"
        if last_bar_move_pct is not None and abs(last_bar_move_pct) > self.cfg.max_bar_move_pct:
            return f"vela fuera de rango {last_bar_move_pct:.1f} %"
        return None

    def can_open(self, equity: float, now: datetime, open_positions: int, open_risk_usd: float,
                 spread_pct: float | None = None, last_bar_move_pct: float | None = None) -> tuple[bool, str, float]:
        """(permitido, motivo, multiplicador de riesgo)."""
        self._roll_calendar(now)
        mult = self.risk_multiplier(equity)
        if self.state.killed:
            return False, f"kill switch: {self.state.kill_reason}", 0.0
        if self.state.halted_manual:
            return False, "detenido manualmente", 0.0
        if mult == 0.0:
            return False, f"drawdown {self.drawdown(equity):.1%}: sin entradas nuevas hasta revisión", 0.0
        if open_positions >= self.cfg.max_positions:
            return False, "máximo de posiciones abiertas", mult
        if self.state.day_realized_pnl <= -equity * self.cfg.daily_loss_limit_pct / 100:
            return False, "límite de pérdida diaria", mult
        if self.state.week_realized_pnl <= -equity * self.cfg.weekly_loss_limit_pct / 100:
            return False, "límite de pérdida semanal", mult
        if open_risk_usd + equity * self.cfg.risk_pct * mult / 100 > equity * self.cfg.max_total_risk_pct / 100 + 1e-9:
            return False, "riesgo abierto total al máximo", mult
        m = self.check_market(spread_pct, last_bar_move_pct)
        if m:
            return False, m, mult
        return True, "ok", mult

    def position_size(self, equity: float, stop_dist: float, mult: float, price: float, lot_step: float,
                      min_notional: float, cash: float, fee_pct: float = 0.1) -> tuple[float, float]:
        """(cantidad, riesgo_usd). Cantidad 0 si no cumple mínimos."""
        import math
        if stop_dist <= 0 or price <= 0:
            return 0.0, 0.0
        risk_usd = equity * self.cfg.risk_pct * mult / 100
        qty = risk_usd / stop_dist
        qty = min(qty, 0.997 * cash / (price * (1 + fee_pct / 100)))  # margen para spread/slippage del fill
        qty = math.floor(qty / lot_step + 1e-9) * lot_step if lot_step > 0 else qty
        if qty * price < min_notional or qty <= 0:
            return 0.0, 0.0
        return round(qty, 12), qty * stop_dist
