async function loadInsights() {
    const response = await fetch('/api/insights');
    const insights = await response.json();
    const container = document.getElementById('insightsContainer');
    if (!container) return;

    container.innerHTML = (insights || []).map(item => `
        <div class="col-md-6">
            <div class="card p-3">
                <h5>Executive Summary</h5>
                <p>${item.summary || 'Summary unavailable'}</p>
                <p><strong>Strengths:</strong> ${item.strengths || 'N/A'}</p>
                <p><strong>Weaknesses:</strong> ${item.weaknesses || 'N/A'}</p>
                <p><strong>Risks:</strong> ${item.risks || 'N/A'}</p>
                <p><strong>Recommendations:</strong> ${item.recommendations || 'N/A'}</p>
            </div>
        </div>
    `).join('');
}

loadInsights();
