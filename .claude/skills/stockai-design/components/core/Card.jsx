import React from 'react';

/**
 * StockAI Card — the raised panel surface. Optional uppercase title row
 * (card-t) with an optional right-aligned accessory (badge, count, dot).
 */
export function Card({ title, accessory, children, style, bodyStyle, ...rest }) {
  return (
    <div
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--r-xl)',
        padding: '10px',
        ...style,
      }}
      {...rest}
    >
      {title != null && (
        <div
          style={{
            fontSize: 'var(--fs-label)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--ls-wide)',
            color: 'var(--dim)',
            marginBottom: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{title}</span>
          {accessory != null && <span>{accessory}</span>}
        </div>
      )}
      <div style={bodyStyle}>{children}</div>
    </div>
  );
}
