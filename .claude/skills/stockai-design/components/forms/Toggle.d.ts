import React from 'react';

export interface ToggleProps extends Omit<React.HTMLAttributes<HTMLSpanElement>, 'onChange'> {
  /** On/off state. @default false */
  checked?: boolean;
  /** Called with the next boolean state. */
  onChange?: (next: boolean) => void;
}

/**
 * Pill switch. Off track is grey, on track is amber — the toggle used for
 * Auto-Pilot and per-run auto-execute.
 */
export function Toggle(props: ToggleProps): JSX.Element;
