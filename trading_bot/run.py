"""Punto de entrada del bot.

    python -m trading_bot.run --mode paper     # testnet de Binance (por defecto)
    python -m trading_bot.run --mode live      # dinero real: exige tres confirmaciones explícitas
    python -m trading_bot.run --mode replay --symbols BTC/USDT --start 2025-01-01   # repetición histórica con exchange simulado
    python -m trading_bot.run --mode paper --once   # un solo ciclo (para cron)
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import yaml

from .data import store as datastore
from .execution.bot import TradingBot
from .execution.exchange import CcxtExchange, SimulatedExchange
from .monitoring.alerts import Alerter
from .portfolio.state import StateStore
from .risk import RiskConfig, RiskEngine
from .strategies import REGISTRY

ROOT = Path(__file__).resolve().parent


def build(cfg: dict, mode: str, root: Path, symbols=None, start=None):
    symbols = symbols or cfg["symbols"]
    strategy = REGISTRY[cfg["strategy"]](**cfg["params"])
    if mode == "replay":
        feeds = {}
        for s in symbols:
            found = datastore.finest_available(root / "data_store" / "parquet", "spot", s.replace("/", ""))
            df = datastore.resample(datastore.load(found[0]), cfg["timeframe"])
            feeds[s] = df[df.index >= start] if start else df
        x = SimulatedExchange(feeds, cash=500.0)
        x.cursor = {s: 300 for s in feeds}
        store = StateStore(":memory:")
    else:
        key, secret = os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET")
        if not key or not secret:
            raise SystemExit("Faltan BINANCE_API_KEY / BINANCE_API_SECRET en el entorno")
        if mode == "live":
            if cfg["PAPER_TRADING"] or not cfg["i_understand_live_risk"] or os.environ.get("LIVE_CONFIRM") != "yes":
                raise SystemExit("Modo live bloqueado: requiere PAPER_TRADING=false, i_understand_live_risk=true y LIVE_CONFIRM=yes")
        x = CcxtExchange(key, secret, sandbox=(mode != "live"))
        Path(cfg["db_path"]).parent.mkdir(parents=True, exist_ok=True)
        store = StateStore(root / cfg["db_path"])
    alerter = Alerter(store, telegram=(mode != "replay"))
    equity0 = float(x.balances().get("USDT", 0.0))
    risk = RiskEngine(RiskConfig(**cfg["risk"]), initial_equity=equity0)
    bot = TradingBot(x, strategy, symbols, cfg["timeframe"], risk, store, alerter, mode=mode)
    bot.reconcile()
    return bot, x


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["paper", "live", "replay"], default="paper")
    p.add_argument("--once", action="store_true")
    p.add_argument("--symbols", nargs="+")
    p.add_argument("--start", default=None)
    p.add_argument("--root", default=".")
    a = p.parse_args(argv)
    cfg = yaml.safe_load(open(ROOT / "config" / "live.yaml"))
    bot, x = build(cfg, a.mode, Path(a.root), a.symbols, a.start)
    if a.mode == "replay":
        n = min(len(f) for f in x.feeds.values())
        while max(x.cursor.values()) < n - 1:
            x.phase = "open"; bot.run_once()
            x.phase = "intrabar"; bot.run_once()
            x.advance()
        x.phase = "open"
        t = bot.store.trades()
        eq, cash = bot.equity()
        print(f"replay: {len(t)} operaciones | PnL cerrado {t['pnl'].sum():+.2f} USD | equity final {eq:.2f} (efectivo {cash:.2f}) | "
              f"win rate {100*(t['pnl']>0).mean():.1f} % | expectancy {t['r_multiple'].mean():.3f} R | slippage total {t['slippage_cost'].sum():.2f} USD")
        return
    bot.alert.send("info", f"bot iniciado en modo {a.mode} | {cfg['symbols']} {cfg['timeframe']} | {bot.strategy}")
    while True:
        try:
            bot.run_once()
        except Exception as e:  # noqa: BLE001
            bot.alert.send("error", f"excepción no controlada en el ciclo: {type(e).__name__}: {e}")
        if a.once:
            break
        time.sleep(cfg["poll_seconds"])


if __name__ == "__main__":
    main()
