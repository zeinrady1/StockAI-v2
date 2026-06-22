import React from 'react';

/**
 * StockAI Tabs — the horizontal tab strip used across panels (Chart / AI
 * Analysis / Market / Movers / All Stocks). Active tab is green with a green
 * underline; the strip sits on a raised surface and scrolls horizontally.
 */
export function Tabs({ tabs = [], active, onChange, style, ...rest }) {
  return (
    <div
      style={{
        display: 'flex',
        borderBottom: '1px solid var(--border)',
        background: 'var(--surface)',
        overflowX: 'auto',
        ...style,
      }}
      {...rest}
    >
      {tabs.map((t) => {
        const id = typeof t === 'string' ? t : t.id;
        const label = typeof t === 'string' ? t : t.label;
        const isActive = id === active;
        return (
          <div
            key={id}
            onClick={() => onChange && onChange(id)}
            style={{
              flexShrink: 0,
              padding: '7px 10px',
              fontSize: 'var(--fs-tiny)',
              cursor: 'pointer',
              color: isActive ? 'var(--green)' : 'var(--dim)',
              borderBottom: `2px solid ${isActive ? 'var(--green)' : 'transparent'}`,
              transition: 'all 0.1s',
              textTransform: 'uppercase',
              letterSpacing: 'var(--ls-label)',
              whiteSpace: 'nowrap',
            }}
          >
            {label}
          </div>
        );
      })}
    </div>
  );
}
