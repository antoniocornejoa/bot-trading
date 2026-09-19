# Fase 0 · Marco de investigación cuantitativa

**Proyecto:** sistema de trading algorítmico con capital inicial de US$500 y escalamiento condicionado a evidencia estadística.
**Estado:** propuesta de marco. No se ha optimizado ninguna estrategia. No existe todavía ningún resultado.
**Fecha:** 2026-09-19

Este documento responde a la "primera tarea": fijar *cómo* se va a investigar y *qué* haría falta para afirmar que una estrategia tiene ventaja estadística, antes de escribir el sistema. Todo lo que aquí se afirma sobre mercados y estrategias son **hipótesis a contrastar con datos**, no conclusiones.

---

## 0. Posición inicial honesta (léase antes que nada)

1. **La tasa base es desfavorable.** La mayoría de las estrategias técnicas simples sobre activos líquidos no sobreviven a los costes reales. El resultado más probable de una investigación honesta es "no hay evidencia suficiente" para varias familias. El marco está diseñado para llegar a esa conclusión rápido y barato cuando sea la correcta (sección 9, reglas de parada).

2. **US$500 no es un capital para ganar dinero, es un capital para comprar información.** Con una expectativa realista de un sistema robusto (10–30 % anual) el resultado esperado del primer año es de US$50–150. La infraestructura mínima (un VPS de US$5/mes) ya consume el 12 % anual del capital. La primera etapa se mide por *si el proceso funciona en vivo como en el backtest*, no por el dinero.

3. **La estadística manda sobre el calendario.** Demostrar una ventaja exige un número mínimo de operaciones independientes (sección 6.4). Ese número, dividido por la frecuencia de la estrategia, fija cuánto tiempo tarda cada gate de capital. Un sistema diario en un solo activo (~25 operaciones/año) *no puede* validarse en vivo en un plazo razonable. Esto restringe timeframes y número de activos tanto como los costes.

4. **Restricción de este entorno.** La sesión de Claude Code en la que se redacta esto tiene la red bloqueada por política hacia todos los proveedores de datos probados (Binance, Kraken, Yahoo, Stooq, Alpaca, OANDA, Dukascopy: 403 del proxy). PyPI sí está permitido. Por tanto, la descarga de datos (Fase 3) deberá ejecutarse en el ordenador o VPS del propietario, o habrá que ampliar la política de red de la sesión. El código de descarga se puede escribir y probar con datos sintéticos aquí, pero no ejecutar contra los proveedores.

5. **Qué se hereda del repositorio actual.** El bot existente (`src/`) tiene un backtester de barras con ejecución en la apertura siguiente, comisiones y slippage, un explorador con separación train/test y un broker ccxt para Binance. Es correcto en su nivel, pero no cubre walk-forward, Monte Carlo, múltiples estrategias ni contabilidad de portfolio. Se construirá un paquete nuevo (`trading_bot/`) y el bot actual queda como referencia hasta reemplazarlo.

---

## 1. Mercados candidatos

### 1.1 Filtro previo por viabilidad con US$500

Antes de mirar ningún backtest, varios mercados quedan fuera o condicionados por restricciones de ejecución que ningún backtest puede arreglar.

| Mercado | Viable con US$500 | Restricción determinante |
|---|---|---|
| Futuros de índices (ES, NQ, incluso micros MES/MNQ) | **No** | Margen intradía de un micro ~US$1.500–2.500. Overnight más. |
| CFDs sobre índices | Condicional | Viable por tamaño, pero spread + financiación overnight + calidad del broker. Automatización vía MT5/cTrader. Riesgo de contraparte. |
| ETF (SPY, QQQ, IWM, GLD) | Condicional | **PDT rule**: con menos de US$25.000 en cuenta de margen, máximo 3 day-trades en 5 días hábiles. En cuenta cash no aplica PDT pero el efectivo liquida T+1. Consecuencia: solo estrategias de *swing* (holding ≥ 1 día). Fraccionarios disponibles (Alpaca, IBKR). Comisión IBKR Pro ~US$0,35 mínimo/orden = 0,07 % sobre US$500; Alpaca 0. Elegibilidad del broker para residentes de Chile: **verificar** (IBKR sí; Alpaca según país). |
| Forex spot (EUR/USD, GBP/USD, USD/JPY) | **Sí** | Tamaño mínimo 1 unidad (OANDA) o micro-lote. Spread EUR/USD ~0,6–1 pip ≈ 0,006–0,01 %: **el coste de transacción más bajo de la lista**. Apalancamiento disponible (usarlo solo para dimensionar, no para amplificar). 24/5. Verificar disponibilidad de OANDA/IBKR en Chile. |
| Cripto spot (BTC, ETH, SOL) | **Sí** | Orden mínima ~US$5–10. 24/7. API excelente (ya integrada). Coste alto: 0,1 % por lado (0,075 % con BNB) → ida y vuelta ≈ 0,20 % + slippage ≈ 0,25–0,30 %. |
| Cripto perpetuos (BTC, ETH) | Condicional | Taker 0,05 %, maker 0,02 %. Funding cada 8 h. Permite corto y acceso a funding/OI como features. Riesgo de liquidación si se usa apalancamiento; se usaría 1× o menos. Disponibilidad regulatoria según país. |
| Oro spot / XAU/USD vía FX broker | Sí | Spread ~0,02–0,03 %. Alternativa a GLD sin PDT. |

### 1.2 Consecuencia inmediata: el coste fija el timeframe mínimo

