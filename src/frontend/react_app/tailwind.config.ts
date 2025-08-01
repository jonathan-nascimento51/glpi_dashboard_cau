import type { Config } from 'tailwindcss'

export const theme = {
  extend: {
    colors: {
      primary: 'var(--primary)',
      'primary-light': 'var(--primary-light)',
      secondary: 'var(--secondary)',
      'accent-green': 'var(--accent-green)',
      'accent-amber': 'var(--accent-amber)',
      'accent-red': 'var(--accent-red)',
      'accent-purple': 'var(--accent-purple)',
      'accent-cyan': 'var(--accent-cyan)',
      surface: 'var(--surface)',
      'surface-secondary': 'var(--surface-secondary)',
      'surface-tertiary': 'var(--surface-tertiary)',
      'surface-hover': 'var(--surface-hover)',
      border: 'var(--border)',
      'border-light': 'var(--border-light)',
      'text-primary': 'var(--text-primary)',
      'text-secondary': 'var(--text-secondary)',
      'text-muted': 'var(--text-muted)'
    },
    spacing: {
      xs: 'var(--spacing-xs)',
      sm: 'var(--spacing-sm)',
      md: 'var(--spacing-md)',
      lg: 'var(--spacing-lg)',
      xl: 'var(--spacing-xl)'
    },
    borderRadius: {
      '2xl': '1rem'
    },
    boxShadow: {
      xs: 'var(--shadow-xs)',
      sm: 'var(--shadow-sm)',
      md: 'var(--shadow-md)',
      lg: 'var(--shadow-lg)',
      xl: 'var(--shadow-xl)'
    },
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px'
    }
  }
}

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx,css}'],
  theme,
  plugins: []
}

export default config
