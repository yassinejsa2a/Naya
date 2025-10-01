// Authentication Module for NAYA

class Auth {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.loadUserFromStorage();
    }

    // Load user data from localStorage
    loadUserFromStorage() {
        const token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
        const user = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);

        if (token && user) {
            try {
                this.currentUser = JSON.parse(user);
                this.isAuthenticated = true;
                api.setToken(token);
            } catch (error) {
                console.error('Error parsing user data:', error);
                this.logout();
            }
        }
    }

    // Save user data to localStorage
    saveUserToStorage(user, token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(user));
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
    }

    // Register new user
    async register(userData) {
        try {
            const response = await api.register(userData);
            
            // Auto-login after registration
            const loginResponse = await api.login({
                email: userData.email,
                password: userData.password
            });

            this.handleLoginSuccess(loginResponse);
            return response;
        } catch (error) {
            throw error;
        }
    }

    // Login user
    async login(credentials) {
        try {
            const response = await api.login(credentials);
            this.handleLoginSuccess(response);
            return response;
        } catch (error) {
            throw error;
        }
    }

    // Handle successful login
    handleLoginSuccess(response) {
        const user = {
            id: response.user_id,
            username: response.username
        };

        this.currentUser = user;
        this.isAuthenticated = true;
        
        api.setToken(response.token);
        this.saveUserToStorage(user, response.token);
        
        this.updateUI();
    }

    // Logout user
    logout() {
        this.currentUser = null;
        this.isAuthenticated = false;
        
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        
        api.setToken(null);
        this.updateUI();
        
        // Redirect to home
        showSection('home');
    }

    // Update UI based on authentication state
    updateUI() {
        const loginLink = document.getElementById('loginLink');
        const registerLink = document.getElementById('registerLink');
        const profileLink = document.getElementById('profileLink');
        const logoutBtn = document.getElementById('logoutBtn');
        const addReviewBtn = document.getElementById('addReviewBtn');
        const addPhotoBtn = document.getElementById('addPhotoBtn');

        if (this.isAuthenticated) {
            // Show authenticated user UI
            loginLink.style.display = 'none';
            registerLink.style.display = 'none';
            profileLink.style.display = 'block';
            logoutBtn.style.display = 'block';
            
            if (addReviewBtn) addReviewBtn.style.display = 'block';
            if (addPhotoBtn) addPhotoBtn.style.display = 'block';
        } else {
            // Show guest user UI
            loginLink.style.display = 'block';
            registerLink.style.display = 'block';
            profileLink.style.display = 'none';
            logoutBtn.style.display = 'none';
            
            if (addReviewBtn) addReviewBtn.style.display = 'none';
            if (addPhotoBtn) addPhotoBtn.style.display = 'none';
        }
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Check if user is authenticated
    isLoggedIn() {
        return this.isAuthenticated;
    }
}

// Initialize authentication
const auth = new Auth();

// Form handlers
document.addEventListener('DOMContentLoaded', function() {
    // Login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                showLoading('Logging in...');
                await auth.login({ email, password });
                showSuccess('Login successful!');
                showSection('home');
            } catch (error) {
                showError('Login failed: ' + error.message);
            } finally {
                hideLoading();
            }
        });
    }

    // Register form handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            
            try {
                showLoading('Creating account...');
                await auth.register({ username, email, password });
                showSuccess('Account created successfully!');
                showSection('home');
            } catch (error) {
                showError('Registration failed: ' + error.message);
            } finally {
                hideLoading();
            }
        });
    }

    // Logout button handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            auth.logout();
            showSuccess('Logged out successfully!');
        });
    }

    // Initialize UI
    auth.updateUI();
});

// Utility functions for showing messages
function showLoading(message = 'Loading...') {
    // You can implement a loading spinner here
    console.log(message);
}

function hideLoading() {
    // Hide loading spinner
    console.log('Loading complete');
}

function showError(message) {
    // You can implement error display here
    alert('Error: ' + message);
    console.error(message);
}

function showSuccess(message) {
    // You can implement success display here
    console.log('Success: ' + message);
}