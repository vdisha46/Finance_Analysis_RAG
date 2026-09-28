async function loadValuation() {
    const response = await fetch('/api/valuation');
    const result = await response.json();
    const container = document.getElementById('valuationMetrics');
    if (!container) return;

    const metrics = [
        ['P/E Ratio', result.pe_ratio],
        ['P/B Ratio', result.pb_ratio],
        ['EV/EBITDA', result.ev_ebitda],
        ['EV/Sales', result.ev_sales],
        ['PEG Ratio', result.peg_ratio],
        ['Intrinsic Value', result.dcf.intrinsic_value],
        ['Fair Value', result.dcf.fair_value],
        ['Terminal Value', result.dcf.terminal_value],
    ];

    container.innerHTML = metrics.map(([label, value]) => `
        <div class="col-md-3">
            <div class="card p-3">
                <div class="text-muted">${label}</div>
                <h5>${value !== null && value !== undefined ? Number(value).toFixed(2) : 'N/A'}</h5>
            </div>
        </div>
    `).join('');
}

loadValuation();
