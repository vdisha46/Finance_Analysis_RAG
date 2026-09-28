async function loadRatios() {
    const response = await fetch('/api/ratios');
    const ratios = await response.json();

    const cardsContainer = document.getElementById('ratioCards');
    if (!cardsContainer) return;

    const sample = ratios[0] || {};
    const metrics = [
        ['Current Ratio', sample.current_ratio],
        ['Quick Ratio', sample.quick_ratio],
        ['Cash Ratio', sample.cash_ratio],
        ['Gross Margin', sample.gross_margin],
        ['Operating Margin', sample.operating_margin],
        ['EBITDA Margin', sample.ebitda_margin],
        ['Net Margin', sample.net_margin],
        ['ROE', sample.roe],
        ['ROA', sample.roa],
        ['Debt to Equity', sample.debt_to_equity],
    ];

    cardsContainer.innerHTML = metrics.map(([label, value]) => `
        <div class="col-md-3">
            <div class="card p-3">
                <div class="text-muted">${label}</div>
                <h4>${value !== null && value !== undefined ? Number(value).toFixed(2) : 'N/A'}</h4>
            </div>
        </div>
    `).join('');

    const labels = metrics.map(([label]) => label);
    const values = metrics.map(([, value]) => value ?? 0);
    renderBarChart('ratioChart', labels, values, 'Ratios', '#0d6efd');
}

loadRatios();
