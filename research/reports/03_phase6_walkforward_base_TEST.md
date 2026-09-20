# Fase 6 · Walk-forward

Escenario **base**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. **TEST ABIERTO: se usa todo el histórico.**

## H-A2 · ma_momentum · 4h

### BTCUSDT: 14 ventanas, 274 operaciones OOS
- expectancy OOS 0.436 R, t = 2.00, PF 1.90, Sharpe 1.10, DD -21.5 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.59, ventana dominante 26 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.060, p95 0.229; Sharpe p95 0.78

### ETHUSDT: 14 ventanas, 226 operaciones OOS
- expectancy OOS 0.534 R, t = 2.36, PF 1.93, Sharpe 1.16, DD -13.8 %
- ventanas positivas 71 %, eficiencia WF (mediana) 0.53, ventana dominante 21 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.143, p95 0.312; Sharpe p95 0.93

### SOLUSDT: 8 ventanas, 198 operaciones OOS
- expectancy OOS 0.223 R, t = 0.89, PF 1.36, Sharpe 0.59, DD -21.7 %
- ventanas positivas 50 %, eficiencia WF (mediana) 0.01, ventana dominante 75 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.012, p95 0.146; Sharpe p95 0.75

### Agregado (todos los símbolos)
- 698 operaciones OOS | win rate 16.0 % | avg win 5.18 R | avg loss -0.50 R | payoff 10.26
- expectancy 0.407 R | t = 3.07 (p = 0.0022) | PF 1.80 | coste/beneficio bruto 0.19
- t sobre retornos mensuales agregados: t = 2.71 (p = 0.0083, 82 meses)
- Deflated Sharpe, SR por operación 0.116. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01282 → SR0 0.266, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00003 → SR0 0.014, **DSR = 1.000**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.005, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |   123 |   0.304 |    17.946 |      -26.853 |
| bull    |         12 |   249 |   1.072 |  1654.44  |      123.578 |
| lateral |         17 |   326 |   0.171 |   423.132 |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |   125 |   0.602 |   709.445 |
| vol_baja  |         15 |   327 |   0.101 |   196.51  |
| vol_media |         14 |   246 |   0.869 |  1189.56  |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    27 |   1.041 |    93.26  |       16.94  |
|   2020 |          4 |    83 |   1.17  |   593.196 |      209.973 |
|   2021 |          4 |    91 |   0.147 |    35.259 |        7.919 |
|   2022 |          5 |    67 |   0.376 |   163.329 |      -26.094 |
|   2023 |          6 |   127 |   0.921 |   636.046 |       89.526 |
|   2024 |          6 |   115 |   0.336 |   307.916 |       24.364 |
|   2025 |          6 |   112 |   0.072 |    63.245 |      -12.553 |
|   2026 |          3 |    76 |   0.232 |   203.264 |       10.449 |

### Ventanas

| symbol   | start      | end        | params                      |   trades |   expectancy_R |   pnl_usd | trend   | vol       |   bh_ret_pct |
|:---------|:-----------|:-----------|:----------------------------|---------:|---------------:|----------:|:--------|:----------|-------------:|
| BTCUSDT  | 2019-08-22 | 2020-02-21 | {'n': 100, 'atr_mult': 2.0} |       19 |          0.249 |    22.24  | lateral | vol_baja  |       -4.26  |
| BTCUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 2.0} |       21 |          0.939 |   101.417 | bull    | vol_media |       20.522 |
| BTCUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       25 |          1.331 |   222.181 | bull    | vol_alta  |      386.439 |
| BTCUSDT  | 2021-02-22 | 2021-08-24 | {'n': 100, 'atr_mult': 3.0} |       27 |         -0.044 |   -12.498 | bull    | vol_media |      -11.397 |
| BTCUSDT  | 2021-08-24 | 2022-02-23 | {'n': 100, 'atr_mult': 2.0} |       29 |         -0.157 |   -39.66  | bear    | vol_baja  |      -19.61  |
| BTCUSDT  | 2022-02-23 | 2022-08-24 | {'n': 150, 'atr_mult': 2.0} |       18 |         -0.208 |   -29.719 | bear    | vol_media |      -44.517 |
| BTCUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 2.0} |       19 |          0.835 |   109.758 | lateral | vol_baja  |       10.766 |
| BTCUSDT  | 2023-02-23 | 2023-08-25 | {'n': 200, 'atr_mult': 3.0} |       19 |         -0.072 |   -12.796 | lateral | vol_media |        8.998 |
| BTCUSDT  | 2023-08-25 | 2024-02-23 | {'n': 200, 'atr_mult': 3.0} |       21 |          1.581 |   285.69  | bull    | vol_alta  |       95.959 |
| BTCUSDT  | 2024-02-23 | 2024-08-24 | {'n': 200, 'atr_mult': 2.0} |       12 |          0.737 |    97.312 | lateral | vol_alta  |       24.918 |
| BTCUSDT  | 2024-08-24 | 2025-02-22 | {'n': 200, 'atr_mult': 4.0} |       14 |          0.578 |    97.343 | lateral | vol_media |       50.186 |
| BTCUSDT  | 2025-02-22 | 2025-08-24 | {'n': 200, 'atr_mult': 2.0} |       19 |          0.191 |    44.003 | lateral | vol_baja  |       19.036 |
| BTCUSDT  | 2025-08-24 | 2026-02-22 | {'n': 200, 'atr_mult': 2.0} |       11 |         -0.627 |   -92.657 | lateral | vol_alta  |      -41.087 |
| BTCUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 2.0} |       20 |          0.487 |   114.364 | lateral | vol_baja  |       14.096 |
| ETHUSDT  | 2019-08-22 | 2020-02-21 | {'n': 200, 'atr_mult': 3.0} |        8 |          1.832 |    71.02  | bear    | vol_media |       38.141 |
| ETHUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       15 |          1.573 |   136.981 | bull    | vol_media |       48.995 |
| ETHUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 2.0} |       22 |          0.838 |   132.616 | bull    | vol_media |      383.937 |
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n': 200, 'atr_mult': 3.0} |       15 |          0.953 |   120.039 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n': 200, 'atr_mult': 2.0} |       20 |         -0.166 |   -32.622 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n': 200, 'atr_mult': 2.0} |        7 |          0.846 |    54.956 | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 4.0} |        8 |          0.401 |    29.746 | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n': 150, 'atr_mult': 2.0} |       20 |         -0.389 |   -74.396 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n': 150, 'atr_mult': 2.0} |       18 |          1.168 |   199.583 | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          0.236 |    37.906 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n': 150, 'atr_mult': 2.0} |       17 |         -0.039 |   -13.121 | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          1.442 |   260.216 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n': 150, 'atr_mult': 2.0} |       21 |         -0.385 |  -111.078 | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n': 100, 'atr_mult': 2.0} |       25 |          0.573 |   173.001 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |          0.005 |    -1.412 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.271 |   -43.445 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 2.0} |       16 |          3.509 |   281.412 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 2.0} |       25 |          0.487 |    86.782 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 2.0} |       32 |          0.014 |     1.695 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n': 100, 'atr_mult': 3.0} |       23 |          0.022 |     3.33  | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n': 100, 'atr_mult': 2.0} |       23 |         -0.213 |   -40.569 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n': 150, 'atr_mult': 2.0} |       31 |         -0.362 |   -84.101 | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 0.062, p95 0.266