Regla de decisión previa a cualquier backtest: **una estrategia solo es candidata en un timeframe si el coste de ida y vuelta es inferior al 20–25 % del movimiento típico de la barra** (mediana del rango |close−open| o del ATR). Si el coste supera ese umbral, la ventaja tendría que ser implausiblemente grande para sobrevivir. Cifras orientativas que se verificarán con datos:

| Activo / timeframe | Movimiento típico por barra | Coste ida y vuelta | Ratio coste/movimiento | Candidato |
|---|---|---|---|---|
| BTC spot 1 m | ~0,05 % | 0,25 % | 5× | **Excluido a priori** |
| BTC spot 5 m | ~0,10 % | 0,25 % | 2,5× | **Excluido a priori** |
| BTC spot 15 m | ~0,20 % | 0,25 % | 1,2× | Excluido |
| BTC spot 1 h | ~0,45 % | 0,25 % | 0,55 | Marginal, solo con baja rotación |
| BTC spot 4 h | ~1,0 % | 0,25 % | 0,25 | Sí |
| BTC spot 1 d | ~2,0 % | 0,25 % | 0,12 | Sí |
| BTC perp 15 m (maker) | ~0,20 % | ~0,08 % | 0,4 | Marginal |
| EUR/USD 15 m | ~0,05 % | ~0,012 % | 0,24 | Sí (por coste) |
| EUR/USD 1 h | ~0,10 % | ~0,012 % | 0,12 | Sí |
| SPY 1 d | ~0,7 % | ~0,03–0,1 % | 0,05–0,15 | Sí (swing) |

Esto responde a la sección 4 del brief sin necesidad de backtest: **1 m y 5 m quedan descartados en cripto spot por coste**, y solo serían reconsiderables en FX o en perpetuos con órdenes maker, donde aparece otro problema (incertidumbre de ejecución) que se trata en 6.2.

### 1.3 Dimensiones que se medirán por mercado (Fase 1)

Para cada activo candidato se producirá una ficha con datos, no con opiniones:

- **Liquidez y coste**: volumen diario en USD, spread medio y percentil 95 por hora del día, profundidad a 10 pb (cripto: del order book; FX/ETF: del broker).
- **Volatilidad**: realized vol anualizada, distribución por hora del día y día de la semana, autocorrelación de la volatilidad (clustering).
- **Estructura de retornos**: autocorrelación de retornos a 1, 5, 20 barras (positiva → momentum, negativa → reversión), variance ratio test (Lo–MacKinlay), Hurst exponent por ventanas. Esto dice *qué familia de estrategia tiene sentido económico* en ese activo y timeframe **antes** de probarla.
- **Colas**: curtosis, frecuencia de saltos > 4σ, gaps (ETF) y velas de liquidación (cripto).
- **Horarios**: FX y ETF tienen sesiones; cripto es 24/7 pero con actividad concentrada en horario EE. UU./Europa.
- **Correlación cruzada**: entre activos y con SPY/DXY/VIX para saber si diversificar aporta algo.
- **Automatización**: API disponible, testnet/paper, latencia, límites de tasa, fiabilidad histórica.
- **Capital mínimo / máximo**: orden mínima, y capital al que el tamaño de orden supera el 1 % del volumen del libro en los primeros niveles (primer indicio de impacto).

### 1.4 Hipótesis inicial (a refutar), no conclusión

Por ejecución, cripto spot y FX son los únicos donde US$500 opera sin fricción regulatoria. Por coste, FX es claramente mejor; por documentación académica de ventajas persistentes (momentum de series temporales, carry vía funding), cripto tiene más literatura reciente. Los ETF solo entran en swing diario. **La decisión se tomará con las fichas de 1.3 y los resultados de Fase 5–6, no con esta hipótesis.**

Sesgo de supervivencia reconocido: elegir BTC/ETH/SOL "porque son los grandes hoy" ya es un sesgo. Mitigación: cualquier resultado en cripto se contrastará también sobre el universo de los 10 mayores por capitalización *en cada fecha* (datos de CoinGecko/CoinMarketCap históricos), incluyendo activos que luego cayeron.

---

## 2. Timeframes candidatos

Derivado de 1.2 y de la necesidad estadística de la sección 6.4:

| Timeframe | Rol | Justificación |
|---|---|---|
| **4 h** | Primario para cripto | Coste tolerable, ~2.190 barras/año, ~40–120 operaciones/año por activo según familia. Suficiente para acumular muestra en 3 activos en meses, no años. |
| **1 d** | Primario para ETF/FX, secundario en cripto | Menor ruido, estrategias de tendencia y reversión mejor documentadas. Pocas operaciones: exige varios activos para tener muestra. |
| **1 h** | Secundario / features multi-timeframe | Solo para estrategias con holding de días (baja rotación) o como fuente de features intradía para decisiones en 4 h. |
| **15 m** | Solo FX, y perps con maker | Se evalúa únicamente si FX resulta candidato. |
| 1 m / 5 m | **Excluidos** | Coste > movimiento en spot. Además, la calidad de simulación de fills a esa escala sin datos de libro es insuficiente para afirmar nada. |

Criterio de elección final (Fase 6): el timeframe que maximice `expectancy neta por operación × operaciones/año` sujeto a `drawdown máximo`, `ratio coste/beneficio bruto < 35 %` y `estabilidad walk-forward`. No se elegirá por número de operaciones ni por retorno bruto.

---

## 3. Estrategias candidatas

Cada familia se registra con hipótesis económica y condiciones de fallo *antes* de probarla. Si no puede explicarse por qué debería ganar dinero, no se prueba (sección 10, "data dredging").

