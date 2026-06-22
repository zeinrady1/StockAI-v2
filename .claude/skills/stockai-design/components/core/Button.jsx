import React from 'react';

/**
 * StockAI Button — monospace, dense, with semantic variants.
 * Primary (green, black text) = the main action (Run AI Analysis, Go, Buy).
 * Secondary (ghost outline) = supporting actions (Refresh Intel).
 * buy/sell = execution buttons keyed to market colors.
 */
export function Button({
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
    whiteSpace: 'nowrap',
  };

  const sizes = {
    sm: { padding: '4px 10px', fontSize: 'var(--fs-tiny)', borderRadius: 'var(--r-md)' },
    md: { padding: '9px', fontSize: 'var(--fs-value)', borderRadius: 'var(--r-lg)' },
    inline: { padding: '5px 12px', fontSize: 'var(--fs-base)', borderRadius: 'var(--r-md)' },
  };

  const variants = {
    primary: { background: 'var(--green)', color: '#000' },
    secondary: { background: 'transparent', border: '1px solid var(--border2)', color: 'var(--muted)' },
    buy: { background: 'var(--green)', color: '#000' },
    sell: { background: 'var(--red)', color: '#fff' },
  };

  const disabledStyle = disabled
    ? { background: 'var(--border2)', color: 'var(--dim)', boxShadow: 'none' }
    : {};

  return (
    <button
      disabled={disabled}
      style={{ ...base, ...sizes[size], ...variants[variant], ...disabledStyle, ...style }}
      {...rest}
    >
      {children}
    </button>
  );
}
