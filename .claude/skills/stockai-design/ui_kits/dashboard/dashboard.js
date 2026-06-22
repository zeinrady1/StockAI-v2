/* StockAI dashboard — mock data + interactions. Recreation only; no live data. */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ── Ticker tape ──
  const tapeData = [
    ['S&P 500', '6,142.30', 0.42], ['Nasdaq', '20,118.7', 0.61], ['Dow', '43,210', 0.18],
    ['VIX', '13.84', -3.10], ['NVDA', '118.40', 2.40], ['AAPL', '231.20', 0.55],
    ['MSFT', '478.90', -0.31], ['TSLA', '342.10', 3.82], ['META', '612.40', 1.12],
    ['BTC', '101,420', 1.94], ['ETH', '3,812', -0.62], ['GOLD', '2,684', 0.21],
  ];
  const tape = $('#tape');
  if (tape) {
    const html = tapeData.map(([s, p, c]) => {
      const cl = c >= 0 ? 'g' : 'r';
      const arrow = c >= 0 ? '▲' : '▼';
      return `<span class="tk"><b>${s}</b> ${p} <span class="c ${cl}">${arrow} ${c >= 0 ? '+' : ''}${c.toFixed(2)}%</span></span>`;
    }).join('');
    tape.innerHTML = html + html; // duplicate for seamless loop
  }

  // ── Live clock ──
  const clock = $('#clock');
  function tick() {
    if (!clock) return;
    const d = new Date();
    const hh = String(9 + (d.getSeconds() % 7)).padStart(2, '0'); // fake market hour-ish
    const t = d.toLocaleTimeString('en-US', { hour12: false });
    clock.textContent = t + ' ET';
  }
  setInterval(tick, 1000); tick();

  // ── Positions ──
  const positions = [
    ['NVDA', 25, 118.40, 9.2], ['PLTR', 80, 42.10, 4.1],
    ['AMD', 40, 168.30, -1.8], ['COIN', 15, 254.90, 12.4],
  ];
  $('#positions').innerHTML = positions.map(([t, sh, px, pl]) => {
    const cl = pl >= 0 ? 'g' : 'r';
    return `<div class="pos-row">
      <div><div class="ptk">${t}</div><div class="psub">${sh} sh @ $${px}</div></div>
      <div style="text-align:right"><div class="${cl}" style="font-weight:800;font-size:12px">${pl >= 0 ? '+' : ''}${pl}%</div>
      <div class="psub">$${(sh * px).toLocaleString()}</div></div>
    </div>`;
  }).join('');

  // ── Watchlist ──
  const watch = [
    ['TSLA', 342.10, 3.82], ['META', 612.40, 1.12], ['AAPL', 231.20, 0.55],
    ['MSTR', 1842.0, -2.31], ['HOOD', 38.40, 5.12], ['ARM', 142.80, -0.84],
  ];
  $('#watchlist').innerHTML = watch.map(([t, px, c]) => {
    const cl = c >= 0 ? 'g' : 'r';
    return `<div class="wl-row">
      <span class="ptk" style="color:var(--yellow);font-size:11px">${t}</span>
      <span><span style="font-size:10px">$${px}</span> <span class="${cl}" style="font-size:10px;font-weight:700">${c >= 0 ? '+' : ''}${c}%</span></span>
    </div>`;
  }).join('');

  // ── Intel feeds ──
  const congress = [
    ['NVDA', 'Purchase', 'N. Pelosi (CA) · $1M–5M · Jun 18'],
    ['PANW', 'Purchase', 'J. Hern (OK) · $50K–100K · Jun 17'],
    ['LMT', 'Sale', 'M. Green (TN) · $100K–250K · Jun 16'],
    ['MSFT', 'Purchase', 'R. Wexton (VA) · $15K–50K · Jun 15'],
    ['XOM', 'Sale', 'D. Crenshaw (TX) · $250K–500K · Jun 14'],
  ];
  const insider = [
    ['TSLA', 'SELL', 'E. Musk (CEO) · 120,000 sh · $42.1M · Jun 18'],
    ['AMZN', 'SELL', 'A. Jassy (CEO) · 25,000 sh · $5.4M · Jun 17'],
    ['COIN', 'BUY', 'B. Armstrong (CEO) · 8,000 sh · $2.0M · Jun 16'],
    ['META', 'SELL', 'M. Zuckerberg (CEO) · 40,000 sh · $24.5M · Jun 15'],
    ['NVDA', 'BUY', 'J. Huang (CEO) · 12,000 sh · $1.4M · Jun 14'],
  ];
  const news = [
    ['Reuters', 'Fed holds rates, signals two cuts later this year as inflation cools'],
    ['Bloomberg', 'Nvidia extends rally on sovereign-AI demand; analysts lift targets'],
    ['CNBC', 'Tesla robotaxi pilot expands to three new metros ahead of schedule'],
    ['WSJ', 'Crypto majors climb as spot-ETF inflows hit a record week'],
    ['Barron’s', 'Semis lead market breadth; small caps catch a bid on soft-landing hopes'],
  ];
  $('#acc-cong').innerHTML = congress.map(([t, a, m]) => {
    const cls = /purchase|buy/i.test(a) ? 'ia-b' : 'ia-s';
    return `<div class="intel-item"><span class="it">${t}</span><span class="${cls}">${a}</span><div class="im">${m}</div></div>`;
  }).join('');
  $('#acc-ins').innerHTML = insider.map(([t, a, m]) => {
    const cls = a === 'BUY' ? 'ia-b' : 'ia-s';
    return `<div class="intel-item"><span class="it">${t}</span><span class="${cls}">${a}</span><div class="im">${m}</div></div>`;
  }).join('');
  $('#acc-nws').innerHTML = news.map(([src, h]) =>
    `<div class="ni"><div class="nt">${src}</div><a>${h}</a></div>`).join('');

  // ── Accordion toggle ──
  $$('.acc-hdr').forEach(h => h.addEventListener('click', () => {
    h.classList.toggle('open');
    $('#acc-' + h.dataset.acc).classList.toggle('open');
  }));

  // ── Center tabs ──
  $$('#cTabs .tab').forEach(t => t.addEventListener('click', () => {
    $$('#cTabs .tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    $$('.tab-content').forEach(c => c.classList.remove('active'));
    $('#ct-' + t.dataset.c).classList.add('active');
  }));

  // ── Movers (for the Movers tab) ──
  const movers = [
    ['SMCI', 28.4], ['CVNA', 14.1], ['APP', 11.8], ['RBLX', 9.2],
    ['PYPL', -8.6], ['ENPH', -7.1], ['LULU', -6.4], ['WBA', -5.9],
  ];
  $('#moversOut').innerHTML = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">' +
    movers.map(([t, c]) => {
      const cl = c >= 0 ? 'g' : 'r';
      return `<div class="stat" style="display:flex;justify-content:space-between;align-items:center;cursor:pointer">
        <span class="ptk" style="color:var(--yellow);font-size:11px">${t}</span>
        <span class="${cl}" style="font-weight:800">${c >= 0 ? '+' : ''}${c}%</span></div>`;
    }).join('') + '</div>';

  // ── AI Analysis output ──
  const setups = [
    { tk: 'NVDA', act: 'buy', conf: 8, px: '$118.40 · entry $116 · target $134', sigs: ['RSI 41', 'MACD cross', 'Insider buy', 'Rev +62% YoY'], rsn: 'Pullback to the 50-day with bullish insider flow and accelerating data-center revenue. Sized at 5% of book.' },
    { tk: 'SOFI', act: 'sell', conf: 7, px: '$9.12 · stop $9.40', sigs: ['RSI 71', 'Below 200DMA', 'Congress sale'], rsn: 'Overbought into resistance with a notable Congressional sale this week.' },
    { tk: 'AMD', act: 'hold', conf: 5, px: '$168.30', sigs: ['Range-bound', 'Earnings 7d'], rsn: 'Wait for the print before sizing in.' },
  ];
  function accent(a) { return a === 'buy' ? 'var(--green)' : a === 'sell' ? 'var(--red)' : 'var(--yellow)'; }
  function wash(a) { return a === 'buy' ? 'var(--green-wash)' : a === 'sell' ? 'var(--red-wash)' : 'var(--yellow-wash)'; }
  function renderAnalysis() {
    $('#analysisOut').innerHTML =
      `<div style="font-size:8px;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin-bottom:8px">Regime: <span class="g">Risk-On</span> · VIX 13.8 · breadth positive</div>` +
      setups.map(s => {
        const ac = accent(s.act);
        const sigs = s.sigs.map(x => `<span style="background:var(--blue-wash);color:var(--blue);border:1px solid var(--blue-line);padding:1px 5px;border-radius:4px;font-size:8px">${x}</span>`).join('');
        const eb = s.act !== 'hold' ? `<button style="margin-top:6px;padding:4px 10px;border-radius:5px;border:none;cursor:pointer;font-size:9px;font-weight:700;font-family:inherit;background:${ac};color:${s.act === 'sell' ? '#fff' : '#000'}">${s.act === 'buy' ? 'Execute Buy' : 'Close Position'}</button>` : '';
        return `<div style="border:1px solid var(--border);border-left:3px solid ${ac};border-radius:6px;padding:9px;margin-bottom:6px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="font-size:14px;font-weight:800">${s.tk}</span>
            <span style="display:flex;gap:6px;align-items:center">
              <span style="font-size:9px;color:var(--dim)">conf <b style="color:${ac}">${s.conf}/10</b></span>
              <span style="padding:2px 7px;border-radius:4px;font-size:9px;font-weight:800;text-transform:uppercase;background:${wash(s.act)};color:${ac}">${s.act}</span>
            </span>
          </div>
          <div style="font-size:10px;color:var(--muted)">${s.px}</div>
          <div style="display:flex;flex-wrap:wrap;gap:3px;margin-top:4px">${sigs}</div>
          <div style="font-size:9px;color:var(--muted);margin-top:5px;line-height:1.5">${s.rsn}</div>
          ${eb}
        </div>`;
      }).join('');
  }
  renderAnalysis();
  $('#runAi').addEventListener('click', () => {
    $('#runAi').textContent = '◷ Analyzing…';
    setTimeout(() => {
      $('#runAi').textContent = '▶ Run AI Analysis';
      $$('#cTabs .tab').forEach(x => x.classList.remove('active'));
      $('#cTabs .tab[data-c="analysis"]').classList.add('active');
      $$('.tab-content').forEach(c => c.classList.remove('active'));
      $('#ct-analysis').classList.add('active');
    }, 900);
  });

  // ── Trade form ──
  const qty = $('#ordQty'), total = $('#ordTotal'), submit = $('#submitOrder');
  const tkIn = $('#ordTk');
  let side = 'buy';
  const PX = 118.40;
  function refreshOrder() {
    const q = parseInt(qty.value || '0', 10);
    total.textContent = '$' + (q * PX).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    submit.textContent = `${side === 'buy' ? 'Buy' : 'Sell'} ${q} ${tkIn.value || 'NVDA'}`;
    submit.className = 'btn ' + (side === 'buy' ? 'submit-buy' : 'submit-sell');
  }
  qty.addEventListener('input', refreshOrder);
  tkIn.addEventListener('input', refreshOrder);
  $('#sideBuy').addEventListener('click', () => { side = 'buy'; $('#sideBuy').classList.add('active'); $('#sideSell').classList.remove('active'); refreshOrder(); });
  $('#sideSell').addEventListener('click', () => { side = 'sell'; $('#sideSell').classList.add('active'); $('#sideBuy').classList.remove('active'); refreshOrder(); });
  submit.addEventListener('click', () => {
    const t = $('#orderToast');
    t.textContent = `✓ ${side === 'buy' ? 'Bought' : 'Sold'} ${qty.value} ${tkIn.value} @ $${PX} (paper)`;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2600);
  });
  refreshOrder();

  // ── Candlestick chart (canvas) ──
  const cv = $('#candles');
  function drawCandles() {
    if (!cv) return;
    const stage = cv.parentElement;
    const w = cv.width = stage.clientWidth * devicePixelRatio;
    const h = cv.height = stage.clientHeight * devicePixelRatio;
    const ctx = cv.getContext('2d');
    ctx.clearRect(0, 0, w, h);

    // grid
    ctx.strokeStyle = 'rgba(36,48,68,0.5)';
    ctx.lineWidth = 1;
    for (let i = 1; i < 6; i++) { const y = h * i / 6; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    // generate deterministic-ish candles trending up
    const n = 60;
    let price = 96;
    const candles = [];
    let seed = 7;
    const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    for (let i = 0; i < n; i++) {
      const drift = 0.45;
      const open = price;
      const move = (rnd() - 0.5) * 4 + drift;
      const close = Math.max(60, open + move);
      const high = Math.max(open, close) + rnd() * 2.2;
      const low = Math.min(open, close) - rnd() * 2.2;
      candles.push({ open, close, high, low });
      price = close;
    }
    const lo = Math.min(...candles.map(c => c.low));
    const hi = Math.max(...candles.map(c => c.high));
    const pad = 26 * devicePixelRatio;
    const yOf = p => h - pad - ((p - lo) / (hi - lo)) * (h - pad * 2);
    const cw = w / n;
    const bodyW = cw * 0.6;
    candles.forEach((c, i) => {
      const x = i * cw + cw / 2;
      const up = c.close >= c.open;
      const col = up ? '#00e676' : '#ff4444';
      ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 1 * devicePixelRatio;
      ctx.beginPath(); ctx.moveTo(x, yOf(c.high)); ctx.lineTo(x, yOf(c.low)); ctx.stroke();
      const yO = yOf(c.open), yC = yOf(c.close);
      const top = Math.min(yO, yC), bh = Math.max(2, Math.abs(yC - yO));
      ctx.fillRect(x - bodyW / 2, top, bodyW, bh);
    });

    // last price line
    const lastY = yOf(candles[n - 1].close);
    ctx.strokeStyle = 'rgba(0,230,118,0.5)'; ctx.setLineDash([4 * devicePixelRatio, 4 * devicePixelRatio]);
    ctx.beginPath(); ctx.moveTo(0, lastY); ctx.lineTo(w, lastY); ctx.stroke(); ctx.setLineDash([]);
  }
  drawCandles();
  window.addEventListener('resize', drawCandles);
  // redraw when chart tab becomes active (canvas sized 0 while hidden)
  new ResizeObserver(drawCandles).observe(cv.parentElement);
})();
