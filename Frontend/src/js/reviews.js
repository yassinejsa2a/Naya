// Reviews Management for NAYA

// Initialize reviews functionality
document.addEventListener('DOMContentLoaded', function() {
    setupReviewForm();
});

// Setup add review form
function setupReviewForm() {
    const addReviewForm = document.getElementById('addReviewForm');
    
    if (addReviewForm) {
        addReviewForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!auth.isLoggedIn()) {
                showError('You must be logged in to add a review');
                return;
            }
            
            const formData = new FormData(this);
            const reviewData = {
                place_id: this.dataset.placeId || await getOrCreatePlace(),
                title: document.getElementById('reviewTitle').value.trim(),
                text: document.getElementById('reviewText').value.trim(),
                rating: document.getElementById('reviewRating').value ? parseInt(document.getElementById('reviewRating').value) : null
            };
            
            try {
                showLoading('Adding review...');
                const response = await api.createReview(reviewData);
                
                showSuccess('Review added successfully!');
                document.getElementById('reviewModal').style.display = 'none';
                this.reset();
                
                // Reload current section data
                loadSectionData(currentSection);
                
            } catch (error) {
                showError('Failed to add review: ' + error.message);
            } finally {
                hideLoading();
            }
        });
    }
}

// Get or create place for review
async function getOrCreatePlace() {
    const placeName = document.getElementById('reviewPlace').value.trim();
    
    if (!placeName) {
        throw new Error('Place name is required');
    }
    
    try {
        // First, try to find existing place
        const placesResponse = await api.getPlaces({ limit: 1 });
        
        // For now, create a simple place object
        // In a full implementation, you'd search for existing places
        const placeData = {
            name: placeName,
            country: 'Unknown', // You'd need to get this from user input or geocoding
            description: `Place added via review: ${placeName}`
        };
        
        const newPlace = await api.createPlace(placeData);
        return newPlace.place_id;
        
    } catch (error) {
        console.error('Error creating place:', error);
        throw new Error('Failed to create place for review');
    }
}

// Load reviews with advanced filtering
async function loadReviewsWithFilters(filters = {}) {
    try {
        showLoading('Loading reviews...');
        
        const params = {
            limit: filters.limit || CONFIG.DEFAULTS.REVIEWS_PER_PAGE,
            offset: filters.offset || 0
        };
        
        // Add filters
        if (filters.country) params.country = filters.country;
        if (filters.user_id) params.user_id = filters.user_id;
        if (filters.place_id) params.place_id = filters.place_id;
        
        const response = await api.getReviews(params);
        
        return response;
        
    } catch (error) {
        console.error('Error loading reviews:', error);
        throw error;
    } finally {
        hideLoading();
    }
}

// Edit review
async function editReview(reviewId) {
    try {
        // Get review data
        const review = await api.getReview(reviewId);
        
        // Populate edit form (you'd need to create this modal)
        const editModal = createEditReviewModal(review);
        document.body.appendChild(editModal);
        editModal.style.display = 'block';
        
    } catch (error) {
        showError('Failed to load review for editing: ' + error.message);
    }
}

