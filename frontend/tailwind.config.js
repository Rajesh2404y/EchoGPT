export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        ink: "#08090f",
        panel: "rgba(19, 23, 34, 0.74)",
        line: "rgba(255, 255, 255, 0.1)",
        mint: "#40d6a3",
        coral: "#ff8066",
        amber: "#f8c14a",
        sky: "#62b7ff",
      },
      boxShadow: {
        glow: "0 18px 60px rgba(64, 214, 163, 0.14)",
      },
    },
  },
  plugins: [],
};
