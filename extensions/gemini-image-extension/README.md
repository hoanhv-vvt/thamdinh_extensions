# Gemini Image Analyzer Extension

This is a Chrome extension that allows you to analyze images using Google's Gemini API directly from your browser. You can upload an image, provide a prompt, and get a text response describing or analyzing the image.

## Installation

1.  **Clone or Download** this repository to your local machine.
2.  Open Google Chrome and navigate to `chrome://extensions/`.
3.  Enable **Developer mode** in the top right corner of the extension page.
4.  Click the **Load unpacked** button.
5.  Select the `extensions/gemini-image-extension` directory (the folder containing this `README.md` file).

## Configuration

To use this extension, you need a Google Gemini API Key.

1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key.
2.  Click the extension icon in your Chrome toolbar.
3.  Paste your API Key into the "Gemini API Key" field.
4.  Click **Save Key**. The key will be stored locally in your browser storage.

## Usage

1.  Click the extension icon to open the popup.
2.  **Choose Image**: Click the button to upload an image from your computer. A preview will appear.
3.  **Prompt**: Enter a question or instruction about the image (e.g., "What ingredients are in this food?", "Extract text from this image"). The default is "Describe this image".
4.  **Analyze**: Click the "Analyze Image" button.
5.  Wait a moment for the AI to process. The result will appear below.

## Troubleshooting

-   **Error: API Key not valid**: Ensure you have copied the key correctly and that it has permission to use the Gemini API.
-   **Network Error**: Check your internet connection.
-   **Image issues**: Ensure the image is a valid format (JPEG, PNG, WEBP) and not too large.

---
*Powered by Google Gemini*
