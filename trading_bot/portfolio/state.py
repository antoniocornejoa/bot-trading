"""Persistencia (SQLite): posiciones, operaciones, órdenes enviadas, equity y estado de riesgo.

Al reiniciar, el bot reconstruye su estado desde aquí y lo reconcilia con el exchange.
Cada operación registra todo lo que exige el brief (sección 33): tiempos, símbolo, precios,
stop, objetivo, tamaño, riesgo, señales, features, probabilidad, resultado, comisiones,
slippage y PnL, más el precio de referencia para comparar con el backtest.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS positions (
  symbol TEXT PRIMARY KEY, qty REAL, entry_price REAL, entry_ref REAL, entry_fee REAL, entry_time TEXT,
  signal_time TEXT, stop REAL, stop_initial REAL, take_profit REAL, risk_usd REAL, client_id TEXT,
  equity_at_entry REAL, params TEXT, features TEXT, p_win REAL);
CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, signal_time TEXT, entry_time TEXT, exit_time TEXT,
  entry_price REAL, entry_ref REAL, exit_price REAL, exit_ref REAL, qty REAL, stop_initial REAL, stop_final REAL,
  take_profit REAL, risk_usd REAL, reason TEXT, fees REAL, slippage_cost REAL, pnl REAL, r_multiple REAL,
  equity_at_entry REAL, params TEXT, features TEXT, p_win REAL, mode TEXT);
CREATE TABLE IF NOT EXISTS orders (client_id TEXT PRIMARY KEY, symbol TEXT, side TEXT, qty REAL, price REAL,
  fee REAL, timestamp TEXT, exchange_id TEXT);
CREATE TABLE IF NOT EXISTS equity (timestamp TEXT PRIMARY KEY, equity REAL, cash REAL, open_positions INTEGER);
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, level TEXT, message TEXT);
"""


def _iso(t) -> str | None:
    if t is None:
        return None
    return pd.Timestamp(t).isoformat()


class StateStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.con = sqlite3.connect(str(path), detect_types=0)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(SCHEMA)

    # --- kv -------------------------------------------------------------------
    def get(self, key, default=None):
        r = self.con.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

    def set(self, key, value):
        self.con.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (key, json.dumps(value, default=str)))
        self.con.commit()

    # --- órdenes (idempotencia) ---------------------------------------------------
    def order_seen(self, client_id) -> bool:
        return self.con.execute("SELECT 1 FROM orders WHERE client_id=?", (client_id,)).fetchone() is not None

    def record_order(self, fill):
        self.con.execute("INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?,?)",
                         (fill.client_id, fill.symbol, fill.side, fill.qty, fill.price, fill.fee, _iso(fill.timestamp), fill.exchange_id))
        self.con.commit()

    # --- posiciones -----------------------------------------------------------------
    def positions(self) -> dict:
        rows = self.con.execute("SELECT * FROM positions").fetchall()
        out = {}
        for r in rows:
            d = dict(r)
            d["params"] = json.loads(d["params"] or "{}"); d["features"] = json.loads(d["features"] or "{}")
            out[d["symbol"]] = d
        return out

    def upsert_position(self, p: dict):
        d = {**p, "params": json.dumps(p.get("params", {}), default=str), "features": json.dumps(p.get("features", {}), default=str),
             "entry_time": _iso(p.get("entry_time")), "signal_time": _iso(p.get("signal_time"))}
        cols = ["symbol", "qty", "entry_price", "entry_ref", "entry_fee", "entry_time", "signal_time", "stop", "stop_initial",
                "take_profit", "risk_usd", "client_id", "equity_at_entry", "params", "features", "p_win"]
        self.con.execute(f"INSERT OR REPLACE INTO positions ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                         [d.get(c) for c in cols])
        self.con.commit()

    def delete_position(self, symbol):
        self.con.execute("DELETE FROM positions WHERE symbol=?", (symbol,)); self.con.commit()

    # --- operaciones -----------------------------------------------------------------
    def record_trade(self, t: dict):
        d = {**t, "params": json.dumps(t.get("params", {}), default=str), "features": json.dumps(t.get("features", {}), default=str)}
        for k in ("signal_time", "entry_time", "exit_time"):
            d[k] = _iso(d.get(k))
        cols = ["symbol", "signal_time", "entry_time", "exit_time", "entry_price", "entry_ref", "exit_price", "exit_ref", "qty",
                "stop_initial", "stop_final", "take_profit", "risk_usd", "reason", "fees", "slippage_cost", "pnl", "r_multiple",
                "equity_at_entry", "params", "features", "p_win", "mode"]
        self.con.execute(f"INSERT INTO trades ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", [d.get(c) for c in cols])
        self.con.commit()

    def trades(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM trades ORDER BY exit_time", self.con)

    # --- equity y eventos -----------------------------------------------------------
    def snapshot(self, ts, equity, cash, n_pos):
        self.con.execute("INSERT OR REPLACE INTO equity VALUES (?,?,?,?)", (_iso(ts), equity, cash, n_pos)); self.con.commit()

    def equity_curve(self) -> pd.Series:
        df = pd.read_sql("SELECT timestamp, equity FROM equity ORDER BY timestamp", self.con)
        return pd.Series(df["equity"].to_numpy(), index=pd.to_datetime(df["timestamp"]), dtype=float)

    def event(self, ts, level, message):
        self.con.execute("INSERT INTO events (timestamp, level, message) VALUES (?,?,?)", (_iso(ts), level, message)); self.con.commit()

    def events(self, n=50) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM events ORDER BY id DESC LIMIT {int(n)}", self.con)
