import React from 'react';

export interface IntelRowProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Bold amber ticker symbol. */
  ticker: string;
  /** Action label — green for buy/purchase, red otherwise. */
  action?: string;
  /** Dim meta line beneath (trader, role, size, date). */
  meta?: React.ReactNode;
  onClick?: React.MouseEventHandler;
}

/**
 * One row of the Congress / Insider / News intel feeds: amber ticker + colored
 * action over a dim meta line. Hover highlights and bleeds into the gutter.
 */
export function IntelRow(props: IntelRowProps): JSX.Element;
