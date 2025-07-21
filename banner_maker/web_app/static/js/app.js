// AI Banner Maker - Frontend JavaScript

class BannerMaker {
    constructor() {
        this.currentSessionId = null;
        this.uploadedImagePath = null;
        this.pollInterval = null;
        this.currentUrl = null;
        this.currentTempImage = null; // Track temp images for cleanup
        this.selectedCopy = null; // Track selected copy
        this.copyVariants = []; // Store generated copy variants
        
        this.initializeEventListeners();
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

        // Regenerate with same copy button - fastest option
        const regenerateWithCopyBtn = document.getElementById('regenerateWithCopyBtn');
        if (regenerateWithCopyBtn) {
            regenerateWithCopyBtn.addEventListener('click', () => {
                this.regenerateWithSameCopy();
            });
        }

        // Regenerate button - keep current URL and settings
        const regenerateBtn = document.getElementById('regenerateBtn');
        if (regenerateBtn) {
            regenerateBtn.addEventListener('click', () => {
                this.regenerateBanner();
            });
        }

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

        // Regenerate copy button
        const regenerateCopyBtn = document.getElementById('regenerateCopyBtn');
        if (regenerateCopyBtn) {
            regenerateCopyBtn.addEventListener('click', () => {
                this.generateCopy();
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
        const fileInput = document.getElementById('productImage');
        const removeButton = document.getElementById('removeImage');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop for files and extracted images
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drop-zone-active');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drop-zone-active');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drop-zone-active');
            
            // Check if it's an extracted image (JSON data)
            const imageData = e.dataTransfer.getData('text/plain');
            if (imageData) {
                try {
                    const image = JSON.parse(imageData);
                    this.handleExtractedImageDrop(image);
                    return;
                } catch (e) {
                    // Not JSON, continue with file handling
                }
            }
            
            // Handle file drop
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Remove image
        removeButton.addEventListener('click', () => {
            this.removeUploadedImage();
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

            // Show preview immediately
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewImage = document.getElementById('previewImage');
                const uploadedFileName = document.getElementById('uploadedFileName');
                previewImage.src = e.target.result;
                uploadedFileName.textContent = file.name;
                document.getElementById('uploadArea').classList.add('hidden');
                uploadPreview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);

            // Upload file to server
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.uploadedImagePath = result.filepath;
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

    async generateBanner() {
        await this.generateBannerWithOptions({});
    }

    async generateBannerWithOptions(options = {}) {
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

        // Store current URL for regeneration
        this.currentUrl = url;

        const formData = {
            url: url,
            size: document.getElementById('bannerSize').value,
            product_image_path: this.uploadedImagePath,
            ...options
        };

        try {
            // Show progress section
            this.showProgressSection();
            
            // Start generation
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
                this.startPolling();
            } else {
                throw new Error(result.error || 'Failed to start generation');
            }

        } catch (error) {
            console.error('Generation error:', error);
            this.showError('Failed to start generation: ' + error.message);
            this.hideProgressSection();
        }
    }

    showProgressSection() {
        document.getElementById('progressSection').classList.remove('hidden');
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Disable form
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
        
        // Scroll to progress section
        document.getElementById('progressSection').scrollIntoView({ behavior: 'smooth' });
    }

    hideProgressSection() {
        document.getElementById('progressSection').classList.add('hidden');
        
        // Re-enable form
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-magic mr-2"></i>Generate AI Banner';
    }

    startPolling() {
        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${this.currentSessionId}`);
                const result = await response.json();

                this.updateProgress(result);

                if (result.status === 'completed') {
                    this.stopPolling();
                    this.showResults(result);
                } else if (result.status === 'copy_selection_required') {
                    this.stopPolling();
                    this.handleCopySelectionRequired(result);
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

    showResults(result) {
        this.hideProgressSection();
        
        // Show results section
        document.getElementById('resultsSection').classList.remove('hidden');
        
        // Set banner preview
        document.getElementById('bannerPreview').src = result.banner_url + '?t=' + Date.now();
        
        // Set Canva view link
        if (result.export_url) {
            document.getElementById('viewInCanva').href = result.export_url;
            document.getElementById('viewInCanva').style.display = 'flex';
        } else {
            document.getElementById('viewInCanva').style.display = 'none';
        }
        
        // Show generation details
        this.showGenerationDetails(result);
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }

    showGenerationDetails(result) {
        const detailsContainer = document.getElementById('generationDetails');
        
        const details = [
            { label: 'Image Source', value: result.image_source, icon: 'fas fa-image' },
            { label: 'Copy Type', value: result.copy_used?.type || 'auto', icon: 'fas fa-pen' },
            { label: 'Dimensions', value: result.dimensions, icon: 'fas fa-expand' },
            { label: 'Copy Used', value: result.copy_used?.text || 'N/A', icon: 'fas fa-quote-left' }
        ];

        detailsContainer.innerHTML = details.map(detail => `
            <div class="flex items-start">
                <i class="${detail.icon} text-gray-400 mr-3 mt-1"></i>
                <div>
                    <span class="font-medium text-gray-700">${detail.label}:</span>
                    <span class="text-gray-600 ml-2">${detail.value}</span>
                </div>
            </div>
        `).join('');
    }

    async regenerateWithSameCopy() {
        if (!this.currentUrl) {
            this.showError('No URL to regenerate with');
            return;
        }

        // Check if copy cache exists for this URL
        try {
            const response = await fetch(`/api/cache/${encodeURIComponent(this.currentUrl)}`);
            const data = await response.json();
            
            if (!data.has_copy_cache) {
                this.showError('No cached copy data available. Use "Regenerate with Same URL" instead.');
                return;
            }
        } catch (error) {
            this.showError('Could not check copy cache status');
            return;
        }

        // Use the stored URL and current form settings with copy skip
        document.getElementById('url').value = this.currentUrl;
        
        // Trigger generation with copy skip enabled
        await this.generateBannerWithOptions({ skip_copy: true });
    }

    async regenerateBanner() {
        if (!this.currentUrl) {
            this.showError('No URL to regenerate with');
            return;
        }

        // Use the stored URL and current form settings
        document.getElementById('url').value = this.currentUrl;
        
        // Trigger generation with current settings
        await this.generateBanner();
    }

    resetForm() {
        // Hide results
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Clear form
        document.getElementById('url').value = '';
        document.getElementById('bannerSize').value = 'MD_RECT';
        
        // Reset URL help text
        const urlHelpText = document.querySelector('#url').parentElement.querySelector('p');
        if (urlHelpText) {
            urlHelpText.innerHTML = "We'll extract content and images from this page";
            urlHelpText.className = "text-sm text-gray-500 mt-1";
        }
        
        // Remove uploaded image
        this.removeUploadedImage();
        
        // Reset copy state
        this.selectedCopy = null;
        this.copyVariants = [];
        document.getElementById('generatedCopySection').classList.add('hidden');
        
        // Reset copy status display
        const statusDisplay = document.getElementById('copyStatusDisplay');
        statusDisplay.innerHTML = `
            <span class="text-gray-500">
                <i class="fas fa-exclamation-triangle mr-2 text-orange-500"></i>
                Please generate and select copy first
            </span>
        `;
        statusDisplay.className = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50';
        
        // Disable banner generation again
        const generateBtn = document.getElementById('generateBtn');
        const helpText = generateBtn.parentElement.querySelector('p');
        generateBtn.disabled = true;
        generateBtn.className = 'bg-gradient-to-r from-gray-400 to-gray-500 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200';
        
        if (helpText) {
            helpText.textContent = 'Please generate and select copy to enable banner generation';
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
                this.displayCopyVariants(result.variants);
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

    displayCopyVariants(variants) {
        const container = document.getElementById('copyVariantsContainer');
        container.innerHTML = '';

        variants.forEach((variant, index) => {
            const variantDiv = document.createElement('div');
            variantDiv.className = 'border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors';
            
            variantDiv.innerHTML = `
                <label class="flex items-start space-x-3 cursor-pointer">
                    <input type="radio" name="copyVariant" value="${index}" class="mt-1" ${index === 0 ? 'checked' : ''}>
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-2">
                            <span class="font-semibold text-gray-800 capitalize">${variant.type}</span>
                            <span class="text-xs text-gray-500">${variant.char_count} chars</span>
                        </div>
                        <p class="text-gray-700">${variant.text}</p>
                        <p class="text-xs text-gray-500 mt-1">${variant.tone}</p>
                    </div>
                </label>
            `;
            
            container.appendChild(variantDiv);
        });
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
                <p>Click "Generate AI Banner" to load copy options</p>
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
        generateBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Generate Banner with Selected Copy';
        
        // Add event listener to radio buttons to update button text
        const radioButtons = document.querySelectorAll('input[name="copyVariant"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', () => {
                generateBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Generate Banner with Selected Copy';
            });
        });
    }

    resetGenerateButton() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Generate AI Banner';
    }

    handleCopySelectionRequired(result) {
        // Hide progress section
        this.hideProgressSection();
        
        // Display copy variants
        if (result.copy_variants) {
            this.displayCopyVariants(result.copy_variants);
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
            // Show preview immediately
            const previewImage = document.getElementById('previewImage');
            const uploadedFileName = document.getElementById('uploadedFileName');
            previewImage.src = image.src;
            uploadedFileName.textContent = `Extracted: ${image.alt || 'Untitled'}`;
            document.getElementById('uploadArea').classList.add('hidden');
            document.getElementById('uploadPreview').classList.remove('hidden');

            // Clean up previous upload if exists
            if (this.uploadedImagePath) {
                await this.cleanupUploadedImage(this.uploadedImagePath);
            }

            // Convert image URL to file and upload
            await this.downloadAndUploadImage(image.src, image.alt || 'extracted_image');
            
            this.showSuccessMessage('Image added from extracted images!');
            
        } catch (error) {
            console.error('Error handling extracted image drop:', error);
            this.showError('Failed to use extracted image: ' + error.message);
            this.removeUploadedImage();
        }
    }

    async downloadAndUploadImage(imageUrl, filename) {
        try {
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
                // Fallback: try to fetch directly and upload as blob
                const imgResponse = await fetch(imageUrl, { mode: 'cors' });
                if (!imgResponse.ok) {
                    throw new Error('Failed to download image');
                }
                
                const blob = await imgResponse.blob();
                const file = new File([blob], `${filename}.jpg`, { type: 'image/jpeg' });
                await this.handleFileUpload(file);
                return;
            }

            const result = await response.json();
            if (result.success) {
                this.uploadedImagePath = result.filepath;
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Download and upload error:', error);
            throw error;
        }
    }

    async showCropModal(image) {
        // Create crop modal with loading state
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
            <div class="bg-white rounded-lg crop-modal overflow-hidden flex flex-col">
                <div class="p-4 border-b border-gray-200 flex justify-between items-center flex-shrink-0">
                    <h3 class="text-lg font-semibold">Crop Image</h3>
                    <button id="closeCropModal" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="flex-1 p-4 overflow-hidden">
                    <div id="cropImageContainer" class="crop-image-container mb-4">
                        <div class="loading-state">
                            <i class="fas fa-spinner fa-spin text-2xl text-gray-400 mb-2"></i>
                            <p class="text-gray-600">Loading image for cropping...</p>
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

        let cropper = null;

        // Close modal function
        const closeModal = async () => {
            if (cropper) {
                cropper.destroy();
            }
            // Clean up temp image if it exists
            if (this.currentTempImage) {
                await this.cleanupTempImage(this.currentTempImage);
                this.currentTempImage = null;
            }
            modal.remove();
        };

        // Close button event
        modal.querySelector('#closeCropModal').addEventListener('click', closeModal);

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        try {
            // Try to load image through our proxy to avoid CORS issues
            const proxiedImageUrl = await this.getProxiedImageUrl(image.src, image.alt || 'crop_image');
            
            // Create image element with the proxied URL
            const cropImageContainer = modal.querySelector('#cropImageContainer');
            cropImageContainer.innerHTML = `
                <img id="cropImage" src="${proxiedImageUrl}" 
                     alt="${image.alt || 'Image to crop'}" 
                     crossorigin="anonymous"
                     style="max-width: 100%; max-height: 60vh; width: auto; height: auto;">
            `;

            const cropImage = modal.querySelector('#cropImage');
            
            // Wait for image to load
            await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('Image loading timed out'));
                }, 10000); // 10 second timeout
                
                cropImage.onload = () => {
                    clearTimeout(timeout);
                    resolve();
                };
                cropImage.onerror = () => {
                    clearTimeout(timeout);
                    reject(new Error('Failed to load image'));
                };
            });

            // Initialize cropper with responsive settings
            cropper = new Cropper(cropImage, {
                aspectRatio: NaN, // Free aspect ratio
                viewMode: 1, // Restrict crop box not to exceed the size of the canvas
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
            });

            // Enable buttons
            const resetBtn = modal.querySelector('#resetCrop');
            const useBtn = modal.querySelector('#useCropped');
            resetBtn.disabled = false;
            useBtn.disabled = false;

            // Reset crop button
            resetBtn.addEventListener('click', () => {
                cropper.reset();
            });

            // Use cropped image button
            useBtn.addEventListener('click', async () => {
                try {
                    useBtn.disabled = true;
                    useBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';

                    // Try to get cropped canvas
                    let canvas;
                    try {
                        canvas = cropper.getCroppedCanvas({
                            maxWidth: 2048,
                            maxHeight: 2048,
                            imageSmoothingEnabled: true,
                            imageSmoothingQuality: 'high',
                        });
                    } catch (canvasError) {
                        console.error('Canvas generation failed:', canvasError);
                        throw new Error('Cannot crop this image due to CORS restrictions. Try using the original image instead.');
                    }
                    
                    if (!canvas) {
                        throw new Error('Failed to generate cropped image canvas. This may be due to CORS restrictions.');
                    }
                    
                    // Try to convert to data URL
                    let croppedDataUrl;
                    try {
                        croppedDataUrl = canvas.toDataURL('image/jpeg', 0.9);
                    } catch (dataUrlError) {
                        console.error('Data URL conversion failed:', dataUrlError);
                        throw new Error('Cannot process this image due to security restrictions. Try using the original image instead.');
                    }
                    
                    if (!croppedDataUrl || croppedDataUrl === 'data:,') {
                        throw new Error('Failed to process cropped image. Try using the original image instead.');
                    }
                    
                    // Upload cropped image
                    await this.uploadCroppedImage(croppedDataUrl, image.alt || 'cropped_image');
                    
                    // Clean up temp image before closing
                    if (this.currentTempImage) {
                        await this.cleanupTempImage(this.currentTempImage);
                        this.currentTempImage = null;
                    }
                    
                    closeModal();
                    this.showSuccessMessage('Cropped image uploaded successfully!');
                    
                } catch (error) {
                    console.error('Error cropping image:', error);
                    
                    // Show user-friendly error message with fallback option
                    const errorMessage = error.message.includes('CORS') || error.message.includes('security') || error.message.includes('canvas') ?
                        'This image cannot be cropped due to security restrictions.' :
                        'Failed to crop image: ' + error.message;
                    
                    this.showError(errorMessage + ' You can still use the original image by dragging it to the upload area.');
                    
                    useBtn.disabled = false;
                    useBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Use Cropped Image';
                }
            });

        } catch (error) {
            console.error('Error loading image for cropping:', error);
            
            // Show error in modal
            const cropImageContainer = modal.querySelector('#cropImageContainer');
            cropImageContainer.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-3"></i>
                    <p class="text-red-600 mb-2">Failed to load image for cropping</p>
                    <p class="text-sm text-gray-500">${error.message}</p>
                    <button id="useOriginal" class="mt-4 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                        <i class="fas fa-download mr-2"></i>Use Original Image Instead
                    </button>
                </div>
            `;

            // Use original image button
            modal.querySelector('#useOriginal').addEventListener('click', async () => {
                try {
                    await this.handleExtractedImageDrop(image);
                    closeModal();
                } catch (error) {
                    this.showError('Failed to use original image: ' + error.message);
                }
            });
        }
    }

    async getProxiedImageUrl(imageUrl, filename) {
        try {
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

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Failed to proxy image`);
            }

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
                this.uploadedImagePath = result.filepath;
                
                // Show preview
                const previewImage = document.getElementById('previewImage');
                const uploadedFileName = document.getElementById('uploadedFileName');
                previewImage.src = dataUrl;
                uploadedFileName.textContent = `Cropped: ${filename}`;
                document.getElementById('uploadArea').classList.add('hidden');
                document.getElementById('uploadPreview').classList.remove('hidden');
                
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
            // Show loading state
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
            
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
                this.displayCopyVariants(result.variants);
                this.showSuccessMessage(`Generated ${result.variants.length} copy variants`);
            } else {
                throw new Error(result.error || 'Failed to generate copy');
            }

        } catch (error) {
            console.error('Error generating copy:', error);
            this.showError('Failed to generate copy: ' + error.message);
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-pen-fancy mr-2"></i>Generate Copy';
        }
    }

    displayCopyVariants(variants) {
        const section = document.getElementById('generatedCopySection');
        const container = document.getElementById('copyVariantsContainer');
        
        // Clear previous variants
        container.innerHTML = '';
        
        variants.forEach((variant, index) => {
            const variantDiv = document.createElement('div');
            variantDiv.className = 'border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors';
            
            variantDiv.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                            ${variant.type}
                        </span>
                        <span class="text-xs text-gray-500">${variant.char_count} chars</span>
                    </div>
                    <button class="select-copy-btn px-3 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600 transition-colors" 
                            data-index="${index}">
                        Select
                    </button>
                </div>
                <div class="mb-3">
                    <textarea class="copy-text w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                              rows="2" 
                              data-index="${index}">${variant.text}</textarea>
                </div>
                <p class="text-xs text-gray-500">${variant.tone}</p>
            `;
            
            container.appendChild(variantDiv);
        });

        // Add event listeners for select buttons and text changes
        container.querySelectorAll('.select-copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.selectCopy(index);
            });
        });

        container.querySelectorAll('.copy-text').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.updateCopyVariant(index, e.target.value);
            });
        });
        
        // Show the section
        section.classList.remove('hidden');
    }

    updateCopyVariant(index, newText) {
        if (this.copyVariants[index]) {
            this.copyVariants[index].text = newText;
            this.copyVariants[index].char_count = newText.length;
            
            // Update character count display
            const container = document.getElementById('copyVariantsContainer');
            const charCountSpan = container.children[index].querySelector('.text-xs.text-gray-500');
            charCountSpan.textContent = `${newText.length} chars`;
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
                this.selectedCopy = selectedCopy;
                this.updateCopyStatus(selectedCopy);
                this.enableBannerGeneration();
                this.showSuccessMessage('Copy selected successfully!');
            } else {
                throw new Error(result.error || 'Failed to save copy selection');
            }

        } catch (error) {
            console.error('Error selecting copy:', error);
            this.showError('Failed to select copy: ' + error.message);
        }
    }

    updateCopyStatus(selectedCopy) {
        const statusDisplay = document.getElementById('copyStatusDisplay');
        const indicator = document.getElementById('selectedCopyIndicator');
        
        statusDisplay.innerHTML = `
            <span class="text-green-600">
                <i class="fas fa-check-circle mr-2"></i>
                Selected: "${selectedCopy.text.substring(0, 50)}${selectedCopy.text.length > 50 ? '...' : ''}"
            </span>
        `;
        statusDisplay.className = 'w-full px-4 py-3 border border-green-300 rounded-lg bg-green-50';
        
        if (indicator) {
            indicator.classList.remove('hidden');
        }
    }

    enableBannerGeneration() {
        const generateBtn = document.getElementById('generateBtn');
        const helpText = generateBtn.parentElement.querySelector('p');
        
        generateBtn.disabled = false;
        generateBtn.className = 'bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200';
        
        if (helpText) {
            helpText.textContent = 'Ready to generate your AI banner!';
            helpText.className = 'text-sm text-green-600 mt-2';
        }
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