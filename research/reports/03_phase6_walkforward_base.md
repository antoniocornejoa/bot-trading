# Fase 6 · Walk-forward

Escenario **base**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. Solo train+validation (80 % inicial): **el test sigue cerrado**.

## H-A1 · donchian_trend · 4h

### BTCUSDT: 10 ventanas, 125 operaciones OOS
- expectancy OOS 0.372 R, t = 1.65, PF 1.77, Sharpe 1.07, DD -8.3 %
- ventanas positivas 70 %, eficiencia WF (mediana) 0.44, ventana dominante 41 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.021, p95 0.219; Sharpe p95 0.79

### ETHUSDT: 10 ventanas, 133 operaciones OOS
- expectancy OOS 0.144 R, t = 1.09, PF 1.28, Sharpe 0.53, DD -11.5 %
- ventanas positivas 60 %, eficiencia WF (mediana) 0.33, ventana dominante 29 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.062, p95 0.253; Sharpe p95 0.89

### SOLUSDT: 5 ventanas, 51 operaciones OOS
- expectancy OOS 0.305 R, t = 1.35, PF 1.85, Sharpe 0.91, DD -5.4 %
- ventanas positivas 80 %, eficiencia WF (mediana) 0.51, ventana dominante 50 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.102, p95 0.497; Sharpe p95 1.45

### Agregado (todos los símbolos)
- 309 operaciones OOS | win rate 38.2 % | avg win 1.79 R | avg loss -0.68 R | payoff 2.63
- expectancy 0.263 R | t = 2.32 (p = 0.0211) | PF 1.57 | coste/beneficio bruto 0.22
- t sobre retornos mensuales agregados: t = 2.07 (p = 0.0425, 64 meses)
- Deflated Sharpe, SR por operación 0.132. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01282 → SR0 0.266, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 24 configuraciones de H-A1 = 0.00146 → SR0 0.090, **DSR = 0.851**
  - por familias: M = 3 familias, varianza dentro de H-A1 → SR0 0.033, **DSR = 0.993**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          5 |    44 |   0.175 |    45.814 |      -24.155 |
| bull    |         11 |   164 |   0.315 |   257.176 |      128.189 |
| lateral |          9 |   101 |   0.6   |   141.408 |       13.135 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          5 |    72 |   0.305 |    98.273 |
| vol_baja  |          9 |   100 |   0.526 |   147.007 |
| vol_media |         11 |   137 |   0.317 |   199.118 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    18 |   0.785 |    69.645 |       16.94  |
|   2020 |          4 |    73 |   0.377 |   110.987 |      209.973 |
|   2021 |          4 |    61 |   0.087 |    11.389 |        7.919 |
|   2022 |          5 |    48 |   0.801 |   136.963 |      -26.094 |
|   2023 |          6 |    59 |   0.384 |   119.893 |       89.526 |
|   2024 |          4 |    50 |   0.001 |    -4.479 |       23.843 |

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
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        7 |         -0.074 |    -2.673 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |        6 |          0.151 |     4.301 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n_entry': 100, 'n_exit': 20, 'atr_mult': 3.0, 'ema_filter': 200} |       10 |          0.84  |    41.708 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 100}  |       16 |          0.152 |    12.762 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n_entry': 20, 'n_exit': 10, 'atr_mult': 3.0, 'ema_filter': 200}  |       12 |          0.363 |    24.361 | bull    | vol_media |       35.838 |

### Nulo aleatorio agregado: expectancy p50 0.055, p95 0.382

## H-A2 · ma_momentum · 4h

### BTCUSDT: 10 ventanas, 210 operaciones OOS
- expectancy OOS 0.499 R, t = 1.89, PF 2.16, Sharpe 1.27, DD -21.5 %
- ventanas positivas 60 %, eficiencia WF (mediana) 0.59, ventana dominante 34 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.089, p95 0.260; Sharpe p95 0.99

### ETHUSDT: 10 ventanas, 148 operaciones OOS
- expectancy OOS 0.632 R, t = 2.22, PF 2.23, Sharpe 1.26, DD -13.8 %
- ventanas positivas 80 %, eficiencia WF (mediana) 0.53, ventana dominante 25 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.165, p95 0.507; Sharpe p95 1.30

### SOLUSDT: 5 ventanas, 121 operaciones OOS
- expectancy OOS 0.495 R, t = 1.23, PF 2.04, Sharpe 1.11, DD -16.0 %
- ventanas positivas 60 %, eficiencia WF (mediana) 0.02, ventana dominante 76 % del beneficio
- nulo aleatorio (100 réplicas, mismas ventanas): expectancy p50 0.089, p95 0.319; Sharpe p95 1.40

### Agregado (todos los símbolos)
- 479 operaciones OOS | win rate 16.5 % | avg win 5.75 R | avg loss -0.49 R | payoff 11.73
- expectancy 0.539 R | t = 3.04 (p = 0.0025) | PF 2.16 | coste/beneficio bruto 0.14
- t sobre retornos mensuales agregados: t = 2.73 (p = 0.0082, 63 meses)
- Deflated Sharpe, SR por operación 0.139. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01282 → SR0 0.266, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00003 → SR0 0.014, **DSR = 1.000**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.005, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          5 |    77 |   0.463 |    55.186 |      -24.155 |
| bull    |         11 |   234 |   1.038 |  1394.22  |      128.189 |
| lateral |          9 |   168 |   0.277 |   295.379 |       13.135 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          5 |    91 |   1.011 |   842.671 |
| vol_baja  |          9 |   188 |   0.11  |    56.991 |
| vol_media |         11 |   200 |   0.925 |   845.122 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    27 |   1.041 |    93.26  |       16.94  |
|   2020 |          4 |    83 |   1.17  |   593.196 |      209.973 |
|   2021 |          4 |    91 |   0.147 |    35.259 |        7.919 |
|   2022 |          5 |    67 |   0.376 |   163.329 |      -26.094 |
|   2023 |          6 |   127 |   0.921 |   636.046 |       89.526 |
|   2024 |          4 |    84 |   0.369 |   223.694 |       23.843 |

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
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |          0.005 |    -1.412 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.271 |   -43.445 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 2.0} |       16 |          3.509 |   281.412 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 2.0} |       25 |          0.487 |    86.782 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 2.0} |       32 |          0.014 |     1.695 | bull    | vol_media |       35.838 |

### Nulo aleatorio agregado: expectancy p50 0.105, p95 0.372
