<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	
	const API_URL = 'http://localhost:8000';
	
	type Document = {
		document_id: number;
		title: string;
		created_at: string;
		last_modified_at: string;
		current_version_number: number | null;
	};
	
	let documents = $state<Document[]>([]);
	let loading = $state(true);
	let error = $state('');
	let showCreateModal = $state(false);
	let newDocTitle = $state('');
	let newDocContent = $state('');
	
	async function fetchDocuments() {
		const token = localStorage.getItem('access_token');
		
		if (!token) {
			goto('/auth');
			return;
		}
		
		try {
			const res = await fetch(`${API_URL}/documents`, {
				headers: {
					'Authorization': `Bearer ${token}`
				},
				credentials: 'include'
			});
			
			if (res.status === 401) {
				// Token expired
				localStorage.removeItem('access_token');
				goto('/auth');
				return;
			}
			
			if (!res.ok) throw new Error('Failed to fetch documents');
			
			documents = await res.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load documents';
		} finally {
			loading = false;
		}
	}
	
	async function createDocument() {
		const token = localStorage.getItem('access_token');
		if (!token) return;
		
		try {
			const res = await fetch(`${API_URL}/documents`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					title: newDocTitle,
					content: { text: newDocContent }
				})
			});
			
			if (!res.ok) throw new Error('Failed to create document');
			
			// Reset form and close modal
			newDocTitle = '';
			newDocContent = '';
			showCreateModal = false;
			
			// Refresh list
			await fetchDocuments();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to create document');
		}
	}
	
	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	onMount(() => {
		fetchDocuments();
	});
</script>

<div class="documents-page">
	<div class="header">
		<h1>Your Documents</h1>
		<button onclick={() => showCreateModal = true} class="create-btn">
			+ New Document
		</button>
	</div>
	
	{#if loading}
		<div class="loading">Loading your documents...</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if documents.length === 0}
		<div class="empty">
			<p>No documents yet. Create your first one!</p>
		</div>
	{:else}
		<div class="documents-grid">
			{#each documents as doc}
				<a href="/documents/{doc.document_id}" class="doc-card">
					<div class="doc-header">
						<h3>{doc.title}</h3>
						{#if doc.current_version_number !== null}
							<span class="version-badge">v{doc.current_version_number}</span>
						{/if}
					</div>
					<div class="doc-meta">
						<p>Created: {formatDate(doc.created_at)}</p>
						<p>Modified: {formatDate(doc.last_modified_at)}</p>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>

{#if showCreateModal}
	<div class="modal-backdrop" onclick={() => showCreateModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<h2>Create New Document</h2>
			
			<form onsubmit={(e) => { e.preventDefault(); createDocument(); }}>
				<div class="form-group">
					<label for="title">Title</label>
					<input 
						id="title"
						type="text" 
						bind:value={newDocTitle}
						placeholder="My Document"
						required
						maxlength="255"
					/>
				</div>
				
				<div class="form-group">
					<label for="content">Initial Content</label>
					<textarea 
						id="content"
						bind:value={newDocContent}
						placeholder="Start writing..."
						rows="10"
						required
					></textarea>
				</div>
				
				<div class="modal-actions">
					<button type="button" onclick={() => showCreateModal = false} class="cancel-btn">
						Cancel
					</button>
					<button type="submit" class="submit-btn">
						Create
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	.documents-page {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}
	
	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}
	
	h1 {
		margin: 0;
		font-size: 2.5rem;
	}
	
	.create-btn {
		background: var(--color-primary);
		color: var(--color-text);
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 600;
		font-size: 1rem;
	}
	
	.loading, .empty {
		text-align: center;
		color: var(--color-muted);
		padding: 4rem 2rem;
		font-style: italic;
	}
	
	.error {
		background: rgba(220, 38, 38, 0.1);
		border: 1px solid rgba(220, 38, 38, 0.3);
		color: #fca5a5;
		padding: 1rem;
		border-radius: 6px;
		text-align: center;
	}
	
	.documents-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1.5rem;
	}
	
	.doc-card {
		background: var(--color-surface);
		border: var(--border);
		border-radius: 8px;
		padding: 1.5rem;
		transition: all 0.2s;
		cursor: pointer;
	}
	
	.doc-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}
	
	.doc-header {
		display: flex;
		justify-content: space-between;
		align-items: start;
		margin-bottom: 1rem;
	}
	
	.doc-card h3 {
		margin: 0;
		font-size: 1.3rem;
		color: var(--color-text);
	}
	
	.version-badge {
		background: var(--color-primary);
		color: var(--color-text);
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 600;
	}
	
	.doc-meta {
		color: var(--color-muted);
		font-size: 0.875rem;
	}
	
	.doc-meta p {
		margin: 0.25rem 0;
	}
	
	/* Modal Styles */
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}
	
	.modal {
		background: var(--color-surface);
		border: var(--border);
		border-radius: 12px;
		padding: 2rem;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
	}
	
	.modal h2 {
		margin-top: 0;
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
	
	input, textarea {
		width: 100%;
		padding: 0.75rem;
		background: var(--color-bg);
		border: var(--border);
		border-radius: 6px;
		color: var(--color-text);
		font-family: var(--font-body);
		font-size: 1rem;
		resize: vertical;
	}
	
	input:focus, textarea:focus {
		outline: none;
		border-color: var(--color-primary);
	}
	
	.modal-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 2rem;
	}
	
	.cancel-btn {
		background: transparent;
		color: var(--color-muted);
		padding: 0.75rem 1.5rem;
		border: 1px solid var(--color-muted);
		border-radius: 6px;
	}
	
	.submit-btn {
		background: var(--color-primary);
		color: var(--color-text);
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 600;
	}
</style>