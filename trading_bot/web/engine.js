// Motor de backtesting en JavaScript: réplica exacta de trading_bot/backtesting/engine.py,
// features/ta.py y strategies/{trend,benchmarks}.py. Validado contra el motor Python
// operación por operación (ver validate.js).
const QE = (() => {
  const NaN_ = Number.NaN;
  const isnan = (x) => Number.isNaN(x);

  // ---------- indicadores causales (pandas ewm adjust=False, min_periods=n)
  function ewm(x, alpha, n) {
    const out = new Array(x.length).fill(NaN_);
    let y = NaN_, seen = 0;
    for (let i = 0; i < x.length; i++) {
      const v = x[i];
      if (isnan(v)) { out[i] = NaN_; continue; }
      seen++;
      y = isnan(y) ? v : alpha * v + (1 - alpha) * y;
      out[i] = seen >= n ? y : NaN_;
    }
    return out;
  }
  const ema = (x, n) => ewm(x, 2 / (n + 1), n);
  function sma(x, n) {
    const out = new Array(x.length).fill(NaN_); let s = 0;
    for (let i = 0; i < x.length; i++) { s += x[i]; if (i >= n) s -= x[i - n]; if (i >= n - 1) out[i] = s / n; }
    return out;
  }
  function trueRange(o, h, l, c) {
    const out = new Array(c.length);
    for (let i = 0; i < c.length; i++) {
      const hl = h[i] - l[i];
      if (i === 0) { out[i] = hl; continue; }
      out[i] = Math.max(hl, Math.abs(h[i] - c[i - 1]), Math.abs(l[i] - c[i - 1]));
    }
    return out;
  }
  const atr = (o, h, l, c, n) => ewm(trueRange(o, h, l, c), 1 / n, n);
  function rollingMaxShift(x, n) { // max de las n barras ANTERIORES
    const out = new Array(x.length).fill(NaN_);
    for (let i = n; i < x.length; i++) { let m = -Infinity; for (let k = i - n; k < i; k++) if (x[k] > m) m = x[k]; out[i] = m; }
    return out;
  }
  function rollingMinShift(x, n) {
    const out = new Array(x.length).fill(NaN_);
    for (let i = n; i < x.length; i++) { let m = Infinity; for (let k = i - n; k < i; k++) if (x[k] < m) m = x[k]; out[i] = m; }
    return out;
  }
  function rollingMax1(x, n) { // rolling max, min_periods=1, incluye la actual
    const out = new Array(x.length);
    for (let i = 0; i < x.length; i++) { let m = -Infinity; for (let k = Math.max(0, i - n + 1); k <= i; k++) if (x[k] > m) m = x[k]; out[i] = m; }
    return out;
  }

  // ---------- estrategias → señales {entry, exit, stopDist, tpDist, trail}
  const STRATEGIES = {
    ma_momentum: {
      label: "Tendencia por media móvil (H-A2, candidata validada)",
      defaults: { n: 200, atr_mult: 2.0, atr_n: 14 },
      help: { n: "Velas de la media lenta (200 = la más elegida por el walk-forward)", atr_mult: "Stop en múltiplos del ATR", atr_n: "Periodo del ATR" },
      generate(b, p) {
        const ma = sma(b.c, p.n), a = atr(b.o, b.h, b.l, b.c, p.atr_n), n = b.c.length;
        const s = empty(n);
        for (let i = 0; i < n; i++) {
          s.entry[i] = b.c[i] > ma[i] && !isnan(ma[i]) && !isnan(a[i]);
          s.exit[i] = b.c[i] < ma[i];
          s.stopDist[i] = p.atr_mult * a[i];
        }
        return s;
      },
    },
    donchian_trend: {
      label: "Ruptura de canal Donchian (H-A1)",
      defaults: { n_entry: 55, n_exit: 20, atr_n: 14, atr_mult: 3.0, ema_filter: 200 },
      help: { n_entry: "Ruptura del máximo de N velas", n_exit: "Salida por mínimo de N velas", atr_mult: "Stop en múltiplos del ATR", ema_filter: "Filtro de tendencia (EMA)", atr_n: "Periodo del ATR" },
      generate(b, p) {
        const upper = rollingMaxShift(b.h, p.n_entry), lower = rollingMinShift(b.l, p.n_exit);
        const a = atr(b.o, b.h, b.l, b.c, p.atr_n), filt = ema(b.c, p.ema_filter), rm = rollingMax1(b.c, p.n_exit), n = b.c.length;
        const s = empty(n);
        for (let i = 0; i < n; i++) {
          s.entry[i] = b.c[i] > upper[i] && b.c[i] > filt[i] && !isnan(a[i]) && !isnan(upper[i]) && !isnan(filt[i]);
          s.exit[i] = b.c[i] < lower[i];
          s.stopDist[i] = p.atr_mult * a[i];
          s.trail[i] = rm[i] - p.atr_mult * a[i];
        }
        return s;
      },
    },
  };
  function empty(n) {
    return { entry: new Array(n).fill(false), exit: new Array(n).fill(false), stopDist: new Array(n).fill(NaN_), tpDist: new Array(n).fill(NaN_), trail: new Array(n).fill(NaN_) };
  }

  // ---------- costes (backtesting/costs.py)
  const SCENARIOS = {
    optimistic: { name: "optimistic", fee: 0.075, halfSpread: 0.005, slip: 0.010, impact: 0.0, stopMult: 1.0 },
    base: { name: "base", fee: 0.100, halfSpread: 0.010, slip: 0.030, impact: 0.05, stopMult: 1.0 },
    pessimistic: { name: "pessimistic", fee: 0.100, halfSpread: 0.030, slip: 0.100, impact: 0.10, stopMult: 2.0 },
  };
  function adverse(sc, notional, prevQv, isStop) {
    let imp = 0;
    if (sc.impact > 0 && prevQv && prevQv > 0) imp = sc.impact * (notional / prevQv) * 100;
    return sc.halfSpread + sc.slip * (isStop ? sc.stopMult : 1) + imp;
  }
  const buyFill = (sc, ref, notional, prevQv) => ref * (1 + adverse(sc, notional, prevQv, false) / 100);
  const sellFill = (sc, ref, notional, prevQv, isStop) => ref * (1 - adverse(sc, notional, prevQv, isStop) / 100);
  const fee = (sc, fill, qty) => fill * qty * sc.fee / 100;
  const roundLot = (qty, step) => step > 0 ? Math.round(Math.floor(qty / step + 1e-9) * step * 1e12) / 1e12 : qty;

  // ---------- motor (backtesting/engine.py) + modo bot opcional (risk/engine.py: escalones por DD y kill switch)
  function run(b, s, sc, opt) {
    const { initialCapital = 500, riskPct = 1.0, minNotional = 5, lotStep = 1e-5, bot = null } = opt;
    const n = b.c.length, o = b.o, h = b.h, lo = b.l, c = b.c, qv = b.qv;
    let cash = initialCapital, pos = null, peak = initialCapital, killed = false, halted = false;
    const equity = new Array(n), trades = [];
    let skippedMin = 0, skippedRisk = 0;
    const closePos = (i, ref, reason, isStop) => {
      const notional = pos.qty * ref;
      const fill = sellFill(sc, ref, notional, i > 0 ? qv[i - 1] : 0, isStop);
      const f = fee(sc, fill, pos.qty);
      const proceeds = fill * pos.qty - f;
      cash += proceeds;
      const pnl = proceeds - pos.costBasis;
      const slip = (pos.entryPrice - pos.entryRef) * pos.qty + (ref - fill) * pos.qty;
      trades.push({ signalI: pos.signalI, entryI: pos.entryI, exitI: i, entryTs: b.ts[pos.entryI], exitTs: b.ts[i],
        entryPrice: pos.entryPrice, exitPrice: fill, qty: pos.qty, stopInitial: pos.stopInitial, stopFinal: pos.stop,
        riskUsd: pos.riskUsd, reason, fees: pos.entryFee + f, slippage: slip, pnl, r: pos.riskUsd > 0 ? pnl / pos.riskUsd : 0,
        barsHeld: i - pos.entryI, equityAtEntry: pos.equityAtEntry });
      pos = null;
    };
    for (let i = 0; i < n; i++) {
      let exited = false;
      if (pos) {
        if (i > 0 && s.exit[i - 1]) { closePos(i, o[i], "signal", false); exited = true; }
        else {
          if (i > 0 && !isnan(s.trail[i - 1]) && s.trail[i - 1] > pos.stop) pos.stop = s.trail[i - 1];
          const stop = pos.stop, tp = pos.tp;
          if (o[i] <= stop) { closePos(i, o[i], "stop", true); exited = true; }
          else if (!isnan(tp) && o[i] >= tp) { closePos(i, o[i], "take_profit", false); exited = true; }
          else if (lo[i] <= stop) { closePos(i, stop, "stop", true); exited = true; }
          else if (!isnan(tp) && h[i] >= tp) { closePos(i, tp, "take_profit", false); exited = true; }
        }
      }
      // modo bot: kill switch por drawdown (cierra y se detiene) y escalones de riesgo
      let mult = 1.0;
      if (bot) {
        const eqPrev = i > 0 ? equity[i - 1] : initialCapital;
        if (eqPrev > peak) peak = eqPrev;
        const dd = 1 - eqPrev / peak;
        if (!killed && dd >= bot.ddKill) { killed = true; bot.events.push({ i, kind: "kill", msg: `drawdown ${(dd*100).toFixed(1)} % ≥ ${(bot.ddKill*100).toFixed(0)} %: kill switch` }); }
        if (killed) { if (pos) { closePos(i, o[i], "kill", false); exited = true; } mult = 0; }
        else if (dd >= bot.ddHalt) mult = 0;
        else { mult = 0; for (const [upper, m] of bot.tiers) { if (dd < upper) { mult = m; break; } } }
      }
      if (!pos && !exited && i > 0 && s.entry[i - 1]) {
        const sd = s.stopDist[i - 1];
        if (!(isnan(sd) || sd <= 0)) {
          if (bot && mult === 0) { skippedRisk++; }
          else {
            const equityNow = cash;
            const riskUsd = equityNow * riskPct * mult / 100;
            let qty = riskUsd / sd;
            const ref = o[i];
            const fill = buyFill(sc, ref, qty * ref, qv[i - 1]);
            const qtyCash = cash / (fill * (1 + sc.fee / 100));
            if (qty > qtyCash) qty = qtyCash;
            qty = roundLot(qty, lotStep);
            if (qty * fill < minNotional || qty <= 0) skippedMin++;
            else {
              const f = fee(sc, fill, qty);
              cash -= fill * qty + f;
              pos = { qty, entryPrice: fill, entryRef: ref, entryFee: f, costBasis: fill * qty + f, stop: fill - sd, stopInitial: fill - sd,
                tp: !isnan(s.tpDist[i - 1]) ? fill + s.tpDist[i - 1] : NaN_, riskUsd: qty * sd, entryI: i, signalI: i - 1, equityAtEntry: equityNow };
              if (lo[i] <= pos.stop) closePos(i, pos.stop, "stop", true);
              else if (!isnan(pos.tp) && h[i] >= pos.tp) closePos(i, pos.tp, "take_profit", false);
            }
          }
        }
      }
      equity[i] = cash + (pos ? pos.qty * c[i] : 0);
    }
    if (pos) { closePos(n - 1, c[n - 1], "end", false); equity[n - 1] = cash; }
    return { trades, equity, initialCapital, skippedMin, skippedRisk, killed };
  }

  // ---------- métricas (backtesting/metrics.py)
  function metrics(res, barsPerYear) {
    const eq = res.equity, n = eq.length, cap = res.initialCapital, t = res.trades;
    const years = n / barsPerYear;
    const out = { trades: t.length, skippedMin: res.skippedMin, skippedRisk: res.skippedRisk, killed: res.killed };
    out.totalReturn = 100 * (eq[n - 1] / cap - 1);
    out.cagr = years > 0 && eq[n - 1] > 0 ? 100 * (Math.pow(eq[n - 1] / cap, 1 / years) - 1) : NaN_;
    const r = []; for (let i = 1; i < n; i++) r.push(eq[i] / eq[i - 1] - 1);
    const mean = r.reduce((a, v) => a + v, 0) / r.length;
    const sd = Math.sqrt(r.reduce((a, v) => a + (v - mean) ** 2, 0) / (r.length - 1));
    out.sharpe = sd > 0 ? mean / sd * Math.sqrt(barsPerYear) : NaN_;
    const dsd = Math.sqrt(r.reduce((a, v) => a + (v < 0 ? v * v : 0), 0) / r.length);
    out.sortino = dsd > 0 ? mean / dsd * Math.sqrt(barsPerYear) : NaN_;
    let pk = -Infinity, mdd = 0, ddSum = 0, ddCnt = 0; const dd = new Array(n);
    for (let i = 0; i < n; i++) { if (eq[i] > pk) pk = eq[i]; dd[i] = eq[i] / pk - 1; if (dd[i] < mdd) mdd = dd[i]; if (dd[i] < 0) { ddSum += dd[i]; ddCnt++; } }
    out.maxDD = 100 * mdd; out.avgDD = ddCnt ? 100 * ddSum / ddCnt : 0; out.dd = dd;
    out.calmar = mdd < 0 && !isnan(out.cagr) ? out.cagr / Math.abs(out.maxDD) : NaN_;
    if (!t.length) { Object.assign(out, { winRate: NaN_, avgWinR: NaN_, avgLossR: NaN_, payoff: NaN_, pf: NaN_, expR: NaN_, tStat: NaN_, maxWins: 0, maxLosses: 0, costRatio: NaN_, tradesPerYear: 0, avgBars: NaN_ }); return out; }
    const R = t.map(x => x.r), pnl = t.map(x => x.pnl), wins = pnl.map(v => v > 0);
    const nw = wins.filter(Boolean).length;
    out.winRate = 100 * nw / t.length;
    const wR = R.filter((_, i) => wins[i]), lR = R.filter((_, i) => !wins[i]);
    out.avgWinR = wR.length ? wR.reduce((a, v) => a + v, 0) / wR.length : 0;
    out.avgLossR = lR.length ? lR.reduce((a, v) => a + v, 0) / lR.length : 0;
    out.payoff = out.avgLossR < 0 ? Math.abs(out.avgWinR / out.avgLossR) : NaN_;
    const gp = pnl.filter(v => v > 0).reduce((a, v) => a + v, 0), gl = -pnl.filter(v => v < 0).reduce((a, v) => a + v, 0);
    out.pf = gl > 0 ? gp / gl : (gp > 0 ? Infinity : 0);
    out.expR = R.reduce((a, v) => a + v, 0) / R.length;
    const rsd = R.length > 1 ? Math.sqrt(R.reduce((a, v) => a + (v - out.expR) ** 2, 0) / (R.length - 1)) : 0;
    out.tStat = rsd > 0 ? out.expR / (rsd / Math.sqrt(R.length)) : NaN_;
    let bw = 0, bl = 0, cw = 0, cl = 0; for (const w of wins) { if (w) { cw++; cl = 0; } else { cl++; cw = 0; } bw = Math.max(bw, cw); bl = Math.max(bl, cl); }
    out.maxWins = bw; out.maxLosses = bl;
    const costs = t.reduce((a, x) => a + x.fees + x.slippage, 0), gross = pnl.reduce((a, v) => a + v, 0) + costs;
    out.costsTotal = costs; out.costRatio = gross > 0 ? costs / gross : Infinity;
    out.tradesPerYear = years > 0 ? t.length / years : NaN_;
    out.avgBars = t.reduce((a, x) => a + x.barsHeld, 0) / t.length;
    return out;
  }

  const BARS_PER_YEAR = { "1h": 8760, "4h": 2190, "1d": 365 };
  const LIMITS = { BTCUSDT: { minNotional: 5, lotStep: 0.00001 }, ETHUSDT: { minNotional: 5, lotStep: 0.0001 }, SOLUSDT: { minNotional: 5, lotStep: 0.001 } };
  function toBars(rows) {
    const n = rows.length, b = { ts: new Array(n), o: new Array(n), h: new Array(n), l: new Array(n), c: new Array(n), qv: new Array(n) };
    for (let i = 0; i < n; i++) { const r = rows[i]; b.ts[i] = r[0] * 3600000; b.o[i] = r[1]; b.h[i] = r[2]; b.l[i] = r[3]; b.c[i] = r[4]; b.qv[i] = r[5]; }
    return b;
  }
  function slice(b, from, to) { const s = {}; for (const k of Object.keys(b)) s[k] = b[k].slice(from, to); return s; }
  function sliceSig(s, from, to) { const o = {}; for (const k of Object.keys(s)) o[k] = s[k].slice(from, to); return o; }
  return { STRATEGIES, SCENARIOS, BARS_PER_YEAR, LIMITS, run, metrics, toBars, slice, sliceSig, ema, sma, atr };
})();
if (typeof module !== "undefined") module.exports = QE;
