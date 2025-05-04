function getUrl() {
    let url = sessionStorage.getItem("url");

    if (!url) {
        window.alert("Sorry there seems to be a big problem!");
        window.location.href = "/src/landing-page/landing-page.html"
    }

    return url;
}

