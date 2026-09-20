# Fase 5 · Candidatas en train / validation

Escenario de costes: **base** (ida y vuelta 0.28 % sin impacto). Partición 60/20/20 por tiempo; el 20 % final (test) **no se ha usado**.

## BTCUSDT  (base 1h, hash `74ead4110a1098b3`)

### 4h · 19,757 velas (2017-08-17 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=100.000, median_val_expectancy_R=0.376, median_train_expectancy_R=0.523, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        20 |       10 |          2 |          200 |            163 |                0.405 |          2.948 |                 1.935 |           58 |              0.58  |        1.473 |               2.252 |        1.733 |         18.902 |                 -9.309 |            0.18  |
|        20 |       20 |          2 |          200 |            163 |                0.404 |          2.942 |                 1.928 |           59 |              0.553 |        1.418 |               2.152 |        1.678 |         18.221 |                 -9.309 |            0.188 |
|        20 |       10 |          3 |          200 |            123 |                0.645 |          2.681 |                 3.067 |           50 |              0.474 |        1.388 |               2.17  |        1.619 |         13.139 |                 -8.712 |            0.152 |
|        20 |       10 |          2 |          100 |            190 |                0.325 |          2.672 |                 1.711 |           63 |              0.61  |        1.644 |               2.279 |        1.913 |         22.011 |                 -8.041 |            0.173 |
|        20 |       20 |          2 |          100 |            190 |                0.324 |          2.663 |                 1.702 |           64 |              0.584 |        1.588 |               2.183 |        1.858 |         21.288 |                 -9.194 |            0.18  |

#### H-G1 · trend_pullback
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=4.167, median_val_expectancy_R=-0.062, median_train_expectancy_R=-0.055, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          20 |        2   |        3 |            132 |                0.018 |          0.261 |                 1.043 |           50 |             -0.095 |       -0.794 |               0.772 |       -0.586 |         -2.696 |                 -7.622 |            8.444 |
|         50 |          20 |        2   |        2 |            132 |                0.007 |          0.111 |                 1.013 |           50 |             -0.132 |       -1.177 |               0.687 |       -0.86  |         -3.664 |                 -8.375 |          inf     |
|         50 |          20 |        1.5 |        3 |            137 |                0.008 |          0.099 |                 1.007 |           55 |             -0.209 |       -1.514 |               0.646 |       -1.166 |         -6.322 |                -13.776 |          inf     |
|         50 |          25 |        2   |        3 |            190 |               -0.002 |         -0.036 |                 0.985 |           78 |             -0.005 |       -0.054 |               0.977 |       -0.04  |         -0.352 |                 -7.635 |            1.079 |
|         50 |          20 |        1.5 |        2 |            137 |               -0.005 |         -0.064 |                 0.978 |           55 |             -0.253 |       -1.988 |               0.571 |       -1.515 |         -7.558 |                -14.708 |          inf     |

#### H-A2 · ma_momentum
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=100.000, median_val_expectancy_R=0.417, median_train_expectancy_R=0.570, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          3 |            233 |                0.417 |          2.302 |                 2.347 |           87 |              0.277 |        1.074 |               1.812 |        1.202 |         12.811 |                -10.929 |            0.225 |
| 100 |          2 |            241 |                0.601 |          2.288 |                 2.216 |           88 |              0.417 |        1.093 |               1.831 |        1.226 |         19.235 |                -16.002 |            0.226 |
| 100 |          4 |            233 |                0.307 |          2.256 |                 2.329 |           87 |              0.199 |        1.025 |               1.758 |        1.144 |          9.237 |                 -8.623 |            0.231 |
| 150 |          3 |            185 |                0.581 |          2.103 |                 2.802 |           83 |              0.279 |        1.038 |               1.836 |        1.133 |         12.245 |                -11.914 |            0.236 |
| 150 |          4 |            184 |                0.438 |          2.101 |                 2.868 |           82 |              0.21  |        1.029 |               1.841 |        1.12  |          9.206 |                 -9.108 |            0.232 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=17.640, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.920, max_drawdown_pct=-83.879, cagr_pct=49.980, cost_ratio=0.002
- **ma_momentum**: trades=218, win_rate_pct=14.679, expectancy_R=0.637, t_stat=2.336, profit_factor=3.092, payoff=18.195, sharpe=1.402, max_drawdown_pct=-16.086, cagr_pct=18.612, cost_ratio=0.096
- **rsi2_meanrev**: trades=328, win_rate_pct=64.024, expectancy_R=-0.048, t_stat=-1.798, profit_factor=0.751, payoff=0.426, sharpe=-0.643, max_drawdown_pct=-16.073, cagr_pct=-2.219, cost_ratio=8.970
- **random**: n=200, expectancy_R_p50=0.049, expectancy_R_p95=0.202, total_return_p95=44.023, sharpe_p95=0.880

