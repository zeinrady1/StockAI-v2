import React from 'react';

/**
 * StockAI TradeCard — an AI recommendation block from the Analysis tab.
 * Left-accent bar keyed to the action (green buy / red sell / amber hold),
 * a header row with ticker + action tag + confidence, optional signal chips,
 * a rationale line, and an execute button.
 */
export function TradeCard({
  ticker, action = 'hold', confidence, price, signals = [], rationale, onExecute, style, ...rest
}) {
  const al = String(action).toLowerCase();
  const accent = al === 'buy' ? 'var(--green)' : al === 'sell' ? 'var(--red)' : 'var(--yellow)';
  const tagBg = al === 'buy' ? 'var(--green-wash)' : al === 'sell' ? 'var(--red-wash)' : 'var(--yellow-wash)';

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderLeft: `3px solid ${accent}`,
        borderRadius: 'var(--r-md)',
        padding: '9px',
        marginBottom: '6px',
        ...style,
      }}
      {...rest}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <span style={{ fontSize: 'var(--fs-lg)', fontWeight: 'var(--fw-black)' }}>{ticker}</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {confidence != null && (
            <span style={{ fontSize: 'var(--fs-tiny)', color: 'var(--dim)' }}>
              conf <b style={{ color: accent }}>{confidence}/10</b>
            </span>
          )}
          <span
            style={{
              padding: '2px 7px',
              borderRadius: 'var(--r-xs)',
              fontSize: 'var(--fs-tiny)',
              fontWeight: 'var(--fw-black)',
              textTransform: 'uppercase',
              background: tagBg,
              color: accent,
            }}
          >
            {al}
          </span>
        </span>
      </div>

      {price != null && (
        <div style={{ fontSize: 'var(--fs-small)', color: 'var(--muted)' }}>{price}</div>
      )}

      {signals.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '3px', marginTop: '4px' }}>
          {signals.map((s, i) => (
            <span
              key={i}
              style={{
                background: 'var(--blue-wash)',
                color: 'var(--blue)',
                border: '1px solid var(--blue-line)',
                padding: '1px 5px',
                borderRadius: 'var(--r-xs)',
                fontSize: 'var(--fs-label)',
              }}
            >
              {s}
            </span>
          ))}
        </div>
      )}

      {rationale && (
        <div style={{ fontSize: 'var(--fs-tiny)', color: 'var(--muted)', marginTop: '5px', lineHeight: 'var(--lh-body)' }}>
          {rationale}
        </div>
      )}

      {onExecute && al !== 'hold' && al !== 'watch' && (
        <button
          onClick={onExecute}
          style={{
            marginTop: '6px',
            padding: '4px 10px',
            borderRadius: 'var(--r-sm)',
            border: 'none',
            cursor: 'pointer',
            fontSize: 'var(--fs-tiny)',
            fontWeight: 'var(--fw-bold)',
            fontFamily: 'var(--font-mono)',
            background: accent,
            color: al === 'sell' ? '#fff' : '#000',
          }}
        >
          {al === 'buy' ? 'Execute Buy' : 'Close Position'}
        </button>
      )}
    </div>
  );
}
