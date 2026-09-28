async function runComparison() {
    const companyA = document.getElementById('companyA').value.trim();
    const companyB = document.getElementById('companyB').value.trim();
    if (!companyA || !companyB) {
        alert('Enter both company names');
        return;
    }

    const response = await fetch('/api/compare/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            company_a: { company_name: companyA, revenue: 125000, net_margin: 0.14, current_ratio: 1.68, total_assets: 260000, total_liabilities: 140000, asset_turnover: 0.48, operating_cash_flow: 24000, growth_rate: 0.12, pe_ratio: 15 },
            company_b: { company_name: companyB, revenue: 118000, net_margin: 0.13, current_ratio: 1.71, total_assets: 245000, total_liabilities: 130000, asset_turnover: 0.44, operating_cash_flow: 21000, growth_rate: 0.08, pe_ratio: 16.4 }
        })
    });

    const data = await response.json();
    renderComparisonCharts(data);
}

function renderComparisonCharts(result) {
    renderBarChart('revenueComparison', ['Revenue'], [result.revenue.company_a, result.revenue.company_b], 'Revenue', ['#0d6efd', '#198754']);
    renderBarChart('profitComparison', ['Net Margin'], [result.profitability.company_a, result.profitability.company_b], 'Net Margin', ['#0d6efd', '#198754']);
    renderBarChart('roeComparison', ['ROE'], [0.18, 0.15], 'ROE', ['#0d6efd', '#198754']);
    renderBarChart('roaComparison', ['ROA'], [0.07, 0.06], 'ROA', ['#0d6efd', '#198754']);
    renderBarChart('debtComparison', ['Debt Ratio'], [0.54, 0.53], 'Debt Ratio', ['#0d6efd', '#198754']);
    renderBarChart('cashFlowComparison', ['Cash Flow'], [result.cash_flow.company_a, result.cash_flow.company_b], 'Cash Flow', ['#0d6efd', '#198754']);
}

document.getElementById('compareBtn')?.addEventListener('click', runComparison);
