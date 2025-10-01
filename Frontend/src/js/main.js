// Main JavaScript file for NAYA Travel Journal

// Global variables
let currentSection = 'home';
let map = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('NAYA Travel Journal loaded');
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize modals
    initializeModals();
    
    // Load initial data
    loadInitialData();
    
    // Show home section by default
    showSection('home');
});

// Navigation handling
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                const sectionName = href.substring(1);
                showSection(sectionName);
            }
        });
    });
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show requested section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
        
        // Load section-specific data
        loadSectionData(sectionName);
        
        // Update URL hash
        window.location.hash = sectionName;
    }
}

// Load data specific to each section
async function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'home':
            await loadRecentReviews();
            initializeMap();
            break;
        case 'reviews':
            await loadAllReviews();
            break;
        case 'photos':
            await loadAllPhotos();
            break;
        case 'profile':
            if (auth.isLoggedIn()) {
                await loadUserProfile();
            } else {
                showSection('login');
            }
            break;
    }
}

// Load initial data for the app
async function loadInitialData() {
    try {
        // Load recent reviews for home page
        await loadRecentReviews();
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Load recent reviews
async function loadRecentReviews() {
    try {
        const response = await api.getReviews({ limit: 6 });
        displayReviews(response.reviews, 'reviewsList');
    } catch (error) {
        console.error('Error loading recent reviews:', error);
        document.getElementById('reviewsList').innerHTML = '<p class="error">Failed to load reviews</p>';
    }
}

// Load all reviews
async function loadAllReviews() {
    try {
        const response = await api.getReviews({ limit: CONFIG.DEFAULTS.REVIEWS_PER_PAGE });
        displayReviews(response.reviews, 'allReviewsList');
        setupReviewFilters();
    } catch (error) {
        console.error('Error loading all reviews:', error);
        document.getElementById('allReviewsList').innerHTML = '<p class="error">Failed to load reviews</p>';
    }
}

// Load all photos
async function loadAllPhotos() {
    try {
        const response = await api.getPhotos({ limit: CONFIG.DEFAULTS.PHOTOS_PER_PAGE });
        displayPhotos(response.photos, 'photosList');
        setupPhotoFilters();
    } catch (error) {
        console.error('Error loading photos:', error);
        document.getElementById('photosList').innerHTML = '<p class="error">Failed to load photos</p>';
    }
}

// Load user profile
async function loadUserProfile() {
    try {
        const profile = await api.getProfile();
        displayUserProfile(profile);
        
        // Load user's reviews and photos
        const reviewsResponse = await api.getReviews({ user_id: profile.id });
        const photosResponse = await api.getPhotos({ user_id: profile.id });
        
        displayReviews(reviewsResponse.reviews, 'myReviewsList');
        displayPhotos(photosResponse.photos, 'myPhotosList');
    } catch (error) {
        console.error('Error loading user profile:', error);
    }
}

// Display reviews in a container
function displayReviews(reviews, containerId) {
    const container = document.getElementById(containerId);
    
    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<p class="loading">No reviews found</p>';
        return;
    }
    
    const reviewsHTML = reviews.map(review => `
        <div class="review-card" data-review-id="${review.id}">
            <div class="review-header">
                <div>
                    <div class="review-title">${review.title || 'Untitled Review'}</div>
                    <div class="review-place">${review.place_name || 'Unknown Place'}</div>
                    <div class="review-meta">
                        By ${review.author || 'Anonymous'} • ${formatDate(review.created_at)}
                    </div>
                </div>
                ${review.rating ? `<div class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}</div>` : ''}
            </div>
            <div class="review-text">${review.text}</div>
            ${auth.isLoggedIn() && auth.getCurrentUser().id === review.user_id ? 
                '<div class="review-actions"><button onclick="editReview(\'' + review.id + '\')">Edit</button><button onclick="deleteReview(\'' + review.id + '\')">Delete</button></div>' : ''
            }
        </div>
    `).join('');
    
    container.innerHTML = reviewsHTML;
}

