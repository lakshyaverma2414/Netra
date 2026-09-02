
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
          "secondary-fixed": "#ffdcc2",
          "on-secondary-fixed-variant": "#6d3a00",
          "on-secondary-container": "#683700",
          "surface": "#f7f9fb",
          "surface-tint": "#4a5f85",
          "primary-fixed-dim": "#b1c7f3",
          "on-primary-fixed": "#011b3e",
          "inverse-on-surface": "#eff1f3",
          "background": "#f7f9fb",
          "outline-variant": "#c4c6cf",
          "on-surface": "#191c1e",
          "on-tertiary-fixed": "#012200",
          "on-error-container": "#93000a",
          "tertiary": "#001400",
          "on-primary-fixed-variant": "#32476c",
          "on-tertiary-container": "#34a025",
          "error-container": "#ffdad6",
          "surface-variant": "#e0e3e5",
          "primary": "#000f27",
          "error": "#ba1a1a",
          "secondary-fixed-dim": "#ffb77a",
          "saffron-accent": "#FF9933",
          "on-primary": "#ffffff",
          "on-primary-container": "#778cb5",
          "secondary": "#8f4e00",
          "tertiary-fixed": "#8dfc75",
          "surface-container-highest": "#e0e3e5",
          "surface-container-high": "#e6e8ea",
          "primary-container": "#0b2447",
          "inverse-primary": "#b1c7f3",
          "on-secondary": "#ffffff",
          "india-green": "#138808",
          "surface-container-low": "#f2f4f6",
          "inverse-surface": "#2d3133",
          "surface-container": "#eceef0",
          "surface-container-lowest": "#ffffff",
          "deep-navy": "#0B2447",
          "tertiary-container": "#012c00",
          "on-secondary-fixed": "#2e1500",
          "primary-fixed": "#d6e3ff",
          "tertiary-fixed-dim": "#72de5c",
          "secondary-container": "#fe9832",
          "charcoal": "#1A1A1A",
          "on-surface-variant": "#44474e",
          "surface-dim": "#d8dadc",
          "ash-gray": "#475569",
          "on-background": "#191c1e",
          "outline": "#74777f",
          "on-error": "#ffffff",
          "on-tertiary": "#ffffff",
          "on-tertiary-fixed-variant": "#035300",
          "surface-bright": "#f7f9fb"
      },
      borderRadius: {
          "DEFAULT": "0.125rem",
          "lg": "0.25rem",
          "xl": "0.5rem",
          "full": "0.75rem"
      },
      spacing: {
          "stack-lg": "32px",
          "margin-mobile": "16px",
          "container-max": "1280px",
          "base": "8px",
          "margin-desktop": "32px",
          "stack-sm": "8px",
          "stack-md": "16px",
          "gutter": "24px"
      },
      fontFamily: {
          "body-md": ["Inter"],
          "headline-lg-mobile": ["Montserrat"],
          "display-lg": ["Montserrat"],
          "headline-md": ["Montserrat"],
          "headline-lg": ["Montserrat"],
          "label-sm": ["Inter"],
          "body-lg": ["Inter"],
          "label-md": ["Inter"],
          "title-lg": ["Inter"]
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
