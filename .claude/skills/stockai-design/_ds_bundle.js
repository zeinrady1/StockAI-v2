/* @ds-bundle: {"format":3,"namespace":"StockAIDesignSystem_ed0dbf","components":[{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"IntelRow","sourcePath":"components/data/IntelRow.jsx"},{"name":"Stat","sourcePath":"components/data/Stat.jsx"},{"name":"TickerTag","sourcePath":"components/data/TickerTag.jsx"},{"name":"TradeCard","sourcePath":"components/data/TradeCard.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Toggle","sourcePath":"components/forms/Toggle.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"}],"sourceHashes":{"components/core/Badge.jsx":"4d1f42afb562","components/core/Button.jsx":"a201664110fb","components/core/Card.jsx":"485f2ff29c42","components/data/IntelRow.jsx":"07c4188d7df9","components/data/Stat.jsx":"cc3247204db5","components/data/TickerTag.jsx":"0f4c399c6537","components/data/TradeCard.jsx":"b7d9262b665c","components/forms/Input.jsx":"f6aa17b80c5e","components/forms/Toggle.jsx":"9031124ce984","components/navigation/Tabs.jsx":"a9b522e864bc","ui_kits/dashboard/dashboard.js":"83169c3b5fc9"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.StockAIDesignSystem_ed0dbf = window.StockAIDesignSystem_ed0dbf || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Badge — small pill/chip. Two shapes:
 *  - chip (default): squared 4px-radius tag (Paper, Opus 4.8, signal chips)
 *  - pill: rounded 20px outlook pill (BULLISH / BEARISH / NEUTRAL)
 * Tones map to semantic colors and render a translucent wash + matching border.
 */
