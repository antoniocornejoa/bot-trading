# Fases 8 y 9 · H-A2 {'n': 150, 'atr_mult': 3.0} · 4h · escenario base

## Sensibilidad (train+validation, símbolos agrupados)

Base: 689 operaciones, expectancy 0.554 R, t = 3.47, PF 2.63

| param    |   pct |   value |   trades |   expectancy_R |   t_stat |   profit_factor |
|:---------|------:|--------:|---------:|---------------:|---------:|----------------:|
| n        | -0.3  |  105    |      839 |          0.399 |    3.934 |           2.236 |
| n        | -0.2  |  120    |      767 |          0.452 |    4.035 |           2.396 |
| n        | -0.1  |  135    |      738 |          0.483 |    3.771 |           2.389 |
| n        | -0.05 |  142    |      705 |          0.54  |    3.54  |           2.585 |
| n        |  0    |  150    |      689 |          0.554 |    3.465 |           2.632 |
| n        |  0.05 |  158    |      657 |          0.64  |    3.338 |           2.811 |
| n        |  0.1  |  165    |      621 |          0.683 |    3.405 |           2.888 |
| n        |  0.2  |  180    |      593 |          0.728 |    3.446 |           3.061 |
| n        |  0.3  |  195    |      564 |          0.729 |    3.456 |           3.093 |
| atr_mult | -0.3  |    2.1  |      698 |          0.782 |    3.466 |           2.513 |
| atr_mult | -0.2  |    2.4  |      690 |          0.695 |    3.481 |           2.576 |
| atr_mult | -0.1  |    2.7  |      689 |          0.617 |    3.473 |           2.607 |
| atr_mult | -0.05 |    2.85 |      689 |          0.584 |    3.466 |           2.62  |
| atr_mult |  0    |    3    |      689 |          0.554 |    3.465 |           2.632 |
| atr_mult |  0.05 |    3.15 |      687 |          0.529 |    3.462 |           2.646 |
| atr_mult |  0.1  |    3.3  |      687 |          0.505 |    3.46  |           2.658 |
| atr_mult |  0.2  |    3.6  |      686 |          0.463 |    3.454 |           2.675 |
| atr_mult |  0.3  |    3.9  |      686 |          0.426 |    3.449 |           2.689 |

Veredicto: cambio de signo con ±20 %: **False**; caída media a ±30 %: -5%; frágil: **False**

## Monte Carlo sobre 479 operaciones OOS del walk-forward (5.4 años, 88 op/año agrupando símbolos)

Las operaciones OOS se generaron con 1 % de riesgo; los demás niveles escalan proporcionalmente el retorno por operación.

### Por nivel de riesgo (bloques de 5 operaciones, 5.000 caminos, misma cantidad de operaciones que el histórico OOS)

|   riesgo_% |   final_p5 |   final_p50 |   final_p95 |   DD_p50_% |   DD_p95_% |   DD_peor_% |   rachas_p95 |   P(perder) |   P(ruina -25%) |
|-----------:|-----------:|------------:|------------:|-----------:|-----------:|------------:|-------------:|------------:|----------------:|
|       0.25 |    677.512 |     928.072 |     1354    |     -4.724 |     -8.164 |     -15.712 |           37 |           0 |           0     |
|       0.5  |    895.279 |    1653.75  |     3451.71 |     -9.259 |    -15.76  |     -29.183 |           37 |           0 |           0.001 |
|       0.75 |   1158.59  |    2852.57  |     8368.49 |    -13.61  |    -22.757 |     -40.686 |           37 |           0 |           0.024 |
|       1    |   1472.09  |    4768.42  |    19226.9  |    -17.774 |    -29.254 |     -50.47  |           37 |           0 |           0.121 |

Concentración del beneficio: el 10 % mejor de las operaciones aporta el 175% del beneficio neto; el 5 % mejor, el 137%. Es la naturaleza del seguimiento de tendencia (payoff alto, win rate bajo): la ventaja está en dejar correr pocas operaciones grandes.

### Estrés a 0,5 % de riesgo

| scenario      |   final_p5 |   final_p50 |   max_dd_p50_pct |   max_dd_p95_pct |   consec_losses_p95 |   ruin_prob |
|:--------------|-----------:|------------:|-----------------:|-----------------:|--------------------:|------------:|
| base          |    893.954 |    1613.48  |           -9.565 |          -15.935 |                  40 |       0     |
| win_rate_-5pp |    735.727 |    1202.49  |          -10.321 |          -17.286 |                  41 |       0.003 |
| avg_win_-10%  |    768.391 |    1310.71  |          -10.009 |          -16.775 |                  40 |       0.002 |
| avg_loss_+10% |    811.366 |    1464.48  |          -10.916 |          -18.249 |                  40 |       0.005 |
| slippage_x2   |    670.814 |    1211.15  |          -13.455 |          -22.545 |                  44 |       0.023 |
| drop_best_5%  |    278.21  |     333.709 |          -35.091 |          -45.339 |                  52 |       0.916 |
| blocks_5      |    898.775 |    1702.18  |           -9.299 |          -15.151 |                  37 |       0.001 |

## Simulación de crecimiento a 5 años desde US$500 (NO es una predicción)

Remuestreo de las operaciones OOS a la frecuencia histórica; kill switch a −25 % desde el máximo; P(nivel) = probabilidad de alcanzar el nivel antes de tocar el kill switch; t_med = mediana de años hasta alcanzarlo entre los caminos que lo alcanzan.

|   risk_scale |   n_trades_5y |   ruin_prob |   P(750) |   t_med(750)_años |   P(1000) |   t_med(1000)_años |   P(2000) |   t_med(2000)_años |   P(5000) |   t_med(5000)_años |   P(10000) |   t_med(10000)_años |   P(25000) |   t_med(25000)_años |   P(50000) |   t_med(50000)_años |   final_p5 |   final_p50 |   final_p95 |   max_dd_p50 |   max_dd_p95 |
|-------------:|--------------:|------------:|---------:|------------------:|----------:|-------------------:|----------:|-------------------:|----------:|-------------------:|-----------:|--------------------:|-----------:|--------------------:|-----------:|--------------------:|-----------:|------------:|------------:|-------------:|-------------:|
|         0.25 |           442 |       0     |    0.823 |             3.222 |     0.285 |              4.251 |     0     |            nan     |     0     |            nan     |      0     |             nan     |      0     |             nan     |      0     |             nan     |    653.937 |     881.537 |     1259.36 |       -0.048 |       -0.081 |
|         0.5  |           442 |       0.001 |    0.984 |             1.769 |     0.886 |              2.928 |     0.248 |              4.296 |     0.002 |              4.522 |      0     |             nan     |      0     |             nan     |      0     |             nan     |    835.364 |    1497.75  |     2994.31 |       -0.094 |       -0.156 |
|         0.75 |           442 |       0.023 |    0.987 |             1.198 |     0.962 |              2.069 |     0.678 |              3.669 |     0.126 |              4.466 |      0.012 |               4.658 |      0     |             nan     |      0     |             nan     |   1047.14  |    2467.34  |     6761.73 |       -0.138 |       -0.225 |
|         1    |           442 |       0.133 |    0.96  |             0.904 |     0.935 |              1.549 |     0.805 |              2.996 |     0.38  |              4.07  |      0.121 |               4.443 |      0.011 |               4.624 |      0.001 |               4.794 |   1290.26  |    3937.72  |    14594    |       -0.179 |       -0.289 |
