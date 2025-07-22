// AI Banner Maker - Frontend JavaScript

class BannerMaker {
    constructor() {
        this.currentSessionId = null;
        this.uploadedImages = []; // Array to store multiple uploaded images: [{path: string, isExtracted: boolean, id: string}]
        this.pollInterval = null;
        this.currentUrl = null;
        this.currentTempImage = null; // Track temp images for cleanup
        this.selectedCopy = null; // Track selected copy
        this.copyVariants = []; // Store generated copy variants
        this.generatedBackgroundId = null; // Track generated background asset ID
        this.extractedImagePaths = []; // Track extracted images for cleanup after Canva upload
        
        this.initializeEventListeners();
    }

    // Helper function to safely manipulate element classes
    safeToggleClass(elementId, className, add = true) {
        const element = document.getElementById(elementId);
        if (element) {
            if (add) {
                element.classList.add(className);
            } else {
                element.classList.remove(className);
            }
        } else {
            console.warn(`Element with id '${elementId}' not found`);
        }
    }

    // Helper function to copy text to clipboard
    async copyToClipboard(text, description = 'text') {
        try {
            await navigator.clipboard.writeText(text);
            this.showSuccessMessage(`📋 ${description.charAt(0).toUpperCase() + description.slice(1)} copied to clipboard!`);
            console.log(`Successfully copied ${description} to clipboard:`, text);
        } catch (err) {
            // Fallback for older browsers
            try {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showSuccessMessage(`📋 ${description.charAt(0).toUpperCase() + description.slice(1)} copied to clipboard!`);
                console.log(`Successfully copied ${description} to clipboard (fallback):`, text);
            } catch (fallbackErr) {
                console.error('Failed to copy to clipboard:', fallbackErr);
                this.showError(`Failed to copy ${description} to clipboard. Please copy manually.`);
            }
        }
    }

