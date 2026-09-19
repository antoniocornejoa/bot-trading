# Fase 6 · Walk-forward

Escenario **pessimistic**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. **TEST ABIERTO: se usa todo el histórico.**

## H-A2 · ma_momentum · 4h

### BTCUSDT: 14 ventanas, 270 operaciones OOS
- expectancy OOS 0.363 R, t = 1.73, PF 1.73, Sharpe 0.98, DD -24.5 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.59, ventana dominante 28 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 -0.014, p95 0.160; Sharpe p95 0.53

### ETHUSDT: 14 ventanas, 214 operaciones OOS
- expectancy OOS 0.476 R, t = 2.19, PF 1.90, Sharpe 1.08, DD -16.3 %
- ventanas positivas 71 %, eficiencia WF (mediana) 0.54, ventana dominante 22 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.082, p95 0.300; Sharpe p95 0.89

### SOLUSDT: 8 ventanas, 196 operaciones OOS
- expectancy OOS 0.082 R, t = 0.47, PF 1.13, Sharpe 0.27, DD -21.1 %
- ventanas positivas 25 %, eficiencia WF (mediana) -0.04, ventana dominante 79 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 -0.076, p95 0.084; Sharpe p95 0.37

### Agregado (todos los símbolos)
- 680 operaciones OOS | win rate 15.4 % | avg win 4.72 R | avg loss -0.49 R | payoff 9.70
- expectancy 0.317 R | t = 2.67 (p = 0.0078) | PF 1.68 | coste/beneficio bruto 0.30
- t sobre retornos mensuales agregados: t = 2.32 (p = 0.0231, 82 meses)
- Deflated Sharpe, SR por operación 0.102. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01741 → SR0 0.310, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00006 → SR0 0.019, **DSR = 0.999**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.007, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |   123 |   0.212 |   -23.685 |      -26.853 |
| bull    |         12 |   244 |   0.908 |  1268.06  |      123.578 |
| lateral |         17 |   313 |   0.143 |   220.044 |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |   124 |   0.591 |   607.081 |
| vol_baja  |         15 |   313 |   0.06  |    -4.092 |
| vol_media |         14 |   243 |   0.698 |   861.428 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    25 |   0.977 |    82.166 |       16.94  |
|   2020 |          4 |    82 |   0.987 |   469.749 |      209.973 |
|   2021 |          4 |    90 |   0.145 |    17.644 |        7.919 |
|   2022 |          5 |    67 |   0.239 |    92.765 |      -26.094 |
|   2023 |          6 |   125 |   0.726 |   442.964 |       89.526 |
|   2024 |          6 |   114 |   0.269 |   200.15  |       24.364 |
|   2025 |          6 |   112 |   0.045 |    19.898 |      -12.553 |
|   2026 |          3 |    65 |   0.298 |   139.079 |       10.449 |

### Ventanas

| symbol   | start      | end        | params                      |   trades |   expectancy_R |   pnl_usd | trend   | vol       |   bh_ret_pct |
|:---------|:-----------|:-----------|:----------------------------|---------:|---------------:|----------:|:--------|:----------|-------------:|
| BTCUSDT  | 2019-08-22 | 2020-02-21 | {'n': 100, 'atr_mult': 3.0} |       17 |          0.159 |    12.796 | lateral | vol_baja  |       -4.26  |
| BTCUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       20 |          0.63  |    63.654 | bull    | vol_media |       20.522 |
| BTCUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       25 |          1.288 |   197.167 | bull    | vol_alta  |      386.439 |
| BTCUSDT  | 2021-02-22 | 2021-08-24 | {'n': 100, 'atr_mult': 3.0} |       27 |         -0.048 |   -12.226 | bull    | vol_media |      -11.397 |
| BTCUSDT  | 2021-08-24 | 2022-02-23 | {'n': 100, 'atr_mult': 2.0} |       29 |         -0.211 |   -47.545 | bear    | vol_baja  |      -19.61  |
| BTCUSDT  | 2022-02-23 | 2022-08-24 | {'n': 150, 'atr_mult': 2.0} |       18 |         -0.271 |   -34.394 | bear    | vol_media |      -44.517 |
| BTCUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 2.0} |       19 |          0.739 |    83.735 | lateral | vol_baja  |       10.766 |
| BTCUSDT  | 2023-02-23 | 2023-08-25 | {'n': 200, 'atr_mult': 3.0} |       19 |         -0.123 |   -18.406 | lateral | vol_media |        8.998 |
| BTCUSDT  | 2023-08-25 | 2024-02-23 | {'n': 200, 'atr_mult': 3.0} |       20 |          1.604 |   236.516 | bull    | vol_alta  |       95.959 |
| BTCUSDT  | 2024-02-23 | 2024-08-24 | {'n': 200, 'atr_mult': 2.0} |       12 |          0.674 |    75.357 | lateral | vol_alta  |       24.918 |
| BTCUSDT  | 2024-08-24 | 2025-02-22 | {'n': 200, 'atr_mult': 4.0} |       14 |          0.545 |    77.652 | lateral | vol_media |       50.186 |
| BTCUSDT  | 2025-02-22 | 2025-08-24 | {'n': 200, 'atr_mult': 3.0} |       19 |          0.049 |     8.491 | lateral | vol_baja  |       19.036 |
| BTCUSDT  | 2025-08-24 | 2026-02-22 | {'n': 200, 'atr_mult': 3.0} |       11 |         -0.53  |   -64.886 | lateral | vol_alta  |      -41.087 |
| BTCUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 2.0} |       20 |          0.411 |    77.883 | lateral | vol_baja  |       14.096 |
| ETHUSDT  | 2019-08-22 | 2020-02-21 | {'n': 200, 'atr_mult': 3.0} |        8 |          1.795 |    69.37  | bear    | vol_media |       38.141 |
| ETHUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       15 |          1.539 |   133.053 | bull    | vol_media |       48.995 |
| ETHUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       22 |          0.493 |    75.876 | bull    | vol_media |      383.937 |
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n': 200, 'atr_mult': 3.0} |       14 |          1.047 |   114.414 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n': 200, 'atr_mult': 3.0} |       20 |         -0.208 |   -36.999 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n': 200, 'atr_mult': 4.0} |        7 |          0.398 |    23.805 | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 4.0} |        8 |          0.357 |    23.496 | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n': 150, 'atr_mult': 3.0} |       20 |         -0.383 |   -66.972 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n': 150, 'atr_mult': 2.0} |       18 |          1.091 |   164.122 | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          0.184 |    25.207 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n': 150, 'atr_mult': 2.0} |       17 |         -0.088 |   -19.96  | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          1.391 |   215.718 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n': 150, 'atr_mult': 2.0} |       21 |         -0.441 |  -108.38  | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 3.0} |       14 |          0.898 |   138.447 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |         -0.028 |    -3.877 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.31  |   -49.081 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 3.0} |       15 |          2.475 |   176.785 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 3.0} |       24 |          0.315 |    45.807 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 3.0} |       32 |         -0.015 |    -3.914 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n': 100, 'atr_mult': 3.0} |       23 |         -0.026 |    -4.642 | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n': 100, 'atr_mult': 3.0} |       23 |         -0.175 |   -26.403 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n': 150, 'atr_mult': 2.0} |       31 |         -0.417 |   -77.251 | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 -0.004, p95 0.224