// Display photos in a container
function displayPhotos(photos, containerId) {
    const container = document.getElementById(containerId);
    
    if (!photos || photos.length === 0) {
        container.innerHTML = '<p class="loading">No photos found</p>';
        return;
    }
    
    const photosHTML = photos.map(photo => `
        <div class="photo-card" data-photo-id="${photo.id}">
            <img src="${photo.url}" alt="${photo.caption || 'Travel photo'}" loading="lazy">
            <div class="photo-info">
                <div class="photo-caption">${photo.caption || ''}</div>
                <div class="photo-meta">
                    ${photo.place_name || 'Unknown Location'} • By ${photo.uploader || 'Anonymous'} • ${formatDate(photo.created_at)}
                </div>
                ${auth.isLoggedIn() && auth.getCurrentUser().id === photo.user_id ? 
                    '<div class="photo-actions"><button onclick="deletePhoto(\'' + photo.id + '\')">Delete</button></div>' : ''
                }
            </div>
        </div>
    `).join('');
    
    container.innerHTML = photosHTML;
}

// Display user profile
function displayUserProfile(profile) {
    const container = document.getElementById('profileInfo');
    
    const profileHTML = `
        <div class="profile-info">
            <h3>${profile.username}</h3>
            <p><strong>Email:</strong> ${profile.email}</p>
            <p><strong>Member since:</strong> ${formatDate(profile.created_at)}</p>
        </div>
    `;
    
    container.innerHTML = profileHTML;
}

// Setup review filters
function setupReviewFilters() {
    const countryFilter = document.getElementById('countryFilter');
    const ratingFilter = document.getElementById('ratingFilter');
    
    if (countryFilter) {
        countryFilter.addEventListener('input', debounce(filterReviews, 300));
    }
    
    if (ratingFilter) {
        ratingFilter.addEventListener('change', filterReviews);
    }
}

// Setup photo filters
function setupPhotoFilters() {
    const photoCountryFilter = document.getElementById('photoCountryFilter');
    
    if (photoCountryFilter) {
        photoCountryFilter.addEventListener('input', debounce(filterPhotos, 300));
    }
}

// Filter reviews
async function filterReviews() {
    const country = document.getElementById('countryFilter').value;
    const rating = document.getElementById('ratingFilter').value;
    
    try {
        const params = {};
        if (country) params.country = country;
        // Note: rating filter would need backend support
        
        const response = await api.getReviews(params);
        displayReviews(response.reviews, 'allReviewsList');
    } catch (error) {
        console.error('Error filtering reviews:', error);
    }
}

// Filter photos
async function filterPhotos() {
    const country = document.getElementById('photoCountryFilter').value;
    
    try {
        const params = {};
        if (country) params.country = country;
        
        const response = await api.getPhotos(params);
        displayPhotos(response.photos, 'photosList');
    } catch (error) {
        console.error('Error filtering photos:', error);
    }
}

// Modal handling
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    const closes = document.querySelectorAll('.close');
    
    closes.forEach(close => {
        close.addEventListener('click', function() {
            const modal = this.closest('.modal');
            modal.style.display = 'none';
        });
    });
    
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
    
    // Add review button
    const addReviewBtn = document.getElementById('addReviewBtn');
    if (addReviewBtn) {
        addReviewBtn.addEventListener('click', function() {
            document.getElementById('reviewModal').style.display = 'block';
        });
    }
    
    // Add photo button
    const addPhotoBtn = document.getElementById('addPhotoBtn');
    if (addPhotoBtn) {
        addPhotoBtn.addEventListener('click', function() {
            document.getElementById('photoModal').style.display = 'block';
        });
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Review actions
async function editReview(reviewId) {
    // Implementation for editing reviews
    console.log('Edit review:', reviewId);
}

async function deleteReview(reviewId) {
    if (confirm('Are you sure you want to delete this review?')) {
        try {
            await api.deleteReview(reviewId);
            showSuccess('Review deleted successfully');
            loadSectionData(currentSection);
        } catch (error) {
            showError('Failed to delete review: ' + error.message);
        }
    }
}

// Photo actions
async function deletePhoto(photoId) {
    if (confirm('Are you sure you want to delete this photo?')) {
        try {
            await api.deletePhoto(photoId);
            showSuccess('Photo deleted successfully');
            loadSectionData(currentSection);
        } catch (error) {
            showError('Failed to delete photo: ' + error.message);
        }
    }
}

// Handle browser back/forward
window.addEventListener('hashchange', function() {
    const hash = window.location.hash.substring(1);
    if (hash && document.getElementById(hash)) {
        showSection(hash);
    }
});

// Initialize on load
window.addEventListener('load', function() {
    const hash = window.location.hash.substring(1);
    if (hash && document.getElementById(hash)) {
        showSection(hash);
    }
});