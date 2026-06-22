import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual intent. @default 'primary' */
  variant?: 'primary' | 'secondary' | 'buy' | 'sell';
  /** Sizing. 'md' is the standard block button; 'inline' for toolbar; 'sm' for ghost. @default 'md' */
  size?: 'sm' | 'md' | 'inline';
  /** Stretch to full width. @default false */
  full?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
}

/**
 * Primary action button. Green fill with black text for the loudest action;
 * ghost outline for supporting actions; buy/sell keyed to market semantics.
 * @startingPoint section="Core" subtitle="Primary, ghost, buy/sell buttons" viewport="700x120"
 */
export function Button(props: ButtonProps): JSX.Element;
