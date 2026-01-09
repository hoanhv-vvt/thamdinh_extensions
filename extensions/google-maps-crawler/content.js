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

        // Check if there are multiple search results
        const searchResults = detectSearchResults();

        if (searchResults && searchResults.length > 1) {
            console.log(`🔍 Found ${searchResults.length} search results, processing all...`);
            return await extractFromMultipleResults(searchResults, maxImages);
        } else {
            console.log('📍 Single result or direct location, extracting normally...');
            return await extractImagesFromCurrentPage(maxImages);
        }
    }

    /**
     * Detect if there are multiple search results on the page
     */
    function detectSearchResults() {
        // Wait a bit for results to render
        const selectors = [
            'div[role="article"] a[href*="/maps/place/"]', // Search result links
            'a[aria-label][href*="/maps/place/"]',
            'div.Nv2PK a[href*="/maps/place/"]',
        ];

        for (const selector of selectors) {
            const results = document.querySelectorAll(selector);
            if (results.length > 1) {
                console.log(`Found ${results.length} results using selector: ${selector}`);
                // Limit to 3 results to prevent timeout
                return Array.from(results).slice(0, 3);
            }
        }

        console.log('No multiple results detected');
        return null;
    }

    /**
     * Extract images from multiple search results by clicking each one
     */
    async function extractFromMultipleResults(searchResults, maxImages) {
        const allImageUrls = new Set();
        const imagesPerLocation = Math.ceil(maxImages / searchResults.length);

        for (let i = 0; i < searchResults.length; i++) {
            if (allImageUrls.size >= maxImages) break;

            console.log(`📍 Processing location ${i + 1}/${searchResults.length}...`);

            try {
                // Click on the search result
                const result = searchResults[i];
                result.click();

                // Reduced wait time - 800ms is enough for detail panel
                console.log('⏳ Waiting for location details to load...');
                await new Promise(resolve => setTimeout(resolve, 800));

                // Wait for images with reduced timeout
                await waitForImagesReady(imagesPerLocation, 1500);

                // Extract images from this location
                const locationImages = await extractImagesFromCurrentPage(imagesPerLocation);
                console.log(`✅ Found ${locationImages.length} images from location ${i + 1}`);

                // Add to the combined set
                locationImages.forEach(url => allImageUrls.add(url));

                // If we got enough images, stop early
                if (allImageUrls.size >= maxImages) {
                    console.log(`🎯 Reached target of ${maxImages} images, stopping early`);
                    break;
                }

            } catch (e) {
                console.error(`❌ Error processing location ${i + 1}:`, e);
                continue;
            }
        }

        const result = Array.from(allImageUrls).slice(0, maxImages);
        console.log(`🎉 Total extraction complete: ${result.length} images from ${searchResults.length} locations`);
        return result;
    }

    /**
     * Extract images from the current page state
     */
    async function extractImagesFromCurrentPage(maxImages) {
        // Wait for images to load with intelligent monitoring
        console.log('Waiting for images to load...');
        await waitForImagesReady(maxImages, 3000); // max 3s wait

        const imageUrls = new Set();

        // Get all images after waiting
        const images = document.querySelectorAll('img');
        console.log(`Found ${images.length} img tags after waiting`);

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

    /**
     * Wait for images to load by monitoring count stability
     * @param {number} targetCount - Target number of images to wait for
     * @param {number} maxWaitTime - Maximum time to wait in ms
     */
    async function waitForImagesReady(targetCount, maxWaitTime = 3000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            let lastCount = 0;
            let stableCount = 0;

            const checkInterval = setInterval(() => {
                // Count valid Google Maps images
                const images = document.querySelectorAll('img');
                let validCount = 0;

                for (const img of images) {
                    const src = img.getAttribute('src');
                    if (!src) continue;

                    // Only count Google Maps images
                    if (/googleusercontent\.com|ggpht\.com|streetviewpixels|googleapis\.com/i.test(src)) {
                        validCount++;
                    }
                }

                console.log(`Image count: ${validCount} (stable: ${stableCount}/4)`);

                // Check if count has stabilized
                if (validCount === lastCount && validCount > 0) {
                    stableCount++;
                } else {
                    stableCount = 0;
                }

                lastCount = validCount;

                // Stop conditions
                const elapsed = Date.now() - startTime;
                const isStable = stableCount >= 4; // Stable for 2 seconds (4 * 500ms)
                const hasEnough = validCount >= targetCount;
                const timeout = elapsed >= maxWaitTime;

                if (isStable || hasEnough || timeout) {
                    clearInterval(checkInterval);

                    if (isStable) {
                        console.log(`✅ Image count stable at ${validCount}`);
                    } else if (hasEnough) {
                        console.log(`✅ Reached target count: ${validCount}`);
                    } else {
                        console.log(`⏱️ Timeout after ${elapsed}ms, found ${validCount} images`);
                    }

                    resolve();
                }
            }, 500); // Check every 500ms
        });
    }

})();
