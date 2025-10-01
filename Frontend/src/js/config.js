// Configuration for NAYA Travel Journal

const CONFIG = {
    // Backend API URL - Update this when deploying
    API_BASE_URL: 'http://localhost:5000/api',
    
    // Google Maps API Key - Will be set from backend or environment
    GOOGLE_MAPS_API_KEY: 'YOUR_API_KEY_HERE',
    
    // Local Storage Keys
    STORAGE_KEYS: {
        TOKEN: 'naya_token',
        USER: 'naya_user'
    },
    
    // API Endpoints
    ENDPOINTS: {
        AUTH: {
            REGISTER: '/register',
            LOGIN: '/login',
            PROFILE: '/profile'
        },
        REVIEWS: '/reviews',
        PHOTOS: '/photos',
        PLACES: '/places'
    },
    
    // Default settings
    DEFAULTS: {
        REVIEWS_PER_PAGE: 20,
        PHOTOS_PER_PAGE: 24,
        PLACES_PER_PAGE: 50
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}