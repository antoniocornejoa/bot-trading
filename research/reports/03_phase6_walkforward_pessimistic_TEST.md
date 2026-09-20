# Fase 6 · Walk-forward

Escenario **pessimistic**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. **TEST ABIERTO: se usa todo el histórico.**

## H-A2 · ma_momentum · 4h

### BTCUSDT: 14 ventanas, 270 operaciones OOS
- expectancy OOS 0.336 R, t = 1.71, PF 1.71, Sharpe 0.97, DD -19.9 %
- ventanas positivas 64 %, eficiencia WF (mediana) 0.60, ventana dominante 29 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 -0.023, p95 0.158; Sharpe p95 0.52

### ETHUSDT: 14 ventanas, 215 operaciones OOS
- expectancy OOS 0.463 R, t = 2.13, PF 1.85, Sharpe 1.04, DD -17.5 %
- ventanas positivas 71 %, eficiencia WF (mediana) 0.50, ventana dominante 22 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.067, p95 0.296; Sharpe p95 0.88

### SOLUSDT: 8 ventanas, 196 operaciones OOS
- expectancy OOS 0.072 R, t = 0.41, PF 1.10, Sharpe 0.23, DD -22.3 %
- ventanas positivas 25 %, eficiencia WF (mediana) -0.02, ventana dominante 79 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 -0.078, p95 0.088; Sharpe p95 0.40

### Agregado (todos los símbolos)
- 681 operaciones OOS | win rate 15.4 % | avg win 4.63 R | avg loss -0.49 R | payoff 9.46
- expectancy 0.300 R | t = 2.60 (p = 0.0094) | PF 1.64 | coste/beneficio bruto 0.31
- t sobre retornos mensuales agregados: t = 2.30 (p = 0.0242, 82 meses)
- Deflated Sharpe, SR por operación 0.100. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01861 → SR0 0.321, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00006 → SR0 0.018, **DSR = 0.998**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.007, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          7 |   123 |   0.203 |   -32.555 |      -26.853 |
| bull    |         12 |   246 |   0.89  |  1238.38  |      123.578 |
| lateral |         17 |   312 |   0.118 |   158.969 |        7.022 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          7 |   125 |   0.567 |   576.511 |
| vol_baja  |         15 |   312 |   0.033 |   -55.363 |
| vol_media |         14 |   244 |   0.688 |   843.641 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    25 |   0.977 |    82.166 |       16.94  |
|   2020 |          4 |    82 |   0.987 |   469.749 |      209.973 |
|   2021 |          4 |    91 |   0.112 |     8.325 |        7.919 |
|   2022 |          5 |    66 |   0.177 |    58.378 |      -26.094 |
|   2023 |          6 |   126 |   0.695 |   412.027 |       89.526 |
|   2024 |          6 |   114 |   0.269 |   191.858 |       24.364 |
|   2025 |          6 |   112 |   0.035 |    11.619 |      -12.553 |
|   2026 |          3 |    65 |   0.293 |   130.667 |       10.449 |

### Ventanas

