export default {content: [
  './index.html',
  './src/**/*.{js,ts,jsx,tsx}'
],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: {
          light: "#f7f8fa",
          dark: "#1e1f24"
        },
        border: {
          light: "#e1e3e8",
          dark: "#2b2d33"
        },
        accent: "#4f79ff",
        success: "#37b24d",
        danger: "#f03e3e"
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"]
      },
      borderRadius: {
        sm: "4px",
        DEFAULT: "8px"
      },
      spacing: {
        card: "24px"
      }
    }
  }
}