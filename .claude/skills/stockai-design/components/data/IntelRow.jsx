import React from 'react';

/**
 * StockAI IntelRow — a single row in the Congress / Insider / News feeds.
 * A bold amber ticker + colored action tag, with a dim meta line beneath.
 * Whole row is hover-highlightable and clickable (opens the chart).
 */
export function IntelRow({ ticker, action, meta, onClick, style, ...rest }) {
  const isBuy = action && /buy|purchase|long/i.test(action);
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        padding: hover ? '5px 4px' : '5px 0',
        margin: hover ? '0 -4px' : 0,
        borderBottom: '1px solid var(--border)',
        cursor: onClick ? 'pointer' : 'default',
        background: hover ? 'var(--green-hover)' : 'transparent',
        ...style,
      }}
      {...rest}
    >
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <span style={{ fontWeight: 'var(--fw-black)', color: 'var(--yellow)', fontSize: 'var(--fs-value)' }}>
          {ticker}
        </span>
        {action && (
          <span
            style={{
              fontSize: 'var(--fs-tiny)',
              fontWeight: 'var(--fw-bold)',
              color: isBuy ? 'var(--green)' : 'var(--red)',
            }}
          >
            {action}
          </span>
        )}
      </div>
      {meta && (
        <div
          style={{
            color: 'var(--dim)',
            fontSize: 'var(--fs-tiny)',
            marginTop: '1px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {meta}
        </div>
      )}
    </div>
  );
}