function Badge({
  tone = 'green',
  shape = 'chip',
  children,
  style,
  ...rest
}) {
  const tones = {
    green: {
      color: 'var(--green)',
      bg: 'var(--green-wash)',
      bd: 'var(--green-line)'
    },
    red: {
      color: 'var(--red)',
      bg: 'var(--red-wash)',
      bd: 'var(--red-line)'
    },
    yellow: {
      color: 'var(--yellow)',
      bg: 'var(--yellow-wash)',
      bd: 'rgba(251,191,36,0.25)'
    },
    blue: {
      color: 'var(--blue)',
      bg: 'var(--blue-wash)',
      bd: 'var(--blue-line)'
    },
    purple: {
      color: 'var(--purple)',
      bg: 'var(--purple-wash)',
      bd: 'var(--purple-line)'
    },
    muted: {
      color: 'var(--muted)',
      bg: 'rgba(139,152,174,0.12)',
      bd: 'rgba(139,152,174,0.2)'
    }
  };
  const t = tones[tone] || tones.green;
  const isPill = shape === 'pill';
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-block',
      color: t.color,
      background: t.bg,
      border: `1px solid ${t.bd}`,
      borderRadius: isPill ? 'var(--r-pill)' : 'var(--r-xs)',
      padding: isPill ? '2px 8px' : '1px 5px',
      fontSize: isPill ? 'var(--fs-tiny)' : 'var(--fs-label)',
      fontWeight: isPill ? 'var(--fw-black)' : 'var(--fw-medium)',
      textTransform: isPill ? 'uppercase' : 'none',
      letterSpacing: isPill ? '0.3px' : '0',
      whiteSpace: 'nowrap',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Button — monospace, dense, with semantic variants.
 * Primary (green, black text) = the main action (Run AI Analysis, Go, Buy).
 * Secondary (ghost outline) = supporting actions (Refresh Intel).
 * buy/sell = execution buttons keyed to market colors.
 */
function Button({
  variant = 'primary',
  size = 'md',
  full = false,
  disabled = false,
  children,
  style,
  ...rest
}) {
  const base = {
    fontFamily: 'var(--font-mono)',
    fontWeight: 'var(--fw-bold)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    border: 'none',
    transition: 'all 0.15s',
    width: full ? '100%' : 'auto',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '5px',
    whiteSpace: 'nowrap'
  };
  const sizes = {
    sm: {
      padding: '4px 10px',
      fontSize: 'var(--fs-tiny)',
      borderRadius: 'var(--r-md)'
    },
    md: {
      padding: '9px',
      fontSize: 'var(--fs-value)',
      borderRadius: 'var(--r-lg)'
    },
    inline: {
      padding: '5px 12px',
      fontSize: 'var(--fs-base)',
      borderRadius: 'var(--r-md)'
    }
  };
  const variants = {
    primary: {
      background: 'var(--green)',
      color: '#000'
    },
    secondary: {
      background: 'transparent',
      border: '1px solid var(--border2)',
      color: 'var(--muted)'
    },
    buy: {
      background: 'var(--green)',
      color: '#000'
    },
    sell: {
      background: 'var(--red)',
      color: '#fff'
    }
  };
  const disabledStyle = disabled ? {
    background: 'var(--border2)',
    color: 'var(--dim)',
    boxShadow: 'none'
  } : {};
  return /*#__PURE__*/React.createElement("button", _extends({
    disabled: disabled,
    style: {
      ...base,
      ...sizes[size],
      ...variants[variant],
      ...disabledStyle,
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Card — the raised panel surface. Optional uppercase title row
 * (card-t) with an optional right-aligned accessory (badge, count, dot).
 */
function Card({
  title,
  accessory,
  children,
  style,
  bodyStyle,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: 'var(--card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-xl)',
      padding: '10px',
      ...style
    }
  }, rest), title != null && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-label)',
      textTransform: 'uppercase',
      letterSpacing: 'var(--ls-wide)',
      color: 'var(--dim)',
      marginBottom: '8px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", null, title), accessory != null && /*#__PURE__*/React.createElement("span", null, accessory)), /*#__PURE__*/React.createElement("div", {
    style: bodyStyle
  }, children));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/data/IntelRow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI IntelRow — a single row in the Congress / Insider / News feeds.
 * A bold amber ticker + colored action tag, with a dim meta line beneath.
 * Whole row is hover-highlightable and clickable (opens the chart).
 */
function IntelRow({
  ticker,
  action,
  meta,
  onClick,
  style,
  ...rest
}) {
  const isBuy = action && /buy|purchase|long/i.test(action);
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", _extends({
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      padding: hover ? '5px 4px' : '5px 0',
      margin: hover ? '0 -4px' : 0,
      borderBottom: '1px solid var(--border)',
      cursor: onClick ? 'pointer' : 'default',
      background: hover ? 'var(--green-hover)' : 'transparent',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: '4px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 'var(--fw-black)',
      color: 'var(--yellow)',
      fontSize: 'var(--fs-value)'
    }
  }, ticker), action && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-tiny)',
      fontWeight: 'var(--fw-bold)',
      color: isBuy ? 'var(--green)' : 'var(--red)'
    }
  }, action)), meta && /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--dim)',
      fontSize: 'var(--fs-tiny)',
      marginTop: '1px',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, meta));
}
Object.assign(__ds_scope, { IntelRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/IntelRow.jsx", error: String((e && e.message) || e) }); }

// components/data/Stat.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Stat — an inset well showing a micro-label over a bold value.
 * The building block of the portfolio grid. `tone` colors the value for
 * gains/losses/neutral.
 */
function Stat({
  label,
  value,
  tone,
  style,
  ...rest
}) {
  const toneColor = {
    green: 'var(--green)',
    red: 'var(--red)',
    yellow: 'var(--yellow)'
  }[tone];
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: 'var(--well)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-sm)',
      padding: '6px 8px',
      minWidth: 0,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-micro)',
      color: 'var(--dim)',
      marginBottom: '2px',
      textTransform: 'uppercase',
      letterSpacing: 'var(--ls-label)'
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-value)',
      fontWeight: 'var(--fw-black)',
      color: toneColor || 'var(--text)',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, value));
}
Object.assign(__ds_scope, { Stat });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Stat.jsx", error: String((e && e.message) || e) }); }

// components/data/TickerTag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI TickerTag — a stock symbol rendered in the signature amber-black
 * weight, optionally followed by a buy/sell action label. Click to pull up
 * the chart in the real app.
 */
