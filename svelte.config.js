import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			fallback: 'index.html' // Enable SPA mode for dynamic routes
		}),
		files: {
			assets: 'src/frontend/static',
			lib: 'src/frontend/src/lib',
			routes: 'src/frontend/src/routes',
			appTemplate: 'src/frontend/src/app.html',
		}
	},
};

export default config;

