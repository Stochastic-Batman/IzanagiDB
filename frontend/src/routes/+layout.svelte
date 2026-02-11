<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import '$lib/styles.css';
	import Nav from '$lib/components/Nav.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<Nav />
<main>
	{@render children()}
</main>

<style>
	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}
</style>