function TickerTag({
  symbol,
  action,
  size = 'md',
  onClick,
  style,
  ...rest
}) {
  const fs = size === 'lg' ? 'var(--fs-lg)' : size === 'sm' ? 'var(--fs-base)' : 'var(--fs-value)';
  const isBuy = action && /buy|purchase|long/i.test(action);
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: 'inline-flex',
      alignItems: 'baseline',
      gap: '4px',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    onClick: onClick,
    style: {
      fontWeight: 'var(--fw-black)',
      fontSize: fs,
      color: 'var(--yellow)',
      cursor: onClick ? 'pointer' : 'inherit'
    }
  }, symbol), action && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-tiny)',
      fontWeight: 'var(--fw-bold)',
      color: isBuy ? 'var(--green)' : 'var(--red)'
    }
  }, action));
}
Object.assign(__ds_scope, { TickerTag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/TickerTag.jsx", error: String((e && e.message) || e) }); }

// components/data/TradeCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI TradeCard — an AI recommendation block from the Analysis tab.
 * Left-accent bar keyed to the action (green buy / red sell / amber hold),
 * a header row with ticker + action tag + confidence, optional signal chips,
 * a rationale line, and an execute button.
 */
function TradeCard({
  ticker,
  action = 'hold',
  confidence,
  price,
  signals = [],
  rationale,
  onExecute,
  style,
  ...rest
}) {
  const al = String(action).toLowerCase();
  const accent = al === 'buy' ? 'var(--green)' : al === 'sell' ? 'var(--red)' : 'var(--yellow)';
  const tagBg = al === 'buy' ? 'var(--green-wash)' : al === 'sell' ? 'var(--red-wash)' : 'var(--yellow-wash)';
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      border: '1px solid var(--border)',
      borderLeft: `3px solid ${accent}`,
      borderRadius: 'var(--r-md)',
      padding: '9px',
      marginBottom: '6px',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '4px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-lg)',
      fontWeight: 'var(--fw-black)'
    }
  }, ticker), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '6px'
    }
  }, confidence != null && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--fs-tiny)',
      color: 'var(--dim)'
    }
  }, "conf ", /*#__PURE__*/React.createElement("b", {
    style: {
      color: accent
    }
  }, confidence, "/10")), /*#__PURE__*/React.createElement("span", {
    style: {
      padding: '2px 7px',
      borderRadius: 'var(--r-xs)',
      fontSize: 'var(--fs-tiny)',
      fontWeight: 'var(--fw-black)',
      textTransform: 'uppercase',
      background: tagBg,
      color: accent
    }
  }, al))), price != null && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-small)',
      color: 'var(--muted)'
    }
  }, price), signals.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '3px',
      marginTop: '4px'
    }
  }, signals.map((s, i) => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      background: 'var(--blue-wash)',
      color: 'var(--blue)',
      border: '1px solid var(--blue-line)',
      padding: '1px 5px',
      borderRadius: 'var(--r-xs)',
      fontSize: 'var(--fs-label)'
    }
  }, s))), rationale && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--fs-tiny)',
      color: 'var(--muted)',
      marginTop: '5px',
      lineHeight: 'var(--lh-body)'
    }
  }, rationale), onExecute && al !== 'hold' && al !== 'watch' && /*#__PURE__*/React.createElement("button", {
    onClick: onExecute,
    style: {
      marginTop: '6px',
      padding: '4px 10px',
      borderRadius: 'var(--r-sm)',
      border: 'none',
      cursor: 'pointer',
      fontSize: 'var(--fs-tiny)',
      fontWeight: 'var(--fw-bold)',
      fontFamily: 'var(--font-mono)',
      background: accent,
      color: al === 'sell' ? '#fff' : '#000'
    }
  }, al === 'buy' ? 'Execute Buy' : 'Close Position'));
}
Object.assign(__ds_scope, { TradeCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/TradeCard.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Input — the dark search/text field. Optional leading icon (used for
 * the global search glass). Focus brightens the border to green.
 */
function Input({
  icon,
  style,
  wrapStyle,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      ...wrapStyle
    }
  }, icon && /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: '9px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: 'var(--dim)',
      pointerEvents: 'none',
      fontSize: 'var(--fs-base)'
    }
  }, icon), /*#__PURE__*/React.createElement("input", _extends({
    style: {
      width: '100%',
      background: 'var(--field)',
      border: '1px solid var(--border2)',
      color: 'var(--text)',
      padding: icon ? '6px 12px 6px 30px' : '6px 12px',
      borderRadius: 'var(--r-xl)',
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--fs-value)',
      outline: 'none',
      ...style
    },
    onFocus: e => {
      e.target.style.borderColor = 'var(--green)';
    },
    onBlur: e => {
      e.target.style.borderColor = 'var(--border2)';
    }
  }, rest)));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Toggle.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Toggle — the pill switch. Off = grey track; on = amber track
 * (used for Auto-Pilot / Auto-execute). Knob slides on toggle.
 */
