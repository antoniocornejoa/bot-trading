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
|        20 |       10 |          2 |          200 |            163 |                0.405 |          2.948 |                 1.935 |           58 |              0.577 |        1.464 |               2.238 |        1.727 |         18.791 |                 -9.465 |            0.181 |
|        20 |       20 |          2 |          200 |            163 |                0.404 |          2.942 |                 1.928 |           59 |              0.55  |        1.41  |               2.139 |        1.671 |         18.113 |                 -9.465 |            0.189 |
|        20 |       10 |          3 |          200 |            123 |                0.645 |          2.681 |                 3.067 |           50 |              0.474 |        1.388 |               2.17  |        1.622 |         13.139 |                 -8.712 |            0.152 |
|        20 |       10 |          2 |          100 |            190 |                0.325 |          2.672 |                 1.711 |           63 |              0.608 |        1.636 |               2.266 |        1.906 |         21.895 |                 -8.045 |            0.173 |
|        20 |       20 |          2 |          100 |            190 |                0.324 |          2.663 |                 1.702 |           64 |              0.582 |        1.58  |               2.172 |        1.851 |         21.179 |                 -9.197 |            0.181 |

#### H-G1 · trend_pullback
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=8.333, median_val_expectancy_R=-0.031, median_train_expectancy_R=-0.057, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          20 |        2   |        3 |            131 |                0.026 |          0.363 |                 1.067 |           50 |             -0.101 |       -0.836 |               0.761 |       -0.623 |         -2.858 |                 -7.901 |           15.716 |
|         50 |          20 |        2   |        2 |            131 |                0.014 |          0.209 |                 1.034 |           50 |             -0.138 |       -1.217 |               0.677 |       -0.9   |         -3.828 |                 -8.656 |          inf     |
|         50 |          20 |        1.5 |        3 |            134 |                0.007 |          0.079 |                 1.004 |           54 |             -0.206 |       -1.45  |               0.652 |       -1.104 |         -6.129 |                -13.456 |          inf     |
|         50 |          25 |        2   |        3 |            190 |               -0.003 |         -0.051 |                 0.982 |           78 |             -0.006 |       -0.067 |               0.974 |       -0.051 |         -0.41  |                 -7.628 |            1.093 |
|         50 |          20 |        1.5 |        2 |            134 |               -0.008 |         -0.091 |                 0.972 |           54 |             -0.251 |       -1.912 |               0.576 |       -1.44  |         -7.373 |                -14.399 |          inf     |

#### H-A2 · ma_momentum
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=100.000, median_val_expectancy_R=0.399, median_train_expectancy_R=0.570, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          3 |            233 |                0.417 |          2.301 |                 2.346 |           87 |              0.276 |        1.068 |               1.806 |        1.196 |         12.73  |                -11.118 |            0.225 |
| 100 |          2 |            241 |                0.597 |          2.274 |                 2.206 |           88 |              0.399 |        1.042 |               1.764 |        1.163 |         18.182 |                -17.205 |            0.234 |
| 100 |          4 |            233 |                0.308 |          2.263 |                 2.336 |           87 |              0.198 |        1.021 |               1.752 |        1.139 |          9.186 |                 -8.683 |            0.232 |
| 150 |          3 |            185 |                0.581 |          2.103 |                 2.802 |           82 |              0.285 |        1.05  |               1.855 |        1.149 |         12.419 |                -11.827 |            0.231 |
| 150 |          4 |            184 |                0.438 |          2.101 |                 2.868 |           82 |              0.21  |        1.029 |               1.841 |        1.12  |          9.206 |                 -9.108 |            0.232 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=17.640, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.920, max_drawdown_pct=-83.879, cagr_pct=49.980, cost_ratio=0.002
- **ma_momentum**: trades=217, win_rate_pct=14.747, expectancy_R=0.641, t_stat=2.338, profit_factor=3.102, payoff=18.141, sharpe=1.404, max_drawdown_pct=-16.086, cagr_pct=18.639, cost_ratio=0.095
- **rsi2_meanrev**: trades=327, win_rate_pct=64.220, expectancy_R=-0.046, t_stat=-1.704, profit_factor=0.760, payoff=0.427, sharpe=-0.612, max_drawdown_pct=-15.765, cagr_pct=-2.105, cost_ratio=6.462
- **random**: n=200, expectancy_R_p50=0.050, expectancy_R_p95=0.202, total_return_p95=42.631, sharpe_p95=0.860

