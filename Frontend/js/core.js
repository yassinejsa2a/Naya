const views = Array.from(document.querySelectorAll('.view'));
const mainNav = document.querySelector('.main-nav');
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
const mapView = document.getElementById('map-view');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const reviewForm = document.getElementById('review-form');
const searchForm = document.getElementById('search-form');
const profileForm = document.getElementById('profile-form');
const profilePhotoForm = document.getElementById('profile-photo-form');
const passwordForm = document.getElementById('password-form');
const deactivateForm = document.getElementById('deactivate-form');
const publicProfileView = document.getElementById('public-profile-view');
const publicProfileReviewsList = document.getElementById('public-profile-reviews');
const publicProfileFeedback = document.getElementById('public-profile-feedback');
const publicProfileAvatar = document.getElementById('public-profile-avatar');
const publicProfileUsername = document.getElementById('public-profile-username');
const publicProfileBio = document.getElementById('public-profile-bio');
const publicProfileCreated = document.getElementById('public-profile-created');
const publicProfileReviewsCount = document.getElementById('public-profile-reviews-count');
const publicProfilePhotosCount = document.getElementById('public-profile-photos-count');
const publicProfileBackBtn = document.getElementById('public-profile-back');
const publicProfileTitle = document.getElementById('public-profile-title');
const publicProfileSubtitle = document.getElementById('public-profile-subtitle');
const postedReviewsList = document.getElementById('posted-reviews-list');
const postedReviewsCount = document.getElementById('posted-reviews-count');
const postedReviewsFeedback = document.getElementById('posted-reviews-feedback');
const likedReviewsList = document.getElementById('liked-reviews-list');
const likedReviewsCount = document.getElementById('liked-reviews-count');
const likedReviewsFeedback = document.getElementById('liked-reviews-feedback');

const authFeedback = document.getElementById('auth-feedback');
const feedFeedback = document.getElementById('feed-feedback');
const reviewFeedback = document.getElementById('review-feedback');
const profileFeedback = document.getElementById('profile-feedback');

const reviewsList = document.getElementById('reviews-list');
const reviewDetailPanel = document.getElementById('review-detail');
const reviewDetailBody = document.getElementById('detail-content');
const reviewDetailTitle = document.getElementById('detail-title');
const reviewDetailMeta = document.getElementById('detail-meta');
const closeDetailBtn = document.getElementById('close-detail-btn');
const mapFrame = document.getElementById('map-frame');
const mapFeedList = document.getElementById('map-feed-list');
const heroReviewCount = document.getElementById('hero-review-count');
const heroDestinations = document.getElementById('hero-destinations');
const mapSearchForm = document.getElementById('map-search-form');
const mapSearchInput = document.getElementById('map-search-input');
const mapSearchFeedback = document.getElementById('map-search-feedback');

const profileUsername = document.getElementById('profile-username');
const profileEmail = document.getElementById('profile-email');
const profileCreated = document.getElementById('profile-created');
const profileReviewCount = document.getElementById('profile-review-count');
const profileAvatar = document.getElementById('profile-avatar');

const tabs = Array.from(document.querySelectorAll('.tab'));
const themeToggle = document.getElementById('theme-toggle');
const themeToggleIcon = themeToggle?.querySelector('.icon-toggle__icon') || null;
const themeToggleLabel = themeToggle?.querySelector('.icon-toggle__label') || null;
const profileThemeToggle = document.getElementById('profile-theme-toggle');
const profileThemeToggleIcon = profileThemeToggle?.querySelector('.icon-toggle__icon') || null;
const profileThemeToggleLabel = profileThemeToggle?.querySelector('.icon-toggle__label') || null;
const animatedElements = Array.from(document.querySelectorAll('[data-animate]'));