| Familia | Hipótesis económica | Entrada / salida (esquema) | Cuándo funciona | Cuándo falla | Prioridad |
|---|---|---|---|---|---|
| **A. Trend following (time-series momentum)** | Reacción lenta a información, herding, flujos. Documentado en 50+ años y en cripto. | Precio > media N o ruptura de canal Donchian; salida por stop de volatilidad o cruce inverso. | Tendencias largas (2020–21, 2023–24 cripto). | Rangos prolongados: muchas pérdidas pequeñas (whipsaw). Win rate típico 35–45 %, payoff > 2. | Alta |
| **B. Momentum cross-sectional** | Persistencia relativa entre activos. | Largo el activo con mejor retorno a 1–3 meses del universo, rebalanceo semanal. | Dispersión alta entre activos. | Reversiones bruscas de régimen (momentum crash). | Media (requiere universo ≥ 5 activos) |
| **C. Mean reversion** | Sobre-reacción a corto plazo, provisión de liquidez. | Entrada tras caída extrema (RSI2, z-score) en tendencia mayor alcista; salida en retorno a la media o tiempo. | Mercados en rango, baja vol. | Crisis: el "extremo" sigue extendiéndose; colas gordas. Riesgo de win rate alto con pérdida catastrófica → vigilar (sección 39 del brief). | Media |
| **D. Breakout** | Cambio de información concentrado; participación tras confirmación. | Ruptura de máximo N barras con volumen relativo; stop bajo el rango. | Tras compresión de volatilidad. | Falsos breakouts en rango; costes por rotación. Solapa con A. | Media (se prueba como variante de A) |
| **E. Expansión de volatilidad** | Vol clustering: tras expansión, continúa. | Entrar en dirección del movimiento cuando ATR salta > k× su media. | Inicio de tendencia. | Picos de vol de una sola barra (liquidaciones). | Baja (se usa más como filtro) |
| **F. Contracción de volatilidad** | Compresión precede expansión (squeeze). | Rango N barras en percentil bajo → orden en ambos lados. | Pre-eventos, consolidaciones. | Direccionalidad no predecible: es un filtro, no una señal. | Baja (filtro para A/D) |
| **G. Pullback en tendencia** | Combina A y C: comprar retrocesos en tendencia confirmada. | Tendencia (precio > MA lenta, ADX) + retroceso (RSI corto, distancia a MA rápida) → entrada; salida por objetivo ATR o fallo de tendencia. | Tendencias con ruido. | Tendencia que termina justo en el pullback. | **Alta** (mejor balance win rate / payoff a priori) |
| **H. Detección de régimen** | Las familias anteriores tienen regímenes favorables distintos. | No es estrategia: es un clasificador (vol alta/baja, tendencia/rango) que activa/desactiva o pondera A–G. | Siempre, como capa. | Cambios de régimen abruptos (lag). | Alta (capa transversal) |
| **I. Arbitraje estadístico** | Cointegración (p. ej. ETH/BTC), basis spot-perp, funding carry. | Spread z-score; funding: cobrar carry cuando funding extremo. | Spread estable. | Ruptura de cointegración; con US$500 el basis/carry requiere dos patas y el mínimo de orden lo hace inviable. | Baja hasta > US$5.000 |
| **J. Multi-factor** | Combinar señales débiles no correlacionadas. | Score = suma ponderada de A, C, vol, volumen; operar si score > umbral. | Cuando las señales individuales son marginales. | Sobreajuste de pesos. | Media (Fase 8) |
| **K. Machine learning** | Meta-etiquetado: P(win | features) para *filtrar* operaciones de A/G. | Modelo estima probabilidad de que la operación primaria termine en beneficio; se opera si EV > 0 tras costes. | Si existen features con información condicional real. | Casi siempre cuando se usa para predecir precio. Solo se acepta si supera a la estrategia base en walk-forward (Fase 7). | Condicional |
| **L. Combinación** | Estrategias con retornos poco correlacionados reducen DD del conjunto. | Asignación por riesgo (vol-parity) entre las que pasen los gates individuales. | Correlación < 0,3 entre estrategias. | Correlación que sube en crisis. | Fase 11 |

**Lo que no se prueba** (sección 6 del brief): martingala, grid, promediar pérdidas, aumentar tras perder, stops desproporcionados, apalancamiento > 2× en cualquier caso, y cualquier estrategia cuya expectativa dependa de vender colas (win rate > 80 % con payoff < 0,5).

Familias con **prioridad alta** en Fase 5: A, G y H. Las demás se prueban en Fase 5 como benchmarks o en fases posteriores.

---

## 4. Datos necesarios

### 4.1 Datos primarios (obligatorios)

| Dato | Granularidad | Historia mínima | Uso |
|---|---|---|---|
| OHLCV cripto spot BTC, ETH, SOL (+ top-10 histórico) | 1 m (para agregar a 15 m/1 h/4 h/1 d y para estimar fills) | BTC/ETH desde 2017-08; SOL desde 2020-08 | Todo |
| OHLCV perps BTC, ETH | 1 m | Desde 2019-09 (Binance) | Comparación de costes, features |
| Funding rate BTC, ETH | 8 h | Completa (2019-09) | Feature de posicionamiento / carry |
| Open interest | 5 m – 1 h | Solo 30 días vía API; histórico vía Coinglass/CryptoQuant (de pago) o acumulación propia desde hoy | Feature, si hay historia |
| OHLCV ETF SPY, QQQ, IWM, GLD | 1 d (ajustado por dividendos y splits) + 1 h si disponible | ≥ 2005 (incluye 2008, 2020, 2022) | Swing diario |
| OHLCV FX EUR/USD, GBP/USD, USD/JPY | 1 m (tick si disponible, para spread) | ≥ 2010 | Todo |
| VIX diario | 1 d | ≥ 2005 | Régimen para ETF |
| DXY o USD index | 1 d | ≥ 2010 | Régimen FX/cripto |
| Calendario de eventos macro (FOMC, NFP, CPI) | Evento | ≥ 2015 | Filtro de "no operar" en FX/ETF |

