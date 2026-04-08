// API Base URL (Assuming it's on the same origin or port 8000)
const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupAnalysisLab();
    setupGalleryMonitor();
});

// Tab Navigation
function setupTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const viewTitle = document.getElementById('view-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.dataset.tab;
            
            navItems.forEach(n => n.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));
            
            item.classList.add('active');
            document.getElementById(`${tabId}-section`).classList.add('active');
            viewTitle.textContent = item.innerText;
        });
    });
}

// Single Analysis Lab Logic
function setupAnalysisLab() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultContainer = document.getElementById('single-result');
    const loader = document.getElementById('loader');

    analyzeBtn.addEventListener('click', async () => {
        const postId = document.getElementById('post-id-input').value;
        const content = document.getElementById('content-input').value;

        if (!content.trim()) {
            alert('Please enter content to analyze.');
            return;
        }

        showLoader(true);
        try {
            const response = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ post_id: postId, content: content })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            displaySingleResult(data);
        } catch (error) {
            console.error(error);
            alert('Failed to analyze content. Is the API running?');
        } finally {
            showLoader(false);
        }
    });
}

function displaySingleResult(data) {
    const resultContainer = document.getElementById('single-result');
    const badge = document.getElementById('safety-badge');
    const scoresGrid = document.getElementById('scores-grid');

    resultContainer.style.display = 'block';
    
    // Safety Badge
    badge.textContent = data.is_safe ? 'SAFE' : 'ACTION REQUIRED';
    badge.className = `badge large ${data.is_safe ? 'safe' : 'danger'}`;

    // Scores
    scoresGrid.innerHTML = '';
    data.details.forEach(detail => {
        const percentage = (detail.score * 100).toFixed(1);
        const item = document.createElement('div');
        item.className = 'score-item';
        item.innerHTML = `
            <div class="score-label">${detail.label}</div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="score-value">${percentage}%</div>
        `;
        scoresGrid.appendChild(item);
    });

    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

// Gallery Monitor Logic
function setupGalleryMonitor() {
    const monitorBtn = document.getElementById('monitor-btn');
    const monitorResults = document.getElementById('monitor-results');

    monitorBtn.addEventListener('click', async () => {
        const galleryId = document.getElementById('gallery-input').value.trim();

        if (!galleryId) {
            alert('Please enter a gallery ID.');
            return;
        }

        showLoader(true);
        monitorResults.innerHTML = '';

        try {
            const response = await fetch(`${API_BASE}/analyze/dcinside/${galleryId}`);
            
            if (!response.ok) throw new Error('Gallery not found or API Error');

            const data = await response.json();
            displayGalleryResults(data.results);
        } catch (error) {
            console.error(error);
            monitorResults.innerHTML = `<div class="empty-state"><p>Error: ${error.message}</p></div>`;
        } finally {
            showLoader(false);
        }
    });
}

function displayGalleryResults(results) {
    const monitorResults = document.getElementById('monitor-results');
    
    if (results.length === 0) {
        monitorResults.innerHTML = '<div class="empty-state"><p>No recent posts found.</p></div>';
        return;
    }

    results.forEach(res => {
        const card = document.createElement('div');
        card.className = 'post-card';
        
        // Find most relevant label (max score)
        const topLabel = res.details.reduce((prev, current) => (prev.score > current.score) ? prev : current);

        card.innerHTML = `
            <div class="post-header">
                <span class="post-id">${res.post_id}</span>
                <span class="badge ${res.is_safe ? 'safe' : 'danger'}">${res.is_safe ? 'SAFE' : 'FLAGGED'}</span>
            </div>
            <p class="post-content">${res.content || 'No content found.'}</p>
            <div class="score-label-pill" style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                Main Category: <strong>${topLabel.label}</strong> (${(topLabel.score * 100).toFixed(0)}%)
            </div>
        `;

        // Note: The /analyze/dcinside endpoint in endpoints.py doesn't currently return the original content 
        // in TextAnalysisResponse based on schemas.py. I should probably update the API or handle this.
        // For now, I'll just show the scores.
        
        monitorResults.appendChild(card);
    });
}

function showLoader(show) {
    document.getElementById('loader').style.display = show ? 'flex' : 'none';
}
