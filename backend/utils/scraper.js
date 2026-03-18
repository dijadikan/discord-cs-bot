const axios = require("axios");

async function handleDownload(url, type) {

    // AUTO DETECT
    if (type === "auto") {
        if (url.includes("tiktok")) type = "tiktok";
        else if (url.includes("instagram")) type = "instagram";
        else if (url.includes("youtube")) type = "youtube";
        else if (url.includes("facebook")) type = "facebook";
        else if (url.includes("twitter")) type = "twitter";
    }

    switch (type) {

        case "tiktok":
            return await tiktok(url);

        case "instagram":
            return await instagram(url);

        case "youtube":
            return await youtube(url);

        default:
            throw new Error("Platform not supported yet");
    }
}

// ===== SCRAPER EXAMPLE =====

// TikTok No WM (pakai API publik)
async function tiktok(url) {
    const api = `https://tikwm.com/api/?url=${url}`;
    const res = await axios.get(api);

    return res.data.data.play;
}

// Instagram
async function instagram(url) {
    const api = `https://api.ryzendesu.vip/api/downloader/igdl?url=${url}`;
    const res = await axios.get(api);

    return res.data.data[0].url;
}

// YouTube MP4
async function youtube(url) {
    const api = `https://api.ryzendesu.vip/api/downloader/ytmp4?url=${url}`;
    const res = await axios.get(api);

    return res.data.data.downloadUrl;
}

module.exports = { handleDownload };
