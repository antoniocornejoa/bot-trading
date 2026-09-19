# Fase 6 · Walk-forward

Escenario **pessimistic**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. Solo train+validation (80 % inicial): **el test sigue cerrado**.

## H-A2 · ma_momentum · 4h

### BTCUSDT: 10 ventanas, 206 operaciones OOS
- expectancy OOS 0.423 R, t = 1.65, PF 1.92, Sharpe 1.12, DD -24.5 %
- ventanas positivas 60 %, eficiencia WF (mediana) 0.59, ventana dominante 35 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.004, p95 0.248; Sharpe p95 0.87

### ETHUSDT: 10 ventanas, 147 operaciones OOS
- expectancy OOS 0.539 R, t = 1.99, PF 2.11, Sharpe 1.16, DD -16.3 %
- ventanas positivas 80 %, eficiencia WF (mediana) 0.54, ventana dominante 26 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.104, p95 0.438; Sharpe p95 1.14

### SOLUSDT: 5 ventanas, 119 operaciones OOS
- expectancy OOS 0.282 R, t = 1.00, PF 1.70, Sharpe 0.83, DD -17.0 %
- ventanas positivas 40 %, eficiencia WF (mediana) -0.02, ventana dominante 79 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.016, p95 0.235; Sharpe p95 1.02

### Agregado (todos los símbolos)
- 472 operaciones OOS | win rate 15.7 % | avg win 5.25 R | avg loss -0.47 R | payoff 11.08
- expectancy 0.423 R | t = 2.70 (p = 0.0071) | PF 1.95 | coste/beneficio bruto 0.22
- t sobre retornos mensuales agregados: t = 2.40 (p = 0.0193, 63 meses)
- Deflated Sharpe (M = 61 pruebas registradas; varianza empírica de SR entre 57 configuraciones = 0.01741): SR 0.125, SR0 esperado por azar 0.310, **DSR = 0.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          5 |    77 |   0.337 |     7.359 |      -24.155 |
| bull    |         11 |   229 |   0.865 |  1052.34  |      128.189 |
| lateral |          9 |   166 |   0.222 |   188.048 |       13.135 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          5 |    90 |   0.968 |   698.369 |
| vol_baja  |          9 |   185 |   0.048 |   -38.64  |
| vol_media |         11 |   197 |   0.72  |   588.018 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    25 |   0.977 |    82.166 |       16.94  |
|   2020 |          4 |    82 |   0.987 |   469.749 |      209.973 |
|   2021 |          4 |    90 |   0.145 |    17.644 |        7.919 |
|   2022 |          5 |    67 |   0.239 |    92.765 |      -26.094 |
|   2023 |          6 |   125 |   0.726 |   442.964 |       89.526 |
|   2024 |          4 |    83 |   0.289 |   142.458 |       23.843 |

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
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |         -0.028 |    -3.877 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.31  |   -49.081 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 3.0} |       15 |          2.475 |   176.785 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 3.0} |       24 |          0.315 |    45.807 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 3.0} |       32 |         -0.015 |    -3.914 | bull    | vol_media |       35.838 |

### Nulo aleatorio agregado: expectancy p50 0.039, p95 0.358
