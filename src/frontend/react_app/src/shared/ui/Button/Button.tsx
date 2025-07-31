import type { ButtonHTMLAttributes, FC } from 'react';

export const Button: FC<ButtonHTMLAttributes<HTMLButtonElement>> = ({ children, ...props }) => (
  <button
    type="button"
    className="refresh-btn px-4 py-2 rounded-lg border border-primary bg-surface hover:bg-surface-hover text-primary font-semibold transition-all shadow-md"
    {...props}
  >
    {children}
  </button>
);
