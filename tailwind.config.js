// tailwind.config.js
module.exports = {
    content: [
      './templates/**/*.html',
      './templates/**/*.django',
      './media_app/**/*.py',
      './static/**/*.js',
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            light: '#6366f1',
            DEFAULT: '#4f46e5',
            dark: '#4338ca',
          },
          secondary: {
            light: '#94a3b8',
            DEFAULT: '#64748b',
            dark: '#475569',
          },
        },
      },
    },
    plugins: [
      require('@tailwindcss/forms'),
    ],
    // Отключаем неиспользуемые стили для уменьшения размера CSS
    purge: {
      enabled: true,
      content: [
        './templates/**/*.html',
        './templates/**/*.django',
        './media_app/**/*.py',
        './static/**/*.js',
      ],
    },
  }