const THEME_STORAGE_KEY = 'naya-theme';
const REFRESH_TOKEN_KEY = 'naya-refresh-token';
const DEFAULT_AVATAR =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><rect width="96" height="96" rx="24" fill="#1b3a4b"/><text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" font-family="Poppins, sans-serif" font-size="36" fill="#ffffff">N</text></svg>'
  );
const resolveAvatarUrl = (url) => (url ? url : DEFAULT_AVATAR);
let revealObserver = null;

let storageAvailable = true;
if (typeof window === 'undefined') {
  storageAvailable = false;
} else {
  try {
    const testKey = '__naya_storage_test__';
    window.localStorage.setItem(testKey, testKey);
    window.localStorage.removeItem(testKey);
  } catch (error) {
    storageAvailable = false;
    console.warn('NAYA : stockage local indisponible.', error);
  }
}

const safeStorageGet = (key) => {
  if (!storageAvailable) return null;
  try {
    return window.localStorage.getItem(key);
  } catch (error) {
    storageAvailable = false;
    console.warn('NAYA : lecture du stockage impossible.', error);
    return null;
  }
};

const safeStorageSet = (key, value) => {
  if (!storageAvailable) return;
  try {
    window.localStorage.setItem(key, value);
  } catch (error) {
    storageAvailable = false;
    console.warn('NAYA : ecriture du stockage impossible.', error);
  }
};

const safeStorageRemove = (key) => {
  if (!storageAvailable) return;
  try {
    window.localStorage.removeItem(key);
  } catch (error) {
    storageAvailable = false;
    console.warn('NAYA : suppression du stockage impossible.', error);
  }
};

const getStoredTheme = () => {
  const stored = safeStorageGet(THEME_STORAGE_KEY);
  if (stored === 'dark' || stored === 'light') {
    return stored;
  }
  return null;
};

const updateThemeToggleUI = (toggle, icon, label, isDark) => {
  if (!toggle) return;
  toggle.setAttribute('aria-pressed', String(isDark));
  if (icon) {
    icon.textContent = isDark ? '☀️' : '🌙';
  }
  if (label) {
    label.textContent = isDark ? 'Mode clair' : 'Mode sombre';
  }
};

const applyTheme = (theme) => {
  const resolvedTheme = theme === 'dark' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', resolvedTheme);
  const isDark = resolvedTheme === 'dark';
  updateThemeToggleUI(themeToggle, themeToggleIcon, themeToggleLabel, isDark);
  updateThemeToggleUI(profileThemeToggle, profileThemeToggleIcon, profileThemeToggleLabel, isDark);
};

const setTheme = (theme, { persist = true } = {}) => {
  applyTheme(theme);
  if (!persist) {
    safeStorageRemove(THEME_STORAGE_KEY);
    return;
  }
  safeStorageSet(THEME_STORAGE_KEY, theme === 'dark' ? 'dark' : 'light');
};

const getPreferredTheme = () => {
  const stored = getStoredTheme();
  if (stored) {
    return stored;
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
};

const attachSystemThemeListener = () => {
  if (!window.matchMedia) return;
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const listener = (event) => {
    if (getStoredTheme()) {
      return;
    }
    applyTheme(event.matches ? 'dark' : 'light');
  };
  if (typeof mediaQuery.addEventListener === 'function') {
    mediaQuery.addEventListener('change', listener);
  } else if (typeof mediaQuery.addListener === 'function') {
    mediaQuery.addListener(listener);
  }
};

const initTheme = () => {
  const storedTheme = getStoredTheme();
  const initialTheme = storedTheme || getPreferredTheme();
  applyTheme(initialTheme);
  attachSystemThemeListener();
};

const observeAnimatedElement = (element) => {
  if (!element) return;
  if (!element.hasAttribute('data-animate')) {
    element.setAttribute('data-animate', '');
  }
  if (revealObserver) {
    revealObserver.observe(element);
  } else {
    element.classList.add('is-visible');
  }
};

const initRevealAnimations = () => {
  if (!animatedElements.length) {
    return;
  }
  if ('IntersectionObserver' in window) {
    revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2, rootMargin: '0px 0px -10% 0px' }
    );
    animatedElements.forEach((element) => revealObserver.observe(element));
  } else {
    animatedElements.forEach((element) => element.classList.add('is-visible'));
  }
};

