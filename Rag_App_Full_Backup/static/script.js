const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const dropZoneText = document.getElementById('dropZoneText');
const processBtn = document.getElementById('processBtn');
const resultsContent = document.getElementById('resultsContent');
const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');

let selectedFile = null;

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('active');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

function handleFile(file) {
    selectedFile = file;
    dropZoneText.innerHTML = `<span style="color: #818cf8; font-weight: 500;">${file.name}</span>`;
    processBtn.disabled = false;
}

processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // UI States
    emptyState.classList.add('hidden');
    resultsContent.classList.add('hidden');
    loadingState.classList.remove('hidden');
    processBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to process document');

        const result = await response.json();

        // Update Results
        document.getElementById('resName').textContent = result.name;
        document.getElementById('resRoll').textContent = result.roll_number;
        document.getElementById('resPages').textContent = result.page_count + (result.page_count === 1 ? ' Page' : ' Pages');
        document.getElementById('resMarks').textContent = result.marks;
        document.getElementById('resStatus').textContent = result.status;

        if (result.error) {
            const syncBanner = document.getElementById('syncBanner');
            syncBanner.style.background = 'rgba(239, 68, 68, 0.1)';
            syncBanner.style.borderColor = 'rgba(239, 68, 68, 0.2)';
            syncBanner.style.color = '#f87171';
            document.getElementById('resStatus').textContent = result.error;
            document.getElementById('syncIcon').innerHTML = '<i data-lucide="alert-circle"></i>';
            lucide.createIcons();
        } else {
            const syncBanner = document.getElementById('syncBanner');
            syncBanner.style.background = 'rgba(16, 185, 129, 0.05)';
            syncBanner.style.borderColor = 'rgba(16, 185, 129, 0.1)';
            syncBanner.style.color = '#10b981';
            document.getElementById('syncIcon').innerHTML = '<i data-lucide="check-circle-2"></i>';
            lucide.createIcons();
        }



        // Show Results
        loadingState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

    } catch (error) {
        console.error("Frontend Error:", error);
        alert(`Process Error: ${error.message || 'Unknown error'}. Please check your .env file and backend console.`);
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
    }
    finally {
        processBtn.disabled = false;
    }
});
