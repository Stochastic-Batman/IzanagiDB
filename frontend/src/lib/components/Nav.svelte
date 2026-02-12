<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	
	let isLoggedIn = $state(false);
	
	$effect(() => {
		if (typeof window !== 'undefined') {
			isLoggedIn = !!localStorage.getItem('access_token');
		}
	});
	
	async function handleLogout() {
		await fetch('http://localhost:8000/auth/logout', {
			method: 'POST',
			credentials: 'include'
		});
		
		localStorage.removeItem('access_token');
		isLoggedIn = false;
		goto('/');
	}
</script>

<nav>
	<div class="nav-container">
		<a href="/" class="logo">
			<span class="izanagi">Izanagi</span><span class="db">DB</span>
		</a>
		
		<div class="nav-links">
			{#if isLoggedIn}
				<a href="/documents" class:active={$page.url.pathname.startsWith('/documents')}>
           Documents
				</a>
				<button onclick={handleLogout} class="logout">Logout</button>
			{:else}
				<a href="/auth" class="login-btn">
					Login
				</a>
			{/if}
		</div>
	</div>
</nav>


<style>
	nav {
		background: var(--color-surface);
		border-bottom: var(--border);
		padding: 1rem 0;
	}
	
	.nav-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.logo {
		font-size: 1.5rem;
		font-family: var(--font-heading);
		font-weight: 700;
		font-style: italic;
	}
	
	.izanagi {
		color: var(--color-text);
	}
	
	.db {
		color: var(--color-primary);
	}
	
	.nav-links {
		display: flex;
		gap: 2rem;
		align-items: center;
	}
	
	.nav-links a {
		font-size: 1rem;
		padding: 0.5rem 1rem;
		border-radius: 4px;
	}
	
	.nav-links a.active {
		background: var(--color-primary);
  }

  .login-btn {
    background: var(--color-primary) !important;
  }
	
	.logout {
		background: transparent;
		color: var(--color-text);
		padding: 0.5rem 1rem;
		border-radius: 4px;
		border: 1px solid var(--color-muted);
	}
	
	.logout:hover {
		border-color: var(--color-text);
	}
</style>
