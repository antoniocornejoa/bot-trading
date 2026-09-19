# Fase 6 · Walk-forward

Escenario **base**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. **TEST ABIERTO: se usa todo el histórico.**

## H-A2 · ma_momentum · 4h

### BTCUSDT: 14 ventanas, 270 operaciones OOS
- expectancy OOS 0.425 R, t = 2.00, PF 1.94, Sharpe 1.13, DD -21.5 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.62, ventana dominante 27 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.068, p95 0.239; Sharpe p95 0.81

### ETHUSDT: 14 ventanas, 225 operaciones OOS
- expectancy OOS 0.535 R, t = 2.35, PF 1.92, Sharpe 1.15, DD -14.8 %
- ventanas positivas 71 %, eficiencia WF (mediana) 0.56, ventana dominante 21 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.145, p95 0.361; Sharpe p95 1.05

### SOLUSDT: 8 ventanas, 198 operaciones OOS
- expectancy OOS 0.230 R, t = 0.92, PF 1.38, Sharpe 0.61, DD -20.9 %
- ventanas positivas 38 %, eficiencia WF (mediana) 0.00, ventana dominante 76 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.012, p95 0.153; Sharpe p95 0.78

### Agregado (todos los símbolos)
- 693 operaciones OOS | win rate 16.2 % | avg win 5.09 R | avg loss -0.50 R | payoff 10.20
- expectancy 0.405 R | t = 3.07 (p = 0.0022) | PF 1.81 | coste/beneficio bruto 0.19
- t sobre retornos mensuales agregados: t = 2.74 (p = 0.0076, 82 meses)
- Deflated Sharpe, SR por operación 0.117. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01169 → SR0 0.254, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00004 → SR0 0.014, **DSR = 1.000**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.005, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |   123 |   0.31  |    30.079 |      -26.853 |
| bull    |         12 |   246 |   1.069 |  1605.6   |      123.578 |
| lateral |         17 |   324 |   0.176 |   412.83  |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |   124 |   0.647 |   715.407 |
| vol_baja  |         15 |   325 |   0.094 |   166.364 |
| vol_media |         14 |   244 |   0.861 |  1166.73  |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    25 |   1.015 |    87.272 |       16.94  |
|   2020 |          4 |    82 |   1.104 |   547.464 |      209.973 |
|   2021 |          4 |    90 |   0.18  |    48.251 |        7.919 |
|   2022 |          5 |    67 |   0.376 |   159.429 |      -26.094 |
|   2023 |          6 |   126 |   0.929 |   612.239 |       89.526 |
|   2024 |          6 |   115 |   0.336 |   297.637 |       24.364 |
|   2025 |          6 |   112 |   0.107 |    95.425 |      -12.553 |
|   2026 |          3 |    76 |   0.237 |   200.79  |       10.449 |

### Ventanas

