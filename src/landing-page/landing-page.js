// Handle drag & drop
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(Array.from(e.target.files));
});

function handleFiles(files) {
    const pdfs = files.filter(file => file.type === 'application/pdf');
    if (pdfs.length) {
        alert(`${pdfs.length} PDF file(s) added.`);
    } else {
        alert('Please upload only PDF files.');
    }
}

// Auto-resize textarea
const promptInput = document.getElementById('promptInput');
promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = `${promptInput.scrollHeight}px`;
});