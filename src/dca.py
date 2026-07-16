"""DCA (Dollar Cost Averaging / compra periódica).

En vez de intentar adivinar el mercado, compras una cantidad FIJA cada cierto
tiempo (p. ej. 20 USDT cada semana), pase lo que pase con el precio. Así:
  - Cuando el precio está bajo, tu cantidad fija compra más unidades.
  - Cuando está alto, compra menos.
  - Tu precio medio de compra se suaviza y no dependes de "acertar el momento".

Es lo que históricamente funciona para alguien con poca inversión y sin
complicarse. NO promete ganancias diarias ni es mágico: si el activo cae a
largo plazo, pierdes. Pero elimina el mayor error del principiante: intentar
predecir y operar de más.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# Nombre visible -> código de periodo de pandas.
FRECUENCIAS = {"Diaria": "D", "Semanal": "W", "Mensual": "M"}


@dataclass
class ResultadoDCA:
    invertido: float          # total aportado (suma de todas las compras)
    valor_final: float        # valor actual de lo acumulado
    unidades: float           # cantidad del activo acumulada (ej: BTC)
    num_compras: int
    precio_medio: float       # coste medio por unidad (incluye comisiones)
    valor_lump: float         # cuánto valdría invirtiendo TODO de golpe al inicio
    curva_valor: pd.Series
    curva_invertido: pd.Series

    @property
    def rendimiento_pct(self) -> float:
        return (self.valor_final / self.invertido - 1) * 100 if self.invertido > 0 else 0.0

    @property
    def ganancia(self) -> float:
        return self.valor_final - self.invertido


def backtest_dca(
    df: pd.DataFrame,
    monto_por_compra: float,
    frecuencia: str = "Semanal",
    comision_pct: float = 0.1,
) -> ResultadoDCA:
    """Simula comprar `monto_por_compra` USDT del activo cada periodo.

    Compra en la PRIMERA vela de cada periodo (día/semana/mes). Devuelve el
    resultado con curvas de valor e inversión acumulada para graficar.
    """
    if df.empty:
        raise ValueError("No hay datos para simular.")

    freq = FRECUENCIAS.get(frecuencia, "W")
    # Periodos sobre índice sin zona horaria (evita avisos de pandas).
    periodos = df.index.tz_localize(None).to_period(freq)
    es_primera = ~periodos.duplicated()

    comision = comision_pct / 100.0
    invertido = 0.0
    unidades = 0.0
    compras = 0
    valores: list[float] = []
    invertidos: list[float] = []

    precios = df["close"].to_numpy()
    for i in range(len(df)):
        if es_primera[i]:
            neto = monto_por_compra * (1 - comision)  # la comisión se paga al comprar
            unidades += neto / precios[i]
            invertido += monto_por_compra
            compras += 1
        valores.append(unidades * precios[i])
        invertidos.append(invertido)

    valor_final = unidades * precios[-1]
    precio_medio = invertido / unidades if unidades > 0 else 0.0

    # Comparación: invertir TODO de golpe al principio (lump sum).
    unidades_lump = invertido * (1 - comision) / precios[0] if precios[0] > 0 else 0.0
    valor_lump = unidades_lump * precios[-1]

    return ResultadoDCA(
        invertido=invertido,
        valor_final=valor_final,
        unidades=unidades,
        num_compras=compras,
        precio_medio=precio_medio,
        valor_lump=valor_lump,
        curva_valor=pd.Series(valores, index=df.index, dtype=float),
        curva_invertido=pd.Series(invertidos, index=df.index, dtype=float),
    )
