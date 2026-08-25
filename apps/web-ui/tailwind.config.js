/** @type {import('tailwindcss').Config} */

// The gray scale is driven by CSS variables so the whole UI can be re-themed
// (dark ↔ light) by toggling a class on <html>. Values are space-separated RGB
// triplets; `<alpha-value>` keeps Tailwind's opacity modifiers working.
const gray = {
  50: "rgb(var(--g-50) / <alpha-value>)",
  100: "rgb(var(--g-100) / <alpha-value>)",
  200: "rgb(var(--g-200) / <alpha-value>)",
  300: "rgb(var(--g-300) / <alpha-value>)",
  400: "rgb(var(--g-400) / <alpha-value>)",
  500: "rgb(var(--g-500) / <alpha-value>)",
  600: "rgb(var(--g-600) / <alpha-value>)",
  700: "rgb(var(--g-700) / <alpha-value>)",
  750: "rgb(var(--g-750) / <alpha-value>)",
  800: "rgb(var(--g-800) / <alpha-value>)",
  850: "rgb(var(--g-850) / <alpha-value>)",
  900: "rgb(var(--g-900) / <alpha-value>)",
  950: "rgb(var(--g-950) / <alpha-value>)",
};

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gray,
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(99, 102, 241, 0.35), 0 8px 28px -8px rgba(99, 102, 241, 0.45)",
      },
      animation: {
        "fade-in": "fadeIn 280ms ease-out both",
        "slide-up": "slideUp 320ms ease-out both",
        "toast-in": "toastIn 240ms cubic-bezier(0.21, 1.02, 0.73, 1) both",
      },
    },
  },
  plugins: [],
};
