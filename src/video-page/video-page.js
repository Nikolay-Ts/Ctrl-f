window.addEventListener('DOMContentLoaded', () => {
    const videoUrl = sessionStorage.getItem('url');

    if (!videoUrl) {
        alert("No video URL found in sessionStorage.");
        return;
    }

    const embeded = convertToEmbedUrl(videoUrl);

    document.getElementById("videoFrame").src = embeded;

});

let player;

function onYouTubeIframeAPIReady() {
    const videoUrl = sessionStorage.getItem("videoUrl");
    const embedUrl = convertToEmbedUrl(videoUrl);
    const videoId = extractVideoID(embedUrl);

    player = new YT.Player('player', {
        videoId: videoId,
        playerVars: {
            modestbranding: 1,
            rel: 0
        }
    });
}

function extractVideoID(url) {
    const regex = /(?:embed\/|v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

function seekTo(seconds) {
    if (player && typeof player.seekTo === 'function') {
        player.seekTo(seconds, true); // true = allowSeekAhead
    }
}

function submitPrompt() {
    const prompt = document.getElementById('videoPromptInput').value.trim();
    if (!prompt) {
        alert("Please enter a prompt.");
        return;
    }

    console.log("Submitted prompt:", prompt);
    // TODO: send to backend or store it
}

function convertToEmbedUrl(url) {
    const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? `https://www.youtube.com/embed/${match[1]}` : null;
}

