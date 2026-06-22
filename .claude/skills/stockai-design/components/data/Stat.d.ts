import React from 'react';

export interface StatProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Uppercase micro-label above the value. */
  label: React.ReactNode;
  /** The figure — a number, price, or percentage string. */
  value: React.ReactNode;
  /** Color the value for gains/losses/neutral. Omit for default text. */
  tone?: 'green' | 'red' | 'yellow';
}

/**
 * Inset stat well: tiny uppercase label over a bold value. Tile these in a
 * 2-up grid to build the portfolio / account readout.
 */
export function Stat(props: StatProps): JSX.Element;