### 1d · 3,286 velas (2017-08-18 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=4, pct_val_positive=100.000, median_val_expectancy_R=0.523, median_train_expectancy_R=0.420, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        20 |       10 |          2 |          100 |             35 |                0.61  |          1.87  |                 2.433 |           16 |              0.519 |        1.035 |               2.331 |        1.008 |          4.526 |                 -3.602 |            0.075 |
|        20 |       20 |          2 |          100 |             35 |                0.608 |          1.863 |                 2.422 |           16 |              0.519 |        1.035 |               2.331 |        1.008 |          4.526 |                 -3.602 |            0.075 |
|        55 |       10 |          2 |          100 |             30 |                0.231 |          0.765 |                 1.459 |           11 |              0.527 |        1.033 |               2.441 |        0.84  |          3.186 |                 -3.196 |            0.073 |
|        55 |       20 |          2 |          100 |             30 |                0.231 |          0.765 |                 1.459 |           11 |              0.527 |        1.033 |               2.441 |        0.84  |          3.186 |                 -3.196 |            0.073 |

#### H-G1 · trend_pullback
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=16, pct_val_positive=81.250, median_val_expectancy_R=0.113, median_train_expectancy_R=0.146, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        100 |          25 |        1.5 |        2 |             35 |                0.215 |          1.485 |                 1.739 |           26 |             -0.061 |       -0.3   |               0.874 |       -0.228 |         -0.946 |                 -5.152 |          inf     |
|        100 |          25 |        1.5 |        3 |             35 |                0.205 |          1.423 |                 1.704 |           26 |             -0.011 |       -0.051 |               0.967 |       -0.041 |         -0.252 |                 -5.156 |            1.506 |
|         50 |          25 |        1.5 |        2 |             32 |                0.207 |          1.293 |                 1.634 |           18 |              0.121 |        0.466 |               1.246 |        0.348 |          1.15  |                 -3.363 |            0.314 |
|         50 |          25 |        1.5 |        3 |             32 |                0.207 |          1.278 |                 1.635 |           18 |              0.192 |        0.681 |               1.398 |        0.512 |          1.865 |                 -3.363 |            0.221 |
|        100 |          25 |        2   |        2 |             33 |                0.151 |          1.224 |                 1.62  |           21 |             -0.011 |       -0.062 |               0.961 |       -0.049 |         -0.174 |                 -3.758 |            1.614 |

