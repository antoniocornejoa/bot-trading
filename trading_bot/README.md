# trading_bot · sistema cuantitativo (en construcción)

Paquete nuevo del proyecto de investigación descrito en `research/00_MARCO_INVESTIGACION.md`.
El bot antiguo de `src/` sigue intacto como referencia.

## Estado

| Fase | Módulo | Estado |
|---|---|---|
| 2 Hipótesis | `research/hypotheses.yaml` | registradas H-A1, H-G1, H-H1 y benchmarks; M = 52 |
| 3 Datos | `data/binance_vision.py`, `data/kraken.py`, `data/validation.py`, `data/store.py` | listo; **se ejecuta en tu equipo** |
| 1 Mercados | `research/market_profile.py` | listo; necesita los datos de la fase 3 |
| 4 Backtester | `backtesting/engine.py`, `costs.py`, `metrics.py`, `leakage.py` | núcleo listo y testeado; faltan walk-forward, sensibilidad y Monte Carlo |
| 5 Candidatas | `strategies/trend.py`, `strategies/pullback.py` | implementadas, sin evaluar |

## Qué ejecutar en tu equipo (una vez)

Requiere Python 3.11+ y acceso a internet (Binance y Kraken están disponibles desde Chile).

```bash
cd bot-trading
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r trading_bot/requirements.txt

# 1) Histórico completo de velas 1m spot (BTC/ETH desde 2017-08, SOL desde 2020-08). ~2-3 GB, 20-40 min.
python -m trading_bot.data.binance_vision --markets spot

# 2) Opcional pero recomendado: perpetuos y funding (para costes y features)
python -m trading_bot.data.binance_vision --markets futures funding --symbols BTCUSDT ETHUSDT --start 2019-09

# 3) Contraste de calidad con Kraken (cierres diarios)
python -m trading_bot.data.kraken

# 4) Fichas de mercado (Fase 1)
python -m trading_bot.research.market_profile
```

Resultados:
- `data_store/parquet/spot/<SYMBOL>_klines_1m.parquet` + `*.validation.md` (informe de calidad y hash).
- `research/reports/01_market_profile.md`: **súbelo al repositorio** (o pégalo en la conversación). Con él se decide el timeframe y se abre la Fase 5.

`data_store/` está en `.gitignore`: los datos no se suben, solo los informes.

## Tests

```bash
python -m pytest trading_bot/tests -q
```

Incluye el test de look-ahead (`backtesting/leakage.py`), que toda estrategia nueva debe pasar.

## Convenciones que no se negocian

- Índice de velas = apertura UTC. Se decide con el cierre de `t`, se ejecuta en la apertura de `t+1`.
- Stop y objetivo en la misma vela → se asume stop.
- Costes en tres escenarios; las decisiones se toman con el **base**.
- Toda hipótesis se registra antes de probarse. El test se abre una sola vez.
