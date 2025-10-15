const views = Array.from(document.querySelectorAll('.view'));
const navButtons = Array.from(document.querySelectorAll('.nav-btn[data-target]'));
const logoutBtn = document.getElementById('logout-btn');
const apiConfigBtn = document.getElementById('api-config-btn');
const apiIndicator = document.getElementById('api-indicator');
const globalFeedback = document.getElementById('global-feedback');
const yearEl = document.getElementById('year');
const authView = document.getElementById('auth-view');
const feedView = document.getElementById('feed-view');
const addReviewView = document.getElementById('add-review-view');
const profileView = document.getElementById('profile-view');

const normaliseApiBaseUrl = (value) => {
  if (!value) {
    throw new Error('The API base URL cannot be empty.');
  }

  let candidate = value.trim();
  if (!candidate) {
    throw new Error('The API base URL cannot be empty.');
  }

  if (!/^https?:\/\//i.test(candidate)) {
    candidate = `https://${candidate}`;
  }

  const url = new URL(candidate);
  url.hash = '';
  url.search = '';

  let path = url.pathname || '';
  if (!path || path === '/') {
    path = '/api/v1';
  }

  return `${url.origin}${path.replace(/\/$/, '')}`;
};

const detectDefaultApiBaseUrl = () => {
  const metaTag = document.querySelector('meta[name="naya-api-base"]');
  if (metaTag?.content) {
    try {
      return normaliseApiBaseUrl(metaTag.content);
    } catch (error) {
      console.warn('NAYA: invalid API base defined in <meta name="naya-api-base">.', error);
    }
  }

  if (window.location.origin && window.location.origin.startsWith('http')) {
    try {
      return normaliseApiBaseUrl(window.location.origin);
    } catch (error) {
      console.warn('NAYA: unable to derive API base URL from window.location.origin.', error);
    }
  }

  return 'http://localhost:5000/api/v1';
};

const defaultApiBaseUrl = detectDefaultApiBaseUrl();

let apiBaseUrl = defaultApiBaseUrl;

try {
  const storedBase = window.localStorage.getItem('naya-api-base');
  if (storedBase) {
    apiBaseUrl = normaliseApiBaseUrl(storedBase);
    window.localStorage.setItem('naya-api-base', apiBaseUrl);
  }
} catch (error) {
  console.warn('NAYA: invalid stored API base URL, resetting to default.', error);
  window.localStorage.removeItem('naya-api-base');
  apiBaseUrl = defaultApiBaseUrl;
}

let globalMessageTimeoutId;

const updateApiIndicator = () => {
  if (!apiIndicator) return;
  try {
    const url = new URL(apiBaseUrl);
    apiIndicator.textContent = `API: ${url.origin}${url.pathname}`;
    apiIndicator.title = `${url.origin}${url.pathname}`;
  } catch (error) {
    apiIndicator.textContent = `API: ${apiBaseUrl}`;
    apiIndicator.title = apiBaseUrl;
  }
};

const showGlobalMessage = (message, isError = false, duration = 6000) => {
  if (!globalFeedback) return;

  if (globalMessageTimeoutId) {
    window.clearTimeout(globalMessageTimeoutId);
    globalMessageTimeoutId = null;
  }

  if (!message) {
    globalFeedback.textContent = '';
    globalFeedback.classList.add('hidden');
    globalFeedback.classList.remove('error');
    return;
  }

  globalFeedback.textContent = message;
  globalFeedback.classList.remove('hidden');
  globalFeedback.classList.toggle('error', isError);

  globalMessageTimeoutId = window.setTimeout(() => {
    globalFeedback.textContent = '';
    globalFeedback.classList.add('hidden');
    globalFeedback.classList.remove('error');
  }, duration);
};

const setApiBaseUrl = (value, { persist = true } = {}) => {
  apiBaseUrl = value;
  if (persist) {
    window.localStorage.setItem('naya-api-base', value);
  } else {
    window.localStorage.removeItem('naya-api-base');
  }
  updateApiIndicator();
};

