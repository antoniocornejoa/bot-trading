# Fases 8 y 9 · H-A2 {'n': 150, 'atr_mult': 3.0} · 4h · escenario base

## Sensibilidad (train+validation, símbolos agrupados)

Base: 688 operaciones, expectancy 0.555 R, t = 3.47, PF 2.64

| param    |   pct |   value |   trades |   expectancy_R |   t_stat |   profit_factor |
|:---------|------:|--------:|---------:|---------------:|---------:|----------------:|
| n        | -0.3  |  105    |      839 |          0.399 |    3.925 |           2.227 |
| n        | -0.2  |  120    |      767 |          0.452 |    4.032 |           2.393 |
| n        | -0.1  |  135    |      738 |          0.483 |    3.773 |           2.393 |
| n        | -0.05 |  142    |      704 |          0.54  |    3.541 |           2.587 |
| n        |  0    |  150    |      688 |          0.555 |    3.467 |           2.636 |
| n        |  0.05 |  158    |      657 |          0.639 |    3.332 |           2.796 |
| n        |  0.1  |  165    |      621 |          0.683 |    3.402 |           2.878 |
| n        |  0.2  |  180    |      593 |          0.729 |    3.449 |           3.069 |
| n        |  0.3  |  195    |      563 |          0.731 |    3.458 |           3.101 |
| atr_mult | -0.3  |    2.1  |      697 |          0.782 |    3.462 |           2.504 |
| atr_mult | -0.2  |    2.4  |      689 |          0.696 |    3.48  |           2.572 |
| atr_mult | -0.1  |    2.7  |      688 |          0.618 |    3.472 |           2.606 |
| atr_mult | -0.05 |    2.85 |      688 |          0.585 |    3.467 |           2.623 |
| atr_mult |  0    |    3    |      688 |          0.555 |    3.467 |           2.636 |
| atr_mult |  0.05 |    3.15 |      687 |          0.529 |    3.462 |           2.646 |
| atr_mult |  0.1  |    3.3  |      687 |          0.504 |    3.458 |           2.656 |
| atr_mult |  0.2  |    3.6  |      686 |          0.462 |    3.453 |           2.674 |
| atr_mult |  0.3  |    3.9  |      686 |          0.426 |    3.449 |           2.69  |

Veredicto: cambio de signo con ±20 %: **False**; caída media a ±30 %: -5%; frágil: **False**

## Monte Carlo sobre 474 operaciones OOS del walk-forward (5.4 años, 88 op/año agrupando símbolos)

Las operaciones OOS se generaron con 1 % de riesgo; los demás niveles escalan proporcionalmente el retorno por operación.

### Por nivel de riesgo (bloques de 5 operaciones, 5.000 caminos, misma cantidad de operaciones que el histórico OOS)

|   riesgo_% |   final_p5 |   final_p50 |   final_p95 |   DD_p50_% |   DD_p95_% |   DD_peor_% |   rachas_p95 |   P(perder) |   P(ruina -25%) |
|-----------:|-----------:|------------:|------------:|-----------:|-----------:|------------:|-------------:|------------:|----------------:|
|       0.25 |    672.904 |     913.812 |     1306.07 |     -4.68  |     -7.966 |     -14.124 |           37 |           0 |           0     |
|       0.5  |    885.481 |    1606.95  |     3208.61 |     -9.17  |    -15.376 |     -26.429 |           37 |           0 |           0.001 |
|       0.75 |   1138.82  |    2728.94  |     7457.69 |    -13.482 |    -22.286 |     -37.118 |           37 |           0 |           0.024 |
|       1    |   1437.02  |    4499.52  |    16587.4  |    -17.619 |    -28.642 |     -46.378 |           37 |           0 |           0.117 |

Concentración del beneficio: el 10 % mejor de las operaciones aporta el 177% del beneficio neto; el 5 % mejor, el 138%. Es la naturaleza del seguimiento de tendencia (payoff alto, win rate bajo): la ventaja está en dejar correr pocas operaciones grandes.

### Estrés a 0,5 % de riesgo

| scenario      |   final_p5 |   final_p50 |   max_dd_p50_pct |   max_dd_p95_pct |   consec_losses_p95 |   ruin_prob |
|:--------------|-----------:|------------:|-----------------:|-----------------:|--------------------:|------------:|
| base          |    885.142 |    1588.78  |           -9.333 |          -15.193 |                  39 |       0     |
| win_rate_-5pp |    731.743 |    1226.19  |          -10.109 |          -16.771 |                  41 |       0.002 |
| avg_win_-10%  |    759.451 |    1294.98  |           -9.83  |          -16.159 |                  39 |       0.001 |
| avg_loss_+10% |    800.932 |    1443.33  |          -10.709 |          -17.566 |                  39 |       0.002 |
| slippage_x2   |    666.193 |    1196.17  |          -13.122 |          -21.778 |                  44 |       0.018 |
| drop_best_5%  |    279.257 |     336.729 |          -34.476 |          -44.989 |                  51 |       0.903 |
| blocks_5      |    880.932 |    1628.27  |           -9.239 |          -15.544 |                  36 |       0.001 |

## Simulación de crecimiento a 5 años desde US$500 (NO es una predicción)

Remuestreo de las operaciones OOS a la frecuencia histórica; kill switch a −25 % desde el máximo; P(nivel) = probabilidad de alcanzar el nivel antes de tocar el kill switch; t_med = mediana de años hasta alcanzarlo entre los caminos que lo alcanzan.

|   risk_scale |   n_trades_5y |   ruin_prob |   P(750) |   t_med(750)_años |   P(1000) |   t_med(1000)_años |   P(2000) |   t_med(2000)_años |   P(5000) |   t_med(5000)_años |   P(10000) |   t_med(10000)_años |   P(25000) |   t_med(25000)_años |   P(50000) |   t_med(50000)_años |   final_p5 |   final_p50 |   final_p95 |   max_dd_p50 |   max_dd_p95 |
|-------------:|--------------:|------------:|---------:|------------------:|----------:|-------------------:|----------:|-------------------:|----------:|-------------------:|-----------:|--------------------:|-----------:|--------------------:|-----------:|--------------------:|-----------:|------------:|------------:|-------------:|-------------:|
|         0.25 |           437 |       0     |    0.803 |             3.222 |     0.257 |              4.307 |     0     |            nan     |     0     |            nan     |      0     |             nan     |      0     |             nan     |      0     |              nan    |    642.514 |     871.586 |     1210.96 |       -0.047 |       -0.082 |
|         0.5  |           437 |       0.001 |    0.978 |             1.794 |     0.869 |              2.936 |     0.224 |              4.342 |     0.002 |              4.524 |      0     |             nan     |      0     |             nan     |      0     |              nan    |    808.508 |    1467.07  |     2782.91 |       -0.092 |       -0.158 |
|         0.75 |           437 |       0.026 |    0.987 |             1.234 |     0.956 |              2.079 |     0.649 |              3.645 |     0.1   |              4.49  |      0.008 |               4.604 |      0     |             nan     |      0     |              nan    |    996.394 |    2387.94  |     6067.28 |       -0.136 |       -0.228 |
|         1    |           437 |       0.127 |    0.965 |             0.937 |     0.937 |              1.577 |     0.798 |              3.005 |     0.359 |              4.113 |      0.094 |               4.461 |      0.007 |               4.673 |      0.001 |                4.65 |   1209.85  |    3778.34  |    12717.6  |       -0.177 |       -0.292 |
