import React from 'react';

export interface TickerTagProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Stock/crypto symbol, e.g. "NVDA" or "BTC-USD". */
  symbol: string;
  /** Optional action label after the symbol — colored green for buy, red for sell. */
  action?: string;
  /** @default 'md' */
  size?: 'sm' | 'md' | 'lg';
  onClick?: React.MouseEventHandler;
}

/**
 * A stock symbol in the signature amber/black-weight treatment, optionally
 * with a buy/sell action label. The clickable anchor used throughout intel rows.
 */
export function TickerTag(props: TickerTagProps): JSX.Element;
