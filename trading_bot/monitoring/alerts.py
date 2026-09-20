"""Alertas: siempre a stdout y a la base de datos; opcionalmente a Telegram si existen las
variables de entorno TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID."""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone


class Alerter:
    LEVELS = ("info", "trade", "warning", "error", "kill")

    def __init__(self, store=None, telegram: bool = True):
        self.store = store
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN") if telegram else None
        self.chat = os.environ.get("TELEGRAM_CHAT_ID") if telegram else None
        self.sent: list = []

    def send(self, level: str, message: str, ts: datetime | None = None) -> None:
        ts = ts or datetime.now(timezone.utc)
        line = f"[{ts:%Y-%m-%d %H:%M:%S}] {level.upper()}: {message}"
        print(line, flush=True)
        self.sent.append((level, message))
        if self.store is not None:
            self.store.event(ts, level, message)
        if self.token and self.chat and level != "info":
            try:
                data = json.dumps({"chat_id": self.chat, "text": line}).encode()
                req = urllib.request.Request(f"https://api.telegram.org/bot{self.token}/sendMessage", data=data,
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=10)
            except Exception as e:  # noqa: BLE001 - una alerta fallida no debe tumbar el bot
                print(f"[alerta] fallo enviando a Telegram: {e}", flush=True)
