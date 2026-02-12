<script lang="ts">
	import { goto } from '$app/navigation';
	
	let mode = $state<'login' | 'signup'>('login');
	let username = $state('');
	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);
	
	const API_URL = 'http://localhost:8000';
	
	async function handleSubmit() {
		error = '';
		loading = true;
		
		try {
			if (mode === 'signup') {
				const registerRes = await fetch(`${API_URL}/auth/register`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ username, email, password })
				});
				
				if (!registerRes.ok) {
					const data = await registerRes.json();
					throw new Error(data.detail || 'Registration failed');
				}
				
				// Auto-login after registration
				mode = 'login';
				email = ''; // Clear email field for login
			}
			
			// Login (or after successful registration)
			const loginRes = await fetch(`${API_URL}/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password }),
				credentials: 'include' // includes httpOnly cookie
			});
			
			if (!loginRes.ok) {
				const data = await loginRes.json();
				throw new Error(data.detail || 'Login failed');
			}
			
			const data = await loginRes.json();
			localStorage.setItem('access_token', data.access_token);
			goto('/documents');
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}
	
	function toggleMode() {
		mode = mode === 'login' ? 'signup' : 'login';
		error = '';
	}
</script>

<div class="auth-container">
	<div class="auth-card">
		<h1>{mode === 'login' ? 'Here We Go Again...' : 'Create Account'}</h1>
		<p class="subtitle">
			{mode === 'login' 
				? 'Access your version-controlled documents' 
				: 'Start tracking your document history'}
		</p>
		
		<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
			<div class="form-group">
				<label for="username">Username</label>
				<input 
					id="username"
					type="text" 
					bind:value={username}
					placeholder="your_username"
					required
					minlength="3"
					maxlength="50"
				/>
			</div>
			
			{#if mode === 'signup'}
				<div class="form-group">
					<label for="email">Email</label>
					<input 
						id="email"
						type="email" 
						bind:value={email}
						placeholder="you@example.com"
						required
					/>
				</div>
			{/if}
			
			<div class="form-group">
				<label for="password">Password</label>
				<input 
					id="password"
					type="password" 
					bind:value={password}
					placeholder="••••••••"
					required
					minlength="8"
				/>
			</div>
			
			{#if error}
				<div class="error">{error}</div>
			{/if}
			
			<button type="submit" disabled={loading} class="submit-btn">
				{loading ? 'Loading...' : mode === 'login' ? 'Login' : 'Sign Up'}
			</button>
		</form>
		
		<div class="toggle">
			<button type="button" onclick={toggleMode} class="link-btn">
				{mode === 'login' 
					? "Don't have an account? Sign up" 
					: 'Already have an account? Login'}
			</button>
		</div>
	</div>
</div>

<style>
	.auth-container {
		min-height: calc(100vh - 200px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}
	
	.auth-card {
		background: var(--color-surface);
		border: var(--border);
		border-radius: 12px;
		padding: 3rem;
		max-width: 450px;
		width: 100%;
	}
	
	h1 {
		margin: 0 0 0.5rem 0;
		font-size: 2rem;
		text-align: center;
	}
	
	.subtitle {
		text-align: center;
		color: var(--color-muted);
		margin-bottom: 2rem;
		font-style: italic;
	}
	
	.form-group {
		margin-bottom: 1.5rem;
	}
	
	label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: var(--color-muted);
	}
	
	input {
		width: 100%;
		padding: 0.75rem;
		background: var(--color-bg);
		border: var(--border);
		border-radius: 6px;
		color: var(--color-text);
		font-family: var(--font-body);
		font-size: 1rem;
		transition: border-color 0.2s;
	}
	
	input:focus {
		outline: none;
		border-color: var(--color-primary);
	}
	
	.error {
		background: rgba(220, 38, 38, 0.1);
		border: 1px solid rgba(220, 38, 38, 0.3);
		color: #fca5a5;
		padding: 0.75rem;
		border-radius: 6px;
		margin-bottom: 1rem;
		text-align: center;
	}
	
	.submit-btn {
		width: 100%;
		padding: 0.875rem;
		background: var(--color-primary);
		color: var(--color-text);
		font-size: 1rem;
		font-weight: 600;
		border-radius: 6px;
		margin-top: 1rem;
	}
	
	.submit-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	.toggle {
		text-align: center;
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: var(--border);
	}
	
	.link-btn {
		background: transparent;
		color: var(--color-muted);
		padding: 0.5rem;
		text-decoration: underline;
	}
	
	.link-btn:hover {
		color: var(--color-text);
	}
</style>
