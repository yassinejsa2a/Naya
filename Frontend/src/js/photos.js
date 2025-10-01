// Photos Management for NAYA

// Initialize photos functionality
document.addEventListener('DOMContentLoaded', function() {
    setupPhotoForm();
});

// Setup add photo form
function setupPhotoForm() {
    const addPhotoForm = document.getElementById('addPhotoForm');
    
    if (addPhotoForm) {
        addPhotoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!auth.isLoggedIn()) {
                showError('You must be logged in to upload photos');
                return;
            }
            
            const fileInput = document.getElementById('photoFile');
            const placeInput = document.getElementById('photoPlace');
            const captionInput = document.getElementById('photoCaption');
            
            // Validate inputs
            if (!fileInput.files[0]) {
                showError('Please select a photo to upload');
                return;
            }
            
            if (!placeInput.value.trim()) {
                showError('Please specify a place for this photo');
                return;
            }
            
            try {
                showLoading('Uploading photo...');
                
                // Get or create place
                const placeId = this.dataset.placeId || await getOrCreatePlaceForPhoto();
                
                // Create form data for file upload
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('place_id', placeId);
                
                if (captionInput.value.trim()) {
                    formData.append('caption', captionInput.value.trim());
                }
                
                const response = await api.uploadPhoto(formData);
                
                showSuccess('Photo uploaded successfully!');
                document.getElementById('photoModal').style.display = 'none';
                this.reset();
                
                // Reload current section data
                loadSectionData(currentSection);
                
            } catch (error) {
                showError('Failed to upload photo: ' + error.message);
            } finally {
                hideLoading();
            }
        });
        
        // Setup file input preview
        const fileInput = document.getElementById('photoFile');
        if (fileInput) {
            fileInput.addEventListener('change', handlePhotoPreview);
        }
    }
}