const normaliseApiBaseUrl = (value) => {
  if (!value) {
    throw new Error("L'URL de base de l'API ne peut pas être vide.");
  }

  let candidate = value.trim();
  if (!candidate) {
    throw new Error("L'URL de base de l'API ne peut pas être vide.");
  }

  const hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(candidate);
  if (!hasScheme) {
    const lowered = candidate.toLowerCase();
    const isLocalHost =
      lowered.startsWith('localhost') ||
      lowered.startsWith('127.') ||
      lowered.startsWith('0.0.0.0') ||
      lowered.startsWith('::1');
    const pageProtocol = (typeof window !== 'undefined' && window.location?.protocol) || 'https:';
    const defaultScheme = isLocalHost || pageProtocol === 'http:' ? 'http://' : 'https://';
    candidate = `${defaultScheme}${candidate}`;
  }

  let url;
  try {
    url = new URL(candidate);
  } catch (error) {
    throw new Error("L'URL de base de l'API n'est pas valide.");
  }

  url.hash = '';
  url.search = '';

  let path = url.pathname || '';
  if (!path || path === '/') {
    path = '/api/v1';
  }

  const normalisedPath = path.endsWith('/') ? path.slice(0, -1) : path;
  return `${url.origin}${normalisedPath}`;
};

const detectDefaultApiBaseUrl = () => {
  const metaTag = document.querySelector('meta[name="naya-api-base"]');
  if (metaTag?.content) {
    try {
      return normaliseApiBaseUrl(metaTag.content);
    } catch (error) {
      console.warn('NAYA : URL de base API invalide définie dans <meta name="naya-api-base">.', error);
    }
  }

  const { protocol, origin, hostname, port } = window.location || {};
  const isHttpProtocol = protocol === 'http:' || protocol === 'https:';
  const isLocalHost =
    !hostname ||
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0' ||
    hostname === '::1';

  if (isLocalHost) {
    const localTargetHost = '127.0.0.1';
    const usesDefaultHttpPort = !port || port === '' || port === '80';
    const preferredPort = usesDefaultHttpPort ? '8000' : '5000';
    try {
      return normaliseApiBaseUrl(`${localTargetHost}:${preferredPort}`);
    } catch (error) {
      console.warn(
        "NAYA : tentative de détection de l'API locale échouée, retour à la valeur par défaut.",
        error
      );
      return `http://${localTargetHost}:${preferredPort}/api/v1`;
    }
  }

  if (isHttpProtocol && (!port || port === '' || port === '80' || port === '443' || port === '5000')) {
    try {
      return normaliseApiBaseUrl(origin);
    } catch (error) {
      console.warn("NAYA : impossible de déterminer l'URL de base de l'API depuis window.location.origin.", error);
    }
  }

  if (isHttpProtocol) {
    try {
      return normaliseApiBaseUrl(`${hostname}:5000`);
    } catch (error) {
      console.warn("NAYA : tentative de détection de l'API sur le port 5000 échouée.", error);
    }
  }

  return 'http://127.0.0.1:8000/api/v1';
};

const defaultApiBaseUrl = detectDefaultApiBaseUrl();

let apiBaseUrl = defaultApiBaseUrl;

const storedApiBase = safeStorageGet('naya-api-base');
if (storedApiBase) {
  try {
    apiBaseUrl = normaliseApiBaseUrl(storedApiBase);
    safeStorageSet('naya-api-base', apiBaseUrl);
  } catch (error) {
    console.warn("NAYA : URL de base API stockée invalide, retour à la valeur par défaut.", error);
    safeStorageRemove('naya-api-base');
    apiBaseUrl = defaultApiBaseUrl;
  }
}

