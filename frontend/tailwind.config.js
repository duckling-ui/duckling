/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
          950: '#042f2e',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        }
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 2s linear infinite',
        'bounce-subtle': 'bounce 2s ease-in-out infinite',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(20, 184, 166, 0.3)',
        'glow-lg': '0 0 40px rgba(20, 184, 166, 0.4)',
      },
      typography: ({ theme }) => ({
        invert: {
          css: {
            '--tw-prose-body': theme('colors.gray[300]'),
            '--tw-prose-headings': theme('colors.gray[100]'),
            '--tw-prose-lead': theme('colors.gray[300]'),
            '--tw-prose-links': theme('colors.primary[400]'),
            '--tw-prose-bold': theme('colors.gray[200]'),
            '--tw-prose-counters': theme('colors.primary[500]'),
            '--tw-prose-bullets': theme('colors.primary[500]'),
            '--tw-prose-hr': theme('colors.dark[700]'),
            '--tw-prose-quotes': theme('colors.gray[400]'),
            '--tw-prose-quote-borders': theme('colors.primary[500]'),
            '--tw-prose-captions': theme('colors.gray[400]'),
            '--tw-prose-code': theme('colors.primary[300]'),
            '--tw-prose-pre-code': theme('colors.gray[300]'),
            '--tw-prose-pre-bg': theme('colors.dark[950]'),
            '--tw-prose-th-borders': theme('colors.dark[600]'),
            '--tw-prose-td-borders': theme('colors.dark[700]'),
            // Custom overrides
            'h1': {
              borderBottom: `2px solid ${theme('colors.primary[500]')}`,
              paddingBottom: '0.75rem',
              marginBottom: '1.5rem',
            },
            'h2': {
              borderBottom: `1px solid ${theme('colors.dark[700]')}`,
              paddingBottom: '0.5rem',
              marginTop: '2.5rem',
            },
            'a': {
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            },
            'code': {
              backgroundColor: theme('colors.dark[800]'),
              padding: '0.125rem 0.375rem',
              borderRadius: '0.25rem',
              fontWeight: '400',
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            'pre': {
              border: `1px solid ${theme('colors.dark[700]')}`,
              borderRadius: '0.5rem',
            },
            'pre code': {
              backgroundColor: 'transparent',
              padding: '0',
            },
            'blockquote': {
              backgroundColor: theme('colors.dark[800]/50'),
              borderRadius: '0 0.5rem 0.5rem 0',
              padding: '0.5rem 1rem',
              fontStyle: 'normal',
            },
            'thead': {
              backgroundColor: theme('colors.dark[800]'),
            },
            'th': {
              padding: '0.75rem 1rem',
            },
            'td': {
              padding: '0.75rem 1rem',
            },
            'tbody tr:nth-child(even)': {
              backgroundColor: theme('colors.dark[800]/50'),
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
