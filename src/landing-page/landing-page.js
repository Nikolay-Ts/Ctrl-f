const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const promptInput = document.getElementById('promptInput');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

dropZone.addEventListener('dragover', () => {
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', e => {
    dropZone.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

fileInput.addEventListener('change', e => {
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

promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = `${promptInput.scrollHeight}px`;
});