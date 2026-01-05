// Popup script - Display image links instead of downloading
const addressInput = document.getElementById('address');
const maxImagesInput = document.getElementById('maxImages');
const startBtn = document.getElementById('startBtn');
const statusSection = document.getElementById('status');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');
const statusDetails = document.getElementById('statusDetails');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const resultsSection = document.getElementById('results');
const imageGrid = document.getElementById('imageGrid');
const imageCountSpan = document.getElementById('imageCount');
const copyAllBtn = document.getElementById('copyAllBtn');

const EXTENSION_ID = 'GMAPS_IMG_CRAWLER_2024';
let currentTabId = null;
let startTime = 0;
let pageLoadListener = null;
let imageUrls = [];

function updateStatus(icon, text, details = '', showProgress = false) {
    statusSection.classList.remove('hidden');
    statusIcon.textContent = icon;
    statusText.textContent = text;
    statusDetails.textContent = details;
    progressBar.classList.toggle('hidden', !showProgress);
}

function updateProgress(percent) {
    progressFill.style.width = `${percent}%`;
}

function clearResults() {
    imageGrid.innerHTML = '';
    resultsSection.classList.add('hidden');
    imageUrls = [];
    imageCountSpan.textContent = '0';
}

async function startCrawling() {
    const address = addressInput.value.trim();
    const maxImages = Math.min(parseInt(maxImagesInput.value) || 10, 50);

    if (!address) {
        updateStatus('⚠️', 'Lỗi', 'Vui lòng nhập địa chỉ!');
        return;
    }

    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="spinner"></span> Đang xử lý...';
    clearResults();
    startTime = Date.now();

    updateStatus('🔍', 'Đang mở Google Maps...', `Địa chỉ: ${address}`);

    try {
        const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(address)}`;

        const tab = await chrome.tabs.create({
            url: mapsUrl,
            active: false
        });
        currentTabId = tab.id;

        updateStatus('⏳', 'Đang tải trang...', 'Chờ trang load xong...', true);
        updateProgress(20);

        setupPageLoadListener(maxImages, address);

    } catch (error) {
        console.error('Error:', error);
        updateStatus('❌', 'Lỗi', error.message);
        resetButton();
    }
}

function setupPageLoadListener(maxImages, address) {
    if (pageLoadListener) {
        chrome.tabs.onUpdated.removeListener(pageLoadListener);
    }

    pageLoadListener = function (tabId, changeInfo, tab) {
        if (tabId !== currentTabId) return;

        if (changeInfo.status === 'complete') {
            console.log('✅ Page loaded');
            chrome.tabs.onUpdated.removeListener(pageLoadListener);
            pageLoadListener = null;

            setTimeout(() => {
                sendExtractionMessage(maxImages, address);
            }, 1500);
        }
    };

    chrome.tabs.onUpdated.addListener(pageLoadListener);

    setTimeout(() => {
        if (pageLoadListener) {
            console.log('⏱️ Timeout, forcing extraction');
            chrome.tabs.onUpdated.removeListener(pageLoadListener);
            pageLoadListener = null;
            sendExtractionMessage(maxImages, address);
        }
    }, 10000);
}

function sendExtractionMessage(maxImages, address) {
    updateStatus('📸', 'Đang tìm ảnh...', 'Trích xuất links...', true);
    updateProgress(40);

    chrome.tabs.sendMessage(currentTabId, {
        action: 'extractImages',
        maxImages: maxImages,
        address: address,
        extensionId: EXTENSION_ID
    }, (response) => {
        if (chrome.runtime.lastError) {
            console.error('Error:', chrome.runtime.lastError);
            updateStatus('❌', 'Lỗi', 'Không thể kết nối. Tab vẫn mở.');
            resetButton();
            return;
        }

        if (!response || response.extensionId !== EXTENSION_ID) {
            updateStatus('❌', 'Lỗi', 'Phản hồi không hợp lệ');
            resetButton();
            return;
        }

        handleResponse(response);
    });
}

function handleResponse(response) {
    if (!response.success) {
        updateStatus('❌', 'Lỗi', response.error || 'Không thể trích xuất ảnh');
        resetButton();
        return;
    }

    imageUrls = response.imageUrls || [];
    updateProgress(80);

    if (imageUrls.length === 0) {
        updateStatus('⚠️', 'Không tìm thấy ảnh', 'Trang có thể chưa load đủ ảnh');
        resetButton();
        return;
    }

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    updateProgress(100);
    updateStatus('✅', 'Hoàn thành!', `Tìm thấy ${imageUrls.length} ảnh trong ${elapsed}s`);

    displayImageLinks(imageUrls);

    // Close tab
    if (currentTabId) {
        chrome.tabs.remove(currentTabId, () => {
            if (!chrome.runtime.lastError) {
                console.log('✅ Tab closed');
            }
        });
    }

    resetButton();
}

function displayImageLinks(urls) {
    resultsSection.classList.remove('hidden');
    imageCountSpan.textContent = urls.length;

    const imageGrid = document.getElementById('imageGrid');
    imageGrid.innerHTML = '';

    urls.forEach((url, index) => {
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';

        // Image container
        const imgContainer = document.createElement('div');
        imgContainer.className = 'img-container';

        const img = document.createElement('img');
        img.src = url;
        img.alt = `Image ${index + 1}`;
        img.loading = 'lazy';
        img.onerror = function () {
            this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EError%3C/text%3E%3C/svg%3E';
        };

        imgContainer.appendChild(img);

        // Image info
        const imageInfo = document.createElement('div');
        imageInfo.className = 'image-info';

        const imageNumber = document.createElement('span');
        imageNumber.className = 'image-number';
        imageNumber.textContent = `#${index + 1}`;

        const actionButtons = document.createElement('div');
        actionButtons.className = 'action-buttons';

        // Copy link button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'action-btn';
        copyBtn.innerHTML = '📋';
        copyBtn.title = 'Copy link';
        copyBtn.onclick = (e) => {
            e.stopPropagation();
            copyToClipboard(url, copyBtn);
        };

        // Open in new tab button
        const openBtn = document.createElement('button');
        openBtn.className = 'action-btn';
        openBtn.innerHTML = '🔗';
        openBtn.title = 'Mở ảnh';
        openBtn.onclick = (e) => {
            e.stopPropagation();
            window.open(url, '_blank');
        };

        actionButtons.appendChild(copyBtn);
        actionButtons.appendChild(openBtn);

        imageInfo.appendChild(imageNumber);
        imageInfo.appendChild(actionButtons);

        imageCard.appendChild(imgContainer);
        imageCard.appendChild(imageInfo);

        // Click to open full image
        imageCard.onclick = () => {
            window.open(url, '_blank');
        };

        imageGrid.appendChild(imageCard);
    });
}

