import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "#f9f9ff",
        "surface-dim": "#d3daea",
        "surface-bright": "#f9f9ff",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f0f3ff",
        "surface-container": "#e7eefe",
        "surface-container-high": "#e2e8f8",
        "surface-container-highest": "#dce2f3",
        "on-surface": "#151c27",
        "on-surface-variant": "#3c4a42",
        "inverse-surface": "#2a313d",
        "inverse-on-surface": "#ebf1ff",
        outline: "#6c7a71",
        "outline-variant": "#bbcabf",
        "surface-tint": "#006c49",
        primary: "#006c49",
        "on-primary": "#ffffff",
        "primary-container": "#10b981",
        "on-primary-container": "#00422b",
        "inverse-primary": "#4edea3",
        secondary: "#2b6954",
        "on-secondary": "#ffffff",
        "secondary-container": "#adedd3",
        "on-secondary-container": "#306d58",
        tertiary: "#a43a3a",
        "on-tertiary": "#ffffff",
        "tertiary-container": "#fc7c78",
        "on-tertiary-container": "#711419",
        error: "#ba1a1a",
        "on-error": "#ffffff",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
        "primary-fixed": "#6ffbbe",
        "primary-fixed-dim": "#4edea3",
        background: "#f9f9ff",
        "on-background": "#151c27",
        "surface-variant": "#dce2f3",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        full: "9999px",
      },
      spacing: {
        "margin-mobile": "16px",
        xs: "4px",
        sm: "8px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        "2xl": "48px",
        "3xl": "64px",
        "container-max": "1280px",
        gutter: "24px",
      },
      maxWidth: {
        "container-max": "1280px",
      },
      fontSize: {
        "headline-lg-mobile": [
          "24px",
          { lineHeight: "32px", fontWeight: "600" },
        ],
        "headline-lg": [
          "32px",
          { lineHeight: "40px", letterSpacing: "-0.01em", fontWeight: "600" },
        ],
        "title-md": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-md": [
          "12px",
          { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "600" },
        ],
      },
      boxShadow: {
        card: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.03)",
        "card-hover":
          "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