### 4.2 Datos de mercado para costes realistas

- **Spread histórico**: cripto: snapshots de mejor bid/ask (Binance `bookTicker` acumulado por nosotros, o datos de Tardis/Kaiko de pago). FX: spread real de la cuenta demo del broker. ETF: NBBO no disponible gratis; se usa un modelo (spread ≈ 1 tick para SPY/QQQ).
- **Slippage**: se estima con el modelo de la sección 6.2, calibrado después con las órdenes reales del paper trading. **La calibración con órdenes propias es un entregable de Fase 12.**

### 4.3 Requisitos de calidad (validación automática en Fase 4)

- Continuidad temporal: sin huecos ni duplicados; cada hueco se registra y se decide (rellenar sólo para features, nunca para ejecución).
- OHLC coherente: `low ≤ min(open, close)`, `high ≥ max(open, close)`.
- Volumen no negativo; barras con volumen cero marcadas.
- Comparación cruzada BTC Binance vs Kraken: desviación de cierre > 0,5 % se marca como sospechosa.
- ETF: verificación de ajuste por dividendos (comparar precio ajustado vs no ajustado en ex-dates conocidas).
- Marca de tiempo: todo en UTC, timestamp = *apertura* de la barra, y la barra sólo es "conocida" en `timestamp + duración` (regla anti look-ahead codificada en el loader, no en cada estrategia).

---

## 5. Fuentes de datos

| Fuente | Cubre | Coste | Historia | Notas |
|---|---|---|---|---|
| **Binance `data.binance.vision`** | Spot y futuros, klines 1 m, funding, trades agregados | Gratis | Completa | Descarga masiva en ZIP mensuales/diarios. Fuente principal cripto. |
| Binance REST (ccxt) | Idem, OI últimos 30 días, bookTicker en vivo | Gratis | Completa (paginado) | Ya integrado en `src/data.py`. Bloqueado desde EE. UU. |
| Kraken REST | Spot BTC/ETH/SOL | Gratis | Sólo 720 barras por llamada; histórico completo vía CSV oficial trimestral | Contraste de calidad y alternativa. |
| CoinGecko / CoinMarketCap histórico | Ranking por capitalización por fecha | Gratis (limitado) | 2013+ | Para el universo sin sesgo de supervivencia. |
| Coinglass / CryptoQuant | OI, liquidaciones, long/short ratio | De pago (US$30–100/mes) | 2020+ | **No se contrata en Fase 1**. Sólo si A/G muestran ventaja y se quiere mejorar con ML. |
| **yfinance** | ETF/VIX diario ajustado; intradía 1 h limitado a 730 días, 1 m a 30 días | Gratis | 1993+ diario | Diario fiable; intradía insuficiente para investigación. |
| Stooq | ETF/índices diario | Gratis | Largo | Contraste. |
| **Alpaca Data API** (feed IEX) | Acciones/ETF 1 m desde 2016 | Gratis con cuenta | 2016+ | Mejor opción gratuita intradía en ETF. Verificar disponibilidad de cuenta en Chile. |
| Tiingo / Polygon | ETF intradía completo | US$10–30/mes | Largo | Sólo si ETF intradía resulta candidato (poco probable por PDT). |
| **Dukascopy** | FX tick desde 2003 | Gratis | Completa | Fuente principal FX. Descarga vía `dukascopy-node` o script propio. |
| OANDA v20 API | FX velas 5 s – 1 M, spread real | Gratis con cuenta demo | 2005+ | Fuente de ejecución y de spread real. |
| histdata.com | FX 1 m | Gratis | 2000+ | Contraste. |
| FRED | VIX, tipos, DXY | Gratis | Largo | Régimen macro. |
| ForexFactory / Investing calendario | Eventos macro | Gratis (scraping frágil) | 2007+ | Filtro de eventos. |

**Decisión de Fase 3:** solo fuentes gratuitas. El coste de datos de pago no se justifica con US$500 salvo que una familia ya muestre ventaja sin ellos.

---

## 6. Metodología de backtesting y de demostración de la ventaja

Esta es la sección central: *cómo se va a demostrar que una estrategia tiene ventaja*.

### 6.1 Motor

- **Motor propio, dirigido por eventos, sobre barras**, evolucionando el diseño actual: decisión con el cierre de la barra *t*, ejecución en la barra *t+1* con modelo de fill explícito. Portfolio multi-activo y multi-estrategia con contabilidad en USD, posiciones fraccionarias, comisiones por lado, funding para perps, y **tamaño mínimo y redondeo de lote del exchange real** (con US$500 esto cambia resultados: una orden de US$4 no se puede enviar).
- **Verificación cruzada**: las estrategias más simples (cruce de medias, Donchian) se replican en `backtesting.py` o `vectorbt` y los resultados deben coincidir dentro de tolerancia. Esto detecta errores del motor, no de la estrategia.
- **Semilla y determinismo**: cualquier componente estocástico (Monte Carlo, ML) fija semilla y registra versión de datos (hash del dataset).

### 6.2 Modelo de costes en tres escenarios