const handleApiConfigClick = () => {
  const currentValue = apiBaseUrl;
  const hint = 'Example: https://naya-backend.example.com/api/v1';
  const userInput = window.prompt(`Enter the base URL of your NAYA API.\n${hint}`, currentValue);

  if (userInput === null) {
    return;
  }

  const trimmed = userInput.trim();

  if (!trimmed) {
    setApiBaseUrl(defaultApiBaseUrl, { persist: false });
    showGlobalMessage(`API base reset to default (${defaultApiBaseUrl}).`);
    if (authToken) {
      loadFeed();
      loadProfile();
    }
    return;
  }

  try {
    const normalised = normaliseApiBaseUrl(trimmed);
    setApiBaseUrl(normalised, { persist: true });
    showGlobalMessage(`API base updated to ${normalised}.`);
    if (authToken) {
      loadFeed();
      loadProfile();
    }
  } catch (error) {
    showGlobalMessage(error.message || 'The API base URL is not valid.', true);
  }
};

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const reviewForm = document.getElementById('review-form');
const photoForm = document.getElementById('photo-form');
const searchForm = document.getElementById('search-form');
const profileForm = document.getElementById('profile-form');
const passwordForm = document.getElementById('password-form');
const deactivateForm = document.getElementById('deactivate-form');

const authFeedback = document.getElementById('auth-feedback');
const feedFeedback = document.getElementById('feed-feedback');
const reviewFeedback = document.getElementById('review-feedback');
const photoFeedback = document.getElementById('photo-feedback');
const profileFeedback = document.getElementById('profile-feedback');

const reviewsList = document.getElementById('reviews-list');
const mapFrame = document.getElementById('map-frame');

const profileUsername = document.getElementById('profile-username');
const profileEmail = document.getElementById('profile-email');
const profileCreated = document.getElementById('profile-created');
const profileReviewCount = document.getElementById('profile-review-count');

const tabs = Array.from(document.querySelectorAll('.tab'));

let authToken = window.localStorage.getItem('naya-token');
let currentUser = null;

const formatDate = (iso) => {
  if (!iso) return '—';
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const saveAuthState = (token, user) => {
  authToken = token;
  currentUser = user || null;
  if (token) {
    window.localStorage.setItem('naya-token', token);
  } else {
    window.localStorage.removeItem('naya-token');
  }
  updateLayoutForAuth();
};

const updateLayoutForAuth = () => {
  const isAuthenticated = Boolean(authToken);
  document.querySelector('.main-nav').classList.toggle('hidden', !isAuthenticated);
  logoutBtn.classList.toggle('hidden', !isAuthenticated);
  if (isAuthenticated) {
    showView('feed-view');
    loadFeed();
    loadProfile();
  } else {
    showView('auth-view');
  }
};

const showView = (viewId) => {
  views.forEach((view) => {
    view.classList.toggle('hidden', view.id !== viewId);
  });
};

const setFeedback = (element, message, isError = false) => {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle('error', Boolean(message) && isError);
};

const buildQueryString = (params = {}) => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value);
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
};

const fetchJson = async (endpoint, options = {}, { requiresAuth = false } = {}) => {
  const url = `${apiBaseUrl}${endpoint}`;
  const headers = options.headers ? { ...options.headers } : {};

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (requiresAuth) {
    if (!authToken) throw new Error('Authentication required');
    headers.Authorization = `Bearer ${authToken}`;
  }

  let response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (networkError) {
    console.error('NAYA: network error while reaching the API.', networkError);
    showGlobalMessage(
      `Unable to reach the API at ${apiBaseUrl}. Check the address in “API settings” and your network connection.`,
      true,
      8000
    );
    throw new Error(
      `Unable to reach the API at ${apiBaseUrl}. Please verify your connection or API settings.`
    );
  }
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMessage = data.error || data.message || 'Request failed';
    throw new Error(errorMessage);
  }

  return data;
};

