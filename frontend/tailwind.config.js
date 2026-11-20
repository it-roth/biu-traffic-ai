/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(240 3.7% 15.9%)",
        input: "hsl(240 3.7% 15.9%)",
        ring: "#006CB8",
        background: "hsl(240 10% 3.9%)",
        foreground: "hsl(0 0% 98%)",
        // Official BIU Brand Blue: #006CB8
        primary: {
          50: '#f0f7fc',
          100: '#e0eff9',
          200: '#b8daf2',
          300: '#7bbfea',
          400: '#38a0de',
          500: '#006CB8',
          DEFAULT: '#006CB8',
          600: '#005b9e',
          700: '#00497f',
          800: '#003e6b',
          900: '#063458',
          foreground: '#ffffff',
        },
        biu: {
          blue: '#006CB8',
          darkBlue: '#00497f',
          lightBlue: '#38a0de',
          gold: '#f59e0b',
        },
        secondary: {
          DEFAULT: "hsl(240 3.7% 15.9%)",
          foreground: "hsl(0 0% 98%)",
        },
        destructive: {
          DEFAULT: "hsl(0 62.8% 30.6%)",
          foreground: "hsl(0 0% 98%)",
        },
        muted: {
          DEFAULT: "hsl(240 3.7% 15.9%)",
          foreground: "hsl(240 5% 64.9%)",
        },
        accent: {
          DEFAULT: "#006CB8",
          foreground: "#ffffff",
        },
        card: {
          DEFAULT: "hsl(240 10% 4.9%)",
          foreground: "hsl(0 0% 98%)",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "calc(0.5rem - 2px)",
        sm: "calc(0.5rem - 4px)",
      },
    },
  },
  plugins: [],
}