| Componente | Optimista | Base | Pesimista |
|---|---|---|---|
| Comisión cripto spot | 0,075 % | 0,10 % | 0,10 % |
| Spread cripto (mitad) | 0,005 % | 0,01 % | 0,03 % |
| Slippage cripto (mercado) | 0,01 % | 0,03 % + término proporcional a `tamaño / volumen_barra` | 0,10 % + mismo término × 2 |
| Comisión ETF | 0 | US$0,35/orden | US$1/orden |
| Spread ETF | 1 tick | 1 tick | 2 ticks + 0,02 % en apertura/cierre |
| FX spread EUR/USD | 0,6 pip | 1,0 pip | 2,0 pip (y 5 pip en eventos macro) |
| Latencia | 0 | 1 barra (ya implícita en t+1) | 1 barra + fill al peor de open/close ± 25 % del rango |
| Funding perps | histórico | histórico | histórico × 1,5 cuando adverso |
| Stops | Fill en el nivel | Fill en el nivel − slippage base | Fill en `min(nivel, low de la barra)` ponderado (gap-through) |

**El escenario base es el que decide.** Una estrategia que solo funciona en optimista se descarta. El pesimista se usa para dimensionar el kill switch y los gates.

Para stops y objetivos intrabarra: si en la misma barra se tocan stop y objetivo, **se asume que se ejecutó el stop** (regla conservadora). Con datos de 1 m se resolverá el orden real de toque cuando haya datos.

### 6.3 Protocolo anti-sesgos

| Sesgo | Control |
|---|---|
| Look-ahead | Loader que expone barras solo hasta `t`; features calculadas con `shift` obligatorio; **test automático** que perturba datos futuros y verifica que ninguna señal en `t` cambia. |
| Data leakage en ML | Purged K-fold con embargo (López de Prado) o, mejor, walk-forward puro; etiquetas construidas con triple barrera y sin solapamiento de ventanas entre train/test. Escalado de features ajustado sólo en train. |
| Supervivencia | Universo cripto por capitalización a fecha; ETF elegidos son índices amplios (bajo riesgo). |
| Selección | **Registro de hipótesis** (`research/hypotheses.yaml`): cada estrategia, parámetro y activo probado se registra antes de correrlo con su justificación económica. El número total de pruebas `M` alimenta la corrección de 6.5. |
| Overfitting | Sensibilidad ±5/10/20/30 % en parámetros (sección 24 del brief); *Probability of Backtest Overfitting* (CSCV, Bailey et al.) sobre el conjunto de configuraciones; parámetros elegidos por **meseta**, no por pico. |
| Datos sucios | Validación 4.3, y eliminación de barras marcadas del cálculo de métricas (no de la simulación). |

### 6.4 Cuántas operaciones hacen falta (potencia estadística)

Para una estrategia con expectativa por operación `E` y desviación típica `σ` (ambas en unidades de R = riesgo por operación), el estadístico t de la media es `t = (E/σ)·√N`. Valores típicos de sistemas decentes: `E/σ ≈ 0,10–0,20`.

| E/σ | N para t = 2,0 (p≈0,05) | N para t = 3,0 (umbral tras corrección por múltiples pruebas) |
|---|---|---|
| 0,10 | 400 | 900 |
| 0,15 | 180 | 400 |
| 0,20 | 100 | 225 |

Conclusiones operativas:

- **Backtest**: se exigen ≥ 300 operaciones *fuera de muestra acumuladas* (walk-forward) por estrategia, sumando activos, y ≥ 100 por activo si se afirma algo de un activo.
- **Paper / micro-capital**: con 4 h en 3 activos y ~80 op/año/activo, 100 operaciones se alcanzan en ~5 meses; con diario en 4 ETF (~25 op/año/activo), en ~12 meses. Esto es lo que fija los plazos de los gates de capital, no un calendario arbitrario.
- El Sharpe tiene error estándar `≈ √((1 + SR²/2)/T)` en años: un Sharpe de 1,0 con 3 años tiene SE ≈ 0,7. **Un Sharpe alto en 2 años no significa nada por sí solo.**

### 6.5 Corrección por múltiples pruebas

Con `M` configuraciones probadas, el mejor Sharpe esperado por puro azar crece como `√(2·ln M)` en unidades de error estándar. Con M = 500, el máximo espurio esperado es ~3,5 SE. Por eso:

- Se calcula el **Deflated Sharpe Ratio** (Bailey & López de Prado) con el `M` real del registro de hipótesis, la varianza de Sharpes entre pruebas, la asimetría y la curtosis de los retornos.
- Se exige DSR > 0,95 (probabilidad de que el Sharpe sea > 0 tras deflactar) en el conjunto walk-forward.
- Se mantiene `M` pequeño por diseño: rejillas de parámetros gruesas (3–5 valores), familias priorizadas, y **no se re-prueba nada tras ver el test**.

### 6.6 Validación temporal

1. **Partición fija**: 60 % train / 20 % validation / 20 % test, por tiempo. El test se abre **una sola vez** por familia, al final de Fase 6. Si se toca antes, se declara contaminado y se necesita un test nuevo (datos posteriores).
2. **Walk-forward anclado y rodante**: ventanas de entrenamiento de 2 años (cripto) / 5 años (ETF, FX), re-estimación cada 6 meses, evaluación en los 6 meses siguientes. Se reporta la *eficiencia walk-forward* = retorno OOS / retorno IS (se exige > 0,5) y la fracción de ventanas OOS positivas (> 60 %).
3. **Regímenes**: cada ventana se etiqueta (bull/bear/lateral por pendiente de MA200; vol alta/baja por percentil de RV; crisis: DD del activo > 30 % o VIX > 30) y se reporta expectancy por régimen. Se decide por régimen si operar, reducir o parar.
4. **Estabilidad temporal**: ninguna ventana OOS de 6 meses puede explicar > 40 % del beneficio total; ningún activo > 60 %.

### 6.7 Monte Carlo (Fase 9)

Sobre las operaciones OOS de cada estrategia:

- Remuestreo con reemplazo y permutación del orden → distribución de drawdown máximo, rachas de pérdidas y tiempo bajo el agua (percentiles 5/50/95).
- Perturbaciones: win rate −5 pp, avg win −10 %, avg loss +10 %, slippage ×2, comisión ×1,5, eliminación aleatoria del 10 % de las mejores operaciones (test de dependencia de outliers).
- Bloques (block bootstrap) para conservar autocorrelación de rachas.
- Riesgo de ruina: probabilidad de tocar −25 % (kill switch) antes de +50 % partiendo de US$500 con el sizing elegido.
- **Simulación de crecimiento** (sección 22): trayectorias de 10.000 caminos por 5 años con re-estimación de parámetros de sizing por gate; se reporta la probabilidad de alcanzar cada nivel y el tiempo mediano, con la etiqueta explícita de "simulación, no predicción".

### 6.8 Benchmarks obligatorios

Buy & hold del activo, cash (tipo libre de riesgo), estrategia aleatoria con la misma frecuencia y holding (1.000 réplicas → distribución nula), momentum simple (MA 200) y reversión simple (RSI2). Una estrategia debe superar al percentil 95 de la aleatoria y aportar sobre buy & hold en términos de Sharpe o Calmar, no solo de retorno.

---

## 7. Métricas de evaluación y criterios provisionales de aprobación

Todas las métricas se reportan en escenario base, sobre el conjunto walk-forward OOS, y separadas por activo y régimen.

### 7.1 Métricas

- **Rentabilidad**: retorno total, CAGR, retorno mensual (tabla), mejor/peor mes.
- **Riesgo**: DD máximo, DD medio, duración máxima de DD, volatilidad anualizada, VaR 95 y CVaR 95 diarios, riesgo de ruina (Monte Carlo).
- **Trading**: N, win rate, avg win, avg loss (en R y en %), payoff, profit factor, expectancy en R, máximas rachas, holding medio, coste total / beneficio bruto.
- **Ajustadas**: Sharpe, Sortino, Calmar, recovery factor, **Deflated Sharpe**, eficiencia walk-forward, t-stat de la expectancy.

### 7.2 Umbrales provisionales para pasar de backtest a paper (se revisan con los datos, con justificación)

| Criterio | Umbral | Por qué |
|---|---|---|
| Operaciones OOS | ≥ 300 (≥ 100 por activo reportado) | Potencia estadística (6.4). |
| Expectancy OOS neta | > 0,10 R con t-stat ≥ 2,5 | Margen sobre costes y sobre corrección múltiple. |
| Profit factor OOS | ≥ 1,3 | PF entre 1,0 y 1,3 suele desaparecer con slippage real. |
| Deflated Sharpe | > 0,95 | Corrige el número de pruebas. |
| Sharpe OOS | ≥ 0,8 (cripto 4 h) / ≥ 0,6 (diario) | Ajustado a frecuencia; no se exige > 2, que sería sospechoso. |
| Drawdown máximo OOS | ≤ 20 % con el sizing elegido y P95 Monte Carlo ≤ 30 % | Compatible con kill switch a −25 %. |
| Eficiencia walk-forward | > 0,5 y > 60 % de ventanas positivas | Estabilidad. |
| Sensibilidad | Ninguna variación ±20 % de un parámetro cambia el signo de la expectancy; caída < 40 % con ±30 % | Meseta, no pico. |
| Concentración | Ninguna ventana > 40 % del beneficio; ningún activo > 60 % | Sin dependencia de un período. |
| Benchmark | > P95 de la estrategia aleatoria; Calmar > buy & hold | Aporta valor real. |
| Coste / beneficio bruto | < 35 % | Si los costes se comen más, el margen ante slippage real es nulo. |
| Escenario pesimista | Expectancy ≥ 0 | Supervivencia si los costes son peores de lo estimado. |

Win rate: **sin umbral**. Se reporta y se analiza junto al payoff. Un win rate > 75 % dispara automáticamente la auditoría de la sección 39 del brief (leakage, stops anchos, colas).

### 7.3 Gates de capital (borrador, se calibra en Fase 10)

| Nivel | Capital | Condición para pasar al siguiente |
|---|---|---|
| 0 | Paper | ≥ 60 operaciones y ≥ 3 meses; expectancy live dentro del IC 90 % del backtest; slippage medido ≤ pesimista. |
| 1 | US$500 | ≥ 100 operaciones reales; PF ≥ 1,2; DD ≤ 15 %; sin desviación significativa vs backtest (test de dos muestras sobre R por operación, p > 0,10). |
| 2 | US$750 | +60 operaciones; mismos criterios. |
| 3 | US$1.000 | +80; DD acumulado ≤ 20 %. |
| 4 | US$2.000 | +100; revisión completa de walk-forward con los datos nuevos. |
| 5 | US$5.000 | +150; re-estimación de impacto de mercado (tamaño de orden vs profundidad). |
| 6–8 | 10k / 25k / 50k | +200 cada uno; análisis de capacidad (sección 21) actualizado; posible cambio a órdenes limit/TWAP. |

El paso de nivel es una **decisión manual** del propietario tras un informe generado por el sistema; el bot nunca sube solo. Un retroceso de nivel es automático si se viola DD o si la expectancy en las últimas 100 operaciones cae por debajo del percentil 5 del Monte Carlo.

---

## 8. Arquitectura propuesta

### 8.1 Pipeline