### 1d · 3,286 velas (2017-08-18 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=4, pct_val_positive=100.000, median_val_expectancy_R=0.690, median_train_expectancy_R=0.402, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        20 |       10 |          2 |          100 |             35 |                0.593 |          1.803 |                 2.346 |           15 |              0.652 |        1.258 |               3.08  |        1.175 |          5.389 |                 -3.609 |            0.061 |
|        20 |       20 |          2 |          100 |             35 |                0.591 |          1.796 |                 2.335 |           15 |              0.652 |        1.258 |               3.08  |        1.175 |          5.389 |                 -3.609 |            0.061 |
|        55 |       10 |          2 |          100 |             30 |                0.212 |          0.693 |                 1.401 |           10 |              0.728 |        1.391 |               3.883 |        1.035 |          4.028 |                 -2.471 |            0.054 |
|        55 |       20 |          2 |          100 |             30 |                0.212 |          0.693 |                 1.401 |           10 |              0.728 |        1.391 |               3.883 |        1.035 |          4.028 |                 -2.471 |            0.054 |

#### H-G1 · trend_pullback
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=16, pct_val_positive=75.000, median_val_expectancy_R=0.113, median_train_expectancy_R=0.145, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        100 |          25 |        1.5 |        2 |             34 |                0.204 |          1.372 |                 1.679 |           26 |             -0.128 |       -0.57  |               0.772 |       -0.436 |         -1.928 |                 -5.891 |          inf     |
|        100 |          25 |        1.5 |        3 |             34 |                0.194 |          1.31  |                 1.644 |           26 |             -0.079 |       -0.328 |               0.854 |       -0.256 |         -1.239 |                 -5.899 |          inf     |
|         50 |          25 |        1.5 |        2 |             32 |                0.207 |          1.293 |                 1.634 |           18 |              0.121 |        0.467 |               1.247 |        0.35  |          1.152 |                 -3.363 |            0.313 |
|         50 |          25 |        1.5 |        3 |             32 |                0.207 |          1.278 |                 1.635 |           18 |              0.192 |        0.681 |               1.398 |        0.515 |          1.865 |                 -3.363 |            0.221 |
|        100 |          25 |        2   |        2 |             33 |                0.151 |          1.224 |                 1.62  |           21 |             -0.057 |       -0.282 |               0.855 |       -0.22  |         -0.711 |                 -3.749 |          inf     |

#### H-A2 · ma_momentum
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=3, pct_val_positive=100.000, median_val_expectancy_R=0.857, median_train_expectancy_R=1.840, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          4 |             30 |                1.38  |          1.331 |                 8.839 |           16 |              0.69  |        1.049 |               3.984 |        1.104 |          5.991 |                 -5.55  |            0.029 |
| 100 |          3 |             30 |                1.84  |          1.331 |                 8.64  |           17 |              0.857 |        1.037 |               3.831 |        1.105 |          7.869 |                 -7.168 |            0.031 |
| 100 |          2 |             30 |                2.761 |          1.331 |                 8.301 |           18 |              1.207 |        1.033 |               3.734 |        1.131 |         11.573 |                -10.041 |            0.034 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=20.566, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.958, max_drawdown_pct=-83.187, cagr_pct=53.147, cost_ratio=0.002
- **ma_momentum**: trades=27, win_rate_pct=25.926, expectancy_R=1.701, t_stat=1.736, profit_factor=9.077, payoff=26.805, sharpe=0.718, max_drawdown_pct=-16.639, cagr_pct=6.082, cost_ratio=0.015
- **rsi2_meanrev**: trades=48, win_rate_pct=62.500, expectancy_R=-0.025, t_stat=-0.356, profit_factor=0.858, payoff=0.518, sharpe=-0.120, max_drawdown_pct=-3.531, cagr_pct=-0.174, cost_ratio=inf
- **random**: n=200, expectancy_R_p50=0.249, expectancy_R_p95=0.531, total_return_p95=24.617, sharpe_p95=1.014

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
|       100 |       20 |          2 |          100 |            104 |                0.333 |          2.298 |                 1.778 |           34 |              0.015 |        0.079 |               1.021 |        0.059 |          0.174 |                 -6.097 |            0.906 |
|        55 |       20 |          3 |          200 |             92 |                0.476 |          2.293 |                 2.155 |           31 |              0.289 |        0.83  |               1.667 |        0.766 |          4.759 |                 -6.597 |            0.177 |

