import React from 'react';

/**
 * StockAI TickerTag — a stock symbol rendered in the signature amber-black
 * weight, optionally followed by a buy/sell action label. Click to pull up
 * the chart in the real app.
 */
export function TickerTag({ symbol, action, size = 'md', onClick, style, ...rest }) {
  const fs = size === 'lg' ? 'var(--fs-lg)' : size === 'sm' ? 'var(--fs-base)' : 'var(--fs-value)';
  const isBuy = action && /buy|purchase|long/i.test(action);
  return (
    <span style={{ display: 'inline-flex', alignItems: 'baseline', gap: '4px', ...style }} {...rest}>
      <span
        onClick={onClick}
        style={{
          fontWeight: 'var(--fw-black)',
          fontSize: fs,
          color: 'var(--yellow)',
          cursor: onClick ? 'pointer' : 'inherit',
        }}
      >
        {symbol}
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
    </span>
  );
}