| symbol   | start      | end        | params                      |   trades |   expectancy_R |   pnl_usd | trend   | vol       |   bh_ret_pct |
|:---------|:-----------|:-----------|:----------------------------|---------:|---------------:|----------:|:--------|:----------|-------------:|
| BTCUSDT  | 2019-08-22 | 2020-02-21 | {'n': 100, 'atr_mult': 3.0} |       17 |          0.198 |    16.251 | lateral | vol_baja  |       -4.26  |
| BTCUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       20 |          0.675 |    69.309 | bull    | vol_media |       20.522 |
| BTCUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       25 |          1.331 |   208.486 | bull    | vol_alta  |      386.439 |
| BTCUSDT  | 2021-02-22 | 2021-08-24 | {'n': 100, 'atr_mult': 3.0} |       27 |         -0.025 |    -7.704 | bull    | vol_media |      -11.397 |
| BTCUSDT  | 2021-08-24 | 2022-02-23 | {'n': 100, 'atr_mult': 2.0} |       29 |         -0.157 |   -37.479 | bear    | vol_baja  |      -19.61  |
| BTCUSDT  | 2022-02-23 | 2022-08-24 | {'n': 150, 'atr_mult': 2.0} |       18 |         -0.208 |   -28.022 | bear    | vol_media |      -44.517 |
| BTCUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 2.0} |       19 |          0.835 |   103.59  | lateral | vol_baja  |       10.766 |
| BTCUSDT  | 2023-02-23 | 2023-08-25 | {'n': 200, 'atr_mult': 2.0} |       19 |         -0.063 |   -11.701 | lateral | vol_media |        8.998 |
| BTCUSDT  | 2023-08-25 | 2024-02-23 | {'n': 200, 'atr_mult': 3.0} |       20 |          1.668 |   271.505 | bull    | vol_alta  |       95.959 |
| BTCUSDT  | 2024-02-23 | 2024-08-24 | {'n': 200, 'atr_mult': 2.0} |       12 |          0.737 |    92.093 | lateral | vol_alta  |       24.918 |
| BTCUSDT  | 2024-08-24 | 2025-02-22 | {'n': 200, 'atr_mult': 4.0} |       14 |          0.578 |    92.241 | lateral | vol_media |       50.186 |
| BTCUSDT  | 2025-02-22 | 2025-08-24 | {'n': 200, 'atr_mult': 2.0} |       19 |          0.191 |    41.542 | lateral | vol_baja  |       19.036 |
| BTCUSDT  | 2025-08-24 | 2026-02-22 | {'n': 200, 'atr_mult': 3.0} |       11 |         -0.463 |   -65.221 | lateral | vol_alta  |      -41.087 |
| BTCUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 2.0} |       20 |          0.5   |   113.804 | lateral | vol_baja  |       14.096 |
| ETHUSDT  | 2019-08-22 | 2020-02-21 | {'n': 200, 'atr_mult': 3.0} |        8 |          1.832 |    71.02  | bear    | vol_media |       38.141 |
| ETHUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       15 |          1.573 |   136.981 | bull    | vol_media |       48.995 |
| ETHUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 2.0} |       22 |          0.838 |   132.688 | bull    | vol_media |      383.937 |
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n': 200, 'atr_mult': 3.0} |       14 |          1.068 |   126.315 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n': 200, 'atr_mult': 2.0} |       20 |         -0.166 |   -32.881 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n': 200, 'atr_mult': 2.0} |        7 |          0.846 |    55.299 | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 4.0} |        8 |          0.401 |    29.973 | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n': 150, 'atr_mult': 2.0} |       20 |         -0.446 |   -85.335 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n': 150, 'atr_mult': 2.0} |       18 |          1.168 |   198.563 | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          0.236 |    37.695 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n': 150, 'atr_mult': 2.0} |       17 |         -0.039 |   -13.079 | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          1.442 |   258.983 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n': 150, 'atr_mult': 2.0} |       21 |         -0.385 |  -110.551 | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n': 100, 'atr_mult': 2.0} |       25 |          0.573 |   172.082 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |          0.005 |    -1.412 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.271 |   -43.445 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 2.0} |       16 |          3.519 |   282.652 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 2.0} |       25 |          0.487 |    86.934 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 2.0} |       32 |          0.014 |     1.753 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n': 100, 'atr_mult': 2.0} |       23 |          0.002 |    -1.614 | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n': 100, 'atr_mult': 3.0} |       23 |         -0.146 |   -27.714 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n': 150, 'atr_mult': 2.0} |       31 |         -0.362 |   -85.096 | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 0.062, p95 0.283

## H-A1 · donchian_trend · 4h

### BTCUSDT: 14 ventanas, 180 operaciones OOS
- expectancy OOS 0.317 R, t = 1.81, PF 1.64, Sharpe 0.98, DD -9.4 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.42, ventana dominante 31 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.013, p95 0.192; Sharpe p95 0.63

### ETHUSDT: 14 ventanas, 174 operaciones OOS
- expectancy OOS 0.209 R, t = 1.48, PF 1.44, Sharpe 0.70, DD -11.5 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.32, ventana dominante 28 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.060, p95 0.267; Sharpe p95 0.86

### SOLUSDT: 8 ventanas, 85 operaciones OOS
- expectancy OOS 0.170 R, t = 1.12, PF 1.43, Sharpe 0.57, DD -5.9 %
- ventanas positivas 62 %, eficiencia WF (mediana) 0.24, ventana dominante 49 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.008, p95 0.291; Sharpe p95 0.88

### Agregado (todos los símbolos)
- 439 operaciones OOS | win rate 37.4 % | avg win 1.78 R | avg loss -0.67 R | payoff 2.66
- expectancy 0.246 R | t = 2.57 (p = 0.0104) | PF 1.53 | coste/beneficio bruto 0.23
- t sobre retornos mensuales agregados: t = 2.24 (p = 0.0282, 81 meses)
- Deflated Sharpe, SR por operación 0.123. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01169 → SR0 0.254, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 24 configuraciones de H-A1 = 0.00149 → SR0 0.091, **DSR = 0.821**
  - por familias: M = 3 familias, varianza dentro de H-A1 → SR0 0.033, **DSR = 0.995**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |    66 |   0.132 |    47.219 |      -26.853 |
