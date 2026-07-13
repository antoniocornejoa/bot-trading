# 🪟 Guía para Windows desde cero (sin saber programar)

Objetivo: pasar de "no tengo nada" a **ver el panel visual funcionando** en tu
PC. Sigue los pasos en orden. Copia y pega los comandos tal cual.

---

## Paso 1 · Instalar Python (una sola vez)

1. Entra en 👉 **https://www.python.org/downloads/** y pulsa el botón amarillo
   **"Download Python"**.
2. Abre el archivo descargado.
3. **MUY IMPORTANTE:** en la primera pantalla, marca abajo la casilla
   **"Add python.exe to PATH"** ✅ antes de continuar.
4. Pulsa **"Install Now"** y espera a que termine. Cierra la ventana.

---

## Paso 2 · Descargar el proyecto

1. Abre en el navegador tu repositorio en GitHub:
   `https://github.com/antoniocornejoa/bot-trading`
2. Arriba a la izquierda, donde pone el nombre de la rama, cambia a
   **`claude/trading-bot-feasibility-x23npm`**.
3. Pulsa el botón verde **"Code"** → **"Download ZIP"**.
4. Ve a tu carpeta de Descargas, haz clic derecho en el ZIP →
   **"Extraer todo"**. Se creará una carpeta `bot-trading-...`.

---

## Paso 3 · Abrir la terminal en esa carpeta

1. Entra en la carpeta que acabas de extraer (donde está `dashboard.py`).
2. Haz clic en la **barra de direcciones** del explorador (arriba, donde se ve
   la ruta), escribe **`powershell`** y pulsa **Enter**.
3. Se abre una ventana azul/negra (PowerShell) ya situada en esa carpeta.

---

## Paso 4 · Instalar las dependencias (una sola vez)

Copia esta línea, pégala en PowerShell (clic derecho pega) y pulsa Enter:

```powershell
pip install -r requirements.txt
```

Tardará un par de minutos en descargar todo. Es normal ver mucho texto.

---

## Paso 5 · ¡Abrir el panel visual! 🎉

Copia y pega:

```powershell
python -m streamlit run dashboard.py
```

Se abrirá **solo** una pestaña en tu navegador con el panel. Si no se abre,
copia la dirección `http://localhost:8501` en el navegador.

En el panel:
1. A la izquierda, en **"Fuente de datos"**, elige **Kraken** (datos reales que
   funcionan bien) o **Binance** si va en tu red.
2. Ajusta par, timeframe y riesgo a tu gusto.
3. Pulsa **"▶️ Ejecutar backtest"** y mira los gráficos.

Para **cerrar** el panel: vuelve a PowerShell y pulsa `Ctrl + C`.
Para **volver a abrirlo** otro día: repite solo los pasos 3 y 5.

---

## Si algo falla

| Problema | Solución |
|---|---|
| `pip no se reconoce` | No marcaste "Add to PATH". Reinstala Python (Paso 1) marcando la casilla. |
| `python no se reconoce` | Igual que arriba: reinstala marcando "Add python.exe to PATH". |
| El backtest da error de datos | Cambia la "Fuente de datos" a **Kraken** o a **Datos de ejemplo (demo)**. |
| Se abre pero no veo gráficos | Pulsa el botón **"Ejecutar backtest"** en la barra lateral. |

---

## Siguiente paso (cuando ya lo domines)

Cuando el backtesting te convenza y quieras operar en tiempo real **con dinero
de mentira** (paper), sigue el `README.md` → *Paso 2: Paper trading*. Ahí
crearás claves gratis de la testnet de Binance. **No pases a dinero real hasta
haber probado semanas en paper.**
