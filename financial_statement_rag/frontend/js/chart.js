function renderBarChart(canvasId, labels, values, label, bgColor = '#0d6efd') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: bgColor,
                borderRadius: 6,
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function renderLineChart(canvasId, labels, values, label, color = '#198754') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                borderColor: color,
                backgroundColor: color + '22',
                fill: true,
                tension: 0.35,
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}
