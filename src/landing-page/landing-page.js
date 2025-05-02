const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filePreviewContainer = document.getElementById('filePreviewContainer');
const dropText = document.getElementById('dropText');

function handleFiles(files) {
    const pdfs = files.filter(file => file.type === 'application/pdf');
    if (!pdfs.length) {
        alert('Please upload only PDF files.');
        return;
    }

    filePreviewContainer.innerHTML = ''; // Clear existing previews

    pdfs.forEach(file => {
        const fileDiv = document.createElement('div');
        fileDiv.classList.add('file-preview');

        fileDiv.innerHTML = `
            <img src="icon.png" alt="PDF Icon">
            <span>${file.name}</span>
        `;

        filePreviewContainer.appendChild(fileDiv);
    });

    dropText.innerHTML = `${pdfs.length} PDF file${pdfs.length > 1 ? 's' : ''} added`;
}

// Drag and drop handlers
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, e => {
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

dropZone.addEventListener('drop', (e) => {
    dropZone.classList.remove('dragover');
    handleFiles(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener('change', (e) => {
    handleFiles(Array.from(e.target.files));
});