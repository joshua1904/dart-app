import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';
import { resolve } from 'path';

export default defineConfig({
  plugins: [preact()],
  root: './src',
  build: {
    outDir: '../../static/',     // build files go here (Django static)
    emptyOutDir: true,                // clear old files before build
    rollupOptions: {
      input: resolve(__dirname, 'src/index.tsx'), // entry point
    },
  },
});
