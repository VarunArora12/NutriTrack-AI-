/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        page: "#f8faf8",
        ink: "#18212f",
        mint: "#2fbf71",
        coral: "#ff6b5f",
        skyglass: "#eaf7ff",
      },
      boxShadow: {
        soft: "0 18px 60px rgba(24, 33, 47, 0.12)",
      },
    },
  },
  plugins: [],
};