function Toggle({
  checked = false,
  onChange,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    role: "switch",
    "aria-checked": checked,
    onClick: () => onChange && onChange(!checked),
    style: {
      width: 'var(--tog-w)',
      height: 'var(--tog-h)',
      borderRadius: '9px',
      background: checked ? 'var(--yellow)' : 'var(--border2)',
      cursor: 'pointer',
      position: 'relative',
      transition: 'background 0.2s',
      flexShrink: 0,
      display: 'inline-block',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      content: '""',
      position: 'absolute',
      width: '13px',
      height: '13px',
      borderRadius: '50%',
      background: '#fff',
      top: '2px',
      left: checked ? '17px' : '2px',
      transition: 'left 0.2s'
    }
  }));
}
Object.assign(__ds_scope, { Toggle });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Toggle.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * StockAI Tabs — the horizontal tab strip used across panels (Chart / AI
 * Analysis / Market / Movers / All Stocks). Active tab is green with a green
 * underline; the strip sits on a raised surface and scrolls horizontally.
 */
function Tabs({
  tabs = [],
  active,
  onChange,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: 'flex',
      borderBottom: '1px solid var(--border)',
      background: 'var(--surface)',
      overflowX: 'auto',
      ...style
    }
  }, rest), tabs.map(t => {
    const id = typeof t === 'string' ? t : t.id;
    const label = typeof t === 'string' ? t : t.label;
    const isActive = id === active;
    return /*#__PURE__*/React.createElement("div", {
      key: id,
      onClick: () => onChange && onChange(id),
      style: {
        flexShrink: 0,
        padding: '7px 10px',
        fontSize: 'var(--fs-tiny)',
        cursor: 'pointer',
        color: isActive ? 'var(--green)' : 'var(--dim)',
        borderBottom: `2px solid ${isActive ? 'var(--green)' : 'transparent'}`,
        transition: 'all 0.1s',
        textTransform: 'uppercase',
        letterSpacing: 'var(--ls-label)',
        whiteSpace: 'nowrap'
      }
    }, label);
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/dashboard/dashboard.js
try { (() => {
/* StockAI dashboard — mock data + interactions. Recreation only; no live data. */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ── Ticker tape ──
  const tapeData = [['S&P 500', '6,142.30', 0.42], ['Nasdaq', '20,118.7', 0.61], ['Dow', '43,210', 0.18], ['VIX', '13.84', -3.10], ['NVDA', '118.40', 2.40], ['AAPL', '231.20', 0.55], ['MSFT', '478.90', -0.31], ['TSLA', '342.10', 3.82], ['META', '612.40', 1.12], ['BTC', '101,420', 1.94], ['ETH', '3,812', -0.62], ['GOLD', '2,684', 0.21]];
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
    const hh = String(9 + d.getSeconds() % 7).padStart(2, '0'); // fake market hour-ish
    const t = d.toLocaleTimeString('en-US', {
      hour12: false
    });
    clock.textContent = t + ' ET';
  }
  setInterval(tick, 1000);
  tick();

  // ── Positions ──
  const positions = [['NVDA', 25, 118.40, 9.2], ['PLTR', 80, 42.10, 4.1], ['AMD', 40, 168.30, -1.8], ['COIN', 15, 254.90, 12.4]];
  $('#positions').innerHTML = positions.map(([t, sh, px, pl]) => {
    const cl = pl >= 0 ? 'g' : 'r';
    return `<div class="pos-row">
      <div><div class="ptk">${t}</div><div class="psub">${sh} sh @ $${px}</div></div>
      <div style="text-align:right"><div class="${cl}" style="font-weight:800;font-size:12px">${pl >= 0 ? '+' : ''}${pl}%</div>
      <div class="psub">$${(sh * px).toLocaleString()}</div></div>
    </div>`;
  }).join('');

  // ── Watchlist ──
  const watch = [['TSLA', 342.10, 3.82], ['META', 612.40, 1.12], ['AAPL', 231.20, 0.55], ['MSTR', 1842.0, -2.31], ['HOOD', 38.40, 5.12], ['ARM', 142.80, -0.84]];
  $('#watchlist').innerHTML = watch.map(([t, px, c]) => {
    const cl = c >= 0 ? 'g' : 'r';
    return `<div class="wl-row">
      <span class="ptk" style="color:var(--yellow);font-size:11px">${t}</span>
      <span><span style="font-size:10px">$${px}</span> <span class="${cl}" style="font-size:10px;font-weight:700">${c >= 0 ? '+' : ''}${c}%</span></span>
    </div>`;
  }).join('');

  // ── Intel feeds ──
  const congress = [['NVDA', 'Purchase', 'N. Pelosi (CA) · $1M–5M · Jun 18'], ['PANW', 'Purchase', 'J. Hern (OK) · $50K–100K · Jun 17'], ['LMT', 'Sale', 'M. Green (TN) · $100K–250K · Jun 16'], ['MSFT', 'Purchase', 'R. Wexton (VA) · $15K–50K · Jun 15'], ['XOM', 'Sale', 'D. Crenshaw (TX) · $250K–500K · Jun 14']];
  const insider = [['TSLA', 'SELL', 'E. Musk (CEO) · 120,000 sh · $42.1M · Jun 18'], ['AMZN', 'SELL', 'A. Jassy (CEO) · 25,000 sh · $5.4M · Jun 17'], ['COIN', 'BUY', 'B. Armstrong (CEO) · 8,000 sh · $2.0M · Jun 16'], ['META', 'SELL', 'M. Zuckerberg (CEO) · 40,000 sh · $24.5M · Jun 15'], ['NVDA', 'BUY', 'J. Huang (CEO) · 12,000 sh · $1.4M · Jun 14']];
  const news = [['Reuters', 'Fed holds rates, signals two cuts later this year as inflation cools'], ['Bloomberg', 'Nvidia extends rally on sovereign-AI demand; analysts lift targets'], ['CNBC', 'Tesla robotaxi pilot expands to three new metros ahead of schedule'], ['WSJ', 'Crypto majors climb as spot-ETF inflows hit a record week'], ['Barron’s', 'Semis lead market breadth; small caps catch a bid on soft-landing hopes']];
  $('#acc-cong').innerHTML = congress.map(([t, a, m]) => {
    const cls = /purchase|buy/i.test(a) ? 'ia-b' : 'ia-s';
    return `<div class="intel-item"><span class="it">${t}</span><span class="${cls}">${a}</span><div class="im">${m}</div></div>`;
  }).join('');
  $('#acc-ins').innerHTML = insider.map(([t, a, m]) => {
    const cls = a === 'BUY' ? 'ia-b' : 'ia-s';
    return `<div class="intel-item"><span class="it">${t}</span><span class="${cls}">${a}</span><div class="im">${m}</div></div>`;
  }).join('');
  $('#acc-nws').innerHTML = news.map(([src, h]) => `<div class="ni"><div class="nt">${src}</div><a>${h}</a></div>`).join('');

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
  const movers = [['SMCI', 28.4], ['CVNA', 14.1], ['APP', 11.8], ['RBLX', 9.2], ['PYPL', -8.6], ['ENPH', -7.1], ['LULU', -6.4], ['WBA', -5.9]];
  $('#moversOut').innerHTML = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">' + movers.map(([t, c]) => {
    const cl = c >= 0 ? 'g' : 'r';
    return `<div class="stat" style="display:flex;justify-content:space-between;align-items:center;cursor:pointer">
        <span class="ptk" style="color:var(--yellow);font-size:11px">${t}</span>
        <span class="${cl}" style="font-weight:800">${c >= 0 ? '+' : ''}${c}%</span></div>`;
  }).join('') + '</div>';

  // ── AI Analysis output ──
  const setups = [{
    tk: 'NVDA',
    act: 'buy',
    conf: 8,
    px: '$118.40 · entry $116 · target $134',
    sigs: ['RSI 41', 'MACD cross', 'Insider buy', 'Rev +62% YoY'],
    rsn: 'Pullback to the 50-day with bullish insider flow and accelerating data-center revenue. Sized at 5% of book.'
  }, {
    tk: 'SOFI',
    act: 'sell',
    conf: 7,
    px: '$9.12 · stop $9.40',
    sigs: ['RSI 71', 'Below 200DMA', 'Congress sale'],
    rsn: 'Overbought into resistance with a notable Congressional sale this week.'
  }, {
    tk: 'AMD',
    act: 'hold',
    conf: 5,
    px: '$168.30',
    sigs: ['Range-bound', 'Earnings 7d'],
    rsn: 'Wait for the print before sizing in.'
  }];
  function accent(a) {
    return a === 'buy' ? 'var(--green)' : a === 'sell' ? 'var(--red)' : 'var(--yellow)';
  }
  function wash(a) {
    return a === 'buy' ? 'var(--green-wash)' : a === 'sell' ? 'var(--red-wash)' : 'var(--yellow-wash)';
  }
  function renderAnalysis() {
    $('#analysisOut').innerHTML = `<div style="font-size:8px;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin-bottom:8px">Regime: <span class="g">Risk-On</span> · VIX 13.8 · breadth positive</div>` + setups.map(s => {
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
  const qty = $('#ordQty'),
    total = $('#ordTotal'),
    submit = $('#submitOrder');
  const tkIn = $('#ordTk');
  let side = 'buy';
  const PX = 118.40;
  function refreshOrder() {
    const q = parseInt(qty.value || '0', 10);
    total.textContent = '$' + (q * PX).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    submit.textContent = `${side === 'buy' ? 'Buy' : 'Sell'} ${q} ${tkIn.value || 'NVDA'}`;
    submit.className = 'btn ' + (side === 'buy' ? 'submit-buy' : 'submit-sell');
  }
  qty.addEventListener('input', refreshOrder);
  tkIn.addEventListener('input', refreshOrder);
  $('#sideBuy').addEventListener('click', () => {
    side = 'buy';
    $('#sideBuy').classList.add('active');
    $('#sideSell').classList.remove('active');
    refreshOrder();
  });
  $('#sideSell').addEventListener('click', () => {
    side = 'sell';
    $('#sideSell').classList.add('active');
    $('#sideBuy').classList.remove('active');
    refreshOrder();
  });
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
    for (let i = 1; i < 6; i++) {
      const y = h * i / 6;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // generate deterministic-ish candles trending up
    const n = 60;
    let price = 96;
    const candles = [];
    let seed = 7;
    const rnd = () => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };
    for (let i = 0; i < n; i++) {
      const drift = 0.45;
      const open = price;
      const move = (rnd() - 0.5) * 4 + drift;
      const close = Math.max(60, open + move);
      const high = Math.max(open, close) + rnd() * 2.2;
      const low = Math.min(open, close) - rnd() * 2.2;
      candles.push({
        open,
        close,
        high,
        low
      });
      price = close;
    }
    const lo = Math.min(...candles.map(c => c.low));
    const hi = Math.max(...candles.map(c => c.high));
    const pad = 26 * devicePixelRatio;
    const yOf = p => h - pad - (p - lo) / (hi - lo) * (h - pad * 2);
    const cw = w / n;
    const bodyW = cw * 0.6;
    candles.forEach((c, i) => {
      const x = i * cw + cw / 2;
      const up = c.close >= c.open;
      const col = up ? '#00e676' : '#ff4444';
      ctx.strokeStyle = col;
      ctx.fillStyle = col;
      ctx.lineWidth = 1 * devicePixelRatio;
      ctx.beginPath();
      ctx.moveTo(x, yOf(c.high));
      ctx.lineTo(x, yOf(c.low));
      ctx.stroke();
      const yO = yOf(c.open),
        yC = yOf(c.close);
      const top = Math.min(yO, yC),
        bh = Math.max(2, Math.abs(yC - yO));
      ctx.fillRect(x - bodyW / 2, top, bodyW, bh);
    });

    // last price line
    const lastY = yOf(candles[n - 1].close);
    ctx.strokeStyle = 'rgba(0,230,118,0.5)';
    ctx.setLineDash([4 * devicePixelRatio, 4 * devicePixelRatio]);
    ctx.beginPath();
    ctx.moveTo(0, lastY);
    ctx.lineTo(w, lastY);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  drawCandles();
  window.addEventListener('resize', drawCandles);
  // redraw when chart tab becomes active (canvas sized 0 while hidden)
  new ResizeObserver(drawCandles).observe(cv.parentElement);
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/dashboard/dashboard.js", error: String((e && e.message) || e) }); }

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.IntelRow = __ds_scope.IntelRow;

__ds_ns.Stat = __ds_scope.Stat;

__ds_ns.TickerTag = __ds_scope.TickerTag;

__ds_ns.TradeCard = __ds_scope.TradeCard;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Toggle = __ds_scope.Toggle;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
