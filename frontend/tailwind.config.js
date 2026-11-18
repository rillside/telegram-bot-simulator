/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tg: {
          bg: "#0f172a",          // main dark background
          sidebar: "#1e293b",     // sidebar slate
          hover: "#334155",       // hover items
          active: "#2563eb",      // active chat
          bubbleIn: "#1e293b",    // incoming message (bot)
          bubbleOut: "#2563eb",   // outgoing message (user)
          text: "#f8fafc",        // primary text
          textMuted: "#94a3b8",   // muted text
          accent: "#38bdf8",      // accent cyan/blue
          border: "#334155"       // border line
        }
      }
    },
  },
  plugins: [],
}
