import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	
	server: {
		proxy: {
			"/api": {
				target: "http://localhost:8000",
				changeOrigin: true,
			},
			"/ws": {
				target: "ws://localhost:8000",
				ws: true,
			},
		},
		port: 5173,
		host: "0.0.0.0",
	},
	
	preview: {
		port: 5173,
		host: "0.0.0.0",
	},
	
	build: {
		target: "esnext",
		sourcemap: true,
	},
});

