import React from 'react';

/**
 * StockAI Badge — small pill/chip. Two shapes:
 *  - chip (default): squared 4px-radius tag (Paper, Opus 4.8, signal chips)
 *  - pill: rounded 20px outlook pill (BULLISH / BEARISH / NEUTRAL)
 * Tones map to semantic colors and render a translucent wash + matching border.
 */
export function Badge({ tone = 'green', shape = 'chip', children, style, ...rest }) {
  const tones = {
    green:  { color: 'var(--green)',  bg: 'var(--green-wash)',  bd: 'var(--green-line)' },
    red:    { color: 'var(--red)',    bg: 'var(--red-wash)',    bd: 'var(--red-line)' },
    yellow: { color: 'var(--yellow)', bg: 'var(--yellow-wash)', bd: 'rgba(251,191,36,0.25)' },
    blue:   { color: 'var(--blue)',   bg: 'var(--blue-wash)',   bd: 'var(--blue-line)' },
    purple: { color: 'var(--purple)', bg: 'var(--purple-wash)', bd: 'var(--purple-line)' },
    muted:  { color: 'var(--muted)',  bg: 'rgba(139,152,174,0.12)', bd: 'rgba(139,152,174,0.2)' },
  };
  const t = tones[tone] || tones.green;
  const isPill = shape === 'pill';
  return (
    <span
      style={{
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
        ...style,
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