#### H-A2 · ma_momentum
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=3, pct_val_positive=100.000, median_val_expectancy_R=0.857, median_train_expectancy_R=1.840, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          2 |             30 |                2.769 |          1.335 |                 8.596 |           18 |              1.207 |        1.033 |               3.734 |        1.131 |         11.573 |                -10.041 |            0.034 |
| 100 |          4 |             30 |                1.38  |          1.331 |                 8.839 |           16 |              0.69  |        1.049 |               3.984 |        1.104 |          5.991 |                 -5.55  |            0.029 |
| 100 |          3 |             30 |                1.84  |          1.331 |                 8.64  |           17 |              0.857 |        1.037 |               3.831 |        1.105 |          7.869 |                 -7.168 |            0.031 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=20.566, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.958, max_drawdown_pct=-83.187, cagr_pct=53.147, cost_ratio=0.002
- **ma_momentum**: trades=27, win_rate_pct=25.926, expectancy_R=1.701, t_stat=1.736, profit_factor=9.077, payoff=26.805, sharpe=0.718, max_drawdown_pct=-16.639, cagr_pct=6.082, cost_ratio=0.015
- **rsi2_meanrev**: trades=49, win_rate_pct=63.265, expectancy_R=-0.030, t_stat=-0.424, profit_factor=0.837, payoff=0.489, sharpe=-0.143, max_drawdown_pct=-3.756, cagr_pct=-0.206, cost_ratio=inf
- **random**: n=200, expectancy_R_p50=0.216, expectancy_R_p95=0.496, total_return_p95=22.304, sharpe_p95=0.986

## ETHUSDT  (base 1h, hash `69426de104e9a41d`)

### 4h · 19,757 velas (2017-08-17 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=83.333, median_val_expectancy_R=0.069, median_train_expectancy_R=0.356, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        55 |       10 |          3 |          100 |            106 |                0.452 |          2.447 |                 2.077 |           36 |              0.098 |        0.339 |               1.19  |        0.306 |          1.695 |                 -7.699 |            0.417 |
|        55 |       20 |          3 |          100 |            100 |                0.501 |          2.36  |                 2.093 |           35 |              0.183 |        0.581 |               1.368 |        0.532 |          3.282 |                 -7.997 |            0.264 |
|        55 |       10 |          3 |          200 |             98 |                0.412 |          2.332 |                 2.067 |           32 |              0.189 |        0.591 |               1.434 |        0.545 |          3.117 |                 -6.293 |            0.253 |
|       100 |       20 |          2 |          100 |            104 |                0.334 |          2.304 |                 1.782 |           34 |              0.015 |        0.079 |               1.021 |        0.059 |          0.174 |                 -6.097 |            0.906 |
|        55 |       20 |          3 |          200 |             92 |                0.476 |          2.293 |                 2.155 |           31 |              0.289 |        0.83  |               1.667 |        0.766 |          4.759 |                 -6.597 |            0.177 |

#### H-G1 · trend_pullback
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=0.000, median_val_expectancy_R=-0.146, median_train_expectancy_R=-0.036, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          30 |        1.5 |        3 |            290 |                0.016 |          0.276 |                 1.027 |           96 |             -0.217 |       -2.43  |               0.577 |       -1.699 |        -11.095 |                -20.724 |          inf     |
|         50 |          25 |        2   |        3 |            208 |               -0.007 |         -0.121 |                 0.971 |           66 |             -0.097 |       -1.147 |               0.701 |       -0.819 |         -3.615 |                 -8.479 |          inf     |
|         50 |          25 |        1.5 |        3 |            216 |               -0.01  |         -0.152 |                 0.966 |           69 |             -0.174 |       -1.719 |               0.616 |       -1.232 |         -6.692 |                -13.492 |          inf     |
|         50 |          20 |        2   |        3 |            133 |               -0.013 |         -0.179 |                 0.954 |           35 |             -0.044 |       -0.407 |               0.83  |       -0.282 |         -0.884 |                 -3.522 |            1.977 |
|         50 |          30 |        2   |        3 |            280 |               -0.009 |         -0.181 |                 0.965 |           88 |             -0.163 |       -2.132 |               0.578 |       -1.492 |         -7.766 |                -14.223 |          inf     |

