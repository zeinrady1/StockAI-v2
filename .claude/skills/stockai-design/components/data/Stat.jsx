import React from 'react';

/**
 * StockAI Stat — an inset well showing a micro-label over a bold value.
 * The building block of the portfolio grid. `tone` colors the value for
 * gains/losses/neutral.
 */
export function Stat({ label, value, tone, style, ...rest }) {
  const toneColor = {
    green: 'var(--green)',
    red: 'var(--red)',
    yellow: 'var(--yellow)',
  }[tone];
  return (
    <div
      style={{
        background: 'var(--well)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--r-sm)',
        padding: '6px 8px',
        minWidth: 0,
        ...style,
      }}
      {...rest}
    >
      <div
        style={{
          fontSize: 'var(--fs-micro)',
          color: 'var(--dim)',
          marginBottom: '2px',
          textTransform: 'uppercase',
          letterSpacing: 'var(--ls-label)',
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 'var(--fs-value)',
          fontWeight: 'var(--fw-black)',
          color: toneColor || 'var(--text)',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {value}
      </div>
    </div>
  );
}
