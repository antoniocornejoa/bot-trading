"""Carga y valida la configuración del bot (config.yaml + .env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VALID_MODES = {"backtest", "paper", "live"}


@dataclass
class Config:
    """Configuración completa del bot, ya validada."""

    raw: dict[str, Any]
    mode: str
    exchange: str
    symbol: str
    timeframe: str
    strategy: dict[str, Any]
    risk: dict[str, Any]
    costes: dict[str, Any]
    backtest: dict[str, Any]
    live_bot: dict[str, Any]
    understand_live_risk: bool

    # Credenciales (se rellenan según el modo)
    api_key: str = ""
    api_secret: str = ""
    use_testnet: bool = True


def load_config(path: str | Path = ROOT / "config.yaml") -> Config:
    """Lee config.yaml, valida los valores y resuelve las claves de API."""
    load_dotenv(ROOT / ".env")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    mode = str(raw.get("mode", "backtest")).lower()
    if mode not in VALID_MODES:
        raise ValueError(
            f"'mode' inválido: {mode!r}. Debe ser uno de {sorted(VALID_MODES)}."
        )

    understand = bool(raw.get("i_understand_live_risk", False))

    cfg = Config(
        raw=raw,
        mode=mode,
        exchange=str(raw["exchange"]).lower(),
        symbol=raw["symbol"],
        timeframe=raw["timeframe"],
        strategy=raw["strategy"],
        risk=raw["risk"],
        costes=raw["costes"],
        backtest=raw["backtest"],
        live_bot=raw["live_bot"],
        understand_live_risk=understand,
    )

    _resolve_credentials(cfg)
    _validate(cfg)
    return cfg


def _resolve_credentials(cfg: Config) -> None:
    """Selecciona las claves de testnet o reales según el modo."""
    if cfg.mode == "live":
        cfg.use_testnet = False
        cfg.api_key = os.getenv("BINANCE_API_KEY", "")
        cfg.api_secret = os.getenv("BINANCE_API_SECRET", "")
    else:
        # backtest no necesita claves; paper usa testnet.
        cfg.use_testnet = True
        cfg.api_key = os.getenv("BINANCE_TESTNET_API_KEY", "")
        cfg.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "")


def _validate(cfg: Config) -> None:
    """Comprobaciones de seguridad antes de dejar arrancar el bot."""
    # El gran seguro anti-accidentes para dinero real.
    if cfg.mode == "live":
        if not cfg.understand_live_risk:
            raise SystemExit(
                "\n[BLOQUEADO] mode=live pero 'i_understand_live_risk' es false.\n"
                "Para operar con dinero REAL debes cambiarlo a true en config.yaml\n"
                "de forma consciente. El bot no arranca en real por accidente.\n"
            )
        if not cfg.api_key or not cfg.api_secret:
            raise SystemExit(
                "\n[BLOQUEADO] modo real sin claves. Rellena BINANCE_API_KEY y\n"
                "BINANCE_API_SECRET en el archivo .env.\n"
            )

    if cfg.mode == "paper" and (not cfg.api_key or not cfg.api_secret):
        raise SystemExit(
            "\n[BLOQUEADO] modo paper sin claves de testnet.\n"
            "Crea claves gratis en https://testnet.binance.vision/ y ponlas en .env\n"
            "(BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET).\n"
        )

    r = cfg.risk
    if not (0 < r["riesgo_por_operacion_pct"] <= 100):
        raise ValueError("riesgo_por_operacion_pct debe estar entre 0 y 100.")
    if r["stop_loss_atr_mult"] <= 0:
        raise ValueError("stop_loss_atr_mult debe ser mayor que 0.")
    if cfg.strategy["ema_fast"] >= cfg.strategy["ema_slow"]:
        raise ValueError("ema_fast debe ser menor que ema_slow.")
