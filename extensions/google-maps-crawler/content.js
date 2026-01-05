// Fast content script - optimized for speed
(function () {
    'use strict';

    const EXTENSION_ID = 'GMAPS_IMG_CRAWLER_2024';

    if (window[EXTENSION_ID]) {
        console.log('Content script already loaded');
        return;
    }
    window[EXTENSION_ID] = true;

    console.log('✅ Fast content script loaded');

    let isExtracting = false;

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (!message || message.extensionId !== EXTENSION_ID) {
            return false;
        }

        if (message.action === 'extractImages') {
            if (isExtracting) {
                sendResponse({ success: false, error: 'Đang xử lý...', extensionId: EXTENSION_ID });
                return true;
            }

            isExtracting = true;
            console.log(`🚀 Fast extraction (max: ${message.maxImages})`);

            // Fast extraction - no waiting
            extractImagesFast(message.maxImages)
                .then(imageUrls => {
                    console.log(`✅ Found ${imageUrls.length} images in ${performance.now()}ms`);
                    sendResponse({
                        success: true,
                        imageUrls: imageUrls,
                        address: message.address,
                        extensionId: EXTENSION_ID
                    });
                })
                .catch(error => {
                    console.error('❌ Error:', error);
                    sendResponse({
                        success: false,
                        error: error.message || 'Lỗi khi trích xuất ảnh',
                        extensionId: EXTENSION_ID
                    });
                })
                .finally(() => {
                    isExtracting = false;
                });

            return true;
        }

        return false;
    });

    async function extractImagesFast(maxImages = 20) {
        maxImages = Math.min(maxImages, 50);

        const imageUrls = new Set();

        // NO WAITING - extract immediately
        console.log('Extracting images from current page state...');

        // Get all images at once
        const images = document.querySelectorAll('img');
        console.log(`Found ${images.length} img tags`);

        for (const img of images) {
            if (imageUrls.size >= maxImages) break;

            try {
                const src = img.getAttribute('src');
                if (!src) continue;

                // Quick filters
                if (/logo|icon|marker|branding|\/maps\/vt\//i.test(src)) continue;
                if (!/googleusercontent\.com|ggpht\.com|streetviewpixels|googleapis\.com/i.test(src)) continue;
                if (/=s0|=w48|=h48/i.test(src)) continue;

                // Create high-quality URL
                let highQualityUrl = src;
                if (src.includes('=')) {
                    const baseUrl = src.split('=')[0];
                    if (/streetview|thumbnail/i.test(src)) {
                        highQualityUrl = src.replace(/w\d+-h\d+/g, 'w1200-h600');
                    } else {
                        highQualityUrl = `${baseUrl}=w2048-h2048`;
                    }
                }

                imageUrls.add(highQualityUrl);
            } catch (e) {
                continue;
            }
        }

        const result = Array.from(imageUrls).slice(0, maxImages);
        console.log(`Extraction complete: ${result.length} images`);
        return result;
    }

})();
