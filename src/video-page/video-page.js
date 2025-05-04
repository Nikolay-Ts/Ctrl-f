// Wait for DOM loaded so we can bail early if storage is missing
window.addEventListener('DOMContentLoaded', () => {
    // Allow either key name, depending on which you set in submitVideo()
    const rawUrl = sessionStorage.getItem('videoUrl') || sessionStorage.getItem('url');
    const tsString = sessionStorage.getItem('timestamp');

    if (!rawUrl) {
        alert('No video URL found in sessionStorage.');
        return window.location.href = '/src/landing-page/landing-page.html';
    }
    if (!tsString || isNaN(parseFloat(tsString))) {
        alert('No valid timestamp found in sessionStorage.');
        return window.location.href = '/src/landing-page/landing-page.html';
    }
});

// Called by the YouTube IFrame API once it has loaded
function onYouTubeIframeAPIReady() {
    // Same storage lookup as above
    const rawUrl = sessionStorage.getItem('videoUrl') || sessionStorage.getItem('url');
    const timestamp = parseFloat(sessionStorage.getItem('timestamp'));

    // Extract the 11-char video ID
    const videoId = extractVideoID(rawUrl);
    if (!videoId) {
        console.error('Invalid YouTube URL:', rawUrl);
        return;
    }

    // Instantiate the player
    new YT.Player('player', {
        videoId,
        playerVars: {
            autoplay: 1,       // autoplay on load
            playsinline: 1,       // inline on iOS
            modestbranding: 1,    // remove YouTube logo
            rel: 0,               // no related videos at end
            start: timestamp     // jump to stored timestamp
        }
    });
}

// Helper: pull out the ID from a watch/short/embed URL
function extractVideoID(url) {
    const m = url.match(/(?:v=|\/embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})/);
    return m ? m[1] : null;
}