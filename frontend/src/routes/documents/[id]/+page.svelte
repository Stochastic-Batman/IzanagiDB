<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { diffWords } from 'diff';
	
	const API_URL = 'http://localhost:8000';
	const documentId = $page.params.id;
	
	type Document = {
		document_id: number;
		title: string;
		created_at: string;
		last_modified_at: string;
		current_version_number: number | null;
		content: { text: string; [key: string]: any } | null;
	};
	
	type Version = {
		document_id: number;
		version_number: number;
		modified_by: number | null;
		modified_at: string;
	};
	
	let document = $state<Document | null>(null);
	let versions = $state<Version[]>([]);
	let editMode = $state(false);
	let editContent = $state('');
	let loading = $state(true);
	let showVersions = $state(false);
	let selectedVersion = $state<number | null>(null);
	let versionContent = $state<string | null>(null);
	let showDiff = $state(false);
	
	async function fetchDocument() {
		const token = localStorage.getItem('access_token');
		if (!token) {
			goto('/auth');
			return;
		}
		
		try {
			const res = await fetch(`${API_URL}/documents/${documentId}`, {
				headers: { 'Authorization': `Bearer ${token}` },
				credentials: 'include'
			});
			
			if (res.status === 401) {
				goto('/auth');
				return;
			}
			if (res.status === 403) {
				alert('Access denied');
				goto('/documents');
				return;
			}
			
			if (!res.ok) throw new Error('Failed to fetch document');
			
			document = await res.json();
			editContent = document?.content?.text || '';
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to load document');
			goto('/documents');
		} finally {
			loading = false;
		}
	}
	
	async function fetchVersions() {
		const token = localStorage.getItem('access_token');
		if (!token) return;
		
		try {
			const res = await fetch(`${API_URL}/documents/${documentId}/versions`, {
				headers: { 'Authorization': `Bearer ${token}` },
				credentials: 'include'
			});
			
			if (!res.ok) throw new Error('Failed to fetch versions');
			
			versions = await res.json();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to load versions');
		}
	}
	
	async function fetchSpecificVersion(versionNumber: number) {
		const token = localStorage.getItem('access_token');
		if (!token) return;
		
		try {
			const res = await fetch(`${API_URL}/documents/${documentId}/versions/${versionNumber}`, {
				headers: { 'Authorization': `Bearer ${token}` },
				credentials: 'include'
			});
			
			if (!res.ok) throw new Error('Failed to fetch version');
			
			const data = await res.json();
			versionContent = data.content?.text || '';
			selectedVersion = versionNumber;
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to load version');
		}
	}
	
	async function commitVersion() {
		const token = localStorage.getItem('access_token');
		if (!token) return;
		
		if (editContent === document?.content?.text) {
			alert('No changes to commit');
			return;
		}
		
		try {
			const res = await fetch(`${API_URL}/documents/${documentId}/commit`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					content: { text: editContent }
				})
			});
			
			if (!res.ok) throw new Error('Failed to commit version');
			
			// Refresh document
			editMode = false;
			await fetchDocument();
			if (showVersions) {
				await fetchVersions();
			}
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to commit');
		}
	}
	
	function toggleVersions() {
		showVersions = !showVersions;
		if (showVersions && versions.length === 0) {
			fetchVersions();
		}
	}
	
	function viewVersion(versionNumber: number) {
		fetchSpecificVersion(versionNumber);
		showDiff = false;
	}
	
	function closeVersionView() {
		selectedVersion = null;
		versionContent = null;
		showDiff = false;
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
	
	function getDiff() {
		if (!versionContent || !document?.content?.text) return [];
		return diffWords(versionContent, document.content.text);
	}
	
	onMount(() => {
		fetchDocument();
	});
</script>

{#if loading}
	<div class="loading">Loading document...</div>
{:else if document}
	<div class="document-viewer">
		<div class="toolbar">
			<div>
				<a href="/documents" class="back-link">← Back to Documents</a>
				<h1>{document.title}</h1>
				<p class="meta">
					Version {document.current_version_number ?? 0} • 
					Last modified {formatDate(document.last_modified_at)}
				</p>
			</div>
			
			<div class="actions">
				<button onclick={toggleVersions} class="secondary-btn">
					{showVersions ? 'Hide' : 'Show'} Versions
				</button>
				
				{#if editMode}
					<button onclick={() => { editMode = false; editContent = document?.content?.text || ''; }} class="secondary-btn">
						Cancel
					</button>
					<button onclick={commitVersion} class="primary-btn">
						Commit New Version
					</button>
				{:else}
					<button onclick={() => editMode = true} class="primary-btn">
						Edit
					</button>
				{/if}
			</div>
		</div>
		
		<div class="content-area">
			<div class="main-content">
				{#if selectedVersion !== null}
					<div class="version-header">
						<h2>Viewing Version {selectedVersion}</h2>
						<div class="version-actions">
							<button onclick={() => showDiff = !showDiff} class="secondary-btn">
								{showDiff ? 'Hide' : 'Show'} Diff
							</button>
							<button onclick={closeVersionView} class="secondary-btn">
								Back to Current
							</button>
						</div>
					</div>
					
					{#if showDiff}
						<div class="diff-view">
							{#each getDiff() as part}
								<span class:added={part.added} class:removed={part.removed}>
									{part.value}
								</span>
							{/each}
						</div>
					{:else}
						<div class="content-display">
							{versionContent}
						</div>
					{/if}
				{:else if editMode}
					<textarea
						bind:value={editContent}
						placeholder="Write your content..."
						class="editor"
					></textarea>
				{:else}
					<div class="content-display">
						{document.content?.text || 'No content yet.'}
					</div>
				{/if}
			</div>
			
			{#if showVersions}
				<div class="versions-sidebar">
					<h3>Version History</h3>
					
					{#if versions.length === 0}
						<p class="muted">Loading versions...</p>
					{:else}
						<div class="version-list">
							{#each versions as version}
								<button
									onclick={() => viewVersion(version.version_number)}
									class="version-item"
									class:active={selectedVersion === version.version_number}
								>
									<div class="version-number">v{version.version_number}</div>
									<div class="version-date">{formatDate(version.modified_at)}</div>
								</button>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.loading {
		text-align: center;
		padding: 4rem;
		color: var(--color-muted);
		font-style: italic;
	}
	
	.document-viewer {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}
	
	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: start;
		margin-bottom: 2rem;
		gap: 2rem;
	}
	
	.back-link {
		color: var(--color-muted);
		font-size: 0.9rem;
		display: inline-block;
		margin-bottom: 0.5rem;
	}
	
	.back-link:hover {
		color: var(--color-text);
	}
	
	h1 {
		margin: 0;
		font-size: 2.5rem;
	}
	
	.meta {
		color: var(--color-muted);
		margin: 0.5rem 0 0 0;
		font-style: italic;
	}
	
	.actions {
		display: flex;
		gap: 1rem;
		flex-shrink: 0;
	}
	
	.primary-btn {
		background: var(--color-primary);
		color: var(--color-text);
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 600;
	}
	
	.secondary-btn {
		background: transparent;
		color: var(--color-text);
		padding: 0.75rem 1.5rem;
		border: 1px solid var(--color-muted);
		border-radius: 6px;
	}
	
	.secondary-btn:hover {
		border-color: var(--color-text);
	}
	
	.content-area {
		display: grid;
		grid-template-columns: 1fr;
		gap: 2rem;
	}
	
	.content-area:has(.versions-sidebar) {
		grid-template-columns: 1fr 300px;
	}
	
	.main-content {
		background: var(--color-surface);
		border: var(--border);
		border-radius: 8px;
		padding: 2rem;
		min-height: 500px;
	}
	
	.version-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: var(--border);
	}
	
	.version-header h2 {
		margin: 0;
		font-size: 1.3rem;
	}
	
	.version-actions {
		display: flex;
		gap: 0.5rem;
	}
	
	.content-display {
		white-space: pre-wrap;
		line-height: 1.8;
		font-size: 1.1rem;
	}
	
	.editor {
		width: 100%;
		min-height: 500px;
		background: var(--color-bg);
		border: var(--border);
		border-radius: 6px;
		color: var(--color-text);
		font-family: var(--font-body);
		font-size: 1.1rem;
		line-height: 1.8;
		padding: 1rem;
		resize: vertical;
	}
	
	.editor:focus {
		outline: none;
		border-color: var(--color-primary);
	}
	
	.diff-view {
		white-space: pre-wrap;
		line-height: 1.8;
		font-size: 1.1rem;
		font-family: monospace;
	}
	
	.diff-view .added {
		background: rgba(34, 197, 94, 0.2);
		color: #86efac;
	}
	
	.diff-view .removed {
		background: rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		text-decoration: line-through;
	}
	
	.versions-sidebar {
		background: var(--color-surface);
		border: var(--border);
		border-radius: 8px;
		padding: 1.5rem;
		height: fit-content;
		position: sticky;
		top: 2rem;
	}
	
	.versions-sidebar h3 {
		margin: 0 0 1rem 0;
		font-size: 1.1rem;
	}
	
	.version-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.version-item {
		background: var(--color-bg);
		border: var(--border);
		border-radius: 6px;
		padding: 0.75rem;
		text-align: left;
		transition: all 0.2s;
		width: 100%;
	}
	
	.version-item:hover {
		border-color: var(--color-primary);
	}
	
	.version-item.active {
		background: var(--color-primary);
		border-color: var(--color-primary);
	}
	
	.version-number {
		font-weight: 600;
		margin-bottom: 0.25rem;
	}
	
	.version-date {
		font-size: 0.85rem;
		color: var(--color-muted);
	}
	
	.muted {
		color: var(--color-muted);
		font-style: italic;
		text-align: center;
	}
</style>
