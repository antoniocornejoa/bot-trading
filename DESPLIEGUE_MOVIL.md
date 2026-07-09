# 📱 Ver el panel desde el móvil (gratis)

Esta guía despliega el **panel de backtesting** en internet, gratis, para que lo
abras desde el teléfono como una web normal. No necesitas ordenador para usarlo
después (sí para el paso de despliegue, que se hace una sola vez).

> ⚠️ Esto NO opera con dinero real. Es solo el panel visual para probar
> estrategias (backtesting). Operar de verdad 24/7 necesita un servidor de pago
> (~3-5 €/mes); ver la sección final.

---

## Qué vas a usar: Streamlit Community Cloud

- Es **gratis** para apps públicas.
- Despliega directamente desde tu repositorio de GitHub.
- La app "se duerme" si nadie la usa y **despierta sola** al abrir el enlace.

---

## Pasos (una sola vez, desde un ordenador)

1. **Ten el código en GitHub.** Ya está: repositorio `bot-trading`, rama
   `claude/trading-bot-feasibility-x23npm`. (Para que sea gratis, el repo debe
   ser **público**, o usar la opción de repos privados de Streamlit.)

2. Entra en 👉 **https://share.streamlit.io** y pulsa *Sign in with GitHub*.

3. Pulsa **"Create app"** → **"Deploy a public app from GitHub"** y rellena:
   - **Repository:** `antoniocornejoa/bot-trading`
   - **Branch:** `claude/trading-bot-feasibility-x23npm` (o `main` si lo fusionas)
   - **Main file path:** `dashboard.py`

4. Pulsa **"Deploy"**. Espera 1-2 minutos mientras instala las dependencias.

5. Te dará una URL del tipo `https://tu-app.streamlit.app`.
   **Guárdala en el móvil** (añádela a la pantalla de inicio) y ábrela cuando
   quieras. ¡Ya está!

---

## Importante para que funcione en la nube

Los servidores gratuitos de Streamlit están en EE. UU. y **Binance bloquea esas
IPs**. Por eso, en el panel (barra lateral → *Fuente de datos*):

- **"Datos de ejemplo (demo)"** → funciona siempre, en cualquier sitio (datos
  simulados, para ver cómo se comporta la estrategia).
- **"Kraken"** → datos reales que sí funcionan desde EE. UU.
- **"Binance"** → puede fallar en la nube; úsalo cuando ejecutes en tu propio
  ordenador o servidor.

---

## Y para operar de verdad desde el móvil (de pago, barato)

Cuando hayas probado a fondo y quieras operar 24/7:

1. Alquila un **VPS** pequeño (~3-5 €/mes: Hetzner, DigitalOcean, Contabo…).
2. Instalas el proyecto ahí y ejecutas `python run_bot.py` en modo `paper` y,
   más adelante, `live`.
3. Lo controlas por SSH desde el móvil (con apps como Termius) o dejando el
   panel desplegado para consultar.

Pídemelo y te preparo la guía del VPS paso a paso cuando llegues a ese punto.
