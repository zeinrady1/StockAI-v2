import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Uppercase eyebrow title shown in the card-t row. Omit for a plain panel. */
  title?: React.ReactNode;
  /** Right-aligned accessory in the title row (Badge, count text, status dot). */
  accessory?: React.ReactNode;
  children?: React.ReactNode;
  bodyStyle?: React.CSSProperties;
}

/**
 * Raised dark panel with an optional uppercase title row. The fundamental
 * container for every block in the dashboard.
 */
export function Card(props: CardProps): JSX.Element;