```
DATA (loaders por fuente, cache Parquet, hash de dataset)
  → DATA VALIDATION (reglas 4.3, informe de calidad)
  → FEATURE ENGINEERING (solo información ≤ t, registro por feature de su justificación)
  → MARKET REGIME (etiquetas de tendencia/vol/crisis, versionadas)
  → SIGNAL ENGINE (estrategias A–G como clases con la misma interfaz)
  → ML MODEL (opcional: meta-etiquetado P(win|x), desactivable)
  → EXPECTED VALUE (EV neto = p·avg_win − (1−p)·avg_loss − costes; opera si EV > umbral)
  → RISK ENGINE (riesgo por operación, límites diario/semanal, escalones por DD, kill switch)
  → POSITION SIZING (fractional fixed, vol-target; Kelly fraccional solo como techo)
  → ORDER ENGINE (idempotencia, reintentos, reconciliación con el exchange)
  → EXCHANGE (adaptadores: Binance spot/perp vía ccxt; OANDA; Alpaca/IBKR; simulador)
  → PORTFOLIO (contabilidad, posiciones, PnL realizado/no realizado, exposición)
  → DATABASE (SQLite en Fase 1–12; PostgreSQL cuando haya más de un proceso)
  → MONITORING (métricas en vivo, comparación live vs backtest, alertas)
```

El mismo pipeline sirve para backtest, paper y live: solo cambia el adaptador de EXCHANGE y la fuente de DATA. Esto es lo que permite comparar live contra backtest operación a operación.

### 8.2 Estructura del proyecto

```
trading_bot/
├── config/         # YAML por entorno; PAPER_TRADING=True por defecto; live exige dos flags
├── data/           # loaders (binance_vision, ccxt, dukascopy, yfinance, alpaca), validación, cache
├── features/       # cada feature en su módulo con docstring de justificación y test anti-lookahead
├── regime/         # clasificadores de régimen
├── strategies/     # base.py (interfaz) + trend.py, pullback.py, meanrev.py, breakout.py
├── models/         # meta-labeling, entrenamiento walk-forward, registro de modelos
├── backtesting/    # motor de eventos, modelo de costes, walk-forward, monte_carlo, métricas, sensibilidad
├── risk/           # sizing, límites, escalones por DD, kill_switch, capital_gates
├── execution/      # order engine, adaptadores de exchange, simulador
├── portfolio/      # contabilidad y exposición
├── monitoring/     # logging estructurado, alertas (Telegram/email), dashboard Streamlit
├── research/       # hypotheses.yaml, notebooks, informes por fase
├── tests/          # unit + property + tests de leakage y de órdenes duplicadas
├── main.py / backtest.py / paper_trade.py / live_trade.py
├── requirements.txt, docker-compose.yml (Fase 13), README.md
```

### 8.3 Tecnología, con criterio de proporcionalidad

- Python 3.11, pandas + NumPy (Polars si el volumen de 1 m lo exige), SciPy/statsmodels para tests, scikit-learn y LightGBM para ML (XGBoost como contraste), `backtesting.py`/vectorbt solo para verificación cruzada.
- Almacenamiento: Parquet para datos, SQLite para operaciones y estado. **PostgreSQL, Redis y Docker se introducen en Fase 13** si hay más de un proceso o más de un host; antes serían complejidad sin beneficio para un bot de US$500.
- FastAPI: endpoint de salud y, si se quiere, receptor de webhooks de TradingView como fuente de señal externa (no como núcleo).
- Despliegue: VPS pequeño o free tier (Oracle Cloud ARM) para paper y live; el dashboard Streamlit ya existente se reutiliza como base.

---

## 9. Plan de experimentación

Cada fase tiene entregable, criterio de éxito y **regla de parada**. El orden respeta el brief; las duraciones son estimadas y dependen de disponibilidad de datos.

| Fase | Entregable | Criterio para continuar | Regla de parada |
|---|---|---|---|
| **1. Mercados** | Fichas 1.3 por activo con datos reales; tabla coste/movimiento por timeframe verificada | Al menos 3 activos con ratio coste/movimiento < 0,3 en algún timeframe ≥ 1 h | Si ninguno cumple: replantear broker/mercado antes de seguir |
| **2. Estrategias** | `hypotheses.yaml` con A, G, H (+ benchmarks C, D) especificadas por completo antes de correr nada | Cada hipótesis con justificación y condiciones de fallo escritas | — |
| **3. Datasets** | Descargas, validación, informe de calidad, hash | < 0,1 % de barras marcadas; cruce Binance/Kraken dentro de tolerancia | Fuente inutilizable → sustituir |
| **4. Backtester** | Motor + costes + walk-forward + métricas + tests de leakage; verificación cruzada con `backtesting.py` | Coincidencia dentro de 1 % en 3 estrategias simples; tests en verde | — |
| **5. Candidatas** | A, G con rejilla gruesa; C, D como benchmarks; solo train+validation | ≥ 1 configuración con expectancy > 0 en validation con t ≥ 2 en escenario base | **Si nada pasa: informe "sin evidencia" y decisión del propietario** |
| **6. Walk-forward** | WF anclado y rodante; test abierto una sola vez; regímenes | Umbrales 7.2 | Si no pasa, no se re-optimiza sobre el test: se vuelve a Fase 2 con hipótesis nuevas registradas |
| **7. ML** | Meta-etiquetado sobre la mejor de Fase 6; features de sección 8 del brief con selección por MI/permutation; comparación con/sin ML en WF | Mejora de expectancy neta ≥ 15 % y DD no peor, en WF | Si no mejora: **ML se descarta** y se documenta |
| **8. Optimización robusta** | Sensibilidad ±5/10/20/30 %, PBO/CSCV, elección por meseta | Umbrales de sensibilidad 7.2 | Estrategia frágil → descartada aunque sea rentable |
| **9. Monte Carlo** | Distribuciones de DD, rachas, ruina; simulación de crecimiento por escenarios | P95 DD ≤ 30 %; riesgo de ruina < 5 % | Ajustar sizing o descartar |
| **10. Risk** | Sizing (0,25–1 % comparados por Monte Carlo), escalones por DD, kill switch, gates calibrados | Nivel de riesgo que maximiza mediana de crecimiento con P(ruina) < 5 % | — |
| **11. Portfolio** | Correlación entre estrategias/activos; asignación por riesgo; comparación single vs combinado | Combinado mejora Calmar y DD sin bajar expectancy | Si no mejora: una sola estrategia |
| **12. Paper** | Bot en testnet/demo ≥ 3 meses y ≥ 60 op; calibración de slippage real; comparación live vs backtest | Gate 0 | Desviación significativa → auditoría antes de dinero real |
| **13. Arquitectura live** | Order engine idempotente, reconciliación, reconexión, alertas, kill switch probado con fallos inyectados | Tests de 30 del brief en verde | — |
| **14. Código final** | Repositorio completo, CI, documentación | — | — |
| **15. Manual** | Operación, gates, qué hacer ante cada alerta, procedimiento de subida/bajada de nivel | — | — |

