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
            //storePdfBlobInSession(file);
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

// function storePdfBlobInSession(file) {
//     const reader = new FileReader();
//     reader.onload = () => {
//         // reader.result is a "data:application/pdf;base64,..." string
//         sessionStorage.setItem(
//             `${file.name}`,
//             (reader.result)
//         );
//     };
//     reader.onerror = () => {
//         console.error('Failed to read file:', file.name, reader.error);
//     };
//     reader.readAsDataURL(file);
// }


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

function showLoader() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}
function hideLoader() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

/**
 * Sends uploaded PDF files to the backend for annotation.
 * Saves the response JSON to sessionStorage under 'annotatedPdfs'.
 * 
 * @param {String} query
 * @param {FileList} files - The uploaded PDF files
 */
async function SubmitPdf() {
    if (uploadedFiles.length > 0) {
        fileUploadError.classList.add('d-none');

        const prompt = promptInput.value.trim();
        const formData = new FormData();
        
        totalSize = 0;
        const MAX_SIZE = 5 * 1024 * 1024; // 5MB in bytes

        for (let i = 0; i < uploadedFiles.length; i++) {
            totalSize += uploadedFiles[i].size;

        if (totalSize > MAX_SIZE) {
            alert ("You cannot upload more than 5MB")
            return;
        }
            formData.append('pdfs', uploadedFiles[i]);
        }

        formData.append("prompt", prompt);

        showLoader();

        try {
            const response = await fetch("http://34.141.67.42:3000/submit", {
                method: "POST",
                body: formData
            });


            if (response.status !== 200) {
                window.alert("Error with the server (not 200)");
                return;
            }

            const data = await response.json();
            console.log("Response JSON:", data);

            if (!data) {
                window.alert("The data seems to be empty");
                return;
            }

            sessionStorage.setItem("annotatedPdfs", JSON.stringify(data));
            window.location.href = "/src/chat-view/chat-view.html";
        } catch (error) {
            console.error(error);
            window.alert("Error with the server");
        }
    } else {
        hideLoader();
        fileUploadError.classList.remove('d-none');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('loaded');
});

function showPdf() {
    document.getElementById('pdfSection').classList.remove('d-none');
    document.getElementById('videoSection').classList.add('d-none');
}

function showVideo() {
    document.getElementById('pdfSection').classList.add('d-none');
    document.getElementById('videoSection').classList.remove('d-none');
}

const youtubeUrlInput = document.getElementById('youtubeUrl');
const youtubeLinkWarning = document.getElementById('youtubeLinkWarning');

function validateYouTubeLink() {
    const url = youtubeUrlInput.value.trim();
    if (!url) {
        youtubeLinkWarning.classList.remove('d-none');
        return false;
    } else {
        youtubeLinkWarning.classList.add('d-none');
        return true;
    }
}

function validateVideoPrompt() {
    const prompt = document.getElementById('videoPromptInput').value.trim();
    const promptGuard = document.querySelector('#videoSection #promptGuard');
    const promptGuardpdf = document.querySelector('#pdfSection #promptGuard');

    if (!prompt) {
        promptGuard.classList.remove('d-none');
        promptGuardpdf.classList.remove('d-none');
        return false;
    } else {
        promptGuard.classList.add('d-none');
        promptGuardpdf.classList.remove('d-none');
        return true;
    }
}

youtubeUrlInput.addEventListener('input', () => {
    if (youtubeUrlInput.value.trim()) {
        youtubeLinkWarning.classList.add('d-none');
    }
});

/**
 * 
 * @param {string} prompt
 * @param {string} url
 * 
 * @returns 
 */
async function submitVideo() {
    if (!validateYouTubeLink()) return;
    if (!validateVideoPrompt()) return;

    const url = youtubeUrlInput.value.trim();
    const prompt = promptInput.value.trim();

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("video", url);

    showLoader();

    try {
        const response = await fetch("http://34.141.67.42:3000/submit", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            window.alert("Did not get 200");
            return;
        }

        const data = await response.text();

        if (!data) {
            window.alert("The data seems to be empty");
            return;
        }

        sessionStorage.setItem("timestamp", data);
        sessionStorage.setItem("url", url);
        window.location.href = "/src/video-page/video-page.html"
    } catch (error) {
        hideLoader();
        console.error(error);
        window.alert("Error with the server");
    }
}