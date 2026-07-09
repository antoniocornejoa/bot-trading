"""Genera un informe VISUAL en HTML del backtest (se abre en el navegador).

No usa librerías externas ni internet: los gráficos son SVG dibujados a mano,
así el archivo es autónomo y se abre con doble clic en cualquier ordenador.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def _muestrear(valores: list[float], maximo: int = 600) -> list[float]:
    """Reduce el número de puntos para que el SVG no sea gigante."""
    n = len(valores)
    if n <= maximo:
        return valores
    paso = n / maximo
    return [valores[int(i * paso)] for i in range(maximo)]


def _puntos(valores: list[float], ancho: float, alto: float, pad: float):
    """Convierte una lista de valores en coordenadas (x, y) para el SVG."""
    vmin, vmax = min(valores), max(valores)
    rango = (vmax - vmin) or 1.0
    n = len(valores)
    coords = []
    for i, v in enumerate(valores):
        x = pad + (ancho - 2 * pad) * (i / (n - 1 or 1))
        y = pad + (alto - 2 * pad) * (1 - (v - vmin) / rango)
        coords.append((x, y))
    return coords, vmin, vmax


def _svg_area(valores: list[float], ancho=760, alto=240, pad=12) -> str:
    """Gráfico de línea con relleno (curva de capital)."""
    vals = _muestrear(valores)
    if len(vals) < 2:
        return "<p class='vacio'>Sin datos suficientes para el gráfico.</p>"
    coords, _, _ = _puntos(vals, ancho, alto, pad)
    linea = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    base = alto - pad
    area = f"M{coords[0][0]:.1f},{base:.1f} " + \
           " ".join(f"L{x:.1f},{y:.1f}" for x, y in coords) + \
           f" L{coords[-1][0]:.1f},{base:.1f} Z"
    ex, ey = coords[-1]
    return f"""<svg viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none" class="chart" role="img" aria-label="Curva de capital">
  <path d="{area}" fill="url(#grad)" />
  <polyline points="{linea}" fill="none" stroke="var(--accent)" stroke-width="2" vector-effect="non-scaling-stroke" />
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" fill="var(--accent)" />
</svg>"""


def _svg_precio(precios: list[float], marcadores: list[dict],
                ancho=760, alto=240, pad=12) -> str:
    """Gráfico de precio con marcas de compra (verde) y venta (roja)."""
    vals = _muestrear(precios)
    if len(vals) < 2:
        return "<p class='vacio'>Sin datos suficientes para el gráfico.</p>"
    coords, vmin, vmax = _puntos(vals, ancho, alto, pad)
    linea = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    rango = (vmax - vmin) or 1.0

    puntos_svg = []
    for m in marcadores:
        x = pad + (ancho - 2 * pad) * m["frac"]
        y = pad + (alto - 2 * pad) * (1 - (m["precio"] - vmin) / rango)
        color = "var(--pos)" if m["tipo"] == "compra" else "var(--neg)"
        puntos_svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}" '
            f'stroke="var(--surface)" stroke-width="1" />'
        )

    return f"""<svg viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none" class="chart" role="img" aria-label="Precio con operaciones">
  <polyline points="{linea}" fill="none" stroke="var(--muted)" stroke-width="1.5" vector-effect="non-scaling-stroke" />
  {''.join(puntos_svg)}