**Regla global**: ninguna fase reabre el conjunto de test. Cualquier idea nueva después de Fase 6 se registra y se evalúa sobre datos posteriores a la fecha de registro (forward test), no sobre el test ya usado.

---

## 10. Riesgos metodológicos

| Riesgo | Cómo se manifiesta | Mitigación en este marco |
|---|---|---|
| **Data dredging / múltiples pruebas** | Se prueban cientos de combinaciones y "algo" funciona | Registro de hipótesis con `M`; DSR; rejillas gruesas; test abierto una vez |
| **Look-ahead sutil** | Indicadores centrados, escalado global, etiquetas que ven el futuro, barras de 4 h agregadas con cierre parcial | Loader con corte temporal; test automático de perturbación; triple barrera con embargo |
| **Costes subestimados** | Backtest en optimista; slippage constante irreal | Tres escenarios; decisión en base; calibración con órdenes reales en paper; término de impacto |
| **Muestra pequeña** | 40 operaciones "excelentes" | Mínimos de 6.4; t-stat obligatorio; IC en todos los informes |
| **Supervivencia del universo** | Solo activos que sobrevivieron | Universo por capitalización a fecha |
| **Régimen único** | Cripto 2020–21 explica todo | Concentración temporal ≤ 40 %; reporte por régimen; walk-forward |
| **Curve fitting de stops/objetivos** | Múltiplos ATR "óptimos" en un pico | Sensibilidad y meseta; expectancy vs stop/TP en superficie, no en punto |
| **Fills intrabarra ficticios** | Stop y TP en la misma barra | Regla conservadora (stop primero); datos 1 m para resolver |
| **Discrepancia live vs backtest** | Ejecución real peor, latencia, rechazos | Mismo pipeline en ambos; comparación operación a operación; kill switch por divergencia |
| **ML como caja negra** | Modelo que memoriza | Solo meta-etiquetado; walk-forward; SHAP para verificar que usa features con sentido; comparación con/sin |
| **Sesgo del investigador** | Rebajar un umbral "porque casi pasa" | Umbrales escritos antes (7.2); cambios de umbral requieren justificación escrita y se aplican a la siguiente hipótesis, no a la actual |
| **Riesgo operativo con US$500** | Coste fijo de infraestructura y de tiempo | Free tier / equipo propio; medir el sistema por *proceso*, no por dinero, hasta nivel 3 |
| **Contraparte y regulación** | Exchange o broker no disponible en Chile, o que cambia condiciones | Verificar elegibilidad antes de Fase 12; adaptadores intercambiables |
| **Entorno de desarrollo sin red a mercados** | No se pueden descargar datos desde esta sesión | Descarga en equipo propio o VPS; código de loaders probado con datos sintéticos y fixtures |

---

## 11. Qué haría que se afirme "hay ventaja estadística"

Se afirmará, y solo entonces se pasará dinero real, cuando **todo** esto se cumpla a la vez, en escenario base, sobre datos que no se usaron para diseñar ni elegir:

1. Expectancy neta positiva con t ≥ 2,5 sobre ≥ 300 operaciones walk-forward OOS.
2. Deflated Sharpe > 0,95 usando el número real de hipótesis probadas.
3. Estabilidad: eficiencia WF > 0,5, > 60 % de ventanas positivas, sin ventana ni activo dominante.
4. Meseta de parámetros: signo de la expectancy invariante a ±20 %.
5. Monte Carlo: P95 de drawdown ≤ 30 % y riesgo de ruina < 5 % con el sizing elegido.
6. Supera al percentil 95 de la estrategia aleatoria equivalente y a buy & hold en Calmar.
7. Sobrevive (expectancy ≥ 0) en el escenario pesimista.
8. Paper trading de ≥ 3 meses y ≥ 60 operaciones sin desviación significativa respecto al backtest.

Si alguna familia no llega, se dirá. El informe "no hay evidencia suficiente con estos datos" es un resultado válido de este proyecto y ahorra los US$500.

---

## 12. Siguiente paso propuesto

1. Confirmar el país de residencia fiscal y los brokers/exchanges accesibles (Binance, Kraken, OANDA, IBKR, Alpaca) para cerrar el filtro 1.1.
2. Decidir dónde se ejecutará la descarga de datos (equipo propio, VPS, o ampliar la política de red de esta sesión).
3. Con eso, arrancar Fase 1 (fichas de mercado con datos reales) y Fase 2 (registro de hipótesis) en paralelo, y Fase 4 (motor) que no depende de los datos reales.