let authToken = safeStorageGet('naya-token');
let refreshToken = safeStorageGet(REFRESH_TOKEN_KEY);
let currentUser = null;
let lastReviews = [];
let mapReviews = [];
let highlightedReviewId = null;
let globalMessageTimeoutId;
let currentDetailReviewId = null;
let lastCreatedReviewId = null;
let activeEditReviewId = null;
let publicProfileUserId = null;
let publicProfileReviews = [];
let postedReviews = [];
let likedReviews = [];
let likedReviewsTotal = 0;
const likedReviewIds = new Set();
const reviewCommentsCache = new Map();
const placeIdCache = new Map();

const formatDate = (iso) => {
  if (!iso) return '—';
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const updateApiIndicator = () => {
  if (!apiIndicator) return;
  try {
    const url = new URL(apiBaseUrl);
    apiIndicator.textContent = `API : ${url.origin}${url.pathname}`;
    apiIndicator.title = `${url.origin}${url.pathname}`;
  } catch (error) {
    apiIndicator.textContent = `API : ${apiBaseUrl}`;
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
    safeStorageSet('naya-api-base', value);
  } else {
    safeStorageRemove('naya-api-base');
  }
  placeIdCache.clear();
  updateApiIndicator();
};

const handleApiConfigClick = () => {
  const currentValue = apiBaseUrl;
  const hint = 'Exemple : https://naya-backend.exemple.com/api/v1';
  const userInput = window.prompt(`Indiquez l'URL de base de votre API NAYA.\n${hint}`, currentValue);

  if (userInput === null) {
    return;
  }

  const trimmed = userInput.trim();

  if (!trimmed) {
    setApiBaseUrl(defaultApiBaseUrl, { persist: false });
    showGlobalMessage(`URL de base réinitialisée (${defaultApiBaseUrl}).`);
    if (authToken) {
      loadFeed();
      loadProfile();
    }
    return;
  }

  try {
    const normalised = normaliseApiBaseUrl(trimmed);
    setApiBaseUrl(normalised, { persist: true });
    showGlobalMessage(`URL de base mise à jour : ${normalised}.`);
    if (authToken) {
      loadFeed();
      loadProfile();
    }
  } catch (error) {
    showGlobalMessage(error.message || "L'URL de base de l'API n'est pas valide.", true);
  }
};

const setFeedback = (element, message, isError = false) => {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle('error', Boolean(message) && isError);
};

const setProfileAvatar = (url, username = '') => {
  if (!profileAvatar) return;
  const finalUrl = resolveAvatarUrl(url);
  if (profileAvatar.src !== finalUrl) {
    profileAvatar.src = finalUrl;
  }
  profileAvatar.alt = username ? `Photo de profil de ${username}` : 'Photo de profil';
};

const attachUserProfileHandler = (element, user) => {
  if (!element || !user?.id) return;
  element.dataset.userId = user.id;
  element.classList.add('is-link');
  element.setAttribute('role', 'button');
  if (!element.hasAttribute('tabindex')) {
    element.tabIndex = 0;
  }
  const labelName = user.username || 'ce voyageur';
  element.setAttribute('aria-label', `Afficher le profil de ${labelName}`);
  const handler = (event) => {
    event.stopPropagation();
    if (currentUser?.id && String(currentUser.id) === String(user.id)) {
      showView('profile-view');
      loadProfile();
      return;
    }
    showPublicProfile(user.id);
  };
  element.addEventListener('click', handler);
  element.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handler(event);
    }
  });
};

