<script>
    import UserName from "./UserName.svelte"
</script>

<main>
	<h2>SocialUser</h2>
    <UserName />
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}
	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>