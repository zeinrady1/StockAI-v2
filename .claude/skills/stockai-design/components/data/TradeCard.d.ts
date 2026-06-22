import React from 'react';

export interface TradeCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Symbol the recommendation is for. */
  ticker: string;
  /** Recommended action — sets the left-accent color and tag. @default 'hold' */
  action?: 'buy' | 'sell' | 'hold' | 'watch';
  /** Confidence score out of 10. */
  confidence?: number;
  /** Price / entry line, e.g. "$118.40 · entry $116". */
  price?: React.ReactNode;
  /** Signal chips (technical / fundamental tags). */
  signals?: string[];
  /** AI rationale text. */
  rationale?: React.ReactNode;
  /** If provided (and action is buy/sell), renders an execute button. */
  onExecute?: React.MouseEventHandler;
}

/**
 * AI recommendation card from the Analysis tab: action-keyed left accent,
 * confidence, signal chips, rationale, and an execute button.
 * @startingPoint section="Data" subtitle="AI trade recommendation card" viewport="700x220"
 */
export function TradeCard(props: TradeCardProps): JSX.Element;