// Handle photo preview
function handlePhotoPreview(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid image file (JPEG, PNG, or GIF)');
        event.target.value = '';
        return;
    }
    
    // Validate file size (e.g., 5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        showError('File size must be less than 5MB');
        event.target.value = '';
        return;
    }
    
    // Create preview
    const reader = new FileReader();
    reader.onload = function(e) {
        // Remove existing preview
        const existingPreview = document.getElementById('photoPreview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        // Create new preview
        const preview = document.createElement('div');
        preview.id = 'photoPreview';
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Photo preview" style="max-width: 200px; max-height: 200px; margin-top: 10px; border-radius: 5px;">
        `;
        
        event.target.parentNode.appendChild(preview);
    };
    
    reader.readAsDataURL(file);
}

// Get or create place for photo
async function getOrCreatePlaceForPhoto() {
    const placeName = document.getElementById('photoPlace').value.trim();
    
    if (!placeName) {
        throw new Error('Place name is required');
    }
    
    try {
        // Create a simple place object
        const placeData = {
            name: placeName,
            country: 'Unknown', // You'd need to get this from user input or geocoding
            description: `Place added via photo upload: ${placeName}`
        };
        
        const newPlace = await api.createPlace(placeData);
        return newPlace.place_id;
        
    } catch (error) {
        console.error('Error creating place:', error);
        throw new Error('Failed to create place for photo');
    }
}

// Load photos with advanced filtering
async function loadPhotosWithFilters(filters = {}) {
    try {
        showLoading('Loading photos...');
        
        const params = {
            limit: filters.limit || CONFIG.DEFAULTS.PHOTOS_PER_PAGE,
            offset: filters.offset || 0
        };
        
        // Add filters
        if (filters.country) params.country = filters.country;
        if (filters.user_id) params.user_id = filters.user_id;
        if (filters.place_id) params.place_id = filters.place_id;
        
        const response = await api.getPhotos(params);
        
        return response;
        
    } catch (error) {
        console.error('Error loading photos:', error);
        throw error;
    } finally {
        hideLoading();
    }
}

// Delete photo with confirmation
async function deletePhoto(photoId) {
    const confirmed = confirm('Are you sure you want to delete this photo? This action cannot be undone.');
    
    if (!confirmed) return;
    
    try {
        showLoading('Deleting photo...');
        await api.deletePhoto(photoId);
        
        showSuccess('Photo deleted successfully!');
        
        // Reload current section data
        loadSectionData(currentSection);
        
    } catch (error) {
        showError('Failed to delete photo: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Create photo lightbox/modal for full-size viewing
function createPhotoLightbox(photo) {
    const lightbox = document.createElement('div');
    lightbox.className = 'photo-lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-overlay">
            <div class="lightbox-content">
                <span class="lightbox-close">&times;</span>
                <img src="${photo.url}" alt="${photo.caption || 'Travel photo'}">
                <div class="lightbox-info">
                    <h3>${photo.place_name || 'Unknown Location'}</h3>
                    <p>${photo.caption || ''}</p>
                    <div class="photo-meta">
                        By ${photo.uploader || 'Anonymous'} • ${formatDate(photo.created_at)}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add styles for lightbox
    const styles = `
        <style>
        .photo-lightbox {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 3000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .lightbox-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
        }
        
        .lightbox-content {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            background: white;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .lightbox-content img {
            width: 100%;
            height: auto;
            max-height: 70vh;
            object-fit: contain;
        }
        
        .lightbox-close {
            position: absolute;
            top: 10px;
            right: 15px;
            color: white;
            font-size: 30px;
            font-weight: bold;
            cursor: pointer;
            z-index: 3001;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .lightbox-info {
            padding: 15px;
        }
        
        .lightbox-info h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        
        .lightbox-info p {
            margin: 0 0 10px 0;
            color: #555;
        }
        
        .lightbox-info .photo-meta {
            font-size: 0.9rem;
            color: #7f8c8d;
        }
        </style>
    `;
    
    if (!document.getElementById('lightbox-styles')) {
        const styleElement = document.createElement('div');
        styleElement.id = 'lightbox-styles';
        styleElement.innerHTML = styles;
        document.head.appendChild(styleElement);
    }
    
    // Setup close functionality
    const closeBtn = lightbox.querySelector('.lightbox-close');
    const overlay = lightbox.querySelector('.lightbox-overlay');
    
    const closeLightbox = () => {
        lightbox.remove();
    };
    
    closeBtn.addEventListener('click', closeLightbox);
    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            closeLightbox();
        }
    });
    
    // Close on escape key
    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            closeLightbox();
            document.removeEventListener('keydown', handleKeyDown);
        }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    return lightbox;
}

// Show photo in lightbox
function showPhotoInLightbox(photoId) {
    // Find photo data (you'd need to store this or fetch it)
    const photoCard = document.querySelector(`[data-photo-id="${photoId}"]`);
    if (!photoCard) return;
    
    const img = photoCard.querySelector('img');
    const caption = photoCard.querySelector('.photo-caption')?.textContent || '';
    const meta = photoCard.querySelector('.photo-meta')?.textContent || '';
    
    const photo = {
        url: img.src,
        caption: caption,
        place_name: meta.split('•')[0]?.trim() || 'Unknown Location',
        uploader: meta.split('•')[1]?.split('•')[0]?.replace('By', '').trim() || 'Anonymous',
        created_at: meta.split('•')[2]?.trim() || ''
    };
    
    const lightbox = createPhotoLightbox(photo);
    document.body.appendChild(lightbox);
}

// Sort photos
function sortPhotos(photos, sortBy = 'date', order = 'desc') {
    return photos.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'date':
                aValue = new Date(a.created_at);
                bValue = new Date(b.created_at);
                break;
            case 'place':
                aValue = (a.place_name || '').toLowerCase();
                bValue = (b.place_name || '').toLowerCase();
                break;
            case 'uploader':
                aValue = (a.uploader || '').toLowerCase();
                bValue = (b.uploader || '').toLowerCase();
                break;
            default:
                return 0;
        }
        
        if (order === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
}

// Filter photos by multiple criteria
function filterPhotos(photos, filters) {
    return photos.filter(photo => {
        // Filter by country/place
        if (filters.country && !photo.place_name?.toLowerCase().includes(filters.country.toLowerCase())) {
            return false;
        }
        
        // Filter by uploader
        if (filters.uploader && !photo.uploader?.toLowerCase().includes(filters.uploader.toLowerCase())) {
            return false;
        }
        
        // Filter by caption content
        if (filters.searchText) {
            const searchText = filters.searchText.toLowerCase();
            const caption = (photo.caption || '').toLowerCase();
            const placeName = (photo.place_name || '').toLowerCase();
            
            if (!caption.includes(searchText) && !placeName.includes(searchText)) {
                return false;
            }
        }
        
        return true;
    });
}

// Create photo gallery grid
function createPhotoGallery(photos, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!photos || photos.length === 0) {
        container.innerHTML = '<p class="loading">No photos found</p>';
        return;
    }
    
    const photosHTML = photos.map(photo => `
        <div class="photo-card" data-photo-id="${photo.id}">
            <img src="${photo.url}" 
                 alt="${photo.caption || 'Travel photo'}" 
                 loading="lazy"
                 onclick="showPhotoInLightbox('${photo.id}')">
            <div class="photo-info">
                <div class="photo-caption">${photo.caption || ''}</div>
                <div class="photo-meta">
                    ${photo.place_name || 'Unknown Location'} • By ${photo.uploader || 'Anonymous'} • ${formatDate(photo.created_at)}
                </div>
                ${auth.isLoggedIn() && auth.getCurrentUser().id === photo.user_id ? 
                    `<div class="photo-actions">
                        <button onclick="deletePhoto('${photo.id}')" class="btn-small btn-danger">Delete</button>
                    </div>` : ''
                }
            </div>
        </div>
    `).join('');
    
    container.innerHTML = photosHTML;
}

// Export functions for global access
window.deletePhoto = deletePhoto;
window.showPhotoInLightbox = showPhotoInLightbox;