| symbol   | start      | end        | params                      |   trades |   expectancy_R |   pnl_usd | trend   | vol       |   bh_ret_pct |
|:---------|:-----------|:-----------|:----------------------------|---------:|---------------:|----------:|:--------|:----------|-------------:|
| BTCUSDT  | 2019-08-22 | 2020-02-21 | {'n': 100, 'atr_mult': 3.0} |       17 |          0.159 |    12.796 | lateral | vol_baja  |       -4.26  |
| BTCUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       20 |          0.63  |    63.654 | bull    | vol_media |       20.522 |
| BTCUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       25 |          1.288 |   197.167 | bull    | vol_alta  |      386.439 |
| BTCUSDT  | 2021-02-22 | 2021-08-24 | {'n': 100, 'atr_mult': 3.0} |       27 |         -0.067 |   -16.035 | bull    | vol_media |      -11.397 |
| BTCUSDT  | 2021-08-24 | 2022-02-23 | {'n': 100, 'atr_mult': 2.0} |       29 |         -0.211 |   -47.357 | bear    | vol_baja  |      -19.61  |
| BTCUSDT  | 2022-02-23 | 2022-08-24 | {'n': 150, 'atr_mult': 2.0} |       18 |         -0.271 |   -34.239 | bear    | vol_media |      -44.517 |
| BTCUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 4.0} |       18 |          0.429 |    49.513 | lateral | vol_baja  |       10.766 |
| BTCUSDT  | 2023-02-23 | 2023-08-25 | {'n': 200, 'atr_mult': 3.0} |       19 |         -0.123 |   -17.522 | lateral | vol_media |        8.998 |
| BTCUSDT  | 2023-08-25 | 2024-02-23 | {'n': 200, 'atr_mult': 3.0} |       21 |          1.517 |   222.682 | bull    | vol_alta  |       95.959 |
| BTCUSDT  | 2024-02-23 | 2024-08-24 | {'n': 200, 'atr_mult': 2.0} |       12 |          0.674 |    71.537 | lateral | vol_alta  |       24.918 |
| BTCUSDT  | 2024-08-24 | 2025-02-22 | {'n': 200, 'atr_mult': 4.0} |       14 |          0.545 |    73.529 | lateral | vol_media |       50.186 |
| BTCUSDT  | 2025-02-22 | 2025-08-24 | {'n': 200, 'atr_mult': 3.0} |       19 |          0.049 |     8.048 | lateral | vol_baja  |       19.036 |
| BTCUSDT  | 2025-08-24 | 2026-02-22 | {'n': 200, 'atr_mult': 3.0} |       11 |         -0.53  |   -61.533 | lateral | vol_alta  |      -41.087 |
| BTCUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 2.0} |       20 |          0.397 |    70.853 | lateral | vol_baja  |       14.096 |
| ETHUSDT  | 2019-08-22 | 2020-02-21 | {'n': 200, 'atr_mult': 3.0} |        8 |          1.795 |    69.37  | bear    | vol_media |       38.141 |
| ETHUSDT  | 2020-02-21 | 2020-08-22 | {'n': 100, 'atr_mult': 3.0} |       15 |          1.539 |   133.053 | bull    | vol_media |       48.995 |
| ETHUSDT  | 2020-08-23 | 2021-02-22 | {'n': 100, 'atr_mult': 3.0} |       22 |          0.493 |    75.876 | bull    | vol_media |      383.937 |
| ETHUSDT  | 2021-02-22 | 2021-08-24 | {'n': 200, 'atr_mult': 3.0} |       15 |          0.933 |   108.456 | bull    | vol_media |       78.157 |
| ETHUSDT  | 2021-08-24 | 2022-02-23 | {'n': 200, 'atr_mult': 3.0} |       20 |         -0.208 |   -36.738 | lateral | vol_baja  |      -15.473 |
| ETHUSDT  | 2022-02-23 | 2022-08-24 | {'n': 200, 'atr_mult': 4.0} |        7 |          0.398 |    23.647 | bear    | vol_media |      -38.38  |
| ETHUSDT  | 2022-08-25 | 2023-02-23 | {'n': 200, 'atr_mult': 4.0} |        8 |          0.357 |    23.335 | lateral | vol_baja  |       -1.931 |
| ETHUSDT  | 2023-02-23 | 2023-08-25 | {'n': 150, 'atr_mult': 2.0} |       20 |         -0.468 |   -78.525 | lateral | vol_baja  |       -0.043 |
| ETHUSDT  | 2023-08-25 | 2024-02-23 | {'n': 150, 'atr_mult': 2.0} |       18 |          1.091 |   160.648 | lateral | vol_alta  |       76.592 |
| ETHUSDT  | 2024-02-23 | 2024-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          0.184 |    24.635 | bull    | vol_alta  |       -6.768 |
| ETHUSDT  | 2024-08-24 | 2025-02-22 | {'n': 150, 'atr_mult': 2.0} |       17 |         -0.088 |   -19.491 | lateral | vol_media |        0.624 |
| ETHUSDT  | 2025-02-22 | 2025-08-24 | {'n': 150, 'atr_mult': 2.0} |       15 |          1.391 |   211.298 | bull    | vol_media |       72.868 |
| ETHUSDT  | 2025-08-24 | 2026-02-22 | {'n': 150, 'atr_mult': 2.0} |       21 |         -0.441 |  -106.095 | lateral | vol_baja  |      -58.939 |
| ETHUSDT  | 2026-02-22 | 2026-08-24 | {'n': 200, 'atr_mult': 3.0} |       14 |          0.898 |   135.573 | lateral | vol_baja  |       25.05  |
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |         -0.028 |    -3.877 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.325 |   -51.198 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 3.0} |       15 |          2.475 |   175.942 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 3.0} |       24 |          0.315 |    45.544 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 3.0} |       32 |         -0.015 |    -3.896 | bull    | vol_media |       35.838 |
| SOLUSDT  | 2025-02-11 | 2025-08-12 | {'n': 100, 'atr_mult': 3.0} |       23 |         -0.005 |    -1.474 | bear    | vol_baja  |      -12.869 |
| SOLUSDT  | 2025-08-12 | 2026-02-10 | {'n': 100, 'atr_mult': 2.0} |       23 |         -0.256 |   -38.625 | bear    | vol_alta  |      -54.326 |
| SOLUSDT  | 2026-02-11 | 2026-08-12 | {'n': 150, 'atr_mult': 2.0} |       31 |         -0.417 |   -75.759 | lateral | vol_baja  |       -7.799 |

### Nulo aleatorio agregado: expectancy p50 -0.008, p95 0.208
