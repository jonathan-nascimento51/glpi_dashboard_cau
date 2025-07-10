import type { ButtonHTMLAttributes, FC } from 'react';

export const Button: FC<ButtonHTMLAttributes<HTMLButtonElement>> = ({ children, ...props }) => (
  <button type="button" {...props}>
    {children}
  </button>
);