function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = '✅';
        button.style.background = '#10b981';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 1000);
    }).catch(err => {
        console.error('Copy failed:', err);
        button.textContent = '❌';
        setTimeout(() => {
            button.textContent = '📋';
        }, 1000);
    });
}

function copyAllLinks() {
    const allLinks = imageUrls.join('\n');
    navigator.clipboard.writeText(allLinks).then(() => {
        const originalText = copyAllBtn.textContent;
        copyAllBtn.textContent = '✅ Đã copy!';
        copyAllBtn.style.background = '#10b981';

        setTimeout(() => {
            copyAllBtn.textContent = originalText;
            copyAllBtn.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Copy all failed:', err);
    });
}

function resetButton() {
    if (pageLoadListener) {
        chrome.tabs.onUpdated.removeListener(pageLoadListener);
        pageLoadListener = null;
    }

    setTimeout(() => {
        startBtn.disabled = false;
        startBtn.innerHTML = '<span class="btn-text">Lấy Links</span>';
    }, 500);
}

// Event listeners
startBtn.addEventListener('click', startCrawling);
copyAllBtn.addEventListener('click', copyAllLinks);

addressInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startCrawling();
});

// Load preferences
chrome.storage.local.get(['maxImages'], (result) => {
    if (result.maxImages) maxImagesInput.value = Math.min(result.maxImages, 50);
});

maxImagesInput.addEventListener('change', () => {
    const value = Math.min(parseInt(maxImagesInput.value) || 10, 50);
    maxImagesInput.value = value;
    chrome.storage.local.set({ maxImages: value });
});
