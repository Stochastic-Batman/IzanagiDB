<script lang="ts">
	import { goto } from '$app/navigation';
</script>

<div class="hero">
	<h1>IzanagiDB</h1>
	<p class="tagline">Version Control for Your Documents</p>
	
	<div class="explanation">
		<p>
			Named after the Uchiha forbidden technique, <strong>IzanagiDB</strong> lets you 
			warp reality by rewinding your documents to any previous state. Every change is 
			tracked, every version preserved.
		</p>
		
		<div class="features">
			<div class="feature">
				<h3>⏮️ Time Travel</h3>
				<p>View any previous version of your documents</p>
			</div>
			
			<div class="feature">
				<h3>👁️ Visual Diffs</h3>
				<p>See exactly what changed between versions</p>
			</div>
			
			<div class="feature">
				<h3>🤝 Collaboration</h3>
				<p>Share documents with other users</p>
			</div>
		</div>
	</div>
	
	<div class="cta">
		<button onclick={() => goto('/auth')}>Get Started</button>
	</div>
	
	<div class="note">
		<p><em>Note: This is a side project for learning full-stack development.</em></p>
	</div>
</div>

<style>
	.hero {
		text-align: center;
		padding: 4rem 2rem;
	}
	
	h1 {
		font-size: 4rem;
		margin: 0;
		font-style: italic;
		background: linear-gradient(135deg, var(--color-text) 0%, var(--color-primary) 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	
	.tagline {
		font-size: 1.5rem;
		color: var(--color-muted);
		margin-top: 0.5rem;
		font-style: italic;
	}
	
	.explanation {
		max-width: 800px;
		margin: 3rem auto;
		text-align: left;
		line-height: 1.8;
	}
	
	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 2rem;
		margin-top: 3rem;
	}
	
	.feature {
		background: var(--color-surface);
		padding: 2rem;
		border-radius: 8px;
		border: var(--border);
	}
	
	.feature h3 {
		margin-top: 0;
		font-size: 1.3rem;
	}
	
	.feature p {
		color: var(--color-muted);
		margin-bottom: 0;
	}
	
	.cta {
		margin: 3rem 0;
	}
	
	.cta button {
		background: var(--color-primary);
		color: var(--color-text);
		padding: 1rem 3rem;
		font-size: 1.2rem;
		border-radius: 8px;
		font-weight: 600;
	}
	
	.note {
		margin-top: 4rem;
		color: var(--color-muted);
		font-size: 0.9rem;
	}
</style>