/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'theme-bg': 'var(--bg)',
        'theme-card': 'var(--card)',
        'theme-text': 'var(--text)',
        'theme-muted': 'var(--muted)',
        'theme-primary': 'var(--primary)',
        'theme-primary-dark': 'var(--primary-dark)',
      },
    },
  },
  plugins: [],
}

