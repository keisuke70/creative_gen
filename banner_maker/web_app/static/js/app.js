// AI Banner Maker - Frontend JavaScript

class BannerMaker {
    constructor() {
        this.currentSessionId = null;
        this.uploadedImagePath = null;
        this.pollInterval = null;
        this.currentUrl = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('bannerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateBanner();
        });

        // File upload
        this.initializeFileUpload();

        // Regenerate with same copy button - fastest option
        document.getElementById('regenerateWithCopyBtn').addEventListener('click', () => {
            this.regenerateWithSameCopy();
        });

        // Regenerate button - keep current URL and settings
        document.getElementById('regenerateBtn').addEventListener('click', () => {
            this.regenerateBanner();
        });

        // Create another button - reset everything
        document.getElementById('createAnotherBtn').addEventListener('click', () => {
            this.resetForm();
        });

        // URL input cache check
        let urlCheckTimeout;
        document.getElementById('url').addEventListener('input', (e) => {
            clearTimeout(urlCheckTimeout);
            urlCheckTimeout = setTimeout(() => {
                this.checkUrlCacheStatus(e.target.value.trim());
            }, 1000); // Check after 1 second of no typing
        });
    }


    initializeFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('productImage');
        const uploadPreview = document.getElementById('uploadPreview');
        const removeButton = document.getElementById('removeImage');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
            
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

    removeUploadedImage() {
        this.uploadedImagePath = null;
        document.getElementById('uploadArea').classList.remove('hidden');
        document.getElementById('uploadPreview').classList.add('hidden');
        document.getElementById('productImage').value = '';
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

        // Store current URL for regeneration
        this.currentUrl = url;

        // Check cache status (unless skip_copy is true)
        if (!options.skip_copy) {
            await this.checkCacheStatus(url);
        }

        const formData = {
            url: url,
            banner_size: document.getElementById('bannerSize').value,
            copy_type: document.getElementById('copyType').value,
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
        
        // Set download links
        document.getElementById('downloadBanner').href = `/api/download/${this.currentSessionId}/banner`;
        document.getElementById('downloadHTML').href = `/api/download/${this.currentSessionId}/html`;
        document.getElementById('downloadCSS').href = `/api/download/${this.currentSessionId}/css`;
        
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
        document.getElementById('bannerSize').value = '1024x1024';
        document.getElementById('copyType').value = 'auto';
        
        // Reset URL help text
        const urlHelpText = document.querySelector('#url + p');
        urlHelpText.innerHTML = "We'll extract content and images from this page";
        urlHelpText.className = "text-sm text-gray-500 mt-1";
        
        // Remove uploaded image
        this.removeUploadedImage();
        
        // Reset session and URL
        this.currentSessionId = null;
        this.currentUrl = null;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async checkUrlCacheStatus(url) {
        const urlHelpText = document.querySelector('#url + p');
        
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
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BannerMaker();
});