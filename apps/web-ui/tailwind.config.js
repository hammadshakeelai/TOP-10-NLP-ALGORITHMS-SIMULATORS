/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gray: {
          750: "#2d3340",
          850: "#181d27",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(99, 102, 241, 0.35), 0 8px 28px -8px rgba(99, 102, 241, 0.45)",
      },
      animation: {
        "fade-in": "fadeIn 280ms ease-out both",
        "slide-up": "slideUp 320ms ease-out both",
      },
    },
  },
  plugins: [],
};
