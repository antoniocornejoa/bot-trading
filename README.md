# 🤖 Bot de Trading de Cripto (Binance)

Bot de trading automático para Binance (mercado **spot**, solo compra-venta,
**sin apalancamiento**) basado en **señales técnicas** (cruce de medias móviles
filtrado por RSI, con stop-loss y take-profit según volatilidad).

Está diseñado para alguien que **no sabe programar**: solo tocas un archivo de
configuración (`config.yaml`) y ejecutas dos comandos.

---

## ⚠️ Lee esto antes de nada (importante, no es relleno)

- **Ningún bot garantiza ganancias diarias.** El que te lo prometa, miente.
  Toda estrategia tiene rachas de pérdidas. El objetivo de este proyecto es que
  operes con **método y control de riesgo**, no que te hagas rico.
- **Empieza SIEMPRE por el backtest y el modo paper.** El bot arranca en modo
  seguro a propósito. Operar con dinero real requiere activarlo tú, con
  intención, en dos sitios distintos.
- **Nunca inviertas dinero que no puedas permitirte perder.** Con cripto puedes
  perder el 100%.
- Este software se ofrece "tal cual", con fines educativos. Tú eres responsable
  de tus decisiones y de tu dinero.

---

## 🧭 Los 3 modos del bot

El bot tiene un "interruptor" en `config.yaml` (campo `mode`):

| Modo       | Qué hace                                   | Riesgo      |
|------------|--------------------------------------------|-------------|
| `backtest` | Prueba la estrategia con datos históricos  | **Ninguno** |
| `paper`    | Opera en tiempo real con dinero de mentira | **Ninguno** |
| `live`     | Opera con **dinero real**                  | **Real**    |

**El camino correcto es siempre: `backtest` → `paper` (semanas) → `live`.**

---

## 📦 Instalación (una sola vez)

Necesitas tener **Python 3.10 o superior** instalado.

1. Descarga este proyecto en tu ordenador.
2. Abre una terminal dentro de la carpeta del proyecto.
3. (Recomendado) Crea un entorno aislado e instala las dependencias:

   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Mac/Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

---

## 🖥️ La forma más fácil de verlo: el panel visual

Si no quieres tocar archivos, usa el **panel web interactivo**. Ajustas todo con
deslizadores y botones, y ves los gráficos al momento en tu navegador:

```bash
streamlit run dashboard.py
```

Se abre solo en el navegador. A la izquierda eliges par, timeframe, medias y
riesgo; pulsas **Ejecutar backtest** y ves la curva de capital, el precio con
las compras/ventas marcadas y las estadísticas. (El panel es solo para
backtesting, sin riesgo.)

> ¿Prefieres la terminal? Sigue con el Paso 1. Ambos caminos hacen lo mismo.

**¿Solo tienes el móvil?** Puedes desplegar este panel gratis en internet y
abrirlo desde el teléfono. Guía: **[DESPLIEGUE_MOVIL.md](DESPLIEGUE_MOVIL.md)**.

---

## 🧪 Paso 1: Backtest (sin riesgo, sin claves)

Prueba si la estrategia habría funcionado con datos históricos. **No necesita
claves de API.**

En `config.yaml` asegúrate de que:
```yaml
mode: backtest
symbol: BTC/USDT
timeframe: 1h
```

Ejecuta:
```bash
python run_backtest.py
```

Además del informe en pantalla, se genera un **informe visual en HTML**
(`results/informe.html`) que puedes abrir con doble clic en el navegador.

Verás un informe con:
- **Rendimiento (%)**: cuánto habrías ganado o perdido.
- **Tasa de acierto**: % de operaciones ganadoras.
- **Profit factor**: ganancias ÷ pérdidas. **Debe ser > 1** para ser rentable.
  Por debajo de 1, la estrategia pierde dinero: NO la lleves a real.
- **Peor bajón (drawdown)**: la mayor caída que habrías sufrido. Si es alta,
  prepárate psicológicamente para verla en real.

👉 Cambia parámetros en `config.yaml` (par, timeframe, medias, riesgo) y vuelve
a ejecutar hasta entender cómo se comporta. **No te obsesiones con encontrar el
"mejor" resultado histórico**: eso se llama *overfitting* y suele fallar en real.

---

## 📝 Paso 2: Paper trading (tiempo real, dinero de mentira)

Aquí el bot opera de verdad en tiempo real, pero contra la **testnet de
Binance**, con dinero ficticio. Es la prueba definitiva antes de arriesgar nada.

1. Crea claves de testnet gratis en 👉 https://testnet.binance.vision/
   (inicia sesión con GitHub, genera una API key HMAC).
2. Copia el archivo `.env.example` a `.env` y pega ahí tus claves de testnet:
   ```
   BINANCE_TESTNET_API_KEY=tu_clave
   BINANCE_TESTNET_API_SECRET=tu_secreto
   ```
