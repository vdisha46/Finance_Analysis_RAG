document.getElementById('uploadForm')?.addEventListener('submit', async function (event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const fileInput = form.querySelector('input[type="file"]');
    const progressBar = document.getElementById('uploadProgress');

    if (!fileInput.files[0]) {
        alert('Select a file to upload');
        return;
    }

    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (!response.ok) {
        alert(data.detail || 'Upload failed');
        return;
    }

    progressBar.style.width = '100%';
    progressBar.textContent = '100%';
    alert(data.message || 'Document uploaded successfully');
    form.reset();
});
