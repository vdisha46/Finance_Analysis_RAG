const financialChartDefinitions = [
    { id: 'grossMarginChart', field: 'gross_margin', label: 'Gross margin', percent: true, color: '#168aad' },
    { id: 'netMarginChart', field: 'net_margin', label: 'Net margin', percent: true, color: '#e76f51' },
    { id: 'ebitdaMarginChart', field: 'ebitda_margin', label: 'EBITDA margin', percent: true, color: '#43aa8b' },
    { id: 'cashRatioChart', field: 'cash_ratio', label: 'Cash ratio', percent: false, color: '#f4a261' },
    { id: 'roeChart', field: 'roe', label: 'Return on equity', percent: true, color: '#577590' },
    { id: 'roaChart', field: 'roa', label: 'Return on assets', percent: true, color: '#90be6d' },
    { id: 'debtToEquityChart', field: 'debt_to_equity', label: 'Debt to equity', percent: false, color: '#9b5de5' },
    { id: 'currentRatioChart', field: 'current_ratio', label: 'Current ratio', percent: false, color: '#f15bb5' },
];

function groupRatiosByCompanyYear(rows, field) {
    const groups = new Map();

    for (const row of rows) {
        if (row[field] === null || row[field] === undefined || row[field] === '') continue;
        const value = Number(row[field]);
        if (!Number.isFinite(value)) continue;

        const company = row.company_name || 'Unknown';
        const year = row.financial_year || 'Year not specified';
        const key = `${company}\u0000${year}`;
        const group = groups.get(key) || { company, year, total: 0, count: 0 };
        group.total += value;
        group.count += 1;
        groups.set(key, group);
    }

    return [...groups.values()]
        .sort((left, right) => left.company.localeCompare(right.company) || left.year.localeCompare(right.year))
        .map(group => ({
            label: `${group.company} (${group.year})`,
            value: group.total / group.count,
        }));
}

function renderFinancialChart(definition, rows) {
    const canvas = document.getElementById(definition.id);
    if (!canvas) return;

    const observations = groupRatiosByCompanyYear(rows, definition.field);
    if (!observations.length) {
        const message = document.createElement('p');
        message.className = 'text-muted small mb-0';
        message.textContent = 'No analyzed values available.';
        canvas.replaceWith(message);
        return;
    }

    const values = observations.map(item => definition.percent ? item.value * 100 : item.value);
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: observations.map(item => item.label),
            datasets: [{
                label: definition.label,
                data: values,
                backgroundColor: definition.color,
                borderRadius: 4,
                maxBarThickness: 48,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: context => `${definition.label}: ${context.parsed.y.toFixed(2)}${definition.percent ? '%' : ''}`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxRotation: 35, minRotation: 0 },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `${value}${definition.percent ? '%' : ''}`,
                    },
                },
            },
        },
    });
}

async function loadFinancialDashboard() {
    const canvases = financialChartDefinitions.map(definition => document.getElementById(definition.id)).filter(Boolean);
    try {
        const response = await fetch('/api/ratios');
        if (!response.ok) throw new Error('Unable to load financial ratios.');
        const rows = await response.json();
        financialChartDefinitions.forEach(definition => renderFinancialChart(definition, rows));
    } catch (error) {
        for (const canvas of canvases) {
            const message = document.createElement('p');
            message.className = 'text-danger small mb-0';
            message.textContent = error.message || 'Unable to load financial ratios.';
            canvas.replaceWith(message);
        }
    }
}

loadFinancialDashboard();