#### H-A2 · ma_momentum
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=100.000, median_val_expectancy_R=0.133, median_train_expectancy_R=0.613, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 200 |          3 |            128 |                0.83  |          2.608 |                 4.241 |           66 |              0.116 |        0.434 |               1.265 |        0.366 |          3.513 |                -11.717 |            0.402 |
| 200 |          2 |            130 |                1.218 |          2.591 |                 4.079 |           68 |              0.182 |        0.469 |               1.271 |        0.399 |          5.266 |                -17.009 |            0.407 |
| 200 |          4 |            128 |                0.613 |          2.566 |                 4.097 |           65 |              0.09  |        0.442 |               1.284 |        0.371 |          2.833 |                 -9.137 |            0.384 |
| 150 |          3 |            171 |                0.546 |          2.423 |                 3.346 |           63 |              0.206 |        0.682 |               1.521 |        0.631 |          6.474 |                -10.048 |            0.268 |
| 150 |          2 |            175 |                0.799 |          2.421 |                 3.378 |           63 |              0.348 |        0.772 |               1.622 |        0.735 |         10.844 |                -14.289 |            0.246 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=9.190, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.808, max_drawdown_pct=-94.079, cagr_pct=37.900, cost_ratio=0.002
- **ma_momentum**: trades=192, win_rate_pct=18.229, expectancy_R=0.585, t_stat=2.558, profit_factor=2.608, payoff=13.689, sharpe=1.142, max_drawdown_pct=-14.500, cagr_pct=15.395, cost_ratio=0.097
- **rsi2_meanrev**: trades=344, win_rate_pct=63.663, expectancy_R=-0.064, t_stat=-2.229, profit_factor=0.718, payoff=0.412, sharpe=-0.853, max_drawdown_pct=-20.277, cagr_pct=-3.090, cost_ratio=inf
- **random**: n=200, expectancy_R_p50=0.075, expectancy_R_p95=0.295, total_return_p95=39.618, sharpe_p95=0.779

### 1d · 3,286 velas (2017-08-18 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=2, pct_val_positive=100.000, median_val_expectancy_R=0.199, median_train_expectancy_R=0.584, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        20 |       20 |          2 |          100 |             33 |                0.584 |          1.981 |                 2.861 |           13 |              0.201 |        0.442 |               1.347 |        0.386 |          1.371 |                 -4.658 |            0.168 |
|        20 |       10 |          2 |          100 |             33 |                0.584 |          1.979 |                 2.861 |           13 |              0.196 |        0.432 |               1.337 |        0.378 |          1.342 |                 -4.664 |            0.171 |

#### H-G1 · trend_pullback
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=12, pct_val_positive=58.333, median_val_expectancy_R=0.015, median_train_expectancy_R=0.161, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          30 |        1.5 |        2 |             52 |                0.242 |          1.973 |                 1.762 |           11 |             -0.138 |       -0.461 |               0.738 |       -0.307 |         -0.862 |                 -3.177 |          inf     |
|         50 |          30 |        1.5 |        3 |             52 |                0.238 |          1.93  |                 1.748 |           11 |             -0.176 |       -0.623 |               0.667 |       -0.398 |         -1.093 |                 -3.552 |          inf     |
|        100 |          30 |        2   |        2 |             52 |                0.155 |          1.627 |                 1.63  |           19 |              0.049 |        0.275 |               1.15  |        0.194 |          0.487 |                 -1.966 |            0.412 |
|        100 |          30 |        2   |        3 |             52 |                0.156 |          1.617 |                 1.633 |           19 |              0.04  |        0.228 |               1.123 |        0.16  |          0.398 |                 -1.966 |            0.462 |
|        100 |          25 |        2   |        3 |             42 |                0.166 |          1.51  |                 1.652 |           17 |              0.008 |        0.041 |               1.015 |        0.031 |          0.047 |                 -2.158 |            0.865 |

