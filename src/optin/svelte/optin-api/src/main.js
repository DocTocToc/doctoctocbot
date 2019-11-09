import App from './App.svelte';

const app = new App({
	target: document.querySelector('category'),
	props: {
		option: 'twitter_dm_category_self'
	}
});

export default app;