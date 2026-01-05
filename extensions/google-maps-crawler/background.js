// Simple background service worker
console.log('Background worker started');

// Store current crawl task
let currentCrawl = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background received:', message.action);

    if (message.action === 'startCrawl') {
        currentCrawl = {
            address: message.address,
            maxImages: message.maxImages,
            folderPath: message.folderPath,
            tabId: message.tabId
        };
        sendResponse({ success: true });
    }

    if (message.action === 'downloadImages') {
        const { imageUrls, address, folderPath } = message;
        downloadImages(imageUrls, address, folderPath);
        sendResponse({ success: true });
    }

    return true;
});

function downloadImages(imageUrls, address, folderPath) {
    const safeName = address.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50);
    const folder = folderPath || '';

    imageUrls.forEach((url, index) => {
        const ext = url.match(/\.(jpg|jpeg|png|gif|webp)/i)?.[1] || 'jpg';
        let filename = `google_maps_${safeName}_${String(index + 1).padStart(3, '0')}.${ext}`;

        if (folder) {
            filename = `${folder}/${filename}`;
        }

        chrome.downloads.download({
            url: url,
            filename: filename,
            conflictAction: 'uniquify',
            saveAs: false
        });
    });
}
