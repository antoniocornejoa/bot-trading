# Veredicto del tramo de TEST · H-A2 (ma_momentum, 4h) · BTC + ETH

Tramo de test: desde 2024-11-11 (20 % final del histórico, nunca usado antes). Regla de decisión escrita antes de abrir el test (ver `trading_bot/research/hypotheses.yaml`).

Operaciones del walk-forward cuya entrada cae en el tramo de test, solo BTC y ETH (SOL excluido por no pasar el walk-forward). Riesgo 0,5 % por operación para el drawdown y el retorno.

|             |   ops |   BTC |   ETH |   win_rate_% |   expectancy_R |        t |   t_mensual |   meses |      PF |   DD_%_riesgo0.5 |   retorno_%_riesgo0.5 |   coste/bruto | desde      | hasta      |
|:------------|------:|------:|------:|-------------:|---------------:|---------:|------------:|--------:|--------:|-----------------:|----------------------:|--------------:|:-----------|:-----------|
| base        |   127 |    59 |    68 |      12.5984 |       0.224459 | 0.852869 |    0.691437 |      19 | 1.4025  |         -12.8042 |              13.7921  |      0.349425 | 2024-12-21 | 2026-08-24 |
| pessimistic |   116 |    59 |    57 |      12.931  |       0.179574 | 0.729202 |    0.565232 |      17 | 1.34501 |         -11.4333 |               9.90541 |      0.48892  | 2024-12-21 | 2026-08-24 |

## Regla de decisión

- expectancy>0 base y pesimista: **cumple**
- PF>=1.3 (base): **cumple**
- DD<=20% a 0.5% (base): **cumple**

**Resultado: H-A2 pasa el test.**

Aviso: el tramo de test tiene menos de dos años y unas 130 operaciones; el t-stat en test por sí solo no alcanza significación. Lo que se afirma es que la ventaja medida en walk-forward no desapareció fuera de muestra, no que esté demostrada más allá de toda duda. La siguiente evidencia independiente es el paper trading (Fase 12).