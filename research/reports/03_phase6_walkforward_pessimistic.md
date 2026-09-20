# Fase 6 · Walk-forward

Escenario **pessimistic**. Ventanas rodantes: 2.0 años de entrenamiento, 6 meses de evaluación. Solo train+validation (80 % inicial): **el test sigue cerrado**.

## H-A2 · ma_momentum · 4h

### BTCUSDT: 10 ventanas, 206 operaciones OOS
- expectancy OOS 0.388 R, t = 1.64, PF 1.90, Sharpe 1.13, DD -19.9 %
- ventanas positivas 60 %, eficiencia WF (mediana) 0.60, ventana dominante 36 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 -0.001, p95 0.250; Sharpe p95 0.87

### ETHUSDT: 10 ventanas, 148 operaciones OOS
- expectancy OOS 0.519 R, t = 1.93, PF 2.01, Sharpe 1.11, DD -17.5 %
- ventanas positivas 80 %, eficiencia WF (mediana) 0.50, ventana dominante 26 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.078, p95 0.431; Sharpe p95 1.13

### SOLUSDT: 5 ventanas, 119 operaciones OOS
- expectancy OOS 0.278 R, t = 0.99, PF 1.68, Sharpe 0.82, DD -17.4 %
- ventanas positivas 40 %, eficiencia WF (mediana) -0.02, ventana dominante 79 % del beneficio
- nulo aleatorio (50 réplicas, mismas ventanas): expectancy p50 0.017, p95 0.235; Sharpe p95 1.02

### Agregado (todos los símbolos)
- 473 operaciones OOS | win rate 15.6 % | avg win 5.09 R | avg loss -0.47 R | payoff 10.88
- expectancy 0.401 R | t = 2.67 (p = 0.0079) | PF 1.90 | coste/beneficio bruto 0.23
- t sobre retornos mensuales agregados: t = 2.43 (p = 0.0182, 63 meses)
- Deflated Sharpe, SR por operación 0.123. Tres supuestos sobre el número y la varianza de las pruebas:
  - conservador: M = 61, varianza entre las 57 configuraciones de todas las familias = 0.01861 → SR0 0.321, **DSR = 0.000**
  - dentro de familia: M = 61, varianza entre las 9 configuraciones de H-A2 = 0.00006 → SR0 0.018, **DSR = 1.000**
  - por familias: M = 3 familias, varianza dentro de H-A2 → SR0 0.007, **DSR = 1.000**

### Por régimen (ventanas OOS)

| trend   |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|:--------|-----------:|------:|--------:|----------:|-------------:|
| bear    |          5 |    77 |   0.337 |     7.544 |      -24.155 |
| bull    |         11 |   231 |   0.845 |  1027.08  |      128.189 |
| lateral |          9 |   165 |   0.176 |   133.845 |       13.135 |

| vol       |   ventanas |   ops |   exp_R |   pnl_usd |
|:----------|-----------:|------:|--------:|----------:|
| vol_alta  |          5 |    91 |   0.951 |   676.669 |
| vol_baja  |          9 |   184 |   0.002 |   -86.509 |
| vol_media |         11 |   198 |   0.708 |   578.306 |

### Por año

|   year |   ventanas |   ops |   exp_R |   pnl_usd |   bh_ret_pct |
|-------:|-----------:|------:|--------:|----------:|-------------:|
|   2019 |          2 |    25 |   0.977 |    82.166 |       16.94  |
|   2020 |          4 |    82 |   0.987 |   469.749 |      209.973 |
|   2021 |          4 |    91 |   0.112 |     8.325 |        7.919 |
|   2022 |          5 |    66 |   0.177 |    58.378 |      -26.094 |
|   2023 |          6 |   126 |   0.695 |   412.027 |       89.526 |
|   2024 |          4 |    83 |   0.289 |   137.821 |       23.843 |

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
| SOLUSDT  | 2022-08-13 | 2023-02-11 | {'n': 200, 'atr_mult': 2.0} |       15 |         -0.028 |    -3.877 | bear    | vol_baja  |      -56.409 |
| SOLUSDT  | 2023-02-11 | 2023-08-13 | {'n': 200, 'atr_mult': 2.0} |       33 |         -0.325 |   -51.198 | lateral | vol_baja  |       18.645 |
| SOLUSDT  | 2023-08-13 | 2024-02-11 | {'n': 100, 'atr_mult': 3.0} |       15 |          2.475 |   175.942 | bull    | vol_media |      337.007 |
| SOLUSDT  | 2024-02-12 | 2024-08-12 | {'n': 100, 'atr_mult': 3.0} |       24 |          0.315 |    45.544 | bull    | vol_baja  |       41.385 |
| SOLUSDT  | 2024-08-12 | 2025-02-10 | {'n': 100, 'atr_mult': 3.0} |       32 |         -0.015 |    -3.896 | bull    | vol_media |       35.838 |

### Nulo aleatorio agregado: expectancy p50 0.029, p95 0.325