// Create edit review modal
function createEditReviewModal(review) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'editReviewModal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Edit Review</h2>
            <form id="editReviewForm">
                <div class="form-group">
                    <label for="editReviewTitle">Title:</label>
                    <input type="text" id="editReviewTitle" value="${review.title || ''}">
                </div>
                <div class="form-group">
                    <label for="editReviewText">Review:</label>
                    <textarea id="editReviewText" required>${review.text}</textarea>
                </div>
                <div class="form-group">
                    <label for="editReviewRating">Rating:</label>
                    <select id="editReviewRating">
                        <option value="">No rating</option>
                        <option value="1" ${review.rating === 1 ? 'selected' : ''}>1 star</option>
                        <option value="2" ${review.rating === 2 ? 'selected' : ''}>2 stars</option>
                        <option value="3" ${review.rating === 3 ? 'selected' : ''}>3 stars</option>
                        <option value="4" ${review.rating === 4 ? 'selected' : ''}>4 stars</option>
                        <option value="5" ${review.rating === 5 ? 'selected' : ''}>5 stars</option>
                    </select>
                </div>
                <button type="submit" class="btn-primary">Update Review</button>
                <button type="button" class="btn-secondary" onclick="closeEditModal()">Cancel</button>
            </form>
        </div>
    `;
    
    // Setup form submission
    const form = modal.querySelector('#editReviewForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const updateData = {
            title: document.getElementById('editReviewTitle').value.trim(),
            text: document.getElementById('editReviewText').value.trim(),
            rating: document.getElementById('editReviewRating').value ? parseInt(document.getElementById('editReviewRating').value) : null
        };
        
        try {
            showLoading('Updating review...');
            await api.updateReview(review.id, updateData);
            
            showSuccess('Review updated successfully!');
            modal.remove();
            
            // Reload current section data
            loadSectionData(currentSection);
            
        } catch (error) {
            showError('Failed to update review: ' + error.message);
        } finally {
            hideLoading();
        }
    });
    
    // Setup close functionality
    const closeBtn = modal.querySelector('.close');
    closeBtn.addEventListener('click', function() {
        modal.remove();
    });
    
    return modal;
}

// Close edit modal
function closeEditModal() {
    const modal = document.getElementById('editReviewModal');
    if (modal) {
        modal.remove();
    }
}

// Delete review with confirmation
async function deleteReview(reviewId) {
    const confirmed = confirm('Are you sure you want to delete this review? This action cannot be undone.');
    
    if (!confirmed) return;
    
    try {
        showLoading('Deleting review...');
        await api.deleteReview(reviewId);
        
        showSuccess('Review deleted successfully!');
        
        // Reload current section data
        loadSectionData(currentSection);
        
    } catch (error) {
        showError('Failed to delete review: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Sort reviews
function sortReviews(reviews, sortBy = 'date', order = 'desc') {
    return reviews.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'date':
                aValue = new Date(a.created_at);
                bValue = new Date(b.created_at);
                break;
            case 'rating':
                aValue = a.rating || 0;
                bValue = b.rating || 0;
                break;
            case 'title':
                aValue = (a.title || '').toLowerCase();
                bValue = (b.title || '').toLowerCase();
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

// Filter reviews by multiple criteria
function filterReviews(reviews, filters) {
    return reviews.filter(review => {
        // Filter by country
        if (filters.country && !review.place_name?.toLowerCase().includes(filters.country.toLowerCase())) {
            return false;
        }
        
        // Filter by rating
        if (filters.minRating && (!review.rating || review.rating < filters.minRating)) {
            return false;
        }
        
        // Filter by author
        if (filters.author && !review.author?.toLowerCase().includes(filters.author.toLowerCase())) {
            return false;
        }
        
        // Filter by text content
        if (filters.searchText) {
            const searchText = filters.searchText.toLowerCase();
            const title = (review.title || '').toLowerCase();
            const text = (review.text || '').toLowerCase();
            
            if (!title.includes(searchText) && !text.includes(searchText)) {
                return false;
            }
        }
        
        return true;
    });
}

// Get review statistics
function getReviewStats(reviews) {
    if (!reviews || reviews.length === 0) {
        return {
            total: 0,
            averageRating: 0,
            ratingDistribution: {}
        };
    }
    
    const reviewsWithRating = reviews.filter(r => r.rating);
    const totalRating = reviewsWithRating.reduce((sum, r) => sum + r.rating, 0);
    const averageRating = reviewsWithRating.length > 0 ? totalRating / reviewsWithRating.length : 0;
    
    const ratingDistribution = {
        1: 0, 2: 0, 3: 0, 4: 0, 5: 0
    };
    
    reviewsWithRating.forEach(review => {
        ratingDistribution[review.rating]++;
    });
    
    return {
        total: reviews.length,
        averageRating: Math.round(averageRating * 10) / 10,
        ratingDistribution
    };
}

// Export functions for global access
window.editReview = editReview;
window.deleteReview = deleteReview;
window.closeEditModal = closeEditModal;