    initializeEventListeners() {
        // Form submission
        const bannerForm = document.getElementById('bannerForm');
        if (bannerForm) {
            bannerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateBanner();
            });
        }

        // File upload
        this.initializeFileUpload();


        // Create another button - reset everything
        const createAnotherBtn = document.getElementById('createAnotherBtn');
        if (createAnotherBtn) {
            createAnotherBtn.addEventListener('click', () => {
                this.resetForm();
            });
        }

        // URL input cache check
        let urlCheckTimeout;
        const urlInput = document.getElementById('url');
        if (urlInput) {
            urlInput.addEventListener('input', (e) => {
                clearTimeout(urlCheckTimeout);
                urlCheckTimeout = setTimeout(() => {
                    this.checkUrlCacheStatus(e.target.value.trim());
                }, 1000); // Check after 1 second of no typing
            });
        }

        // Copy selection mode change (only if element exists)
        const copySelectionMode = document.getElementById('copySelectionMode');
        if (copySelectionMode) {
            copySelectionMode.addEventListener('change', (e) => {
                const isManual = e.target.value === 'manual';
                this.toggleCopyVariantsSection(isManual);
                
                // Reset copy variants display and button when switching modes
                if (isManual) {
                    this.showCopyVariantsPlaceholder();
                } else {
                    this.resetGenerateButton();
                }
            });
        }

        // Extract images button
        const extractImagesBtn = document.getElementById('extractImagesBtn');
        if (extractImagesBtn) {
            extractImagesBtn.addEventListener('click', () => {
                this.extractImages();
            });
        }

        // Generate copy button
        const generateCopyBtn = document.getElementById('generateCopyBtn');
        console.log('Generate Copy button element:', generateCopyBtn);
        if (generateCopyBtn) {
            generateCopyBtn.addEventListener('click', () => {
                console.log('Generate Copy button clicked');
                this.generateCopy();
            });
        } else {
            console.error('Generate Copy button not found!');
        }

        // Generate explanation button
        const generateExplanationBtn = document.getElementById('generateExplanationBtn');
        if (generateExplanationBtn) {
            generateExplanationBtn.addEventListener('click', () => {
                console.log('Generate Explanation button clicked');
                this.generateExplanation();
            });
        }

        // Regenerate copy button
        const regenerateCopyBtn = document.getElementById('regenerateCopyBtn');
        if (regenerateCopyBtn) {
            regenerateCopyBtn.addEventListener('click', () => {
                this.generateCopy();
            });
        }

        // Regenerate explanation button
        const regenerateExplanationBtn = document.getElementById('regenerateExplanationBtn');
        if (regenerateExplanationBtn) {
            regenerateExplanationBtn.addEventListener('click', () => {
                this.generateExplanation();
            });
        }

        // Generate background button
        const generateBackgroundBtn = document.getElementById('generateBackgroundBtn');
        if (generateBackgroundBtn) {
            generateBackgroundBtn.addEventListener('click', () => {
                this.generateBackground();
            });
        }
        
        // Skip background button

        // Regenerate background button
        const regenerateBackgroundBtn = document.getElementById('regenerateBackgroundBtn');
        if (regenerateBackgroundBtn) {
            regenerateBackgroundBtn.addEventListener('click', () => {
                this.generateBackground();
            });
        }
        
        // Send background to existing Canva design button
        const sendBackgroundBtn = document.getElementById('sendBackgroundBtn');
        if (sendBackgroundBtn) {
            sendBackgroundBtn.addEventListener('click', () => {
                this.sendBackgroundToCanva();
            });
        }

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (this.uploadedImagePath) {
                // Use sendBeacon for cleanup on page unload (more reliable than fetch)
                navigator.sendBeacon('/api/cleanup-image', JSON.stringify({
                    image_path: this.uploadedImagePath
                }));
            }
        });
    }


    initializeFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const uploadPreview = document.getElementById('uploadPreview');
        const fileInput = document.getElementById('productImage');
        const removeButton = document.getElementById('removeImage');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Function to handle drag and drop events
        const addDragDropEvents = (element) => {
            element.addEventListener('dragover', (e) => {
                e.preventDefault();
                element.classList.add('drop-zone-active');
            });

            element.addEventListener('dragleave', () => {
                element.classList.remove('drop-zone-active');
            });

            element.addEventListener('drop', (e) => {
                e.preventDefault();
                element.classList.remove('drop-zone-active');
                
                // Check if it's an extracted image (JSON data)
                const imageData = e.dataTransfer.getData('text/plain');
                
                if (imageData && imageData.trim().length > 0) {
                    try {
                        const image = JSON.parse(imageData);
                        // Additional validation to ensure it's actually an extracted image object
                        if (image && typeof image === 'object' && image.src) {
                            console.log('Handling extracted image drop:', image.src);
                            this.handleExtractedImageDrop(image);
                            return;
                        }
                    } catch (e) {
                        // Not JSON, continue with file handling
                        console.log('Failed to parse as JSON, treating as file drop');
                    }
                }
                
                // Handle file drop - support multiple files
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    console.log('Handling file drop:', files.length, 'files');
                    this.handleMultipleFileUpload(Array.from(files));
                }
            });
        };

        // Add drag and drop events to both upload area and preview area
        addDragDropEvents(uploadArea);
        addDragDropEvents(uploadPreview);

        // File input change - handle multiple files
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleMultipleFileUpload(Array.from(e.target.files));
            }
        });

        // Clear all images
        const clearAllButton = document.getElementById('clearAllImages');
        clearAllButton.addEventListener('click', () => {
            this.clearAllImages();
        });
    }

    async handleFileUpload(file) {
        if (!this.isValidImageFile(file)) {
            this.showError('Please upload a valid image file (PNG, JPG, JPEG, GIF, WebP)');
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            this.showError('File size must be less than 16MB');
            return;
        }

        try {
            // Clean up previous upload if exists
            if (this.uploadedImagePath) {
                await this.cleanupUploadedImage(this.uploadedImagePath);
            }

            // Show preview immediately using the grid system - will be updated after upload

            // Upload file to server
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Add to uploaded images array
                this.uploadedImages.push({
                    path: result.filepath,
                    name: file.name,
                    isExtracted: false,
                    id: `uploaded-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
                });

                // Update UI to show uploaded images
                this.updateMultipleImagePreview();
                
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload image: ' + error.message);
            this.removeUploadedImage();
        }
    }

    async removeUploadedImage() {
        // Clean up file from server if exists
        if (this.uploadedImagePath) {
            await this.cleanupUploadedImage(this.uploadedImagePath);
        }

        this.uploadedImagePath = null;
        this.isExtractedImage = false; // Reset extracted image flag
        document.getElementById('uploadArea').classList.remove('hidden');
        document.getElementById('uploadPreview').classList.add('hidden');
        document.getElementById('productImage').value = '';
    }

    async cleanupUploadedImage(imagePath) {
        try {
            const response = await fetch('/api/cleanup-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_path: imagePath
                })
            });

            const result = await response.json();
            if (!result.success && result.error) {
                console.warn('Failed to cleanup image:', result.error);
            }
        } catch (error) {
            console.warn('Error cleaning up image:', error);
        }
    }

    isValidImageFile(file) {
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
        return validTypes.includes(file.type);
    }

    async handleMultipleFileUpload(files) {
        const validFiles = files.filter(file => this.isValidImageFile(file));
        
        if (validFiles.length === 0) {
            this.showError('Please upload valid image files (PNG, JPG, JPEG, GIF, WebP)');
            return;
        }

        // Check file sizes
        const oversizedFiles = validFiles.filter(file => file.size > 16 * 1024 * 1024);
        if (oversizedFiles.length > 0) {
            this.showError(`${oversizedFiles.length} file(s) exceed 16MB limit`);
            return;
        }

        try {
            // Clean up previous uploads if they exist
            await this.clearAllImages();

            // Show immediate local previews for instant feedback
            this.showImmediateLocalPreviews(validFiles);

            // Upload files in parallel while showing progress
            const uploadPromises = validFiles.map(async (file, index) => {
                const tempId = `temp_${Date.now()}_${index}`;
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);

                    const response = await fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (result.success) {
                        const imageData = {
                            path: result.filepath,
                            name: file.name,
                            isExtracted: false,
                            id: `uploaded_${Date.now()}_${index}`
                        };
                        
                        this.uploadedImages.push(imageData);
                        
                        // Update individual preview immediately after upload
                        this.updateSingleImagePreview(imageData, index);
                        
                        return imageData;
                    } else {
                        throw new Error(result.error || `Upload failed for ${file.name}`);
                    }
                } catch (error) {
                    // Mark this preview as failed
                    this.markPreviewAsFailed(index, error.message);
                    throw error;
                }
            });

            await Promise.all(uploadPromises);
            
            this.showSuccessMessage(`Successfully uploaded ${validFiles.length} image(s)`);

        } catch (error) {
            console.error('Multiple upload error:', error);
            this.showError('Failed to upload some images: ' + error.message);
            // Don't clear all images, just remove failed ones
        }
    }

    showImmediateLocalPreviews(files) {
        // Hide upload area and show preview immediately
        document.getElementById('uploadArea').classList.add('hidden');
        const uploadPreview = document.getElementById('uploadPreview');
        uploadPreview.classList.remove('hidden');

        // Update the count
        document.getElementById('uploadedCount').textContent = files.length;

        // Get the grid container
        const uploadedImagesGrid = document.getElementById('uploadedImagesGrid');
        
        // Generate preview HTML with local file previews
        uploadedImagesGrid.innerHTML = files.map((file, index) => {
            const objectUrl = URL.createObjectURL(file);
            return `
                <div class="image-item relative" data-index="${index}">
                    <div class="relative">
                        <img src="${objectUrl}" 
                             alt="${file.name}" 
                             class="w-full h-24 object-cover rounded-lg border border-gray-300">
                        <div class="absolute inset-0 bg-blue-500 bg-opacity-20 rounded-lg flex items-center justify-center">
                            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                        </div>
                    </div>
                    <div class="mt-1 text-xs text-gray-600 truncate px-1" title="${file.name}">
                        ${file.name}
                    </div>
                    <div class="text-xs text-blue-600 px-1">Uploading...</div>
                </div>
            `;
        }).join('');
    }

    updateSingleImagePreview(imageData, index) {
        const uploadedImagesGrid = document.getElementById('uploadedImagesGrid');
        const imageItem = uploadedImagesGrid.querySelector(`[data-index="${index}"]`);
        
        if (imageItem) {
            // Update the preview with uploaded image and remove loading state
            imageItem.innerHTML = `
                <img src="/uploads/${imageData.path.split('/').pop()}" 
                     alt="${imageData.name}" 
                     class="w-full h-24 object-cover rounded-lg border border-gray-300">
                <div class="absolute top-1 right-1">
                    <button type="button" 
                            class="remove-single-image bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors" 
                            data-image-index="${this.uploadedImages.length - 1}"
                            title="Remove ${imageData.name}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="mt-1 text-xs text-gray-600 truncate px-1" title="${imageData.name}">
                    ${imageData.name}
                </div>
                <div class="text-xs text-green-600 px-1">Uploaded ✓</div>
            `;
            
            // Add event listener for remove button
            const removeButton = imageItem.querySelector('.remove-single-image');
            if (removeButton) {
                removeButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const imageIndex = parseInt(e.target.closest('.remove-single-image').getAttribute('data-image-index'));
                    this.removeSingleImage(imageIndex);
                });
            }
            
            // Set the first image as the primary one for backward compatibility
            if (this.uploadedImages.length === 1) {
                this.uploadedImagePath = imageData.path;
            }
        }
    }

    markPreviewAsFailed(index, errorMessage) {
        const uploadedImagesGrid = document.getElementById('uploadedImagesGrid');
        const imageItem = uploadedImagesGrid.querySelector(`[data-index="${index}"]`);
        
        if (imageItem) {
            // Update the preview to show error state
            const statusDiv = imageItem.querySelector('.text-xs:last-child');
            if (statusDiv) {
                statusDiv.textContent = 'Failed ✗';
                statusDiv.className = 'text-xs text-red-600 px-1';
            }
            
            // Remove loading overlay
            const loadingOverlay = imageItem.querySelector('.absolute.inset-0');
            if (loadingOverlay) {
                loadingOverlay.remove();
            }
        }
    }

    async clearAllImages() {
        // Clean up all uploaded images from server
        const cleanupPromises = this.uploadedImages.map(imageData => 
            this.cleanupUploadedImage(imageData.path)
        );
        
        await Promise.all(cleanupPromises);

        // Reset arrays and UI state
        this.uploadedImages = [];
        this.uploadedImagePath = null;
        this.isExtractedImage = false;

        // Reset UI to initial state
        document.getElementById('uploadArea').classList.remove('hidden');
        document.getElementById('uploadPreview').classList.add('hidden');
        
        // Clear the uploaded images grid
        const uploadedImagesGrid = document.getElementById('uploadedImagesGrid');
        if (uploadedImagesGrid) {
            uploadedImagesGrid.innerHTML = '';
        }
        
        // Reset the uploaded count
        const uploadedCount = document.getElementById('uploadedCount');
        if (uploadedCount) {
            uploadedCount.textContent = '0';
        }
        
        // Reset the file input
        document.getElementById('productImage').value = '';

        console.log('All images cleared');
    }

    updateMultipleImagePreview() {
        console.log('updateMultipleImagePreview called, uploadedImages.length:', this.uploadedImages.length);
        
        if (this.uploadedImages.length === 0) {
            console.log('No uploaded images, skipping preview update');
            return;
        }

        // Hide upload area and show preview
        const uploadArea = document.getElementById('uploadArea');
        const uploadPreview = document.getElementById('uploadPreview');
        
        uploadArea.classList.add('hidden');
        uploadPreview.classList.remove('hidden');
        
        console.log('Upload area hidden, preview shown');

        // Update the uploaded count
        const uploadedCount = document.getElementById('uploadedCount');
        uploadedCount.textContent = this.uploadedImages.length;
        console.log('Updated count to:', this.uploadedImages.length);

        // Get the grid container
        const uploadedImagesGrid = document.getElementById('uploadedImagesGrid');
        
        // Generate preview HTML for existing grid (this is used for single additions or refreshes)
        const gridHTML = this.uploadedImages.map((imageData, index) => {
            const imagePath = imageData.path.startsWith('/uploads/') ? imageData.path : `/uploads/${imageData.path.split('/').pop()}`;
            console.log('Generating grid item for image:', imagePath, 'name:', imageData.name);
            
            return `
                <div class="image-item relative" data-image-id="${imageData.id}">
                    <img src="${imagePath}" 
                         alt="${imageData.name}" 
                         class="w-full h-24 object-cover rounded-lg border border-gray-300"
                         onerror="console.error('Failed to load image:', this.src)">
                    <div class="absolute top-1 right-1">
                        <button type="button" 
                                class="remove-single-image bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors" 
                                data-index="${index}"
                                title="Remove ${imageData.name}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="mt-1 text-xs text-gray-600 truncate px-1" title="${imageData.name}">
                        ${imageData.name}
                    </div>
                </div>
            `;
        }).join('');
        
        uploadedImagesGrid.innerHTML = gridHTML;
        console.log('Grid HTML updated with', this.uploadedImages.length, 'images');

        // Add event listeners for individual remove buttons
        uploadedImagesGrid.querySelectorAll('.remove-single-image').forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(e.target.closest('.remove-single-image').getAttribute('data-index'));
                this.removeSingleImage(index);
            });
        });

        // Set the first image as the primary one for backward compatibility
        if (this.uploadedImages.length > 0) {
            this.uploadedImagePath = this.uploadedImages[0].path;
            console.log('Set primary image path to:', this.uploadedImagePath);
        }
    }

    async removeSingleImage(index) {
        if (index < 0 || index >= this.uploadedImages.length) return;

        const imageData = this.uploadedImages[index];
        
        // Clean up the specific image from server
        await this.cleanupUploadedImage(imageData.path);
        
        // Remove from array
        this.uploadedImages.splice(index, 1);
        
        if (this.uploadedImages.length === 0) {
            // No images left, reset to upload state
            await this.clearAllImages();
        } else {
            // Update preview and set new primary image
            this.updateMultipleImagePreview();
            this.uploadedImagePath = this.uploadedImages[0].path;
        }
    }

    async generateBanner() {
        await this.sendToCanva();
    }

    async sendToCanva() {
        const url = document.getElementById('url').value.trim();
        if (!url) {
            this.showError('Please enter a landing page URL');
            return;
        }

        // Check if copy has been selected
        if (!this.selectedCopy) {
            this.showError('Please generate and select copy first');
            return;
        }


        // Store current URL for reference
        this.currentUrl = url;

        // Upload background to Canva first if generated locally
        if (this.generatedBackgroundPath && !this.generatedBackgroundId) {
            try {
                document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading background...';
                
                const bgResponse = await fetch('/api/upload-background-to-canva', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        background_file_path: this.generatedBackgroundPath,
                        background_filename: this.generatedBackgroundFilename
                    })
                });
                
                const bgResult = await bgResponse.json();
                if (bgResult.success) {
                    this.generatedBackgroundId = bgResult.background_asset_id;
                } else {
                    console.warn('Failed to upload background to Canva:', bgResult.error);
                }
            } catch (error) {
                console.warn('Error uploading background to Canva:', error);
            }
        }

        const formData = {
            url: url,
            size: document.getElementById('bannerSize').value,
            product_image_paths: this.uploadedImages.map(img => img.path), // Send all uploaded images
            background_asset_id: this.generatedBackgroundId, // Optional
            selected_copy: this.selectedCopy
        };

        try {
            // Mark extracted images for cleanup after successful Canva upload
            this.markExtractedImagesForCleanup();
            
            // Disable generate button immediately
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending to Canva...';
            
            // Send to Canva (simplified upload)
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.session_id) {
                this.currentSessionId = result.session_id;
                
                // Check if already completed (immediate response from Canva API)
                if (result.status === 'completed') {
                    // Skip progress section entirely - show results directly
                    await this.showResults(result);
                } else {
                    // Show progress section only for async operations
                    this.showProgressSection();
                    this.startPolling();
                }
            } else {
                throw new Error(result.error || 'Failed to send to Canva');
            }

        } catch (error) {
            console.error('Send to Canva error:', error);
            this.showError('Failed to send to Canva: ' + error.message);
            
            // Re-enable button on error
            const generateBtn = document.getElementById('generateBtn');
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.className = 'bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200';
                generateBtn.innerHTML = '<i class="fas fa-upload mr-2"></i>Send to Canva';
            }
            
            this.hideProgressSection();
        }
    }

    showProgressSection() {
        this.safeToggleClass('progressSection', 'hidden', false);
        this.safeToggleClass('resultsSection', 'hidden', true);
        
        // Disable form
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
        
        // Scroll to progress section
        document.getElementById('progressSection').scrollIntoView({ behavior: 'smooth' });
    }

    hideProgressSection() {
        this.safeToggleClass('progressSection', 'hidden', true);
        
        // Re-enable form
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-upload mr-2"></i>Send to Canva';
        }
    }

    startPolling() {
        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${this.currentSessionId}`);
                const result = await response.json();

                this.updateProgress(result);

                if (result.status === 'completed') {
                    this.stopPolling();
                    await this.showResults(result);
                } else if (result.status === 'copy_selection_required') {
                    this.stopPolling();
                    await this.handleCopySelectionRequired(result);
                } else if (result.status === 'error') {
                    this.stopPolling();
                    this.showError('Generation failed: ' + result.error);
                    this.hideProgressSection();
                }

            } catch (error) {
                console.error('Polling error:', error);
                this.stopPolling();
                this.showError('Failed to check generation status');
                this.hideProgressSection();
            }
        }, 2000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    updateProgress(result) {
        const progress = result.progress || 0;
        const message = result.message || 'Processing...';

        // Update progress bar
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('progressPercent').textContent = `${progress}%`;
        document.getElementById('progressText').textContent = message;

        // Update steps
        const stepsContainer = document.getElementById('generationSteps');
        stepsContainer.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-circle-notch fa-spin mr-2 text-blue-500"></i>
                <span>${message}</span>
            </div>
        `;
    }

    async showResults(result) {
        this.hideProgressSection();
        
        // Store design ID for independent background uploads
        if (result.design_id) {
            this.lastDesignId = result.design_id;
            console.log('Stored design ID for future background uploads:', this.lastDesignId);
            
            // Show separate send background button if background was generated locally but not included
            if (this.generatedBackgroundPath && !this.generatedBackgroundId) {
                const sendBackgroundBtn = document.getElementById('sendBackgroundBtn');
                if (sendBackgroundBtn) {
                    sendBackgroundBtn.style.display = 'inline-block';
                }
            }
        }
        
        // Show results section
        this.safeToggleClass('resultsSection', 'hidden', false);
        
        // Set Canva view link
        const viewInCanva = document.getElementById('viewInCanva');
        if (result.export_url && viewInCanva) {
            viewInCanva.href = result.export_url;
            viewInCanva.style.display = 'flex';
        } else if (viewInCanva) {
            viewInCanva.style.display = 'none';
        }
        
        // Scroll to results
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Clean up temporary extracted image after successful Canva upload
        await this.cleanupExtractedImageIfNeeded();
    }

    markExtractedImagesForCleanup() {
        // Mark any extracted images for cleanup after Canva upload
        const extractedImages = this.uploadedImages.filter(img => img.isExtracted);
        if (extractedImages.length > 0) {
            console.log('Marked extracted images for cleanup after Canva upload:', extractedImages.map(img => img.path));
            this.isExtractedImage = true;
            this.extractedImagePaths = extractedImages.map(img => img.path);
        } else {
            this.isExtractedImage = false;
            this.extractedImagePaths = [];
        }
    }

    async cleanupExtractedImageIfNeeded() {
        // Clean up temporary extracted image files after successful Canva upload
        if (this.isExtractedImage && this.extractedImagePaths && this.extractedImagePaths.length > 0) {
            try {
                console.log('Cleaning up temporary extracted images:', this.extractedImagePaths);
                
                const cleanupPromises = this.extractedImagePaths.map(async (imagePath) => {
                    const response = await fetch('/api/cleanup-image', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            image_path: imagePath
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        console.log('✅ Extracted image cleaned up successfully:', imagePath);
                    } else {
                        console.warn('⚠️ Failed to cleanup extracted image:', imagePath, result.error);
                    }
                    
                    return result;
                });
                
                await Promise.all(cleanupPromises);
                
                // Reset tracking flags
                this.isExtractedImage = false;
                this.extractedImagePaths = [];
                
            } catch (error) {
                console.warn('⚠️ Error during extracted image cleanup:', error);
            }
        }
    }

    resetForm() {
        // Hide results and progress sections
        this.safeToggleClass('resultsSection', 'hidden', true);
        this.hideProgressSection();
        
        // Clear form
        const urlInput = document.getElementById('url');
        const bannerSizeSelect = document.getElementById('bannerSize');
        
        if (urlInput) urlInput.value = '';
        if (bannerSizeSelect) bannerSizeSelect.value = 'MD_RECT';
        
        // Reset URL help text
        const urlHelpText = document.querySelector('#url').parentElement.querySelector('p');
        if (urlHelpText) {
            urlHelpText.innerHTML = "We'll extract content and images from this page";
            urlHelpText.className = "text-sm text-gray-500 mt-1";
        }
        
        // Remove uploaded image
        this.removeUploadedImage();
        
        // Hide and clear extracted images section
        this.hideExtractedImages();
        const extractedImagesGrid = document.getElementById('extractedImagesGrid');
        if (extractedImagesGrid) {
            extractedImagesGrid.innerHTML = '';
        }
        
        // Clear extracted images tracking array
        this.extractedImagePaths = [];
        
        // Hide explanation section
        this.safeToggleClass('explanationSection', 'hidden', true);
        const explanationContent = document.getElementById('explanationContent');
        if (explanationContent) {
            explanationContent.innerHTML = '';
        }
        
        // Reset copy state
        this.selectedCopy = null;
        this.copyVariants = [];
        this.generatedBackgroundId = null;
        this.safeToggleClass('generatedCopySection', 'hidden', true);
        this.safeToggleClass('backgroundSection', 'hidden', true);
        
        // Reset copy status display
        const statusDisplay = document.getElementById('copyStatusDisplay');
        statusDisplay.innerHTML = `
            <span class="text-gray-500">
                <i class="fas fa-exclamation-triangle mr-2 text-orange-500"></i>
                Please generate and select copy first
            </span>
        `;
        statusDisplay.className = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50';
        
        // Reset background status display
        const backgroundStatusDisplay = document.getElementById('backgroundStatusDisplay');
        if (backgroundStatusDisplay) {
            backgroundStatusDisplay.innerHTML = `
                <span class="text-gray-500">
                    <i class="fas fa-info-circle mr-2"></i>
                    Select copy first to see background prompt
                </span>
            `;
            backgroundStatusDisplay.className = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50';
        }
        
        // Hide background preview
        const backgroundPreview = document.getElementById('backgroundPreview');
        if (backgroundPreview) {
            backgroundPreview.classList.add('hidden');
        }
        
        // Clear background prompt text
        const backgroundPromptText = document.getElementById('backgroundPromptText');
        if (backgroundPromptText) {
            backgroundPromptText.value = '';
        }
        
        // Disable banner generation again
        const generateBtn = document.getElementById('generateBtn');
        const helpText = generateBtn.parentElement.querySelector('p');
        generateBtn.disabled = true;
        generateBtn.className = 'bg-gradient-to-r from-gray-400 to-gray-500 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200';
        
        if (helpText) {
            helpText.textContent = 'Generate and select copy first. Explanation and background generation are optional.';
            helpText.className = 'text-sm text-gray-500 mt-2';
        }
        
        // Reset session and URL
        this.currentSessionId = null;
        this.currentUrl = null;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async checkUrlCacheStatus(url) {
        const urlHelpText = document.querySelector('#url').parentElement.querySelector('p');
        
        if (!urlHelpText) {
            console.warn('URL help text element not found');
            return;
        }
        
        if (!url || !url.startsWith('http')) {
            urlHelpText.innerHTML = "We'll extract content and images from this page";
            urlHelpText.className = "text-sm text-gray-500 mt-1";
            return;
        }

        try {
            const response = await fetch(`/api/cache/${encodeURIComponent(url)}`);
            const data = await response.json();
            
            if (data.cached) {
                const ageMinutes = Math.floor(data.age_seconds / 60);
                let message;
                
                if (data.has_copy_cache) {
                    const copyAgeMinutes = Math.floor(data.copy_age_seconds / 60);
                    message = copyAgeMinutes < 1 ? 
                        '✅ Page data + copy cached - generation will be fastest!' : 
                        `✅ Page data + copy cached (${copyAgeMinutes} min${copyAgeMinutes !== 1 ? 's' : ''} ago) - generation will be fastest!`;
                } else {
                    message = ageMinutes < 1 ? 
                        '✅ Page data cached - generation will be faster!' : 
                        `✅ Page data cached (${ageMinutes} min${ageMinutes !== 1 ? 's' : ''} ago) - generation will be faster!`;
                }
                
                urlHelpText.innerHTML = message;
                urlHelpText.className = "text-sm text-green-600 mt-1";
            } else {
                urlHelpText.innerHTML = "We'll extract content and images from this page";
                urlHelpText.className = "text-sm text-gray-500 mt-1";
            }
        } catch (error) {
            urlHelpText.innerHTML = "We'll extract content and images from this page";
            urlHelpText.className = "text-sm text-gray-500 mt-1";
        }
    }

    async checkCacheStatus(url) {
        try {
            const response = await fetch(`/api/cache/${encodeURIComponent(url)}`);
            const data = await response.json();
            
            if (data.cached) {
                const ageMinutes = Math.floor(data.age_seconds / 60);
                const message = ageMinutes < 1 ? 
                    'Using cached data (just scraped)' : 
                    `Using cached data (${ageMinutes} min${ageMinutes !== 1 ? 's' : ''} old)`;
                
                this.showCacheNotification(message);
            }
        } catch (error) {
            console.log('Could not check cache status:', error);
        }
    }

    showCacheNotification(message) {
        // Create cache notification
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        notificationDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-clock mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notificationDiv);
        
        // Remove after 4 seconds
        setTimeout(() => {
            if (notificationDiv.parentNode) {
                notificationDiv.parentNode.removeChild(notificationDiv);
            }
        }, 4000);
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }

    showLoadingMessage(message) {
        // Create loading notification
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        loadingDiv.id = 'loading-notification';
        loadingDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Remove any existing loading notification
        const existing = document.getElementById('loading-notification');
        if (existing) {
            existing.remove();
        }
        
        document.body.appendChild(loadingDiv);
        
        // Auto-remove after 10 seconds (in case success/error doesn't clear it)
        setTimeout(() => {
            if (loadingDiv.parentElement) {
                loadingDiv.remove();
            }
        }, 10000);
    }

    hideLoadingMessage() {
        const loadingDiv = document.getElementById('loading-notification');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    toggleCopyVariantsSection(show) {
        const section = document.getElementById('generatedCopySection');
        if (section) {
            if (show) {
                section.classList.remove('hidden');
            } else {
                section.classList.add('hidden');
            }
        }
    }

    async loadCopyVariantsForSelection(url) {
        // Show loading state
        this.showCopyVariantsLoading();

        try {
            const response = await fetch('/api/copy-variants', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const result = await response.json();

            if (result.variants) {
                await this.displayCopyVariants(result.variants);
                this.updateGenerateButtonForCopySelection();
            } else {
                throw new Error(result.error || 'Failed to load copy variants');
            }

        } catch (error) {
            console.error('Error loading copy variants:', error);
            this.showCopyVariantsError(error.message);
        }
    }

    // Legacy method for compatibility
    async loadCopyVariants() {
        const url = document.getElementById('url').value.trim();
        if (!url) {
            this.showCopyVariantsPlaceholder();
            return;
        }
        await this.loadCopyVariantsForSelection(url);
    }

    async displayCopyVariants(variants) {
        const container = document.getElementById('copyVariantsContainer');
        if (!container) {
            console.warn('copyVariantsContainer element not found');
            return;
        }
        
        // Store variants for later use
        this.copyVariants = variants;
        
        container.innerHTML = '';

        variants.forEach((variant, index) => {
            const variantDiv = document.createElement('div');
            variantDiv.className = 'border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors';
            
            variantDiv.innerHTML = `
                <label class="flex items-start space-x-3 cursor-pointer">
                    <input type="radio" name="copyVariant" value="${index}" class="mt-1">
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="font-semibold text-gray-800 capitalize">${variant.type}</span>
                            <div class="flex items-center space-x-2">
                                <span class="text-xs text-gray-500">${variant.char_count} chars</span>
                                <button class="copy-to-clipboard-btn px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors" 
                                        data-copy-text="${variant.text.replace(/"/g, '&quot;')}"
                                        title="Copy to clipboard">
                                    <i class="fas fa-copy"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-gray-700">${variant.text}</p>
                        <p class="text-xs text-gray-500 mt-1">${variant.tone}</p>
                    </div>
                </label>
            `;
            
            container.appendChild(variantDiv);
        });

        // Add event listeners for radio button changes (auto-copy on selection)
        const radioButtons = container.querySelectorAll('input[name="copyVariant"]');
        radioButtons.forEach((radio, index) => {
            radio.addEventListener('change', async () => {
                if (radio.checked) {
                    // Copy to clipboard first
                    await this.copyToClipboard(variants[index].text, `${variants[index].type} copy`);
                    
                    // Save selection to backend
                    await this.selectCopyAndSave(index, false); // false = don't show additional success message since clipboard message was already shown
                }
            });
        });

        // Add event listeners for manual copy buttons
        const copyButtons = container.querySelectorAll('.copy-to-clipboard-btn');
        copyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const copyText = button.getAttribute('data-copy-text');
                this.copyToClipboard(copyText, 'copy');
            });
        });

        // Store the variants for later use
        this.copyVariants = variants;
        
        // Show the generated copy section
        this.safeToggleClass('generatedCopySection', 'hidden', false);
    }

    getSelectedCopyIndex() {
        const selectedRadio = document.querySelector('input[name="copyVariant"]:checked');
        return selectedRadio ? parseInt(selectedRadio.value) : 0;
    }

    showCopyVariantsPlaceholder() {
        const container = document.getElementById('copyVariantsContainer');
        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-pen-fancy text-3xl mb-3"></i>
                <p>Click "Send to Canva" to upload your assets</p>
            </div>
        `;
    }

    showCopyVariantsLoading() {
        const container = document.getElementById('copyVariantsContainer');
        container.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-spinner fa-spin text-3xl mb-3"></i>
                <p>Analyzing landing page and generating copy variants...</p>
                <p class="text-sm text-gray-400 mt-1">This may take a few seconds</p>
            </div>
        `;
    }

    showCopyVariantsError(message) {
        const container = document.getElementById('copyVariantsContainer');
        container.innerHTML = `
            <div class="text-center text-red-500 py-8">
                <i class="fas fa-exclamation-triangle text-3xl mb-3"></i>
                <p>Failed to load copy variants</p>
                <p class="text-sm text-gray-500 mt-1">${message}</p>
            </div>
        `;
    }

    hasCopyVariantsLoaded() {
        const container = document.getElementById('copyVariantsContainer');
        return container.querySelector('input[name="copyVariant"]') !== null;
    }

    hasValidCopySelection() {
        const selectedRadio = document.querySelector('input[name="copyVariant"]:checked');
        return selectedRadio !== null;
    }

    updateGenerateButtonForCopySelection() {
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Generate Banner with Selected Copy';
        }
        // Note: Radio button event listeners are now handled in displayCopyVariants()
    }

    resetGenerateButton() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Generate AI Banner';
    }

    async handleCopySelectionRequired(result) {
        // Hide progress section
        this.hideProgressSection();
        
        // Display copy variants
        if (result.copy_variants) {
            await this.displayCopyVariants(result.copy_variants);
            this.updateGenerateButtonForCopySelection();
        }
        
        // Show success message
        this.showInfo('Copy variants generated! Please select your preferred copy and click the generate button again.');
    }

    showInfo(message) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'fixed top-4 right-4 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        infoDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-info-circle mr-2"></i>
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(infoDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (infoDiv.parentElement) {
                infoDiv.remove();
            }
        }, 5000);
    }

    async extractImages() {
        const url = document.getElementById('url').value.trim();
        const extractBtn = document.getElementById('extractImagesBtn');
        
        if (!url) {
            this.showError('Please enter a URL first');
            return;
        }

        if (!url.startsWith('http')) {
            this.showError('Please enter a valid URL starting with http:// or https://');
            return;
        }

        try {
            // Show loading state
            extractBtn.disabled = true;
            extractBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Extracting...';
            
            // Hide previous results
            this.hideExtractedImages();
            
            // Extract images
            const response = await fetch('/api/extract-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const result = await response.json();

            if (result.success) {
                this.displayExtractedImages(result.images);
                this.showSuccessMessage(`Found ${result.count} images from the page`);
            } else {
                throw new Error(result.error || 'Failed to extract images');
            }

        } catch (error) {
            console.error('Error extracting images:', error);
            this.showError('Failed to extract images: ' + error.message);
        } finally {
            // Reset button state
            extractBtn.disabled = false;
            extractBtn.innerHTML = '<i class="fas fa-images mr-2"></i>Extract Images';
        }
    }

    displayExtractedImages(images) {
        const section = document.getElementById('extractedImagesSection');
        const grid = document.getElementById('extractedImagesGrid');
        
        // Clear previous images
        grid.innerHTML = '';
        
        if (images.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full text-center text-gray-500 py-8">
                    <i class="fas fa-images text-3xl mb-3"></i>
                    <p>No images found on this page</p>
                </div>
            `;
        } else {
            images.forEach((image) => {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'border border-gray-200 rounded-lg p-2 hover:border-blue-300 transition-colors cursor-pointer drag-handle';
                imageDiv.draggable = true;
                imageDiv.dataset.imageData = JSON.stringify(image);
                
                const dimensionsText = image.width && image.height ? 
                    `${image.width}×${image.height}` : 'Unknown size';
                
                const sizeText = image.size ? 
                    this.formatFileSize(parseInt(image.size)) : 'Unknown size';
                
                imageDiv.innerHTML = `
                    <img src="${image.src}" 
                         alt="${image.alt || 'Extracted image'}" 
                         class="w-full h-24 object-cover rounded mb-2"
                         loading="lazy"
                         onerror="this.parentElement.style.display='none'">
                    <p class="text-xs text-gray-600 truncate mb-1" title="${image.alt || 'No description'}">${image.alt || 'No description'}</p>
                    <p class="text-xs text-gray-500">${dimensionsText}</p>
                    <p class="text-xs text-gray-500">${sizeText}</p>
                    <div class="text-center mt-2">
                        <span class="inline-flex items-center text-xs text-blue-600">
                            <i class="fas fa-hand-rock mr-1"></i>
                            Drag to use or click to crop
                        </span>
                    </div>
                `;
                
                // Add drag events
                imageDiv.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', JSON.stringify(image));
                    e.dataTransfer.effectAllowed = 'copy';
                });
                
                // Add click event to show cropping modal
                imageDiv.addEventListener('click', () => {
                    this.showCropModal(image);
                });
                
                grid.appendChild(imageDiv);
            });
        }
        
        // Show the section
        section.classList.remove('hidden');
    }

    hideExtractedImages() {
        const section = document.getElementById('extractedImagesSection');
        section.classList.add('hidden');
    }

    showImageModal(image) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
            <div class="bg-white rounded-lg max-w-4xl max-h-full overflow-auto">
                <div class="p-4 border-b border-gray-200 flex justify-between items-center">
                    <h3 class="text-lg font-semibold">Image Details</h3>
                    <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="p-4">
                    <img src="${image.src}" 
                         alt="${image.alt || 'Extracted image'}" 
                         class="max-w-full max-h-96 mx-auto rounded mb-4">
                    <div class="space-y-2 text-sm">
                        <p><strong>Alt Text:</strong> ${image.alt || 'None'}</p>
                        <p><strong>Title:</strong> ${image.title || 'None'}</p>
                        <p><strong>Dimensions:</strong> ${image.width && image.height ? `${image.width}×${image.height}` : 'Unknown'}</p>
                        <p><strong>Size:</strong> ${image.size ? this.formatFileSize(parseInt(image.size)) : 'Unknown'}</p>
                        <p><strong>Type:</strong> ${image.type}</p>
                        <p><strong>URL:</strong> <a href="${image.src}" target="_blank" class="text-blue-500 hover:underline break-all">${image.src}</a></p>
                    </div>
                </div>
            </div>
        `;
        
        // Add click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
    }

    async handleExtractedImageDrop(image) {
        try {
            console.log('Starting extracted image drop handling for:', image.src);
            
            // Show immediate loading feedback
            this.showLoadingMessage('Adding image from extracted images...');
            
            // Convert image URL to file and upload
            await this.downloadAndUploadImage(image.src, image.alt || 'extracted_image');
            
            // Ensure we have uploaded images
            if (this.uploadedImages.length === 0) {
                throw new Error('Failed to add image to upload collection');
            }
            
            // Force update UI to show the new image
            this.updateMultipleImagePreview();
            
            // Additional verification that the preview is showing
            const uploadPreview = document.getElementById('uploadPreview');
            const uploadArea = document.getElementById('uploadArea');
            
            if (uploadPreview && uploadArea) {
                uploadArea.classList.add('hidden');
                uploadPreview.classList.remove('hidden');
                
                // Update count display
                const countElement = document.getElementById('uploadedCount');
                if (countElement) {
                    countElement.textContent = this.uploadedImages.length;
                }
            }
            
            console.log('Successfully processed extracted image drop. Total images:', this.uploadedImages.length);
            
            // Hide loading message and show success
            this.hideLoadingMessage();
            this.showSuccessMessage('Image added from extracted images!');
            
        } catch (error) {
            console.error('Error handling extracted image drop:', error);
            this.hideLoadingMessage();
            this.showError('Failed to use extracted image: ' + error.message);
        }
    }

    async downloadAndUploadImage(imageUrl, filename) {
        try {
            console.log('Starting download and upload for:', imageUrl, 'filename:', filename);
            
            // Use final proxy approach - this saves the image permanently
            const response = await fetch('/api/proxy-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: imageUrl,
                    filename: filename 
                })
            });

            if (!response.ok) {
                console.warn('Primary proxy failed, trying fallback method');
                // Fallback: try to fetch directly and upload as blob
                const imgResponse = await fetch(imageUrl, { mode: 'cors' });
                if (!imgResponse.ok) {
                    throw new Error('Failed to download image');
                }
                
                const blob = await imgResponse.blob();
                const file = new File([blob], `${filename}.jpg`, { type: 'image/jpeg' });
                await this.handleFileUpload(file);
                console.log('Fallback upload completed successfully');
                return;
            }

            const result = await response.json();
            console.log('Proxy-image response:', result);
            
            if (result.success) {
                this.uploadedImagePath = result.filepath;
                
                // Add to uploaded images array with extracted flag for cleanup
                const imageData = {
                    path: result.filepath,
                    name: `Extracted: ${filename}`,
                    isExtracted: true,  // Mark as extracted for proper cleanup
                    id: `extracted_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
                };
                
                this.uploadedImages.push(imageData);
                console.log('Added extracted image to uploads list:', imageData);
                console.log('Current uploadedImages array length:', this.uploadedImages.length);
                
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Download and upload error:', error);
            throw error;
        }
    }

    async showCropModal(image) {
        try {
            console.log('Opening crop modal for image:', image);
            
            // Create modal immediately with loading state
            const modal = document.createElement('div');
            modal.className = 'crop-modal-overlay';
            modal.innerHTML = `
                <div class="crop-modal-content">
                    <div class="p-4 border-b border-gray-200 flex justify-between items-center flex-shrink-0">
                        <h3 class="text-lg font-semibold">Crop Image</h3>
                        <button id="closeCropModal" class="text-gray-500 hover:text-gray-700 text-xl">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="flex-1 p-4 overflow-hidden">
                        <div id="cropImageContainer" class="crop-image-container mb-4">
                            <div class="loading-state">
                                <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                                <p>Preparing image for cropping...</p>
                                <p class="text-xs text-gray-500 mt-1">Downloading and processing image (CORS bypass)</p>
                            </div>
                        </div>
                        <div class="flex justify-between items-center flex-shrink-0 mt-4">
                            <div class="text-sm text-gray-600">
                                <p><strong>Original:</strong> ${image.width && image.height ? `${image.width}×${image.height}` : 'Unknown'}</p>
                                <p class="text-xs text-gray-500 mt-1">💡 Mouse wheel to zoom, drag to move image</p>
                                <p class="text-xs text-gray-500">🎯 Drag corners to resize crop area</p>
                            </div>
                            <div class="space-x-2">
                                <button id="resetCrop" class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50" disabled>
                                    <i class="fas fa-undo mr-2"></i>Reset
                                </button>
                                <button id="useCropped" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50" disabled>
                                    <i class="fas fa-check mr-2"></i>Use Cropped Image
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            console.log('Modal added to DOM with loading state');
            
            // Now get the proxied image URL in the background
            let proxiedImageUrl;
            try {
                proxiedImageUrl = await this.getProxiedImageUrl(image.src, image.alt || 'crop_image');
                if (!proxiedImageUrl) {
                    throw new Error('No proxied URL returned');
                }
            } catch (proxyError) {
                console.warn('Image proxy failed, using original URL:', proxyError);
                proxiedImageUrl = image.src;
            }
            
            // Replace loading state with actual image
            const cropImageContainer = modal.querySelector('#cropImageContainer');
            cropImageContainer.innerHTML = `
                <img id="cropImage" src="${proxiedImageUrl}" 
                     alt="${image.alt || 'Image to crop'}" 
                     crossorigin="anonymous"
                     style="max-width: 100%; max-height: 60vh; width: auto; height: auto; display: block;">
            `;
            
            const cropImage = modal.querySelector('#cropImage');
            
            // Check if Cropper is available
            if (typeof Cropper === 'undefined') {
                throw new Error('Cropper.js library not loaded. Please refresh the page and try again.');
            }

            // Initialize cropper after image loads
            const cropper = new Cropper(cropImage, {
                aspectRatio: NaN,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 0.8,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
                responsive: true,
                checkOrientation: false,
                modal: true,
                background: true,
                autoCrop: true,
                movable: true,
                rotatable: false,
                scalable: true,
                zoomable: true,
                zoomOnTouch: true,
                zoomOnWheel: true,
                wheelZoomRatio: 0.1,
                cropBoxResizable: true,
                minContainerWidth: 200,
                minContainerHeight: 100,
                ready() {
                    console.log('Cropper initialized successfully');
                    // Enable buttons when cropper is ready
                    const resetBtn = modal.querySelector('#resetCrop');
                    const useBtn = modal.querySelector('#useCropped');
                    if (resetBtn) resetBtn.disabled = false;
                    if (useBtn) useBtn.disabled = false;
                },
            });

            // Close modal function
            const closeModal = async () => {
                console.log('Closing crop modal...');
                if (cropper) {
                    cropper.destroy();
                }
                if (this.currentTempImage) {
                    await this.cleanupTempImage(this.currentTempImage);
                    this.currentTempImage = null;
                }
                modal.remove();
            };

            // Event listeners
            modal.querySelector('#closeCropModal').addEventListener('click', closeModal);
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal();
                }
            });
            
            const resetBtn = modal.querySelector('#resetCrop');
            const useBtn = modal.querySelector('#useCropped');

            resetBtn.addEventListener('click', () => {
                cropper.reset();
            });

            useBtn.addEventListener('click', async () => {
                try {
                    useBtn.disabled = true;
                    useBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';

                    const canvas = cropper.getCroppedCanvas({
                        maxWidth: 2048,
                        maxHeight: 2048,
                        imageSmoothingEnabled: true,
                        imageSmoothingQuality: 'high',
                    });
                    
                    if (!canvas) {
                        throw new Error('Failed to generate cropped image canvas.');
                    }
                    
                    const croppedDataUrl = canvas.toDataURL('image/jpeg', 0.9);
                    
                    if (!croppedDataUrl || croppedDataUrl === 'data:,') {
                        throw new Error('Failed to process cropped image.');
                    }
                    
                    await this.uploadCroppedImage(croppedDataUrl, image.alt || 'cropped_image');
                    
                    if (this.currentTempImage) {
                        await this.cleanupTempImage(this.currentTempImage);
                        this.currentTempImage = null;
                    }
                    
                    closeModal();
                    this.showSuccessMessage('Cropped image uploaded successfully!');
                    
                } catch (error) {
                    console.error('Error cropping image:', error);
                    this.showError('Failed to crop image: ' + error.message);
                } finally {
                    useBtn.disabled = false;
                    useBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Use Cropped Image';
                }
            });

        } catch (error) {
            console.error('Error setting up crop modal:', error);
            this.showError('Failed to open crop modal: ' + error.message);
        }
    }

    async getProxiedImageUrl(imageUrl, filename) {
        try {
            // Use temporary proxy approach for cropping modal
            const response = await fetch('/api/proxy-image-temp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: imageUrl,
                    filename: filename 
                })
            });

            const result = await response.json();
            
            if (result.success && result.is_temp) {
                // Store temp filename for cleanup
                this.currentTempImage = result.temp_filename;
                // Return a URL to the temporary proxied image
                return `/api/download-temp/${result.temp_filename}`;
            } else {
                throw new Error(result.error || 'Failed to proxy image');
            }

        } catch (error) {
            console.error('Error proxying image:', error);
            // Try original URL with crossOrigin attribute
            return imageUrl;
        }
    }

    async cleanupTempImage(filename) {
        if (!filename) return;
        
        try {
            await fetch('/api/cleanup-temp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename })
            });
        } catch (error) {
            console.warn('Failed to cleanup temp image:', error);
        }
    }

    async uploadCroppedImage(dataUrl, filename) {
        try {
            // Clean up previous upload if exists
            if (this.uploadedImagePath) {
                await this.cleanupUploadedImage(this.uploadedImagePath);
            }

            const response = await fetch('/api/upload-cropped', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: dataUrl,
                    filename: filename
                })
            });

            const result = await response.json();
            
            if (result.success) {
                // Add to uploaded images array
                this.uploadedImages.push({
                    path: result.filepath,
                    name: `Cropped: ${filename}`,
                    isExtracted: false,
                    id: `uploaded-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
                });

                // Update UI to show uploaded images
                this.updateMultipleImagePreview();
                
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Error uploading cropped image:', error);
            throw error;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Debug function to test modal display
    testCropModal() {
        console.log('Testing crop modal...');
        const testImage = {
            src: 'https://via.placeholder.com/400x300',
            alt: 'Test Image',
            width: 400,
            height: 300
        };
        this.showCropModal(testImage);
    }

    showSuccessMessage(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        successDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(successDiv);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (successDiv.parentElement) {
                successDiv.remove();
            }
        }, 4000);
    }

    async generateCopy() {
        console.log('generateCopy method called');
        const url = document.getElementById('url').value.trim();
        const generateBtn = document.getElementById('generateCopyBtn');
        const regenerateBtn = document.getElementById('regenerateCopyBtn');
        
        console.log('URL:', url);
        console.log('Generate button:', generateBtn);
        
        if (!url) {
            console.log('No URL provided');
            this.showError('Please enter a URL first');
            return;
        }

        if (!url.startsWith('http')) {
            this.showError('Please enter a valid URL starting with http:// or https://');
            return;
        }

        try {
            // Show loading state for both buttons
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
            
            if (regenerateBtn) {
                regenerateBtn.disabled = true;
                regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Regenerating...';
            }
            
            // Generate copy variants
            const response = await fetch('/api/generate-copy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const result = await response.json();

            if (result.success) {
                this.copyVariants = result.variants;
                await this.displayCopyVariants(result.variants);
                this.showSuccessMessage(`Generated ${result.variants.length} copy variants`);
            } else {
                throw new Error(result.error || 'Failed to generate copy');
            }

        } catch (error) {
            console.error('Error generating copy:', error);
            this.showError('Failed to generate copy: ' + error.message);
        } finally {
            // Reset button states
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-pen-fancy mr-2"></i>Generate Copy';
            
            if (regenerateBtn) {
                regenerateBtn.disabled = false;
                regenerateBtn.innerHTML = '<i class="fas fa-redo mr-2"></i>Regenerate Copy';
            }
        }
    }

    async generateBackground() {
        const url = document.getElementById('url').value.trim();
        const generateBtn = document.getElementById('generateBackgroundBtn');
        
        if (!url) {
            this.showError('Please enter a URL first');
            return;
        }

        if (!this.selectedCopy) {
            this.showError('Please select copy first');
            return;
        }

        try {
            // Show loading state
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
            }
            
            // Update status
            const statusDisplay = document.getElementById('backgroundStatusDisplay');
            if (statusDisplay) {
                statusDisplay.innerHTML = `
                    <span class="text-blue-600">
                        <i class="fas fa-spinner fa-spin mr-2"></i>
                        Generating AI background based on the prompt...
                    </span>
                `;
                statusDisplay.className = 'w-full px-4 py-3 border border-blue-300 rounded-lg bg-blue-50';
            }
            
            // Get edited prompt from textarea
            const promptTextarea = document.getElementById('backgroundPromptText');
            const customPrompt = promptTextarea?.value?.trim();
            
            // Generate background with custom prompt if available
            const response = await fetch('/api/generate-background', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    custom_background_prompt: customPrompt, // Send edited prompt
                    selected_copy: this.selectedCopy
                })
            });

            const result = await response.json();

            if (result.success) {
                // Store generated background data for upload later
                this.generatedBackgroundPath = result.background_file_path;
                this.generatedBackgroundFilename = result.background_filename;
                this.showBackgroundPreview(result.background_url);
                this.updateBackgroundStatus(true);
                this.showSuccessMessage('AI background generated successfully! Click "Send Background to Canva" to upload it.');
                this.showSendBackgroundButton();
                this.checkIfReadyForBannerGeneration();
            } else {
                throw new Error(result.error || 'Failed to generate background');
            }

        } catch (error) {
            console.error('Error generating background:', error);
            this.showError('Failed to generate background: ' + error.message);
            this.updateBackgroundStatus(false);
        } finally {
            // Reset button state
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-paint-brush mr-2"></i>Generate AI Background';
            }
        }
    }
    
    async sendBackgroundToCanva() {
        if (!this.generatedBackgroundPath) {
            this.showError('No background generated yet. Please generate a background first.');
            return;
        }
        
        const sendBtn = document.getElementById('sendBackgroundBtn');
        const originalText = sendBtn.innerHTML;
        
        try {
            // Update button state
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';
            
            const response = await fetch('/api/upload-background-to-canva', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    background_file_path: this.generatedBackgroundPath,
                    background_filename: this.generatedBackgroundFilename
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Store the asset ID for future use
                this.generatedBackgroundId = result.background_asset_id;
                this.showSuccessMessage('🎨 Background uploaded to Canva successfully! It\'s now available in your Canva "Uploads" section.');
            } else {
                throw new Error(result.error || 'Failed to upload background to Canva');
            }
            
        } catch (error) {
            console.error('Error adding background to Canva:', error);
            this.showError('Failed to add background to Canva: ' + error.message);
        } finally {
            // Reset button
            sendBtn.disabled = false;
            sendBtn.innerHTML = originalText;
        }
    }

    showBackgroundPreview(backgroundUrl) {
        const preview = document.getElementById('backgroundPreview');
        if (!preview) {
            console.warn('backgroundPreview element not found');
            return;
        }
        
        const previewImage = preview.querySelector('img');
        if (!previewImage) {
            console.warn('backgroundPreview img element not found');
            return;
        }
        
        previewImage.src = backgroundUrl;
        preview.classList.remove('hidden');
    }

    updateBackgroundStatus(success, message = null) {
        const statusDisplay = document.getElementById('backgroundStatusDisplay');
        if (!statusDisplay) {
            console.warn('backgroundStatusDisplay element not found');
            return;
        }
        
        if (success) {
            statusDisplay.innerHTML = `
                <span class="text-green-600">
                    <i class="fas fa-check-circle mr-2"></i>
                    AI background generated successfully
                </span>
            `;
            statusDisplay.className = 'w-full px-4 py-3 border border-green-300 rounded-lg bg-green-50';
        } else {
            statusDisplay.innerHTML = `
                <span class="text-red-600">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    ${message || 'Background generation failed'}
                </span>
            `;
            statusDisplay.className = 'w-full px-4 py-3 border border-red-300 rounded-lg bg-red-50';
        }
    }
    
    showSendBackgroundButton() {
        const sendBtn = document.getElementById('sendBackgroundBtn');
        if (sendBtn) {
            // Hide initially - will be shown after main send to Canva
            sendBtn.style.display = 'none';
            sendBtn.disabled = false;
        }
    }

    checkIfReadyForBannerGeneration() {
        // Background generation is now optional - just need copy
        if (this.selectedCopy) {
            this.enableBannerGeneration();
        }
    }
    
    showBackgroundPrompt(selectedCopy) {
        const promptSection = document.getElementById('backgroundPromptSection');
        const promptText = document.getElementById('backgroundPromptText');
        
        console.log('🔍 showBackgroundPrompt called');
        console.log('🔍 selectedCopy:', selectedCopy);
        console.log('🔍 background_prompt:', selectedCopy?.background_prompt);
        
        if (promptSection && promptText) {
            // Create a meaningful prompt based on the selected copy
            let prompt = '';
            
            if (selectedCopy && selectedCopy.background_prompt && selectedCopy.background_prompt.trim()) {
                prompt = selectedCopy.background_prompt.trim();
            } else {
                // Create default prompt based on copy type and text
                const copyType = selectedCopy?.type || 'professional';
                const copyText = selectedCopy?.text || '';
                
                prompt = `Create an abstract ${copyType} marketing background that complements this message: "${copyText.substring(0, 100)}...". Use modern, clean design elements that enhance readability without being distracting.`;
                console.log('✅ Using generated default prompt:', prompt);
            }
            
            promptText.value = prompt;

        } else {
            console.error('❌ Missing elements - promptSection:', promptSection, 'promptText:', promptText);
        }
    }
    
    enableCanvaUpload() {
        const generateBtn = document.getElementById('generateBtn');
        const helpText = generateBtn?.parentElement?.querySelector('p');
        
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.className = 'bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200';
        }
        
        if (helpText) {
            helpText.textContent = 'Ready to send to Canva! Background generation is optional.';
            helpText.className = 'text-sm text-green-600 mt-2';
        }
    }

    showBackgroundSection() {
        const backgroundSection = document.getElementById('backgroundSection');
        if (backgroundSection) {
            backgroundSection.classList.remove('hidden');
        } else {
            console.warn('backgroundSection element not found');
        }
    }

    enableBackgroundGeneration() {
        const generateBtn = document.getElementById('generateBackgroundBtn');
        const statusDisplay = document.getElementById('backgroundStatusDisplay');
        
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.className = 'bg-gradient-to-r from-purple-500 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200';
        }
        
        if (statusDisplay) {
            statusDisplay.innerHTML = `
                <span class="text-green-600">
                    <i class="fas fa-check-circle mr-2"></i>
                    Background generation ready, or skip to use Canva's backgrounds
                </span>
            `;
            statusDisplay.className = 'w-full px-4 py-3 border border-green-300 rounded-lg bg-green-50';
        }
    }

    async selectCopy(index) {
        if (!this.copyVariants[index]) {
            this.showError('Invalid copy selection');
            return;
        }

        const selectedCopy = this.copyVariants[index];
        const url = document.getElementById('url').value.trim();

        try {
            // Set selectedCopy immediately to prevent race conditions
            this.selectedCopy = selectedCopy;
            
            // Save selected copy to backend
            const response = await fetch('/api/save-selected-copy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    selected_copy: selectedCopy
                })
            });

            const result = await response.json();
            if (result.success) {
                this.updateCopyStatus(selectedCopy);
                this.showBackgroundSection();
                this.showBackgroundPrompt(selectedCopy);
                this.enableBackgroundGeneration();
                this.enableCanvaUpload(); // Enable Send to Canva immediately
                this.showSuccessMessage('📋 Copy selected successfully and copied to clipboard!');
            } else {
                // Reset on failure
                this.selectedCopy = null;
                throw new Error(result.error || 'Failed to save copy selection');
            }

        } catch (error) {
            console.error('Error selecting copy:', error);
            this.selectedCopy = null;
            this.showError('Failed to select copy: ' + error.message);
        }
    }

    async selectCopyAndSave(index, showSuccessMessage = true) {
        if (!this.copyVariants[index]) {
            this.showError('Invalid copy selection');
            return;
        }

        const selectedCopy = this.copyVariants[index];
        const url = document.getElementById('url').value.trim();

        try {
            // Set selectedCopy immediately to prevent race conditions
            this.selectedCopy = selectedCopy;
            
            // Save selected copy to backend
            const response = await fetch('/api/save-selected-copy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    selected_copy: selectedCopy
                })
            });

            const result = await response.json();
            if (result.success) {
                this.updateCopyStatus(selectedCopy);
                this.showBackgroundSection();
                this.showBackgroundPrompt(selectedCopy);
                this.enableBackgroundGeneration();
                this.enableCanvaUpload(); // Enable Send to Canva immediately
                
                // Only show success message if requested (to avoid duplicate messages)
                if (showSuccessMessage) {
                    this.showSuccessMessage('📋 Copy selected successfully and copied to clipboard!');
                }
            } else {
                // Reset on failure
                this.selectedCopy = null;
                throw new Error(result.error || 'Failed to save copy selection');
            }

        } catch (error) {
            console.error('Error selecting copy:', error);
            this.selectedCopy = null;
            this.showError('Failed to select copy: ' + error.message);
        }
    }

    updateCopyStatus(selectedCopy) {
        const statusDisplay = document.getElementById('copyStatusDisplay');
        const indicator = document.getElementById('selectedCopyIndicator');
        
        if (statusDisplay) {
            statusDisplay.innerHTML = `
                <span class="text-green-600">
                    <i class="fas fa-check-circle mr-2"></i>
                    Selected: "${selectedCopy.text.substring(0, 50)}${selectedCopy.text.length > 50 ? '...' : ''}"
                </span>
            `;
            statusDisplay.className = 'w-full px-4 py-3 border border-green-300 rounded-lg bg-green-50';
        }
        
        if (indicator) {
            indicator.classList.remove('hidden');
        }
    }

    enableBannerGeneration() {
        // This function is now handled by enableCanvaUpload()
        // Background generation is optional
        this.enableCanvaUpload();
    }

    async generateExplanation() {
        console.log('generateExplanation method called');
        
        const url = document.getElementById('url').value.trim();
        if (!url) {
            this.showError('Please enter a URL first');
            return;
        }
        
        const generateBtn = document.getElementById('generateExplanationBtn');
        const regenerateBtn = document.getElementById('regenerateExplanationBtn');
        const originalGenerateText = generateBtn.innerHTML;
        const originalRegenerateText = regenerateBtn ? regenerateBtn.innerHTML : '';
        
        try {
            // Update button states
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
            if (regenerateBtn) {
                regenerateBtn.disabled = true;
                regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Regenerating...';
            }
            
            const response = await fetch('/api/generate-explanation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show the explanation section and populate it
                this.showExplanationSection(result.explanation);
                this.showSuccessMessage('✨ Creative explanation generated successfully!');
                console.log('Explanation generated:', result.explanation);
            } else {
                throw new Error(result.error || 'Failed to generate explanation');
            }
            
        } catch (error) {
            console.error('Error generating explanation:', error);
            this.showError('Failed to generate explanation: ' + error.message);
        } finally {
            // Reset button states
            generateBtn.disabled = false;
            generateBtn.innerHTML = originalGenerateText;
            if (regenerateBtn) {
                regenerateBtn.disabled = false;
                regenerateBtn.innerHTML = originalRegenerateText || '<i class="fas fa-redo mr-2"></i>Regenerate Explanation';
            }
        }
    }

    showExplanationSection(explanation) {
        const explanationSection = document.getElementById('explanationSection');
        const explanationContent = document.getElementById('explanationContent');
        const explanationIndicator = document.getElementById('explanationIndicator');
        const regenerateBtn = document.getElementById('regenerateExplanationBtn');
        
        if (!explanationSection || !explanationContent) {
            console.warn('Explanation section elements not found');
            return;
        }
        
        // Show the section
        explanationSection.classList.remove('hidden');
        
        // Populate the explanation content
        explanationContent.innerHTML = explanation.html_content;
        
        // Show success indicator
        if (explanationIndicator) {
            explanationIndicator.classList.remove('hidden');
        }
        
        // Show regenerate button
        if (regenerateBtn) {
            regenerateBtn.classList.remove('hidden');
        }
        
        // Add copy-to-clipboard functionality for explanation sections
        this.addCopyToClipboardHandlers(explanationContent);
    }

    addCopyToClipboardHandlers(container) {
        // Add copy buttons to each section
        const sections = container.querySelectorAll('h3');
        sections.forEach(section => {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'ml-2 text-xs text-blue-600 hover:text-blue-800 opacity-70 hover:opacity-100';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy section to clipboard';
            
            copyBtn.addEventListener('click', async () => {
                // Get the section content including the heading and following content
                let content = section.outerHTML;
                let nextElement = section.nextElementSibling;
                
                // Collect content until next h3 or end
                while (nextElement && nextElement.tagName !== 'H3') {
                    content += '\n' + nextElement.outerHTML;
                    nextElement = nextElement.nextElementSibling;
                }
                
                // Convert HTML to plain text for clipboard
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = content;
                const plainText = tempDiv.textContent || tempDiv.innerText || '';
                
                await this.copyToClipboard(plainText, 'explanation section');
            });
            
            section.appendChild(copyBtn);
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BannerMaker();
    checkCanvaAuthStatus(); // Check Canva authentication status on load
});

// Canva Authentication Functions
async function checkCanvaAuthStatus() {
    try {
        const response = await fetch('/auth/canva/status');
        const data = await response.json();
        
        updateCanvaAuthUI(data);
        
    } catch (error) {
        console.error('Failed to check Canva auth status:', error);
        updateCanvaAuthUI({
            authenticated: false,
            status: 'error',
            message: 'Failed to check authentication status'
        });
    }
}

function updateCanvaAuthUI(authData) {
    const statusIcon = document.getElementById('canva-status-icon');
    const statusText = document.getElementById('canva-status-text');
    const connectBtn = document.getElementById('canva-connect-btn');
    const connectedDiv = document.getElementById('canva-connected');
    const authNotice = document.getElementById('canva-auth-notice');
    
    if (authData.authenticated) {
        // User is authenticated
        statusIcon.className = 'fas fa-circle text-green-400 mr-2';
        statusText.textContent = 'Canva Ready';
        connectBtn.style.display = 'none';
        connectedDiv.style.display = 'flex';
        
        // Hide the auth notice
        if (authNotice) {
            authNotice.style.display = 'none';
        }
        
    } else {
        // User is not authenticated
        statusIcon.className = 'fas fa-circle text-red-400 mr-2';
        statusText.textContent = 'Canva Not Connected';
        connectBtn.style.display = 'flex';
        connectedDiv.style.display = 'none';
        
        // Show the auth notice
        if (authNotice) {
            authNotice.style.display = 'block';
        }
    }
}

function connectToCanva() {
    // Show loading state
    const connectBtn = document.getElementById('canva-connect-btn');
    const originalHTML = connectBtn.innerHTML;
    connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Connecting...';
    connectBtn.disabled = true;
    
    // Redirect to Canva OAuth flow
    window.location.href = '/auth/canva/authorize';
}

// Check for successful authentication on page load
function checkAuthSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
        // Show success message
        showCanvaAuthSuccess();
        
        // Clean up URL
        const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
        window.history.replaceState({path: cleanUrl}, '', cleanUrl);
        
        // Refresh auth status
        setTimeout(() => {
            checkCanvaAuthStatus();
        }, 1000);
    }
}

function showCanvaAuthSuccess() {
    // Create success notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center z-50';
    notification.innerHTML = `
        <i class="fas fa-check-circle mr-3"></i>
        <span>Successfully connected to Canva!</span>
        <button onclick="this.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Check for auth success on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthSuccess();
});