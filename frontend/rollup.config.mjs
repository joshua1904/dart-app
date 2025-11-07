// frontend/rollup.config.mjs (Revised)
import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import terser from '@rollup/plugin-terser';
import path from 'path';
import { fileURLToPath } from 'url';

// 1. Get the current directory name using ES Module utilities
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 2. Define the absolute path to your Django static output directory
const DJANGO_STATIC_DIR = path.resolve(
  __dirname,
  '..', // Assumes frontend/ is inside your Django project root
  'static',
  'dist'
);

export default {
  // ... rest of the config remains the same
  input: 'src/index.tsx',
  output: {
    file: path.join(DJANGO_STATIC_DIR, 'bundle.js'),
    format: 'es',
    sourcemap: true,
  },
  plugins: [
    resolve(),
    commonjs(),
    typescript({
        tsconfig: './tsconfig.json'
    }),
    terser(),
  ],
};