const reportStatus = document.getElementById('reportStatus');
const reportContent = document.getElementById('reportContent');

function addCell(row, value, tag = 'td') {
    const cell = document.createElement(tag);
    cell.textContent = value ?? 'N/A';
    row.appendChild(cell);
}

function renderReport(report) {
    reportContent.replaceChildren();

    const summary = document.createElement('p');
    summary.textContent = `${report.summary.company_count} companies | ${report.summary.document_count} documents | Generated ${new Date(report.generated_at).toLocaleString()}`;
    reportContent.appendChild(summary);

    const tableWrapper = document.createElement('div');
    tableWrapper.className = 'table-responsive';
    const table = document.createElement('table');
    table.className = 'table table-striped align-middle';
    const header = document.createElement('tr');
    ['Company', 'Year', 'Document', 'Current ratio', 'Net margin', 'ROE', 'Saved insight'].forEach(label => addCell(header, label, 'th'));
    const head = document.createElement('thead');
    head.appendChild(header);
    table.appendChild(head);

    const body = document.createElement('tbody');
    for (const documentData of report.documents) {
        const row = document.createElement('tr');
        addCell(row, documentData.company_name);
        addCell(row, documentData.financial_year || 'Not specified');
        addCell(row, documentData.file_name);
        addCell(row, documentData.ratios.current_ratio);
        addCell(row, documentData.ratios.net_margin);
        addCell(row, documentData.ratios.roe);
        addCell(row, documentData.insights.summary || 'No saved insight');
        body.appendChild(row);
    }
    table.appendChild(body);
    tableWrapper.appendChild(table);
    reportContent.appendChild(tableWrapper);
}

async function generateReport() {
    reportStatus.textContent = 'Generating report preview...';
    const button = document.getElementById('generateReportBtn');
    button.disabled = true;

    try {
        const response = await fetch('/api/reports?format=preview');
        const report = await response.json();
        if (!response.ok) throw new Error(report.detail || 'Unable to generate report');
        renderReport(report);
        reportStatus.textContent = 'Report preview generated from saved documents, ratios, and insights.';
    } catch (error) {
        reportStatus.textContent = error.message || 'Unable to generate report.';
    } finally {
        button.disabled = false;
    }
}

async function downloadReport(format, filename) {
    reportStatus.textContent = `Preparing ${format.toUpperCase()} export...`;
    try {
        const response = await fetch(`/api/reports?format=${format}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Unable to export report');
        }

        const downloadUrl = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
        reportStatus.textContent = `${filename} downloaded.`;
    } catch (error) {
        reportStatus.textContent = error.message || 'Unable to export report.';
    }
}

document.getElementById('generateReportBtn')?.addEventListener('click', generateReport);
document.getElementById('exportPdfBtn')?.addEventListener('click', () => downloadReport('pdf', 'financial_statement_analysis.pdf'));
document.getElementById('exportExcelBtn')?.addEventListener('click', () => downloadReport('xlsx', 'financial_statement_analysis.xlsx'));