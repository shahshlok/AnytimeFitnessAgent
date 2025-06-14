/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
  	extend: {
  		fontFamily: {
  			sans: [
  				'Inter',
  				'sans-serif'
  			]
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
        // --- ADD THESE KEYFRAMES AND ANIMATIONS ---
        keyframes: {
          heartbeat: {
            '0%, 100%': { transform: 'scale(1)', opacity: '1' },
            '50%': { transform: 'scale(1.05)', opacity: '0.9' },
          },
          vibrate: {
            '0%, 100%': { transform: 'translate(0, 0)' },
            '25%': { transform: 'translate(1px, -1px)' },
            '50%': { transform: 'translate(-1px, 1px)' },
            '75%': { transform: 'translate(1px, 1px)' },
          },
          flash: {
            '0%, 100%': { opacity: '0' },
            '50%': { opacity: '0.7' },
          },
          // Add a simple fade-in for the "echoes" as they appear
          'fade-in': {
            '0%': { opacity: '0', transform: 'translateY(10px)' },
            '100%': { opacity: '1', transform: 'translateY(0)' },
          },
          // For listening state, a simple particle animation (if not done with JS)
          'particle-flow': {
            '0%': { transform: 'translate(-50%, -50%) scale(0)', opacity: '0' },
            '25%': { transform: 'translate(-50%, -50%) scale(1)', opacity: '1' },
            '100%': { transform: 'translate(-50%, -50%) scale(1.5)', opacity: '0' },
          },
        },
        animation: {
          heartbeat: 'heartbeat 2s ease-in-out infinite',
          vibrate: 'vibrate 0.1s linear infinite', // Make vibrate faster
          flash: 'flash 0.5s linear infinite', // Make flash faster
          'fade-in': 'fade-in 0.5s ease-out forwards',
          'particle-flow': 'particle-flow 1.5s ease-out infinite',
        },
        // --- END ADDITIONS ---
  	}
  },
  plugins: [
    require('@tailwindcss/typography'),
    require("tailwindcss-animate")
],
}