document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('apiKey');
    const saveKeyBtn = document.getElementById('saveKey');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const promptInput = document.getElementById('promptInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultContainer = document.getElementById('resultContainer');
    const loadingDiv = document.getElementById('loading');
    const resultText = document.getElementById('resultText');

    // Load saved API Key, Prompt, and Images
    chrome.storage.sync.get(['geminiApiKey'], (result) => {
        if (result.geminiApiKey) {
            apiKeyInput.value = result.geminiApiKey;
        }
    });

    chrome.storage.local.get(['savedPrompt', 'savedImages'], (result) => {
        if (result.savedPrompt) {
            promptInput.value = result.savedPrompt;
        }
        if (result.savedImages && Array.isArray(result.savedImages)) {
            selectedFiles = result.savedImages;
            if (selectedFiles.length > 0) {
                updateThumbnails();
            }
        }
    });

    // Save API Key
    saveKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            chrome.storage.sync.set({ geminiApiKey: key }, () => {
                alert('API Key saved!');
            });
        }
    });

    // Save Prompt on change
    promptInput.addEventListener('input', (e) => {
        chrome.storage.local.set({ savedPrompt: e.target.value });
    });

    // Handle Image Selection
    const dropZone = document.getElementById('dropZone');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const dropZonePrompt = document.querySelector('.drop-zone__prompt');

    let selectedFiles = []; // Store objects: { data: base64 (no prefix), mimeType: string, prefix: string }

    // Click to upload
    dropZone.addEventListener('click', () => {
        imageInput.click();
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFiles(e.target.files);
        }
    });

    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-zone--over');
    });

    // Drag leave
    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, (e) => {
            dropZone.classList.remove('drop-zone--over');
        });
    });

    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-zone--over');

        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    async function handleFiles(files) {
        const rawFiles = Array.from(files).filter(file => file.type.startsWith('image/'));

        if (rawFiles.length === 0) {
            alert("Please select valid image files.");
            return;
        }

        // Convert to Base64 objects immediately
        const newImages = await Promise.all(rawFiles.map(async (file) => {
            const fullBase64 = await toBase64(file);
            return {
                data: fullBase64.split(',')[1],
                mimeType: file.type,
                prefix: fullBase64.split(',')[0] + ',' // Keep prefix for display
            };
        }));

        selectedFiles = newImages; // Replace or Append? User probably expects replace if selecting new, but maybe append? Let's replace for simplicity consistent with standard file input, or maybe append?
        // Standard inputs replace. Let's stick to replace for now or append?
        // Let's Append if drag/drop, but input[type=file] usually replaces. 
        // Let's just create a new set for now to align with "resetting" state if user picks new files.
        // Actually, let's keep it simple: Replace current selection with new selection.

        // Save to storage
        chrome.storage.local.set({ savedImages: selectedFiles });

        updateThumbnails();
    }

    function updateThumbnails() {
        imagePreviewContainer.innerHTML = ''; // Clear existing

        if (selectedFiles.length === 0) {
            imagePreviewContainer.hidden = true;
            dropZonePrompt.hidden = false;
            return;
        }

        imagePreviewContainer.hidden = false;
        dropZonePrompt.hidden = true;

        selectedFiles.forEach(fileObj => {
            const img = document.createElement('img');
            img.src = fileObj.prefix + fileObj.data;
            img.classList.add('preview-image');
            imagePreviewContainer.appendChild(img);
        });
    }

    // Analyze Image
    analyzeBtn.addEventListener('click', async () => {
        const apiKey = apiKeyInput.value.trim();
        const prompt = promptInput.value.trim() || "Describe these images";

        if (!apiKey) {
            alert('Please enter and save your Gemini API Key');
            return;
        }

        if (selectedFiles.length === 0) {
            alert('Please select at least one image');
            return;
        }

        resultContainer.hidden = false;
        loadingDiv.hidden = false;
        resultText.innerText = '';

        try {
            // selectedFiles is already in the format we need (array of { data, mimeType })
            const response = await callGeminiAPI(apiKey, selectedFiles, prompt);

            if (response.error) {
                resultText.innerText = `Error: ${response.error.message}`;
            } else {
                const text = response.candidates[0].content.parts[0].text;
                resultText.innerText = text;
            }
        } catch (error) {
            resultText.innerText = `Error: ${error.message}`;
        } finally {
            loadingDiv.hidden = true;
        }
    });

    function toBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    async function callGeminiAPI(apiKey, images, prompt) {
        // Using Gemini 2.0 Flash (Experimental) as requested
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${apiKey}`;

        // Construct parts: Prompt first, then all images
        const parts = [{ text: prompt }];

        images.forEach(img => {
            parts.push({
                inline_data: {
                    mime_type: img.mimeType,
                    data: img.data
                }
            });
        });

        const data = {
            contents: [{
                parts: parts
            }]
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    }
});
