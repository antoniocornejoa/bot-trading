const QE = require(__dirname + "/engine.js"); const fs = require("fs");
const data = JSON.parse(fs.readFileSync(__dirname + "/data.json"));
const cases = JSON.parse(fs.readFileSync(__dirname + "/py_cases.json"));
let ok = 0, bad = 0;
for (const cs of cases) {
  const rows = data[cs.symbol][cs.tf]; const full = QE.toBars(rows);
  const startI = rows.findIndex(r => r[0] * 3600000 >= cs.start_ms);
  const strat = QE.STRATEGIES[cs.strategy]; const sig = strat.generate(full, cs.params);
  const res = QE.run(QE.slice(full, startI), QE.sliceSig(sig, startI), QE.SCENARIOS[cs.scenario], { initialCapital: 500, riskPct: cs.risk, ...QE.LIMITS[cs.symbol] });
  const m = QE.metrics(res, QE.BARS_PER_YEAR[cs.tf]);
  const js = res.trades.map(t => [t.entryTs, t.exitTs, t.reason, +t.pnl.toFixed(6), +t.r.toFixed(6)]);
  const py = cs.trades;
  let same = js.length === py.length;
  if (same) for (let i = 0; i < js.length; i++) { const a = js[i], b = py[i]; if (a[0] !== b[0] || a[1] !== b[1] || a[2] !== b[2] || Math.abs(a[3] - b[3]) > 1e-3 || Math.abs(a[4] - b[4]) > 1e-4) { same = false; console.log("  diff", i, a, b); break; } }
  console.log(`${cs.symbol} ${cs.tf} ${cs.strategy} ${cs.scenario}: js ${js.length} trades, py ${py.length} | expR js ${m.expR.toFixed(4)} py ${cs.expR.toFixed(4)} | equity js ${res.equity[res.equity.length-1].toFixed(4)} py ${cs.final_equity.toFixed(4)} → ${same ? "OK" : "MISMATCH"}`);
  same ? ok++ : bad++;
}
console.log(`\n${ok} OK, ${bad} mismatch`); process.exit(bad ? 1 : 0);