const setMapFeedback = (message, isError = false) => {
  setFeedback(mapSearchFeedback, message, isError);
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

const normaliseFieldValue = (value) => (typeof value === 'string' ? value.trim() : '');

const buildPlaceCacheKey = (name, city, country) =>
  [normaliseFieldValue(name).toLowerCase(), normaliseFieldValue(city).toLowerCase(), normaliseFieldValue(country).toLowerCase()].join(
    '::'
  );

// Keep references to every cached review list so updates stay consistent across the UI
const reviewCollections = () => [lastReviews, mapReviews, publicProfileReviews, postedReviews, likedReviews];

const updateReviewCollections = (reviewId, transformer) => {
  const id = String(reviewId);
  const collections = reviewCollections();
  collections.forEach((collection) => {
    if (!Array.isArray(collection)) return;
    const itemIndex = collection.findIndex((entry) => entry && String(entry.id) === id);
    if (itemIndex !== -1) {
      const current = collection[itemIndex];
      const nextValue = transformer({ ...current });
      collection[itemIndex] = nextValue;
    }
  });
};

const findReviewById = (reviewId) => {
  const id = String(reviewId);
  const collections = reviewCollections();
  for (const collection of collections) {
    if (!Array.isArray(collection)) continue;
    const match = collection.find((entry) => entry && String(entry.id) === id);
    if (match) {
      return match;
    }
  }
  return null;
};

const findExistingPlaceId = async (name, city, country) => {
  if (!name && !city && !country) {
    return null;
  }

  const cacheKey = buildPlaceCacheKey(name, city, country);
  if (placeIdCache.has(cacheKey)) {
    return placeIdCache.get(cacheKey);
  }

  const searchParams = {
    search: name,
    city,
    country,
    limit: 10,
  };

  try {
    const response = await api.places.search(searchParams);
    const candidates = Array.isArray(response?.places) ? response.places : [];
    const targetName = name.toLowerCase();
    const targetCity = city.toLowerCase();
    const targetCountry = country.toLowerCase();

    const matchingPlace = candidates.find((place) => {
      const placeName = normaliseFieldValue(place?.name || '').toLowerCase();
      const placeCity = normaliseFieldValue(place?.city || '').toLowerCase();
      const placeCountry = normaliseFieldValue(place?.country || '').toLowerCase();
      return placeName === targetName && placeCity === targetCity && placeCountry === targetCountry;
    });

    const matchingId = matchingPlace?.id ?? null;
    if (matchingId) {
      placeIdCache.set(cacheKey, matchingId);
    }
    return matchingId;
  } catch (error) {
    console.warn('NAYA : impossible de rechercher un lieu existant.', error);
    return null;
  }
};

const ensurePlaceId = async (payload) => {
  const directId = normaliseFieldValue(payload.place_id || '');
  if (directId) {
    return directId;
  }

  const name = normaliseFieldValue(payload.place_name || '');
  const city = normaliseFieldValue(payload.place_city || '');
  const country = normaliseFieldValue(payload.place_country || '');
  const description = normaliseFieldValue(payload.place_description || '');

  if (!name || !city || !country) {
    throw new Error('Renseignez le nom, la ville et le pays du lieu ou fournissez son identifiant.');
  }

  const cacheKey = buildPlaceCacheKey(name, city, country);
  let existingId = await findExistingPlaceId(name, city, country);
  if (existingId) {
    return existingId;
  }

  try {
    const response = await api.places.create({
      name,
      city,
      country,
      description: description || undefined,
    });

    const createdPlace = response?.data;
    if (createdPlace?.id) {
      placeIdCache.set(cacheKey, createdPlace.id);
      return createdPlace.id;
    }

    // Certains endpoints renvoient la place sous data.place
    if (createdPlace?.place?.id) {
      placeIdCache.set(cacheKey, createdPlace.place.id);
      return createdPlace.place.id;
    }
  } catch (error) {
    if (error.message && error.message.toLowerCase().includes('already exists')) {
      existingId = await findExistingPlaceId(name, city, country);
      if (existingId) {
        return existingId;
      }
    }
    throw error;
  }

  throw new Error("Impossible de déterminer l'identifiant du lieu.");
};

