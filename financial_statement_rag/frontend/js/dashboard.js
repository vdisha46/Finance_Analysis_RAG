async function fetchDashboard() {
    const response = await fetch('/api/dashboard');
    const data = await response.json();

    if (!response.ok) {
        alert(data.detail || 'Unable to load dashboard');
        return;
    }

    document.getElementById('documentsUploaded').textContent = data.documents_uploaded;
    document.getElementById('companiesAnalyzed').textContent = data.companies_analyzed;
    document.getElementById('averageRoe').textContent = `${data.average_roe}%`;
    document.getElementById('averageEbitdaMargin').textContent = `${data.average_ebitda_margin}%`;

    const recentUploads = document.getElementById('recentUploads');
    recentUploads.innerHTML = (data.recent_uploads || []).map(item => `<li class="list-group-item">${item}</li>`).join('');

    const recentQueries = document.getElementById('recentQueries');
    recentQueries.innerHTML = (data.recent_queries || []).map(item => `<li class="list-group-item">${item}</li>`).join('');

    const recentComparisons = document.getElementById('recentComparisons');
    recentComparisons.innerHTML = (data.recent_comparisons || []).map(item => `<li class="list-group-item">${item}</li>`).join('');
}

async function loadDocumentsTable() {
    const response = await fetch('/api/documents');
    const documents = await response.json();
    const tableBody = document.getElementById('documentsTable');

    if (!tableBody) return;

    tableBody.innerHTML = documents.map(doc => `
        <tr>
            <td>${doc.company_name}</td>
            <td>${doc.file_name}</td>
            <td>${doc.file_type}</td>
            <td>${doc.financial_year || 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-outline-danger" data-id="${doc.id}">Delete</button>
            </td>
        </tr>
    `).join('');

    tableBody.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', async () => {
            await fetch(`/api/document/${btn.dataset.id}`, {
                method: 'DELETE'
            });
            loadDocumentsTable();
        });
    });
}

if (document.getElementById('documentsUploaded')) {
    fetchDashboard();
}

if (document.getElementById('documentsTable')) {
    loadDocumentsTable();
}