#### H-G1 · trend_pullback
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=0.000, median_val_expectancy_R=-0.126, median_train_expectancy_R=-0.015, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          30 |        1.5 |        3 |            284 |                0.021 |          0.365 |                 1.04  |           94 |             -0.212 |       -2.256 |               0.592 |       -1.61  |        -10.642 |                -19.993 |              inf |
|         50 |          25 |        2   |        3 |            203 |                0.016 |          0.289 |                 1.04  |           66 |             -0.097 |       -1.146 |               0.701 |       -0.828 |         -3.613 |                 -8.475 |              inf |
|         50 |          30 |        2   |        3 |            275 |                0.01  |          0.216 |                 1.022 |           88 |             -0.17  |       -2.186 |               0.568 |       -1.551 |         -8.079 |                -14.748 |              inf |
|         50 |          25 |        1.5 |        3 |            211 |                0.007 |          0.1   |                 1.004 |           67 |             -0.126 |       -1.234 |               0.698 |       -0.886 |         -4.832 |                -10.355 |              inf |
|        100 |          30 |        2   |        3 |            307 |                0.003 |          0.057 |                 0.998 |          101 |             -0.118 |       -1.531 |               0.698 |       -1.108 |         -6.566 |                -15.158 |              inf |

#### H-A2 · ma_momentum
train 2017-08-17 → 2023-01-22 | validation 2023-01-22 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=100.000, median_val_expectancy_R=0.130, median_train_expectancy_R=0.613, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 200 |          3 |            128 |                0.83  |          2.608 |                 4.241 |           66 |              0.116 |        0.434 |               1.265 |        0.366 |          3.513 |                -11.717 |            0.402 |
| 200 |          2 |            130 |                1.218 |          2.591 |                 4.079 |           68 |              0.182 |        0.468 |               1.271 |        0.399 |          5.257 |                -17.01  |            0.407 |
| 200 |          4 |            128 |                0.613 |          2.566 |                 4.097 |           65 |              0.09  |        0.442 |               1.284 |        0.371 |          2.833 |                 -9.137 |            0.384 |
| 150 |          3 |            171 |                0.546 |          2.423 |                 3.346 |           63 |              0.205 |        0.677 |               1.515 |        0.627 |          6.419 |                -10.119 |            0.269 |
| 150 |          2 |            175 |                0.799 |          2.421 |                 3.378 |           63 |              0.33  |        0.73  |               1.568 |        0.695 |         10.168 |                -14.296 |            0.257 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=9.190, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=0.808, max_drawdown_pct=-94.079, cagr_pct=37.900, cost_ratio=0.002
- **ma_momentum**: trades=192, win_rate_pct=18.229, expectancy_R=0.585, t_stat=2.558, profit_factor=2.608, payoff=13.689, sharpe=1.142, max_drawdown_pct=-14.500, cagr_pct=15.395, cost_ratio=0.097
- **rsi2_meanrev**: trades=342, win_rate_pct=63.743, expectancy_R=-0.060, t_stat=-2.093, profit_factor=0.731, payoff=0.418, sharpe=-0.804, max_drawdown_pct=-19.004, cagr_pct=-2.877, cost_ratio=inf
- **random**: n=200, expectancy_R_p50=0.075, expectancy_R_p95=0.294, total_return_p95=40.913, sharpe_p95=0.788

### 1d · 3,286 velas (2017-08-18 → 2026-08-31)

#### H-A1 · donchian_trend
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=2, pct_val_positive=100.000, median_val_expectancy_R=0.199, median_train_expectancy_R=0.657, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        20 |       20 |          2 |          100 |             32 |                0.657 |          2.216 |                 3.397 |           13 |              0.201 |        0.442 |               1.347 |        0.389 |          1.371 |                 -4.658 |            0.168 |
|        20 |       10 |          2 |          100 |             32 |                0.657 |          2.214 |                 3.396 |           13 |              0.196 |        0.432 |               1.337 |        0.381 |          1.342 |                 -4.664 |            0.171 |

#### H-G1 · trend_pullback
train 2017-08-18 → 2023-01-24 | validation 2023-01-25 → 2024-11-11

