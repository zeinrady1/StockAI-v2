import React from 'react';

/**
 * StockAI Input — the dark search/text field. Optional leading icon (used for
 * the global search glass). Focus brightens the border to green.
 */
export function Input({ icon, style, wrapStyle, ...rest }) {
  return (
    <div style={{ position: 'relative', ...wrapStyle }}>
      {icon && (
        <span
          style={{
            position: 'absolute',
            left: '9px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--dim)',
            pointerEvents: 'none',
            fontSize: 'var(--fs-base)',
          }}
        >
          {icon}
        </span>
      )}
      <input
        style={{
          width: '100%',
          background: 'var(--field)',
          border: '1px solid var(--border2)',
          color: 'var(--text)',
          padding: icon ? '6px 12px 6px 30px' : '6px 12px',
          borderRadius: 'var(--r-xl)',
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--fs-value)',
          outline: 'none',
          ...style,
        }}
        onFocus={(e) => { e.target.style.borderColor = 'var(--green)'; }}
        onBlur={(e) => { e.target.style.borderColor = 'var(--border2)'; }}
        {...rest}
      />
    </div>
  );
}