| bull    |         12 |   173 |   0.405 |   332.864 |      123.578 |
| lateral |         17 |   200 |   0.376 |   237.199 |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |    93 |   0.212 |    90.679 |
| vol_baja  |         15 |   178 |   0.356 |   205.415 |
| vol_media |         14 |   168 |   0.382 |   321.188 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    18 |   0.785 |    69.645 |       16.94  |
|   2020 |          4 |    73 |   0.377 |   110.987 |      209.973 |
|   2021 |          4 |    61 |   0.086 |    10.978 |        7.919 |
|   2022 |          5 |    48 |   0.801 |   136.961 |      -26.094 |
|   2023 |          6 |    59 |   0.384 |   119.893 |       89.526 |
|   2024 |          6 |    72 |   0.071 |    37.421 |       24.364 |
|   2025 |          6 |    66 |   0.214 |    57.986 |      -12.553 |
|   2026 |          3 |    42 |   0.247 |    73.412 |       10.449 |

### Ventanas

| symbol   | start      | end        | params                                                             |   trades |   expectancy_R |   pnl_usd | trend   | vol       |   bh_ret_pct |
|:---------|:-----------|:-----------|:-------------------------------------------------------------------|---------:|---------------:|----------:|:--------|:----------|-------------:|
| BTCUSDT  | 2019-08-22 | 2020-02-21 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 200}  |       10 |          0.58  |    29.237 | lateral | vol_baja  |       -4.26  |
| BTCUSDT  | 2020-02-21 | 2020-08-22 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 2.0, 'ema_filter': 200}  |       16 |          0.475 |    39.522 | bull    | vol_media |       20.522 |
| BTCUSDT  | 2020-08-23 | 2021-02-22 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 200}  |       29 |          0.221 |    35.227 | bull    | vol_alta  |      386.439 |
| BTCUSDT  | 2021-02-22 | 2021-08-24 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       11 |          0.217 |    14.258 | bull    | vol_media |      -11.397 |
| BTCUSDT  | 2021-08-24 | 2022-02-23 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          0.255 |    14.099 | bear    | vol_baja  |      -19.61  |
| BTCUSDT  | 2022-02-23 | 2022-08-24 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100} |        5 |         -0.371 |   -11.71  | bear    | vol_media |      -44.517 |
| BTCUSDT  | 2022-08-25 | 2023-02-23 | {'n_entry': 100, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200} |        5 |          4.161 |   127.357 | lateral | vol_baja  |       10.766 |
| BTCUSDT  | 2023-02-23 | 2023-08-25 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |         -0.038 |    -4.02  | lateral | vol_media |        8.998 |
| BTCUSDT  | 2023-08-25 | 2024-02-23 | {'n_entry': 55, 'n_exit': 10, 'atr_mult': 2.0, 'ema_filter': 200}  |       14 |          0.511 |    52.559 | bull    | vol_alta  |       95.959 |
| BTCUSDT  | 2024-02-23 | 2024-08-24 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 200}  |       14 |         -0.264 |   -29.48  | lateral | vol_alta  |       24.918 |
| BTCUSDT  | 2024-08-24 | 2025-02-22 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100}  |       13 |          0.443 |    44.153 | lateral | vol_media |       50.186 |
| BTCUSDT  | 2025-02-22 | 2025-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100}  |       17 |         -0.068 |   -10.127 | lateral | vol_baja  |       19.036 |
| BTCUSDT  | 2025-08-24 | 2026-02-22 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100}  |       12 |         -0.11  |   -11.054 | lateral | vol_alta  |      -41.087 |
| BTCUSDT  | 2026-02-22 | 2026-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       13 |          0.566 |    55.005 | lateral | vol_baja  |       14.096 |
| ETHUSDT  | 2019-08-22 | 2020-02-21 | {'n_entry': 55, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |        8 |          0.989 |    40.408 | bear    | vol_media |       38.141 |
| ETHUSDT  | 2020-02-21 | 2020-08-22 | {'n_entry': 55, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |       10 |          0.959 |    51.993 | bull    | vol_media |       48.995 |
| ETHUSDT  | 2020-08-23 | 2021-02-22 | {'n_entry': 55, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |       18 |         -0.145 |   -15.755 | bull    | vol_media |      383.937 |
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       20 |          0.112 |    12.206 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       21 |         -0.241 |   -29.586 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       15 |          0.078 |     5.692 | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 200}  |       16 |          0.213 |    18.295 | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       10 |         -0.466 |   -26.726 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100} |        7 |          1.304 |    52.071 | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100} |        8 |         -0.249 |   -12.107 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          0.004 |     0.049 | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          1.429 |    78.447 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        6 |         -0.015 |    -0.683 | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       17 |          0.264 |    24.907 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        7 |         -0.074 |    -2.673 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        6 |          0.151 |     4.301 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |       10 |          0.84  |    41.708 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |       16 |          0.128 |    10.569 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |          0.363 |    24.236 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       13 |         -0.024 |    -2.06  | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          0.07  |     3.463 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |         -0.089 |    -6.5   | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 0.032, p95 0.267