#### H-A2 · ma_momentum
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=3, pct_val_positive=100.000, median_val_expectancy_R=0.334, median_train_expectancy_R=1.133, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          4 |             31 |                0.913 |          1.243 |                 5.194 |           19 |              0.251 |        0.769 |               2.359 |        0.592 |          2.575 |                 -6.395 |            0.075 |
| 100 |          2 |             32 |                1.753 |          1.235 |                 4.777 |           20 |              0.458 |        0.739 |               2.186 |        0.592 |          4.804 |                -11.901 |            0.084 |
| 100 |          3 |             32 |                1.133 |          1.195 |                 4.568 |           19 |              0.334 |        0.769 |               2.339 |        0.6   |          3.406 |                 -8.305 |            0.076 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=10.465, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.834, max_drawdown_pct=-93.965, cagr_pct=40.320, cost_ratio=0.002
- **ma_momentum**: trades=21, win_rate_pct=38.095, expectancy_R=2.398, t_stat=1.240, profit_factor=13.819, payoff=21.917, sharpe=0.526, max_drawdown_pct=-29.548, cagr_pct=6.238, cost_ratio=0.010
- **rsi2_meanrev**: trades=54, win_rate_pct=68.519, expectancy_R=-0.013, t_stat=-0.222, profit_factor=0.916, payoff=0.422, sharpe=-0.072, max_drawdown_pct=-3.383, cagr_pct=-0.104, cost_ratio=5.576
- **random**: n=200, expectancy_R_p50=0.110, expectancy_R_p95=0.437, total_return_p95=19.069, sharpe_p95=0.957

## SOLUSDT  (base 1h, hash `917bc6c2f8132fb2`)

### 4h · 13,257 velas (2020-08-11 → 2026-08-31)

#### H-A1 · donchian_trend
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=75.000, median_val_expectancy_R=0.042, median_train_expectancy_R=0.197, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|       100 |       20 |          3 |          200 |             50 |                0.593 |          2.178 |                 2.548 |           17 |              0.012 |        0.054 |               1.021 |        0.048 |          0.113 |                 -3.339 |            0.839 |
|       100 |       20 |          3 |          100 |             52 |                0.546 |          2.068 |                 2.388 |           17 |              0.012 |        0.054 |               1.021 |        0.048 |          0.113 |                 -3.339 |            0.839 |
|       100 |       10 |          3 |          200 |             56 |                0.458 |          1.99  |                 2.253 |           17 |              0.074 |        0.347 |               1.2   |        0.244 |          0.994 |                 -2.928 |            0.373 |
|       100 |       10 |          3 |          100 |             58 |                0.42  |          1.878 |                 2.12  |           17 |              0.074 |        0.347 |               1.2   |        0.244 |          0.994 |                 -2.928 |            0.373 |
|        55 |       20 |          3 |          100 |             69 |                0.399 |          1.864 |                 2.068 |           26 |             -0.018 |       -0.096 |               0.942 |       -0.065 |         -0.496 |                 -4.095 |            2.301 |

#### H-G1 · trend_pullback
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=0.000, median_val_expectancy_R=-0.177, median_train_expectancy_R=0.035, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          20 |        1.5 |        3 |             93 |                0.11  |          1.149 |                 1.289 |           33 |             -0.206 |       -1.271 |               0.62  |       -1.118 |         -5.577 |                 -9.522 |              inf |
|         50 |          20 |        2   |        3 |             92 |                0.086 |          1.127 |                 1.303 |           33 |             -0.215 |       -1.54  |               0.546 |       -1.391 |         -5.775 |                 -8.147 |              inf |
|         50 |          20 |        1.5 |        2 |             93 |                0.1   |          1.083 |                 1.263 |           33 |             -0.198 |       -1.215 |               0.632 |       -1.076 |         -5.382 |                 -9.524 |              inf |
|         50 |          20 |        2   |        2 |             92 |                0.078 |          1.062 |                 1.277 |           33 |             -0.209 |       -1.49  |               0.557 |       -1.352 |         -5.625 |                 -8.145 |              inf |
|        100 |          20 |        1.5 |        3 |            141 |                0.067 |          0.855 |                 1.153 |           46 |             -0.292 |       -2.218 |               0.493 |       -1.882 |        -10.645 |                -13.506 |              inf |

