import React from 'react';

export interface TabItem {
  id: string;
  label: React.ReactNode;
}

export interface TabsProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  /** Tab list — strings (id === label) or {id, label} objects. */
  tabs: (string | TabItem)[];
  /** Currently-active tab id. */
  active: string;
  /** Fired with the clicked tab id. */
  onChange?: (id: string) => void;
}

/**
 * Horizontal uppercase tab strip on a raised surface. Active tab is green with
 * a green underline; overflow scrolls horizontally.
 * @startingPoint section="Navigation" subtitle="Panel tab strip" viewport="700x80"
 */
export function Tabs(props: TabsProps): JSX.Element;
