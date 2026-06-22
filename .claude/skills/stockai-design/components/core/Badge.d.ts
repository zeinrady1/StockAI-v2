import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Semantic color. @default 'green' */
  tone?: 'green' | 'red' | 'yellow' | 'blue' | 'purple' | 'muted';
  /** 'chip' = squared tag (Paper, model name); 'pill' = rounded outlook pill. @default 'chip' */
  shape?: 'chip' | 'pill';
  children?: React.ReactNode;
}

/**
 * Small translucent-wash badge. Chip shape for status tags; pill shape for
 * BULLISH/BEARISH/NEUTRAL outlook labels.
 * @startingPoint section="Core" subtitle="Status chips & outlook pills" viewport="700x100"
 */
export function Badge(props: BadgeProps): JSX.Element;
