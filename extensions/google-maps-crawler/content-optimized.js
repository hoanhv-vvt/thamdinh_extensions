// Ultra-fast content script - optimized for speed
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
            const startTime = performance.now();
            console.log(`🚀 Fast extraction (max: ${message.maxImages})`);

            extractImagesFast(message.maxImages)
                .then(imageUrls => {
                    const elapsed = Math.round(performance.now() - startTime);
                    console.log(`✅ Found ${imageUrls.length} images in ${elapsed}ms`);
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
            try {
                // Timeout wrapper - max 12 seconds
                const result = await Promise.race([
                    extractFromMultipleResults(searchResults, maxImages),
                    new Promise((_, reject) =>
                        setTimeout(() => reject(new Error('Timeout')), 12000)
                    )
                ]);
                return result;
            } catch (error) {
                console.warn('⚠️ Multi-result timed out, falling back:', error.message);
                return await extractImagesFromCurrentPage(maxImages);
            }
        } else {
            console.log('📍 Single result or direct location, extracting normally...');
            return await extractImagesFromCurrentPage(maxImages);
        }
    }

    function detectSearchResults() {
        const selectors = [
            'div[role="article"] a[href*="/maps/place/"]',
            'a[aria-label][href*="/maps/place/"]',
            'div.Nv2PK a[href*="/maps/place/"]',
        ];

        for (const selector of selectors) {
            const results = document.querySelectorAll(selector);
            if (results.length > 1) {
                console.log(`Found ${results.length} results using selector: ${selector}`);
                return Array.from(results).slice(0, 2); // Only 2 locations for speed
            }
        }

        console.log('No multiple results detected');
        return null;
    }

    async function extractFromMultipleResults(searchResults, maxImages) {
        const allImageUrls = new Set();
        const imagesPerLocation = Math.ceil(maxImages / searchResults.length);

        for (let i = 0; i < searchResults.length; i++) {
            if (allImageUrls.size >= maxImages) break;

            console.log(`📍 Processing location ${i + 1}/${searchResults.length}...`);

            try {
                // Click on the search result
                searchResults[i].click();

                // Dynamic wait - stop when panel appears (max 1s)
                await waitForPanelLoad(800);

                // Optimized image wait with shorter timeout
                await waitForImagesReadyOptimized(imagesPerLocation, 1000);

                // Extract images from this location
                const locationImages = await extractImagesFromCurrentPage(imagesPerLocation);
                console.log(`✅ Found ${locationImages.length} images from location ${i + 1}`);

                locationImages.forEach(url => allImageUrls.add(url));

                // Early stopping
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
        console.log(`🎉 Total: ${result.length} images from ${searchResults.length} locations`);
        return result;
    }

    /**
     * Wait for detail panel to load - OPTIMIZED
     * Uses MutationObserver instead of fixed timeout
     */
    function waitForPanelLoad(maxWait = 800) {
        return new Promise((resolve) => {
            const startTime = Date.now();

            // Look for detail panel indicators
            const checkPanel = () => {
                const panel = document.querySelector('[role="main"]') ||
                    document.querySelector('.m6QErb') ||
                    document.querySelector('[aria-label*="Photos"]');

                if (panel) {
                    console.log('✅ Panel loaded');
                    resolve();
                    return true;
                }
                return false;
            };

            // Check immediately
            if (checkPanel()) return;

            // Use MutationObserver for efficiency
            const observer = new MutationObserver(() => {
                if (checkPanel()) {
                    observer.disconnect();
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            // Fallback timeout
            setTimeout(() => {
                observer.disconnect();
                resolve();
            }, maxWait);
        });
    }

    /**
     * OPTIMIZED: Wait for images using MutationObserver instead of polling
     */
    async function waitForImagesReadyOptimized(targetCount, maxWaitTime = 1000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            let stableTimer = null;

            const checkImages = () => {
                const validImages = getValidImageCount();

                // Early exit if enough images
                if (validImages >= targetCount) {
                    console.log(`✅ Reached target: ${validImages} images`);
                    cleanup();
                    resolve();
                    return true;
                }

                // Stability check - if no changes in 300ms, we're done
                clearTimeout(stableTimer);
                stableTimer = setTimeout(() => {
                    if (validImages > 0) {
                        console.log(`✅ Stable at ${validImages} images`);
                        cleanup();
                        resolve();
                    }
                }, 300); // Reduced from 2s to 300ms

                return false;
            };

            const cleanup = () => {
                if (observer) observer.disconnect();
                clearTimeout(stableTimer);
                clearTimeout(maxTimeout);
            };

            // Use MutationObserver to detect new images
            const observer = new MutationObserver(() => {
                checkImages();
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['src']
            });

            // Initial check
            checkImages();

            // Max timeout
            const maxTimeout = setTimeout(() => {
                const count = getValidImageCount();
                console.log(`⏱️ Timeout after ${Date.now() - startTime}ms, found ${count} images`);
                cleanup();
                resolve();
            }, maxWaitTime);
        });
    }

    /**
     * Count valid Google Maps images - OPTIMIZED with caching
     */
    function getValidImageCount() {
        // Use more specific selector instead of all img tags
        const images = document.querySelectorAll('img[src*="googleusercontent"], img[src*="ggpht"], img[src*="googleapis"]');
        let count = 0;

        for (const img of images) {
            const src = img.getAttribute('src');
            if (!src) continue;

            // Quick negative filters first (faster regex)
            if (/logo|icon|marker|branding|\/maps\/vt\/|=s0|=w48|=h48/i.test(src)) continue;

            count++;
        }

        return count;
    }

    /**
     * Extract images from current page - OPTIMIZED
     */
    async function extractImagesFromCurrentPage(maxImages) {
        // Don't wait again if we just waited in the caller
        const imageUrls = new Set();

        // Use specific selector instead of all img tags
        const images = document.querySelectorAll('img[src*="googleusercontent"], img[src*="ggpht"], img[src*="googleapis"], img[src*="streetviewpixels"]');
        console.log(`Found ${images.length} Google Maps images`);

        for (const img of images) {
            if (imageUrls.size >= maxImages) break;

            try {
                const src = img.getAttribute('src');
                if (!src) continue;

                // Quick filters - negative first
                if (/logo|icon|marker|branding|\/maps\/vt\/|=s0|=w48|=h48/i.test(src)) continue;

                // Create high-quality URL
                let highQualityUrl = src;
                if (src.includes('=')) {
                    const baseUrl = src.split('=')[0];
                    highQualityUrl = /streetview|thumbnail/i.test(src)
                        ? src.replace(/w\d+-h\d+/g, 'w1200-h600')
                        : `${baseUrl}=w2048-h2048`;
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