## H-A1 · donchian_trend · 4h

### BTCUSDT: 14 ventanas, 180 operaciones OOS
- expectancy OOS 0.317 R, t = 1.81, PF 1.64, Sharpe 0.98, DD -9.4 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.42, ventana dominante 31 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.009, p95 0.200; Sharpe p95 0.64

### ETHUSDT: 14 ventanas, 174 operaciones OOS
- expectancy OOS 0.210 R, t = 1.48, PF 1.44, Sharpe 0.70, DD -11.5 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.33, ventana dominante 28 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.060, p95 0.226; Sharpe p95 0.80

### SOLUSDT: 8 ventanas, 85 operaciones OOS
- expectancy OOS 0.175 R, t = 1.16, PF 1.45, Sharpe 0.59, DD -5.9 %
- ventanas positivas 62 %, eficiencia WF (mediana) 0.24, ventana dominante 48 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.007, p95 0.294; Sharpe p95 0.90

### Agregado (todos los símbolos)
- 439 operaciones OOS | win rate 37.4 % | avg win 1.78 R | avg loss -0.67 R | payoff 2.67
- expectancy 0.247 R | t = 2.59 (p = 0.0100) | PF 1.54 | coste/beneficio bruto 0.23
- t sobre retornos mensuales agregados: t = 2.25 (p = 0.0275, 81 meses)
- Deflated Sharpe, SR por operación 0.124. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01282 → SR0 0.266, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 24 configuraciones de H-A1 = 0.00146 → SR0 0.090, **DSR = 0.832**
  - por familias: M = 3 familias, varianza dentro de H-A1 → SR0 0.033, **DSR = 0.995**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |    66 |   0.132 |    47.228 |      -26.853 |
| bull    |         12 |   173 |   0.407 |   335.691 |      123.578 |
| lateral |         17 |   200 |   0.376 |   237.155 |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |    93 |   0.212 |    90.686 |
| vol_baja  |         15 |   178 |   0.358 |   207.555 |
| vol_media |         14 |   168 |   0.383 |   321.833 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    18 |   0.785 |    69.645 |       16.94  |
|   2020 |          4 |    73 |   0.377 |   110.987 |      209.973 |
|   2021 |          4 |    61 |   0.087 |    11.389 |        7.919 |
|   2022 |          5 |    48 |   0.801 |   136.963 |      -26.094 |
|   2023 |          6 |    59 |   0.384 |   119.893 |       89.526 |
|   2024 |          6 |    72 |   0.075 |    39.721 |       24.364 |
|   2025 |          6 |    66 |   0.214 |    58.055 |      -12.553 |
|   2026 |          3 |    42 |   0.247 |    73.421 |       10.449 |

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
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       20 |          0.116 |    12.662 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       21 |         -0.241 |   -29.632 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 100}  |       15 |          0.078 |     5.69  | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 2.0, 'ema_filter': 200}  |       16 |          0.213 |    18.3   | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       10 |         -0.466 |   -26.745 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100} |        7 |          1.304 |    52.09  | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 100} |        8 |         -0.249 |   -12.122 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          0.004 |     0.047 | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          1.429 |    78.515 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n_entry': 55, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |        6 |         -0.015 |    -0.693 | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n_entry': 20, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200}  |       17 |          0.264 |    24.945 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        7 |         -0.074 |    -2.673 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        6 |          0.151 |     4.301 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |       10 |          0.84  |    41.708 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |       16 |          0.152 |    12.762 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |          0.363 |    24.361 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       13 |         -0.024 |    -2.053 | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |        9 |          0.07  |     3.466 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |         -0.089 |    -6.528 | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 0.028, p95 0.248