</svg>"""


def _clase_signo(v: float) -> str:
    return "pos" if v >= 0 else "neg"


def generar_informe_html(df: pd.DataFrame, res, cfg, ruta_salida: str | Path) -> Path:
    """Crea el archivo HTML del informe y devuelve su ruta."""
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    symbol = getattr(cfg, "symbol", "—")
    timeframe = getattr(cfg, "timeframe", "—")
    equity_vals = list(res.curva_equity.values) if res.curva_equity is not None else []

    # Marcadores de operaciones sobre el eje de tiempo del precio.
    t0, t1 = df.index[0], df.index[-1]
    span = (t1 - t0).total_seconds() or 1.0
    marcadores = []
    for op in res.operaciones:
        marcadores.append({"tipo": "compra", "precio": op.entrada_precio,
                           "frac": max(0.0, min(1.0, (op.entrada_fecha - t0).total_seconds() / span))})
        marcadores.append({"tipo": "venta", "precio": op.salida_precio,
                           "frac": max(0.0, min(1.0, (op.salida_fecha - t0).total_seconds() / span))})

    rend = res.rendimiento_pct
    pf = res.profit_factor
    pf_txt = "∞" if pf == float("inf") else f"{pf:.2f}"

    filas = []
    for op in reversed(res.operaciones[-15:]):
        cls = _clase_signo(op.pnl)
        signo = "+" if op.pnl >= 0 else ""
        filas.append(
            f"<tr><td>{op.entrada_fecha.strftime('%Y-%m-%d %H:%M')}</td>"
            f"<td class='num'>{op.entrada_precio:,.2f}</td>"
            f"<td class='num'>{op.salida_precio:,.2f}</td>"
            f"<td class='num {cls}'>{signo}{op.pnl:,.2f}</td>"
            f"<td><span class='chip {op.motivo_salida}'>{op.motivo_salida}</span></td></tr>"
        )
    filas_html = "\n".join(filas) if filas else \
        "<tr><td colspan='5' class='vacio'>Sin operaciones en este periodo.</td></tr>"

    precios = list(df["close"].values)

    html = _PLANTILLA.format(
        symbol=symbol,
        timeframe=timeframe,
        periodo=f"{df.index[0].date()} → {df.index[-1].date()}",
        modo=getattr(cfg, "mode", "backtest"),
        rend=f"{'+' if rend >= 0 else ''}{rend:.2f}%",
        rend_cls=_clase_signo(rend),
        cap_ini=f"{res.equity_inicial:,.0f}",
        cap_fin=f"{res.equity_final:,.2f}",
        ops=res.num_operaciones,
        acierto=f"{res.tasa_acierto_pct:.1f}%",
        pf=pf_txt,
        dd=f"-{res.max_drawdown_pct:.2f}%",
        svg_equity=_svg_area(equity_vals),
        svg_precio=_svg_precio(precios, marcadores),
        filas=filas_html,
    )
    ruta.write_text(html, encoding="utf-8")
    return ruta


_PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Informe de backtest · {symbol}</title>
<style>
  :root {{
    --bg:#f6f7f7; --surface:#ffffff; --border:#e5e8ea; --text:#141a1f;
    --muted:#647079; --accent:#0d9488; --accent-soft:rgba(13,148,136,.14);
    --pos:#15a34a; --neg:#dc2626;
    --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  }}
  @media (prefers-color-scheme:dark) {{
    :root {{ --bg:#0e1216; --surface:#151b21; --border:#232c34; --text:#e8edf0;
      --muted:#8a97a1; --accent:#2dd4bf; --accent-soft:rgba(45,212,191,.12);
      --pos:#34d399; --neg:#f87171; }}
  }}
  :root[data-theme="dark"] {{ --bg:#0e1216; --surface:#151b21; --border:#232c34;
    --text:#e8edf0; --muted:#8a97a1; --accent:#2dd4bf; --accent-soft:rgba(45,212,191,.12);
    --pos:#34d399; --neg:#f87171; }}
  :root[data-theme="light"] {{ --bg:#f6f7f7; --surface:#ffffff; --border:#e5e8ea;
    --text:#141a1f; --muted:#647079; --accent:#0d9488; --accent-soft:rgba(13,148,136,.14);
    --pos:#15a34a; --neg:#dc2626; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font-family:var(--sans);
    line-height:1.5; -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:860px; margin:0 auto; padding:32px 20px 64px; }}
  header {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:8px 14px; margin-bottom:6px; }}
  h1 {{ font-size:1.5rem; font-weight:650; letter-spacing:-.01em; margin:0; }}
  .badge {{ font-family:var(--mono); font-size:.72rem; text-transform:uppercase;
    letter-spacing:.08em; color:var(--accent); background:var(--accent-soft);
    padding:3px 8px; border-radius:6px; }}
  .sub {{ color:var(--muted); font-size:.9rem; margin:0 0 26px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:12px; margin-bottom:30px; }}
  .card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
    padding:16px 18px; }}
  .card .label {{ font-size:.74rem; text-transform:uppercase; letter-spacing:.06em;
    color:var(--muted); margin-bottom:6px; }}
  .card .value {{ font-family:var(--mono); font-size:1.5rem; font-weight:600;
    font-variant-numeric:tabular-nums; letter-spacing:-.02em; }}
  .pos {{ color:var(--pos); }} .neg {{ color:var(--neg); }}
  section {{ background:var(--surface); border:1px solid var(--border); border-radius:14px;
    padding:20px; margin-bottom:20px; }}
  section h2 {{ font-size:.82rem; text-transform:uppercase; letter-spacing:.07em;
    color:var(--muted); margin:0 0 4px; font-weight:600; }}
  section .hint {{ color:var(--muted); font-size:.82rem; margin:0 0 14px; }}
  .chart {{ width:100%; height:230px; display:block; }}
  .legend {{ display:flex; gap:16px; font-size:.8rem; color:var(--muted); margin-top:8px; }}
  .dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px;
    vertical-align:middle; }}
  .tablewrap {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:.86rem; }}
  th, td {{ text-align:left; padding:9px 10px; border-bottom:1px solid var(--border); white-space:nowrap; }}
  th {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:600; }}
  td.num {{ font-family:var(--mono); text-align:right; font-variant-numeric:tabular-nums; }}
  .chip {{ font-size:.72rem; padding:2px 8px; border-radius:20px; background:var(--accent-soft);
    color:var(--accent); text-transform:capitalize; }}
  .chip.stop {{ background:rgba(220,38,38,.14); color:var(--neg); }}
  .chip.objetivo {{ background:rgba(21,163,74,.15); color:var(--pos); }}
  .vacio {{ color:var(--muted); text-align:center; font-size:.86rem; }}
  .aviso {{ font-size:.8rem; color:var(--muted); border-top:1px solid var(--border);
    padding-top:16px; margin-top:26px; }}
  .aviso strong {{ color:var(--text); }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Informe de backtest</h1>
    <span class="badge">{modo}</span>
  </header>
  <p class="sub">{symbol} · vela {timeframe} · {periodo}</p>

  <div class="grid">
    <div class="card"><div class="label">Rendimiento</div><div class="value {rend_cls}">{rend}</div></div>
    <div class="card"><div class="label">Capital final</div><div class="value">{cap_fin}</div></div>
    <div class="card"><div class="label">Operaciones</div><div class="value">{ops}</div></div>
    <div class="card"><div class="label">Aciertos</div><div class="value">{acierto}</div></div>
    <div class="card"><div class="label">Profit factor</div><div class="value">{pf}</div></div>
    <div class="card"><div class="label">Peor bajón</div><div class="value neg">{dd}</div></div>
  </div>

  <section>
    <h2>Evolución del capital</h2>
    <p class="hint">Cómo habrían crecido o caído tus {cap_ini} USDT iniciales.</p>
    {svg_equity}
  </section>

  <section>
    <h2>Precio y operaciones</h2>
    <p class="hint">Cada punto es una operación del bot sobre el precio del activo.</p>
    {svg_precio}
    <div class="legend">
      <span><span class="dot" style="background:var(--pos)"></span>Compra</span>
      <span><span class="dot" style="background:var(--neg)"></span>Venta</span>
    </div>
  </section>

  <section>
    <h2>Últimas operaciones</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Fecha entrada</th><th class="num">Compra</th><th class="num">Venta</th><th class="num">Resultado</th><th>Motivo</th></tr></thead>
        <tbody>
        {filas}
        </tbody>
      </table>
    </div>
  </section>

  <p class="aviso"><strong>Recuerda:</strong> esto es una simulación sobre datos pasados.
  El rendimiento histórico NO garantiza resultados futuros. Antes de usar dinero real,
  prueba en modo <em>paper</em> durante semanas. Ningún bot gana todos los días.</p>
</div>
</body>
</html>"""