const renderReviews = (reviews = []) => {
  reviewsList.innerHTML = '';

  if (!reviews.length) {
    setFeedback(feedFeedback, 'No reviews found yet. Be the first to share an adventure!');
    return;
  }

  setFeedback(feedFeedback, '');

  const fragment = document.createDocumentFragment();

  reviews.forEach((review) => {
    const item = document.createElement('li');
    item.className = 'review-card';
    item.tabIndex = 0;
    item.dataset.reviewId = review.id;
    item.addEventListener('click', () => highlightOnMap(review));
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        highlightOnMap(review);
      }
    });

    const title = document.createElement('h3');
    title.textContent = review.title || 'Untitled experience';

    const meta = document.createElement('div');
    meta.className = 'review-meta';

    const author = document.createElement('span');
    author.textContent = review.user?.username ? `By ${review.user.username}` : 'Anonymous traveler';

    const location = document.createElement('span');
    location.textContent = review.place?.city
      ? `${review.place.city}, ${review.place.country || ''}`.trim()
      : review.place?.name || 'Unmapped location';

    const rating = document.createElement('span');
    rating.className = 'rating';
    rating.textContent = `★ ${review.rating ?? '—'}`;

    const created = document.createElement('span');
    created.textContent = formatDate(review.created_at);

    meta.append(author, location, rating, created);

    const content = document.createElement('p');
    content.textContent = review.content || 'No description provided.';

    item.append(title, meta, content);
    fragment.appendChild(item);
  });

  reviewsList.appendChild(fragment);
};

const highlightOnMap = (review) => {
  const place = review.place || {};
  let mapUrl;
  if (place.latitude && place.longitude) {
    mapUrl = `https://maps.google.com/maps?q=${place.latitude},${place.longitude}&z=12&output=embed`;
  } else if (place.city || place.name) {
    const query = encodeURIComponent(`${place.name || ''} ${place.city || ''} ${place.country || ''}`.trim());
    mapUrl = `https://maps.google.com/maps?q=${query}&z=10&output=embed`;
  }

  if (mapUrl) {
    mapFrame.src = mapUrl;
  }
};

const loadFeed = async (query = {}) => {
  try {
    setFeedback(feedFeedback, 'Loading adventures…');
    const qs = buildQueryString(query);
    const data = await fetchJson(`/reviews${qs}`);
    renderReviews(data.reviews || []);
    setFeedback(feedFeedback, data.reviews?.length ? '' : '');
  } catch (error) {
    console.error(error);
    setFeedback(feedFeedback, error.message || 'Unable to load reviews', true);
  }
};

const loadProfile = async () => {
  if (!authToken) return;
  try {
    const [profile, stats] = await Promise.all([
      fetchJson('/auth/profile', { method: 'GET' }, { requiresAuth: true }),
      fetchJson('/auth/stats', { method: 'GET' }, { requiresAuth: true }),
    ]);

    currentUser = profile;
    profileUsername.textContent = profile.username || 'Traveler';
    profileEmail.textContent = profile.email || '—';
    profileCreated.textContent = formatDate(profile.created_at);
    profileReviewCount.textContent = stats.reviews_count ?? '0';

    profileForm.username.value = profile.username || '';
    profileForm.bio.value = profile.bio || '';
  } catch (error) {
    console.error(error);
    setFeedback(profileFeedback, error.message || 'Failed to load profile', true);
  }
};

const handleLogin = async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = {
    email: formData.get('email').trim(),
    password: formData.get('password').trim(),
  };

  try {
    setFeedback(authFeedback, 'Signing you in…');
    const data = await fetchJson('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    saveAuthState(data.access_token, data.user);
    setFeedback(authFeedback, 'Welcome back! Redirecting to your feed.');
    loginForm.reset();
  } catch (error) {
    setFeedback(authFeedback, error.message || 'Unable to log in', true);
  }
};

