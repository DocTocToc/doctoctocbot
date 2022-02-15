import path from "path";
import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import copy from 'rollup-plugin-copy';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import json from '@rollup/plugin-json';
import sveltePreprocess from 'svelte-preprocess';

const production = !process.env.ROLLUP_WATCH;

const postcssOptions = () => ({
	  extensions: [".scss", ".sass"],
	  extract: false,
	  minimize: true,
	  use: [
	    [
	      "sass",
	      {
	        includePaths: [
	          "./src/theme",
	          "./node_modules",
	          // This is only needed because we're using a local module. :-/
	          // Normally, you would not need this line.
	          path.resolve(__dirname, "..", "node_modules")
	        ]
	      }
	    ]
	  ]
	});

function serve() {
	let server;
	
	function toExit() {
		if (server) server.kill(0);
	}

	return {
		writeBundle() {
			if (server) return;
			server = require('child_process').spawn('npm', ['run', 'start', '--', '--dev'], {
				stdio: ['ignore', 'inherit', 'inherit'],
				shell: true
			});

			process.on('SIGTERM', toExit);
			process.on('exit', toExit);
		}
	};
}

export default {
	input: 'src/main.js',
	output: {
		sourcemap: true,
		format: 'iife',
		name: 'app',
		file: 'public/build/bundle.js'
	},
	plugins: [
		json(),
		svelte({
			// enable run-time checks when not in production
			dev: !production,
			// we'll extract any component CSS out into
			// a separate file - better for performance
			css: css => {
				css.write('public/build/bundle.css');
			}
			//preprocess: sveltePreprocess({ postcss: true }),
		}),
		nodeResolve(),
		copy({
            targets: [
            //	{ 
            //    src: 'node_modules/bootstrap/dist/**/*', 
            //    dest: 'public/vendor/bootstrap' 
            //},
            //{ 
            //    src: 'node_modules/svelte-material-ui/bare.css', 
            //    dest: 'public/vendor/svelte-material-ui/' 
            //},
		      ]
		    }),
		// If you have external dependencies installed from
		// npm, you'll most likely need these plugins. In
		// some cases you'll need additional configuration -
		// consult the documentation for details:
		// https://github.com/rollup/plugins/tree/master/packages/commonjs
		resolve({
			browser: true,
			dedupe: ['svelte']
		}),
		commonjs(),
	    //postcss(postcssOptions()),
		// In dev mode, call `npm run start` once
		// the bundle has been generated
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
                	dest: '../../static/moderation/moderator-api/'
                }
	        ]
		}),
    ],
	watch: {
		clearScreen: false
	}
};
