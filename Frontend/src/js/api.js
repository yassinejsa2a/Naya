// API Communication Module for NAYA

class API {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
        } else {
            localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        }
    }

    // Get authentication headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: this.getHeaders(options.auth !== false),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Authentication methods
    async register(userData) {
        return this.request(CONFIG.ENDPOINTS.AUTH.REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData),
            auth: false
        });
    }

    async login(credentials) {
        return this.request(CONFIG.ENDPOINTS.AUTH.LOGIN, {
            method: 'POST',
            body: JSON.stringify(credentials),
            auth: false
        });
    }

    async getProfile() {
        return this.request(CONFIG.ENDPOINTS.AUTH.PROFILE);
    }

    async updateProfile(userData) {
        return this.request(CONFIG.ENDPOINTS.AUTH.PROFILE, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    // Reviews methods
    async getReviews(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `${CONFIG.ENDPOINTS.REVIEWS}?${queryString}` : CONFIG.ENDPOINTS.REVIEWS;
        return this.request(endpoint, { auth: false });
    }

    async createReview(reviewData) {
        return this.request(CONFIG.ENDPOINTS.REVIEWS, {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    }

    async getReview(reviewId) {
        return this.request(`${CONFIG.ENDPOINTS.REVIEWS}/${reviewId}`, { auth: false });
    }

    async updateReview(reviewId, reviewData) {
        return this.request(`${CONFIG.ENDPOINTS.REVIEWS}/${reviewId}`, {
            method: 'PUT',
            body: JSON.stringify(reviewData)
        });
    }

    async deleteReview(reviewId) {
        return this.request(`${CONFIG.ENDPOINTS.REVIEWS}/${reviewId}`, {
            method: 'DELETE'
        });
    }

    // Photos methods
    async getPhotos(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `${CONFIG.ENDPOINTS.PHOTOS}?${queryString}` : CONFIG.ENDPOINTS.PHOTOS;
        return this.request(endpoint, { auth: false });
    }

    async uploadPhoto(formData) {
        // For file uploads, we don't set Content-Type to let browser set boundary
        const headers = {};
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const url = `${this.baseURL}${CONFIG.ENDPOINTS.PHOTOS}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    }

    async deletePhoto(photoId) {
        return this.request(`${CONFIG.ENDPOINTS.PHOTOS}/${photoId}`, {
            method: 'DELETE'
        });
    }

    // Places methods
    async getPlaces(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `${CONFIG.ENDPOINTS.PLACES}?${queryString}` : CONFIG.ENDPOINTS.PLACES;
        return this.request(endpoint, { auth: false });
    }

    async searchPlaces(query, location = null) {
        const params = { q: query };
        if (location) {
            params.location = location;
        }
        const queryString = new URLSearchParams(params).toString();
        return this.request(`${CONFIG.ENDPOINTS.PLACES}/search?${queryString}`, { auth: false });
    }

    async createPlace(placeData) {
        return this.request(CONFIG.ENDPOINTS.PLACES, {
            method: 'POST',
            body: JSON.stringify(placeData)
        });
    }

    async getPlace(placeId) {
        return this.request(`${CONFIG.ENDPOINTS.PLACES}/${placeId}`, { auth: false });
    }
}

// Create global API instance
const api = new API();