- Look-ahead: ok
- Meseta: configs=24, configs_valid=12, pct_val_positive=41.667, median_val_expectancy_R=-0.018, median_train_expectancy_R=0.184, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|        100 |          30 |        2   |        2 |             51 |                0.178 |          1.888 |                 1.778 |           19 |              0.049 |        0.275 |               1.15  |        0.194 |          0.487 |                 -1.966 |            0.412 |
|         50 |          30 |        1.5 |        2 |             52 |                0.229 |          1.879 |                 1.718 |           11 |             -0.147 |       -0.487 |               0.725 |       -0.325 |         -0.918 |                 -3.246 |          inf     |
|        100 |          30 |        2   |        3 |             51 |                0.179 |          1.873 |                 1.781 |           19 |              0.04  |        0.228 |               1.123 |        0.16  |          0.398 |                 -1.966 |            0.462 |
|         50 |          30 |        1.5 |        3 |             52 |                0.225 |          1.837 |                 1.705 |           11 |             -0.186 |       -0.648 |               0.656 |       -0.416 |         -1.149 |                 -3.65  |          inf     |
|        100 |          25 |        2   |        3 |             41 |                0.194 |          1.793 |                 1.834 |           17 |              0.008 |        0.041 |               1.015 |        0.031 |          0.047 |                 -2.158 |            0.865 |

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
- **rsi2_meanrev**: trades=54, win_rate_pct=68.519, expectancy_R=-0.018, t_stat=-0.293, profit_factor=0.890, payoff=0.410, sharpe=-0.097, max_drawdown_pct=-3.631, cagr_pct=-0.139, cost_ratio=inf
- **random**: n=200, expectancy_R_p50=0.130, expectancy_R_p95=0.464, total_return_p95=19.248, sharpe_p95=0.877

## SOLUSDT  (base 1h, hash `917bc6c2f8132fb2`)

### 4h · 13,257 velas (2020-08-11 → 2026-08-31)

#### H-A1 · donchian_trend
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=75.000, median_val_expectancy_R=0.042, median_train_expectancy_R=0.187, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n_entry |   n_exit |   atr_mult |   ema_filter |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----------:|---------:|-----------:|-------------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|       100 |       20 |          3 |          200 |             50 |                0.593 |          2.178 |                 2.548 |           17 |              0.012 |        0.054 |               1.021 |        0.048 |          0.113 |                 -3.339 |            0.839 |
|       100 |       20 |          3 |          100 |             52 |                0.546 |          2.068 |                 2.388 |           17 |              0.012 |        0.054 |               1.021 |        0.048 |          0.113 |                 -3.339 |            0.839 |
|       100 |       10 |          3 |          200 |             56 |                0.451 |          1.952 |                 2.204 |           17 |              0.074 |        0.347 |               1.2   |        0.244 |          0.994 |                 -2.928 |            0.373 |
|        55 |       20 |          3 |          100 |             69 |                0.396 |          1.842 |                 2.045 |           26 |             -0.018 |       -0.096 |               0.942 |       -0.065 |         -0.496 |                 -4.095 |            2.301 |
|       100 |       10 |          3 |          100 |             58 |                0.414 |          1.841 |                 2.077 |           17 |              0.074 |        0.347 |               1.2   |        0.244 |          0.994 |                 -2.928 |            0.373 |

#### H-G1 · trend_pullback
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=24, pct_val_positive=0.000, median_val_expectancy_R=-0.154, median_train_expectancy_R=0.039, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   ema_slow |   rsi_entry |   stop_atr |   tp_atr |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|-----------:|------------:|-----------:|---------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
|         50 |          20 |        2   |        3 |             91 |                0.098 |          1.288 |                 1.355 |           33 |             -0.172 |       -1.244 |               0.61  |       -1.14  |         -4.661 |                 -6.826 |              inf |
|         50 |          20 |        1.5 |        3 |             92 |                0.12  |          1.246 |                 1.318 |           33 |             -0.164 |       -1.01  |               0.68  |       -0.891 |         -4.481 |                 -8.25  |              inf |
|         50 |          20 |        2   |        2 |             91 |                0.09  |          1.228 |                 1.329 |           33 |             -0.166 |       -1.195 |               0.622 |       -1.101 |         -4.508 |                 -6.826 |              inf |
|         50 |          20 |        1.5 |        2 |             92 |                0.11  |          1.183 |                 1.293 |           33 |             -0.156 |       -0.956 |               0.694 |       -0.848 |         -4.28  |                 -8.252 |              inf |
|        100 |          20 |        1.5 |        3 |            138 |                0.081 |          1.027 |                 1.19  |           44 |             -0.27  |       -2.007 |               0.516 |       -1.691 |         -9.471 |                -12.127 |              inf |

