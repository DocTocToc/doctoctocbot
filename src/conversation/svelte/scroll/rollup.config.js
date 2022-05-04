import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import sveltePreprocess from 'svelte-preprocess';
import typescript from '@rollup/plugin-typescript';
import copy from 'rollup-plugin-copy';
import json from '@rollup/plugin-json';
import css from 'rollup-plugin-css-only';


const production = !process.env.ROLLUP_WATCH;

function serve() {
	let server;

	function toExit() {
		if (server) server.kill(0);
	}

	return {
		writeBundle() {
			if (server) return;
			server = require('child_process').spawn(
				'npm',
				['run', 'start', '--', '--dev'],
				{
				    stdio: ['ignore', 'inherit', 'inherit'],
				    shell: true
			    }
			);

			process.on('SIGTERM', toExit);
			process.on('exit', toExit);
		}
	};
}

export default {
	input: 'src/main.ts',
	output: {
		sourcemap: true,
		format: 'iife',
		name: 'app',
		file: 'public/build/bundle.js'
	},
	plugins: [
		svelte({
			preprocess: sveltePreprocess({ sourceMap: !production }),
			compilerOptions: {
				dev: !production
			}
		}),
		resolve({
			browser: true,
			dedupe: ['svelte']
		}),
		commonjs(),
		typescript({
			sourceMap: !production,
			inlineSources: !production
		}),
		json(),
		css({ output: 'bundle.css' }),
		!production && serve(),
		// Watch the `public` directory and refresh the
		// browser on changes when not in production
		!production && livereload('public'),
		// If we're building for production (npm run build
		// instead of npm run dev), minify
		production && terser(),
		copy({
			targets: [
				{
					src: 'public/*',
					dest: '../../static/conversation/scroll/'
				}
			]
		}),
		copy({
			targets: [
				//	{ 
				//    src: 'node_modules/bootstrap/dist/**/*', 
				//    dest: 'public/vendor/bootstrap' 
				//},
				{
					src: 'node_modules/flatpickr/dist/themes/light.css',
					dest: 'public/vendor/flatpickr/'
				},
				{
					src: 'node_modules/flatpickr/dist/flatpickr.css',
					dest: 'public/vendor/flatpickr/'
				},
			]
		}),
	],
	watch: {
		clearScreen: false
	}
};