#### H-A2 · ma_momentum
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=66.667, median_val_expectancy_R=0.052, median_train_expectancy_R=1.006, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          2 |            159 |                1.038 |          2.016 |                 3.912 |           71 |             -0.053 |       -0.37  |               0.852 |       -0.228 |         -3.441 |                -10.369 |          inf     |
| 100 |          4 |            158 |                0.522 |          2.012 |                 3.907 |           69 |             -0.037 |       -0.49  |               0.822 |       -0.325 |         -2.196 |                 -5.867 |          inf     |
| 100 |          3 |            158 |                0.694 |          2.006 |                 3.869 |           69 |             -0.041 |       -0.411 |               0.844 |       -0.265 |         -2.479 |                 -7.405 |          inf     |
| 150 |          4 |            144 |                0.755 |          1.701 |                 4.517 |           48 |              0.027 |        0.212 |               1.107 |        0.171 |          0.922 |                 -5.409 |            0.543 |
| 150 |          3 |            144 |                1.006 |          1.7   |                 4.375 |           48 |              0.052 |        0.313 |               1.167 |        0.25  |          1.814 |                 -6.806 |            0.446 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=49.136, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=1.266, max_drawdown_pct=-96.599, cagr_pct=124.322, cost_ratio=0.001
- **ma_momentum**: trades=163, win_rate_pct=15.337, expectancy_R=0.977, t_stat=1.698, profit_factor=3.616, payoff=25.082, sharpe=1.374, max_drawdown_pct=-27.495, cagr_pct=29.955, cost_ratio=0.045
- **rsi2_meanrev**: trades=210, win_rate_pct=63.333, expectancy_R=-0.009, t_stat=-0.305, profit_factor=0.940, payoff=0.546, sharpe=-0.125, max_drawdown_pct=-7.295, cagr_pct=-0.413, cost_ratio=1.485
- **random**: n=200, expectancy_R_p50=0.067, expectancy_R_p95=0.386, total_return_p95=24.720, sharpe_p95=0.847

### 1d · 2,208 velas (2020-08-12 → 2026-08-31)

#### H-A1 · donchian_trend
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=0, pct_val_positive=nan, median_val_expectancy_R=nan, median_train_expectancy_R=nan, n_val_t_ge_2=0

Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.

#### H-G1 · trend_pullback
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=1, pct_val_positive=0.000, median_val_expectancy_R=-0.520, median_train_expectancy_R=0.218, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        100 |          30 |        1.5 |        2 |             30 |                0.218 |          1.231 |                 1.602 |           14 |              -0.52 |       -2.271 |               0.285 |       -1.905 |          -5.87 |                 -7.204 |              inf |

#### H-A2 · ma_momentum
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=9, configs_valid=0, pct_val_positive=nan, median_val_expectancy_R=nan, median_train_expectancy_R=nan, n_val_t_ge_2=0

Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=39.712, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=1.231, max_drawdown_pct=-96.270, cagr_pct=115.092, cost_ratio=0.001
- **ma_momentum**: trades=19, win_rate_pct=21.053, expectancy_R=2.922, t_stat=1.283, profit_factor=10.369, payoff=48.646, sharpe=0.790, max_drawdown_pct=-17.945, cagr_pct=10.344, cost_ratio=0.008
- **rsi2_meanrev**: trades=35, win_rate_pct=68.571, expectancy_R=0.016, t_stat=0.255, profit_factor=1.127, payoff=0.519, sharpe=0.104, max_drawdown_pct=-2.406, cagr_pct=0.115, cost_ratio=0.420
- **random**: n=200, expectancy_R_p50=0.092, expectancy_R_p95=0.368, total_return_p95=14.026, sharpe_p95=1.174