const handleRegister = async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const password = formData.get('password').trim();
  const confirmPassword = formData.get('confirmPassword').trim();

  if (password !== confirmPassword) {
    setFeedback(authFeedback, 'Passwords do not match. Please try again.', true);
    return;
  }

  const payload = {
    username: formData.get('username').trim(),
    email: formData.get('email').trim(),
    password,
  };

  try {
    setFeedback(authFeedback, 'Creating your account…');
    await fetchJson('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    setFeedback(authFeedback, 'Account created! You can now log in.', false);
    registerForm.reset();
    tabs.forEach((tab) => tab.classList.remove('active'));
    tabs.find((tab) => tab.dataset.tab === 'login').classList.add('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  } catch (error) {
    setFeedback(authFeedback, error.message || 'Unable to register', true);
  }
};

const handleSearch = (event) => {
  event.preventDefault();
  const term = new FormData(searchForm).get('search').trim();
  loadFeed(term ? { search: term } : {});
  if (term) {
    const query = encodeURIComponent(term);
    mapFrame.src = `https://maps.google.com/maps?q=${query}&z=6&output=embed`;
  }
};

const handleReviewSubmit = async (event) => {
  event.preventDefault();
  if (!authToken) {
    setFeedback(reviewFeedback, 'You need to be logged in to share a review.', true);
    return;
  }

  const formData = new FormData(reviewForm);
  const payload = Object.fromEntries(formData.entries());
  payload.rating = Number(payload.rating);
  if (!payload.visit_date) {
    delete payload.visit_date;
  }

  try {
    setFeedback(reviewFeedback, 'Publishing your review…');
    await fetchJson('/reviews', {
      method: 'POST',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(reviewFeedback, 'Review published successfully!');
    reviewForm.reset();
    loadFeed();
  } catch (error) {
    setFeedback(reviewFeedback, error.message || 'Unable to publish review', true);
  }
};

const handlePhotoSubmit = async (event) => {
  event.preventDefault();
  if (!authToken) {
    setFeedback(photoFeedback, 'Please log in to upload a photo.', true);
    return;
  }

  const formData = new FormData(photoForm);
  const payload = Object.fromEntries(formData.entries());
  Object.keys(payload).forEach((key) => {
    if (payload[key] === '') delete payload[key];
  });

  try {
    setFeedback(photoFeedback, 'Saving photo metadata…');
    await fetchJson('/photos', {
      method: 'POST',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(photoFeedback, 'Photo saved! Attach the actual image through the backend upload workflow.');
    photoForm.reset();
  } catch (error) {
    setFeedback(photoFeedback, error.message || 'Unable to save photo', true);
  }
};

const handleProfileUpdate = async (event) => {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    setFeedback(profileFeedback, 'Updating profile…');
    const result = await fetchJson('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Profile updated!');
    await loadProfile();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Unable to update profile', true);
  }
};

const handlePasswordChange = async (event) => {
  event.preventDefault();
  const formData = new FormData(passwordForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    setFeedback(profileFeedback, 'Updating password…');
    const result = await fetchJson('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Password updated successfully.');
    passwordForm.reset();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Unable to update password', true);
  }
};

const handleDeactivate = async (event) => {
  event.preventDefault();
  if (!confirm('Are you sure you want to deactivate your NAYA account?')) {
    return;
  }

  try {
    setFeedback(profileFeedback, 'Deactivating account…');
    const result = await fetchJson('/auth/deactivate', {
      method: 'PUT',
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Account deactivated.');
    saveAuthState(null, null);
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Unable to deactivate account', true);
  }
};

const handleLogout = () => {
  saveAuthState(null, null);
  setFeedback(authFeedback, 'You have been logged out. See you soon!');
};

const initTabs = () => {
  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((item) => item.classList.remove('active'));
      tab.classList.add('active');

      if (tab.dataset.tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        setFeedback(authFeedback, '');
      } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        setFeedback(authFeedback, '');
      }
    });
  });
};

const initNavigation = () => {
  navButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.target;
      showView(target);
      if (target === 'feed-view') {
        loadFeed();
      }
      if (target === 'profile-view') {
        loadProfile();
      }
    });
  });
};

const initEventListeners = () => {
  loginForm.addEventListener('submit', handleLogin);
  registerForm.addEventListener('submit', handleRegister);
  searchForm.addEventListener('submit', handleSearch);
  reviewForm.addEventListener('submit', handleReviewSubmit);
  photoForm.addEventListener('submit', handlePhotoSubmit);
  profileForm.addEventListener('submit', handleProfileUpdate);
  passwordForm.addEventListener('submit', handlePasswordChange);
  deactivateForm.addEventListener('submit', handleDeactivate);
  logoutBtn.addEventListener('click', handleLogout);
  if (apiConfigBtn) {
    apiConfigBtn.addEventListener('click', handleApiConfigClick);
  }
};

const initApp = () => {
  yearEl.textContent = new Date().getFullYear();
  updateApiIndicator();
  if (window.location.protocol === 'https:' && apiBaseUrl.startsWith('http://')) {
    showGlobalMessage(
      'This page is served over HTTPS. Configure an HTTPS API URL via “API settings” to avoid blocked requests.',
      true,
      8000
    );
  }
  initTabs();
  initNavigation();
  initEventListeners();
  updateLayoutForAuth();

  if (!authToken) {
    showView('auth-view');
  }
};

window.addEventListener('DOMContentLoaded', initApp);