"""Adaptadores de exchange. Misma interfaz para el simulador (tests y paper sin cuenta), la
testnet de Binance (paper) y Binance real (live). Toda orden lleva un `client_id` único por
(símbolo, vela, acción): si se reenvía, el exchange devuelve la orden existente en vez de
duplicarla. Esa es la defensa principal contra órdenes duplicadas tras un reinicio.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd


@dataclass
class Fill:
    client_id: str
    symbol: str
    side: str
    qty: float
    price: float
    fee: float
    timestamp: datetime
    exchange_id: str = ""


class ExchangeError(Exception):
    pass


class Exchange(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame: ...
    @abstractmethod
    def ticker(self, symbol: str) -> dict: ...          # {"last", "bid", "ask"}
    @abstractmethod
    def balances(self) -> dict: ...                      # {"USDT": free, "BTC": free, ...}
    @abstractmethod
    def limits(self, symbol: str) -> dict: ...           # {"min_notional", "lot_step"}
    @abstractmethod
    def market_order(self, symbol: str, side: str, qty: float, client_id: str, ref_price: float | None = None) -> Fill: ...
    @abstractmethod
    def find_order(self, symbol: str, client_id: str) -> Fill | None: ...
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class SimulatedExchange(Exchange):
    """Exchange simulado sobre un DataFrame de velas. `cursor` apunta a la vela "actual": las
    velas < cursor están cerradas. Dos fases por vela: "open" (precio = apertura, donde se
    ejecutan señales) e "intrabar" (precio = mínimo de la vela, donde se vigilan stops; una
    venta con `ref_price` se ejecuta en max(ref, mínimo), es decir, en el nivel del stop si la
    vela lo atravesó, como haría una orden a mercado disparada al tocarlo).
    `fail_next` hace fallar las próximas n llamadas (para probar reconexión)."""

    def __init__(self, feeds: dict[str, pd.DataFrame], cash: float = 500.0, fee_pct: float = 0.1,
                 slippage_pct: float = 0.03, limits: dict | None = None):
        self.feeds = feeds
        self.cursor = {s: 1 for s in feeds}
        self.cash = cash
        self.holdings = {s.split("/")[0]: 0.0 for s in feeds}
        self.fee_pct, self.slippage_pct = fee_pct, slippage_pct
        self._limits = limits or {}
        self.orders: dict[str, Fill] = {}
        self.fail_next = 0
        self.calls = 0
        self.phase = "open"

    def _maybe_fail(self):
        self.calls += 1
        if self.fail_next > 0:
            self.fail_next -= 1
            raise ExchangeError("simulated connection failure")

    def advance(self, symbol: str | None = None, n: int = 1):
        for s in ([symbol] if symbol else list(self.feeds)):
            self.cursor[s] = min(self.cursor[s] + n, len(self.feeds[s]) - 1)

    def now(self) -> datetime:
        s = next(iter(self.feeds))
        return self.feeds[s].index[self.cursor[s]].to_pydatetime()

    def fetch_ohlcv(self, symbol, timeframe, limit):
        self._maybe_fail()
        c = self.cursor[symbol]
        df = self.feeds[symbol].iloc[max(0, c + 1 - limit): c + 1].copy()
        # la vela `cursor` está "en curso": se devuelve con open=high=low=close=apertura, como haría la API
        o = df["open"].iloc[-1]
        df.iloc[-1, [df.columns.get_loc(k) for k in ("high", "low", "close")]] = o
        return df

    def ticker(self, symbol):
        self._maybe_fail()
        col = "open" if self.phase == "open" else "low"
        p = float(self.feeds[symbol][col].iloc[self.cursor[symbol]])
        return {"last": p, "bid": p * (1 - 0.00005), "ask": p * (1 + 0.00005)}

    def balances(self):
        self._maybe_fail()
        return {"USDT": self.cash, **self.holdings}

    def limits(self, symbol):
        return self._limits.get(symbol, {"min_notional": 5.0, "lot_step": 1e-5})

    def market_order(self, symbol, side, qty, client_id, ref_price=None):
        self._maybe_fail()
        if client_id in self.orders:
            return self.orders[client_id]
        p = self.ticker(symbol)["last"]
        if self.phase == "intrabar":
            if side == "sell" and ref_price is not None:
                p = max(float(ref_price), p)      # stop tocado: se ejecuta en el nivel del stop
            elif side == "buy":
                bar = self.feeds[symbol].iloc[self.cursor[symbol]]
                p = float((bar["open"] + bar["close"]) / 2)  # reintento "en algún momento de la vela": precio neutro
        price = p * (1 + self.slippage_pct / 100) if side == "buy" else p * (1 - self.slippage_pct / 100)
        fee = price * qty * self.fee_pct / 100
        base = symbol.split("/")[0]
        if side == "buy":
            cost = price * qty + fee
            if cost > self.cash + 1e-9:
                raise ExchangeError("insufficient funds")
            self.cash -= cost; self.holdings[base] += qty
        else:
            if qty > self.holdings[base] + 1e-9:
                raise ExchangeError("insufficient holdings")
            self.cash += price * qty - fee; self.holdings[base] -= qty
        f = Fill(client_id, symbol, side, qty, price, fee, self.now(), exchange_id=f"sim-{len(self.orders)+1}")
        self.orders[client_id] = f
        return f

    def find_order(self, symbol, client_id):
        return self.orders.get(client_id)


class CcxtExchange(Exchange):
    """Binance vía ccxt. `sandbox=True` apunta a la testnet (paper). Reintenta con backoff."""

    def __init__(self, api_key: str, api_secret: str, sandbox: bool = True, retries: int = 3):
        import ccxt
        self.x = ccxt.binance({"apiKey": api_key, "secret": api_secret, "enableRateLimit": True,
                               "options": {"defaultType": "spot"}})
        if sandbox:
            self.x.set_sandbox_mode(True)
        self.x.load_markets()
        self.retries = retries

    def _retry(self, fn, *a, **kw):
        import ccxt
        last = None
        for i in range(self.retries):
            try:
                return fn(*a, **kw)
            except (ccxt.NetworkError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as e:
                last = e; time.sleep(2 ** i)
        raise ExchangeError(str(last))

    def fetch_ohlcv(self, symbol, timeframe, limit):
        rows = self._retry(self.x.fetch_ohlcv, symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp")
        df["quote_volume"] = df["volume"] * df["close"]
        return df

    def ticker(self, symbol):
        t = self._retry(self.x.fetch_ticker, symbol)
        return {"last": float(t["last"]), "bid": float(t.get("bid") or t["last"]), "ask": float(t.get("ask") or t["last"])}

    def balances(self):
        b = self._retry(self.x.fetch_balance)
        return {k: float(v.get("free", 0.0)) for k, v in b.items() if isinstance(v, dict) and "free" in v}

    def limits(self, symbol):
        m = self.x.market(symbol)
        return {"min_notional": float(m["limits"]["cost"]["min"] or 5.0),
                "lot_step": float(m["precision"]["amount"]) if m["precision"]["amount"] < 1 else 10 ** -m["precision"]["amount"]}

    def market_order(self, symbol, side, qty, client_id, ref_price=None):
        existing = self.find_order(symbol, client_id)
        if existing:
            return existing
        qty = float(self.x.amount_to_precision(symbol, qty))
        o = self._retry(self.x.create_order, symbol, "market", side, qty, None, {"newClientOrderId": client_id})
        o = self._retry(self.x.fetch_order, o["id"], symbol)
        return self._to_fill(o, client_id)

    def find_order(self, symbol, client_id):
        import ccxt
        try:
            o = self._retry(self.x.fetch_order, None, symbol, {"origClientOrderId": client_id})
        except (ccxt.OrderNotFound, ExchangeError):
            return None
        return self._to_fill(o, client_id) if o and o.get("status") in ("closed", "filled") else None

    def _to_fill(self, o, client_id):
        fee = sum(float(f.get("cost", 0)) for f in (o.get("fees") or [])) or float((o.get("fee") or {}).get("cost", 0) or 0)
        return Fill(client_id, o["symbol"], o["side"], float(o["filled"]), float(o["average"] or o["price"]), fee,
                    datetime.fromtimestamp(o["timestamp"] / 1000, tz=timezone.utc), exchange_id=str(o["id"]))