#### H-A2 · ma_momentum
train 2020-08-11 → 2024-03-31 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=9, configs_valid=9, pct_val_positive=66.667, median_val_expectancy_R=0.052, median_train_expectancy_R=1.006, n_val_t_ge_2=0

Top 5 por t-stat en train:

|   n |   atr_mult |   train_trades |   train_expectancy_R |   train_t_stat |   train_profit_factor |   val_trades |   val_expectancy_R |   val_t_stat |   val_profit_factor |   val_sharpe |   val_cagr_pct |   val_max_drawdown_pct |   val_cost_ratio |
|----:|-----------:|---------------:|---------------------:|---------------:|----------------------:|-------------:|-------------------:|-------------:|--------------------:|-------------:|---------------:|-----------------------:|-----------------:|
| 100 |          2 |            159 |                1.04  |          2.019 |                 3.938 |           71 |             -0.07  |       -0.479 |               0.818 |       -0.307 |         -4.408 |                -11.462 |          inf     |
| 100 |          4 |            158 |                0.522 |          2.012 |                 3.907 |           69 |             -0.039 |       -0.508 |               0.816 |       -0.338 |         -2.281 |                 -5.967 |          inf     |
| 100 |          3 |            158 |                0.694 |          2.006 |                 3.869 |           69 |             -0.048 |       -0.474 |               0.824 |       -0.31  |         -2.864 |                 -7.847 |          inf     |
| 150 |          4 |            144 |                0.755 |          1.701 |                 4.517 |           48 |              0.027 |        0.212 |               1.107 |        0.171 |          0.922 |                 -5.409 |            0.543 |
| 150 |          3 |            144 |                1.006 |          1.7   |                 4.375 |           48 |              0.052 |        0.313 |               1.167 |        0.25  |          1.814 |                 -6.806 |            0.446 |

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=49.136, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=1.266, max_drawdown_pct=-96.599, cagr_pct=124.322, cost_ratio=0.001
- **ma_momentum**: trades=163, win_rate_pct=15.337, expectancy_R=0.978, t_stat=1.700, profit_factor=3.632, payoff=25.156, sharpe=1.375, max_drawdown_pct=-27.495, cagr_pct=29.990, cost_ratio=0.045
- **rsi2_meanrev**: trades=209, win_rate_pct=63.636, expectancy_R=-0.003, t_stat=-0.102, profit_factor=0.977, payoff=0.561, sharpe=-0.037, max_drawdown_pct=-7.290, cagr_pct=-0.153, cost_ratio=1.137
- **random**: n=200, expectancy_R_p50=0.067, expectancy_R_p95=0.386, total_return_p95=24.712, sharpe_p95=0.846

### 1d · 2,208 velas (2020-08-12 → 2026-08-31)

#### H-A1 · donchian_trend
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=0, pct_val_positive=nan, median_val_expectancy_R=nan, median_train_expectancy_R=nan, n_val_t_ge_2=0

Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.

#### H-G1 · trend_pullback
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=24, configs_valid=0, pct_val_positive=nan, median_val_expectancy_R=nan, median_train_expectancy_R=nan, n_val_t_ge_2=0

Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.

#### H-A2 · ma_momentum
train 2020-08-12 → 2024-03-30 | validation 2024-03-31 → 2025-06-15

- Look-ahead: ok
- Meseta: configs=9, configs_valid=0, pct_val_positive=nan, median_val_expectancy_R=nan, median_train_expectancy_R=nan, n_val_t_ge_2=0

Ninguna configuración con ≥30 operaciones en train y ≥10 en validation.

#### Benchmarks (train+validation)

- **buy_and_hold**: trades=1, win_rate_pct=100.000, expectancy_R=39.712, t_stat=nan, profit_factor=inf, payoff=nan, sharpe=1.231, max_drawdown_pct=-96.270, cagr_pct=115.092, cost_ratio=0.001
- **ma_momentum**: trades=19, win_rate_pct=21.053, expectancy_R=2.922, t_stat=1.283, profit_factor=10.369, payoff=48.646, sharpe=0.790, max_drawdown_pct=-17.945, cagr_pct=10.344, cost_ratio=0.008
- **rsi2_meanrev**: trades=35, win_rate_pct=68.571, expectancy_R=0.016, t_stat=0.255, profit_factor=1.127, payoff=0.519, sharpe=0.104, max_drawdown_pct=-2.406, cagr_pct=0.115, cost_ratio=0.420
- **random**: n=200, expectancy_R_p50=0.160, expectancy_R_p95=0.566, total_return_p95=17.401, sharpe_p95=1.245
