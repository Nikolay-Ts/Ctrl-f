const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filePreviewContainer = document.getElementById('filePreviewContainer');
const dropText = document.getElementById('dropText');
const promptInput = document.getElementById('promptInput');
const fileUploadError = document.getElementById('fileUploadError');
const cancelBtn = document.getElementById('cancelBtn');
const fileLimitWarning = document.getElementById('fileLimitWarning');
const actionButtons = document.getElementById('actionButtons');

// Store uploaded files
let uploadedFiles = [];

function handleFiles(files) {
    const pdfs = files.filter(file => file.type === 'application/pdf');

    if (!pdfs.length) return;

    const remainingSlots = 10 - uploadedFiles.length;

    if (pdfs.length > remainingSlots) {
        fileUploadError.classList.remove('d-none');
        return;
    } else {
        fileUploadError.classList.add('d-none');
    }

    const filesToAdd = pdfs.slice(0, remainingSlots);

    filesToAdd.forEach(file => {
        if (!uploadedFiles.some(f => f.name === file.name)) {
            uploadedFiles.push(file);
        }
    });

    updateFilePreview();
}

function updateFilePreview() {
    filePreviewContainer.innerHTML = '';

    uploadedFiles.forEach((file, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.classList.add('file-preview');

        fileDiv.innerHTML = `
            <img src="/src/assets/icon.png" alt="PDF Icon">
            <span class="text-truncate" style="max-width: 120px;">${file.name}</span>
            <button class="btn btn-sm btn-close ms-2" aria-label="Remove file" data-index="${index}"></button>
        `;

        filePreviewContainer.appendChild(fileDiv);
        setTimeout(() => fileDiv.classList.add('loaded'), 10); // triggers CSS transition
    });

    // Update drop zone text
    dropText.innerHTML =
        uploadedFiles.length > 0
            ? `${uploadedFiles.length} PDF file${uploadedFiles.length > 1 ? 's' : ''} added`
            : `Drop PDF files here<br>or click below to upload`;

    // Show/hide warning and cancel button
    fileLimitWarning.classList.toggle('d-none', uploadedFiles.length < 10);
    fileUploadError.classList.toggle('d-none', uploadedFiles.length < 10);
    cancelBtn.classList.toggle('d-none', uploadedFiles.length === 0);

    // Attach delete logic
    filePreviewContainer.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index);
            uploadedFiles.splice(index, 1);
            updateFilePreview();
        });
    });
}

// Drag & Drop handlers
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

// Auto-resize prompt textarea
promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = `${promptInput.scrollHeight}px`;
});

// Cancel button logic
cancelBtn.addEventListener('click', () => {
    uploadedFiles = [];
    updateFilePreview();
});

/**
 * Sends uploaded PDF files to the backend for annotation.
 * Saves the response JSON to sessionStorage under 'annotatedPdfs'.
 * 
 * @param {FileList} files - The uploaded PDF files
 */
async function SubmitPdf() {
    if (uploadedFiles.length > 0) {
        fileUploadError.classList.add('d-none');

        const formData = new FormData();
        for (let i = 0; i < uploadedFiles.length; i++) {
            formData.append('pdfs', uploadedFiles[i]);
        }

        try {
            const response = await fetch("http://34.141.67.42:3000/submit", {
                method: "POST",
                body: formData
            });

            console.log(`Response Code: ${response.status}`);
            const responseText = await response.text();
            console.log(`Response Body: ${responseText}`);

            if (!response.ok) {
                window.alert("Error with the server");
                return;
            }

            const data = await response.json();

            if (!data) {
                window.alert("The data seems to be empty");
                return;
            }

            sessionStorage.setItem("annotatedPdfs", JSON.stringify(data));
        } catch (error) {
            console.error(error);
            window.alert("Error with the server");
        }

    } else {
        fileUploadError.classList.remove('d-none');
    }
}

// Trigger fade-in on page load
window.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('loaded');
});