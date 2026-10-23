import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './assets/javascript'),
      // this may not be needed anymore, but leaving it shouldn't hurt
      'use-sync-external-store/shim': path.resolve(__dirname, './node_modules/use-sync-external-store/shim'),
    },
  },
  base: '/static/', // Should match Django's STATIC_URL
  build: {
    manifest: true, // The manifest.json file is needed for django-vite
    outDir: path.resolve(__dirname, './static'), // Output directory for production build
    emptyOutDir: false, // Preserve the outDir to not clobber Django's other files.
    rolldownOptions: {
      input: {
        'site-base-css': path.resolve(__dirname, './assets/styles/site-base.css'),
        'site-tailwind-css': path.resolve(__dirname, './assets/styles/site-tailwind.css'),
        'site': path.resolve(__dirname, './assets/javascript/site.js'),
        'app': path.resolve(__dirname, './assets/javascript/app.js'),
      },
      output: {
        // Output JS bundles to js/ directory with -bundle suffix
        entryFileNames: `js/[name]-bundle.js`,
        // For shared chunks, keep hash for cache busting
        chunkFileNames: `js/[name]-[hash].js`,
        // For CSS and other assets
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            // Try to name CSS files like css/[entry_name].css, removing potential hash
            let baseName = path.basename(assetInfo.name, '.css');
            const hashPattern = /\.[0-9a-fA-F]{8}$/;
            baseName = baseName.replace(hashPattern, '');
            return `css/${baseName}.css`;
          }
          // Default for other assets (fonts, images, etc.)
          return `assets/[name]-[hash][extname]`;
        },
      },
    },
  },
  server: {
    port: parseInt(process.env.DJANGO_VITE_PORT || '5173'), // Default Vite dev server port, must match DJANGO_VITE settings
    strictPort: true, // Vite will exit if the port is already in use
    hmr: {
      // host: 'localhost', // default of localhost is fine as long as Django is running there.
      // protocol: 'ws', // default of ws is fine. Change to 'wss' if Django (dev) server uses HTTPS.
    },
    // Ignore large directories to avoid exhausting system-wide inotify watchers limit
    // when running multiple Vite instances in parallel (e.g., in multiple git worktrees)
    watch: {
      ignored: ['**/.venv/**', '**/node_modules/**', '**/.git/**', path.resolve(__dirname, './static') + '/**'],
    },
  },
});
