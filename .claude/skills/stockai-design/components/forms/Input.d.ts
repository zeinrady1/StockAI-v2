import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Leading icon node (e.g. a search glyph) rendered inside the field. */
  icon?: React.ReactNode;
  /** Style for the positioning wrapper. */
  wrapStyle?: React.CSSProperties;
}

/**
 * Dark text/search field. Border brightens to green on focus. Pass `icon`
 * for the leading search glyph.
 */
export function Input(props: InputProps): JSX.Element;