3. En `config.yaml` pon:
   ```yaml
   mode: paper
   ```
4. Ejecuta:
   ```bash
   python run_bot.py
   ```

El bot revisará el mercado cada minuto, comprará y venderá según la estrategia,
y lo verás todo por pantalla. Déjalo correr **días o semanas**. Si aquí pierde
dinero, en real también lo perdería.

Detén el bot cuando quieras con **Ctrl + C**.

---

## 💸 Paso 3: Dinero real (solo si los pasos 1 y 2 fueron bien)

⚠️ **Solo llega aquí si el backtest fue rentable Y el paper trading aguantó
semanas sin arruinarse.** Si dudas, no lo hagas.

1. En Binance real (perfil → *API Management*) crea una API key con:
   - ✅ Permiso de **Spot Trading** activado.
   - ❌ Permiso de **retiros (Withdrawals) DESACTIVADO**. (Así, aunque te roben
     la clave, no pueden sacar tus fondos.)
2. Pon esas claves en `.env`:
   ```
   BINANCE_API_KEY=tu_clave_real
   BINANCE_API_SECRET=tu_secreto_real
   ```
3. En `config.yaml`, cambia **DOS** cosas a propósito:
   ```yaml
   mode: live
   i_understand_live_risk: true
   ```
4. Ejecuta:
   ```bash
   python run_bot.py
   ```
   El bot te pedirá escribir una frase de confirmación antes de operar.

**Empieza con MUY poco dinero** (lo mínimo que Binance permita, ~10-15 USDT por
operación) hasta que confíes plenamente en el comportamiento real.

---

## ⚙️ Ajustes principales (`config.yaml`)

| Ajuste | Qué controla | Consejo |
|---|---|---|
| `symbol` | Par a operar | Empieza con `BTC/USDT` (mucha liquidez) |
| `timeframe` | Tamaño de vela | `1h` o `4h` = menos ruido y menos comisiones |
| `riesgo_por_operacion_pct` | % arriesgado por trade | 1% es conservador. Nunca subas de ~2% |
| `stop_loss_atr_mult` | Distancia del stop-loss | Más alto = menos stops, pero pérdidas mayores |
| `limite_perdida_diaria_pct` | Freno diario | Si pierdes este % en un día, el bot para |

---

## 🛡️ Cómo te protege el bot

1. **Tamaño de posición por riesgo fijo**: cada operación arriesga como mucho el
   % que definas de tu capital. Un mal trade no te hace un roto grande.
2. **Stop-loss automático**: cada compra lleva un precio de salida por pérdida.
3. **Límite de pérdida diaria**: si un día va mal, deja de operar hasta el
   siguiente. Evita el "efecto bola de nieve".
4. **Solo compras (spot)**: como mucho pierdes lo invertido, nunca más
   (no hay apalancamiento ni deudas).
5. **Doble seguro para dinero real**: `mode: live` **y**
   `i_understand_live_risk: true` **y** una confirmación escrita. Imposible
   activarlo por accidente.

---

## 🧱 Estructura del proyecto (para curiosos)

```
config.yaml          <- LO ÚNICO que necesitas tocar
.env                 <- tus claves (créalo desde .env.example)
dashboard.py         <- panel web visual (streamlit run dashboard.py)
run_backtest.py      <- ejecuta la prueba histórica (+ informe HTML)
run_bot.py           <- ejecuta el bot en vivo (paper/live)
src/
  report.py          <- genera el informe visual en HTML
  config.py          <- carga y valida la configuración
  data.py            <- descarga precios de Binance
  indicators.py      <- EMA, RSI, ATR
  strategy.py        <- reglas de compra/venta
  risk.py            <- gestión de riesgo (lo más importante)
  backtest.py        <- motor de simulación con comisiones
  broker.py          <- ejecuta órdenes reales/testnet
  bot.py             <- bucle en tiempo real
tests/               <- pruebas automáticas
```

---

## ❓ Preguntas frecuentes

**¿Puedo tener ganancias diarias garantizadas?**
No. Nadie puede. Habrá días y semanas de pérdidas incluso si a largo plazo
funciona. Cualquiera que prometa lo contrario intenta estafarte.

**¿Cuánto dinero necesito?**
Con poco capital, las comisiones pesan mucho. Con menos de ~100-200 USDT es
difícil que salga a cuenta. Da igual: **primero backtest y paper, que son
gratis.**

**¿Y si Binance no funciona en mi país?**
El código usa `ccxt`, que soporta muchos exchanges. Se puede adaptar a Kraken u
otro cambiando poco código. Pídemelo si lo necesitas.

**¿Puedo dejarlo corriendo 24/7?**
Sí, cripto opera 24/7. Para producción conviene un pequeño servidor (VPS) y
guardar el estado de las posiciones de forma persistente. Podemos añadirlo.
