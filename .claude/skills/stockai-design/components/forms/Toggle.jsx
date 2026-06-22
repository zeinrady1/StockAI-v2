import React from 'react';

/**
 * StockAI Toggle — the pill switch. Off = grey track; on = amber track
 * (used for Auto-Pilot / Auto-execute). Knob slides on toggle.
 */
export function Toggle({ checked = false, onChange, style, ...rest }) {
  return (
    <span
      role="switch"
      aria-checked={checked}
      onClick={() => onChange && onChange(!checked)}
      style={{
        width: 'var(--tog-w)',
        height: 'var(--tog-h)',
        borderRadius: '9px',
        background: checked ? 'var(--yellow)' : 'var(--border2)',
        cursor: 'pointer',
        position: 'relative',
        transition: 'background 0.2s',
        flexShrink: 0,
        display: 'inline-block',
        ...style,
      }}
      {...rest}
    >
      <span
        style={{
          content: '""',
          position: 'absolute',
          width: '13px',
          height: '13px',
          borderRadius: '50%',
          background: '#fff',
          top: '2px',
          left: checked ? '17px' : '2px',
          transition: 'left 0.2s',
        }}
      />
    </span>
  );
}
