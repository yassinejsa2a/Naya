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
const photoForm = document.getElementById('photo-form');
const searchForm = document.getElementById('search-form');
const profileForm = document.getElementById('profile-form');
const passwordForm = document.getElementById('password-form');
const deactivateForm = document.getElementById('deactivate-form');

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

const tabs = Array.from(document.querySelectorAll('.tab'));
const themeToggle = document.getElementById('theme-toggle');
const themeToggleIcon = themeToggle?.querySelector('.icon-toggle__icon') || null;
const themeToggleLabel = themeToggle?.querySelector('.icon-toggle__label') || null;
const animatedElements = Array.from(document.querySelectorAll('[data-animate]'));

const THEME_STORAGE_KEY = 'naya-theme';
const REFRESH_TOKEN_KEY = 'naya-refresh-token';
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

const applyTheme = (theme) => {
  const resolvedTheme = theme === 'dark' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', resolvedTheme);
  if (themeToggle) {
    const isDark = resolvedTheme === 'dark';
    themeToggle.setAttribute('aria-pressed', String(isDark));
    if (themeToggleIcon) {
      themeToggleIcon.textContent = isDark ? '☀️' : '🌙';
    }
    if (themeToggleLabel) {
      themeToggleLabel.textContent = isDark ? 'Mode clair' : 'Mode sombre';
    }
  }
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
  applyTheme('dark');
  safeStorageRemove(THEME_STORAGE_KEY);
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
    return 'http://127.0.0.1:5000/api/v1';
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

  return 'http://127.0.0.1:5000/api/v1';
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

const findExistingPlaceId = async (name, city, country) => {
  const query = buildQueryString({
    search: name,
    city,
    country,
    limit: 10,
  });

  if (!query) {
    return null;
  }

  const cacheKey = buildPlaceCacheKey(name, city, country);
  if (placeIdCache.has(cacheKey)) {
    return placeIdCache.get(cacheKey);
  }

  try {
    const response = await fetchJson(`/places${query}`);
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
    const response = await fetchJson(
      '/places',
      {
        method: 'POST',
        body: JSON.stringify({
          name,
          city,
          country,
          description: description || undefined,
        }),
      },
      { requiresAuth: true }
    );

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

const fetchJson = async (
  endpoint,
  options = {},
  { requiresAuth = false, skipRefresh = false, useRefreshToken = false } = {}
) => {
  const url = `${apiBaseUrl}${endpoint}`;
  const headers = options.headers ? { ...options.headers } : {};

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (requiresAuth) {
    const tokenToUse = useRefreshToken ? refreshToken : authToken;
    if (!tokenToUse) throw new Error('Authentification requise');
    headers.Authorization = `Bearer ${tokenToUse}`;
  }

  let response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (networkError) {
    console.error("NAYA : erreur réseau lors de l'appel à l'API.", networkError);
    let friendlyMessage = `Impossible de joindre l'API à ${apiBaseUrl}. Vérifiez la connexion et la configuration du serveur.`;

    try {
      const apiUrl = new URL(apiBaseUrl);
      const pageProtocol = window.location?.protocol;
      const isMixedContent = pageProtocol === 'https:' && apiUrl.protocol === 'http:';
      if (isMixedContent) {
        friendlyMessage =
          "Connexion bloquée : l'interface est servie en HTTPS alors que l'API répond en HTTP. Passez l'API en HTTPS ou ouvrez le frontend en HTTP.";
      }
    } catch (urlError) {
      // Ignore parsing error and keep default message
    }

    showGlobalMessage(friendlyMessage, true, 8000);
    throw new Error(friendlyMessage);
  }
  if (response.status === 401 && requiresAuth && !skipRefresh && refreshToken && !useRefreshToken) {
    try {
      await refreshAccessToken();
      headers.Authorization = `Bearer ${authToken}`;
      response = await fetch(url, { ...options, headers });
    } catch (refreshError) {
      clearAuthState();
      throw refreshError;
    }
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMessage = data.error || data.message || 'La requête a échoué';
    if (response.status === 401 && requiresAuth) {
      clearAuthState();
      throw new Error('Session expirée. Merci de vous reconnecter.');
    }
    throw new Error(errorMessage);
  }

  return data;
};

const refreshAccessToken = async () => {
  if (!refreshToken) {
    throw new Error('Session expirée. Merci de vous reconnecter.');
  }

  const response = await fetchJson(
    '/auth/refresh',
    { method: 'POST' },
    { requiresAuth: true, skipRefresh: true, useRefreshToken: true }
  );

  const newToken = response?.access_token;
  if (!newToken) {
    throw new Error('Impossible de rafraîchir la session.');
  }

  saveAuthState(newToken, currentUser, refreshToken, { silent: true });
  return newToken;
};

const updateHeroStats = (reviews = []) => {
  if (heroReviewCount) {
    heroReviewCount.textContent = reviews.length.toLocaleString('fr-FR');
  }

  if (heroDestinations) {
    if (!reviews.length) {
      heroDestinations.textContent = '—';
      return;
    }

    const destinations = new Set();
    reviews.forEach((review) => {
      const place = review.place || {};
      const identifier = [place.city || place.name || '', place.country || '']
        .map((part) => part.trim().toLowerCase())
        .filter(Boolean)
        .join('|');
      if (identifier) {
        destinations.add(identifier);
      }
    });
    heroDestinations.textContent = destinations.size ? destinations.size.toLocaleString('fr-FR') : '—';
  }
};

const highlightReviewItems = () => {
  const id = highlightedReviewId != null ? String(highlightedReviewId) : null;

  if (reviewsList) {
    const cards = reviewsList.querySelectorAll('.review-card');
    cards.forEach((card) => {
      const isActive = id && card.dataset.reviewId === id;
      card.classList.toggle('active', Boolean(isActive));
    });
  }

  if (mapFeedList) {
    const items = mapFeedList.querySelectorAll('.map-feed-entry');
    items.forEach((item) => {
      const isActive = id && item.dataset.reviewId === id;
      item.classList.toggle('active', Boolean(isActive));
    });
  }
};

const renderMapFeed = (reviews = []) => {
  if (!mapFeedList) return;
  mapReviews = Array.isArray(reviews) ? [...reviews] : [];
  mapFeedList.innerHTML = '';

  setMapFeedback('');

  if (!reviews.length) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'map-feed-empty';
    emptyItem.textContent = 'Aucun avis à afficher pour le moment.';
    mapFeedList.appendChild(emptyItem);
    highlightReviewItems();
    setMapFeedback('Aucun avis à afficher pour le moment.', true);
    return;
  }

  const itemsToAnimate = [];

  reviews.forEach((review) => {
    const item = document.createElement('li');
    item.tabIndex = 0;
    item.dataset.reviewId = review.id;
    item.classList.add('map-feed-entry');

    const title = document.createElement('span');
    title.className = 'map-feed-title';
    title.textContent = review.title || 'Avis sans titre';

    const meta = document.createElement('span');
    meta.className = 'map-feed-meta';
    const locationLabel = review.place?.city
      ? `${review.place.city}, ${review.place.country || ''}`.trim()
      : review.place?.name || 'Lieu non cartographié';
    meta.textContent = `${locationLabel} • ★ ${review.rating ?? '—'}`;

    item.append(title, meta);

    item.addEventListener('click', () => {
      highlightOnMap(review);
      showReviewDetail(review.id);
    });
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        highlightOnMap(review);
        showReviewDetail(review.id);
      }
    });

    mapFeedList.appendChild(item);
    itemsToAnimate.push(item);
  });

  requestAnimationFrame(() => {
    itemsToAnimate.forEach((item) => observeAnimatedElement(item));
  });

  highlightReviewItems();
};

const renderReviews = (reviews = []) => {
  reviewsList.innerHTML = '';

  if (!reviews.length) {
    setFeedback(feedFeedback, 'Aucun avis pour le moment. Soyez le premier à partager une aventure !');
    updateHeroStats([]);
    renderMapFeed([]);
    return;
  }

  setFeedback(feedFeedback, '');

  const fragment = document.createDocumentFragment();

  const ids = reviews.map((review) => String(review.id));
  if (highlightedReviewId != null && !ids.includes(String(highlightedReviewId))) {
    highlightedReviewId = null;
  }

  const itemsToAnimate = [];

  reviews.forEach((review) => {
    const item = document.createElement('li');
    item.className = 'review-card';
    item.tabIndex = 0;
    item.dataset.reviewId = review.id;
    item.addEventListener('click', () => {
      highlightOnMap(review);
      showReviewDetail(review.id);
    });
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        highlightOnMap(review);
        showReviewDetail(review.id);
      }
    });

    const title = document.createElement('h3');
    title.textContent = review.title || 'Expérience sans titre';

    const meta = document.createElement('div');
    meta.className = 'review-meta';

    const author = document.createElement('span');
    author.textContent = review.user?.username ? `Par ${review.user.username}` : 'Voyageur anonyme';

    const location = document.createElement('span');
    location.textContent = review.place?.city
      ? `${review.place.city}, ${review.place.country || ''}`.trim()
      : review.place?.name || 'Lieu non cartographié';

    const rating = document.createElement('span');
    rating.className = 'rating';
    rating.textContent = `★ ${review.rating ?? '—'}`;

    const created = document.createElement('span');
    created.textContent = formatDate(review.created_at);

    const metaChildren = [author, location, rating, created];
    if (review.visit_date) {
      const visitDate = document.createElement('span');
      visitDate.textContent = `Visité le ${formatDate(review.visit_date)}`;
      metaChildren.push(visitDate);
    }

    meta.append(...metaChildren);

    const content = document.createElement('p');
    content.textContent = review.content || 'Aucune description fournie.';

    item.append(title, meta, content);

    if (Array.isArray(review.photos) && review.photos.length) {
      const gallery = document.createElement('div');
      gallery.className = 'review-gallery';

      review.photos.forEach((photo) => {
        if (!photo?.file_url) return;

        const figure = document.createElement('figure');
        figure.className = 'review-photo';

        const img = document.createElement('img');
        img.src = photo.file_url;
        img.alt = photo.caption || `Photo de ${review.title || "l'avis"}`;
        img.loading = 'lazy';
        figure.appendChild(img);

        const captionBlock = document.createElement('figcaption');
        if (photo.caption) {
          const caption = document.createElement('span');
          caption.textContent = photo.caption;
          captionBlock.appendChild(caption);
        }
        if (photo.user?.username) {
          const owner = document.createElement('span');
          owner.className = 'photo-owner';
          owner.textContent = `Partagée par ${photo.user.username}`;
          captionBlock.appendChild(owner);
        }
        if (captionBlock.childNodes.length) {
          figure.appendChild(captionBlock);
        }

        gallery.appendChild(figure);
      });

      if (gallery.children.length) {
        item.appendChild(gallery);
      }
    }

    fragment.appendChild(item);
    itemsToAnimate.push(item);
  });

  reviewsList.appendChild(fragment);
  requestAnimationFrame(() => {
    itemsToAnimate.forEach((item) => observeAnimatedElement(item));
  });
  updateHeroStats(reviews);
  renderMapFeed(reviews);
  highlightReviewItems();
  if (currentDetailReviewId) {
    const current = reviews.find((review) => String(review.id) === String(currentDetailReviewId));
    if (current) {
      renderReviewDetailContent(current);
    } else {
      hideReviewDetail();
    }
  }
};

const highlightOnMap = (review) => {
  if (!mapFrame) return;
  const place = review.place || {};
  let mapUrl;
  if (place.latitude && place.longitude) {
    const marker = `${place.latitude},${place.longitude}`;
    mapUrl = `https://maps.google.com/maps?q=${marker}&z=12&iwloc=&output=embed&markers=${marker}`;
  } else if (place.city || place.name) {
    const label = `${place.name || ''} ${place.city || ''} ${place.country || ''}`.trim();
    if (label) {
      const query = encodeURIComponent(label);
      mapUrl = `https://maps.google.com/maps?q=${query}&z=10&iwloc=&output=embed`;
    }
  }

  if (mapUrl) {
    mapFrame.src = mapUrl;
  }

  if (review?.id != null) {
    highlightedReviewId = review.id;
    highlightReviewItems();
    currentDetailReviewId = review.id;
  }
};

const clearDetailPanel = () => {
  if (!reviewDetailBody) return;
  reviewDetailBody.innerHTML = '';
};

const hideReviewDetail = () => {
  if (!reviewDetailPanel) return;
  reviewDetailPanel.classList.add('hidden');
  clearDetailPanel();
  if (reviewDetailTitle) {
    reviewDetailTitle.textContent = 'Sélectionnez un avis';
  }
  if (reviewDetailMeta) {
    reviewDetailMeta.textContent = 'Explorez un avis pour afficher ses détails.';
  }
  currentDetailReviewId = null;
  highlightedReviewId = null;
  highlightReviewItems();
  removeReviewEditForm();
  if (photoForm?.review_id) {
    photoForm.review_id.value = '';
  }
};

const buildRatingLabel = (rating) => {
  if (typeof rating !== 'number' || Number.isNaN(rating)) return 'Note indisponible';
  const stars = '★'.repeat(Math.round(rating));
  return `${stars} (${rating}/5)`;
};

const userOwnsResource = (resourceUserId) => {
  if (!currentUser || !resourceUserId) return false;
  return currentUser.id === resourceUserId;
};

const canManageReview = (review) => {
  if (!currentUser || !review) return false;
  const ownerId = review.user_id || review.user?.id;
  return Boolean(currentUser.is_admin || userOwnsResource(ownerId));
};

const canManagePhoto = (photo) => {
  if (!currentUser || !photo) return false;
  return Boolean(currentUser.is_admin || userOwnsResource(photo.user_id));
};

const removeReviewEditForm = () => {
  const existing = reviewDetailBody?.querySelector('.review-edit-form');
  if (existing) {
    existing.removeEventListener('submit', handleReviewEditSubmit);
    existing.remove();
  }
  activeEditReviewId = null;
};

const handleReviewDelete = async (reviewId) => {
  if (!authToken || !reviewId) {
    setFeedback(reviewFeedback, 'Vous devez être connecté pour supprimer un avis.', true);
    return;
  }

  if (!window.confirm('Confirmez-vous la suppression de cet avis ?')) {
    return;
  }

  try {
    await fetchJson(`/reviews/${reviewId}`, { method: 'DELETE' }, { requiresAuth: true });
    currentDetailReviewId = null;
    highlightedReviewId = null;
    activeEditReviewId = null;
    hideReviewDetail();
    showGlobalMessage('Avis supprimé avec succès.');
    await loadFeed();
    await loadProfile();
  } catch (error) {
    setFeedback(reviewFeedback, error.message || 'Impossible de supprimer cet avis.', true);
  }
};

const handlePhotoDelete = async (photoId) => {
  if (!authToken || !photoId || !currentDetailReviewId) {
    showGlobalMessage('Impossible de supprimer cette photo pour le moment.', true);
    return;
  }

  if (!window.confirm('Supprimer cette photo ?')) {
    return;
  }

  try {
    await fetchJson(`/photos/${photoId}`, { method: 'DELETE' }, { requiresAuth: true });
    showGlobalMessage('Photo supprimée avec succès.');
    await loadFeed();
    await showReviewDetail(currentDetailReviewId);
  } catch (error) {
    showGlobalMessage(error.message || 'Impossible de supprimer la photo.', true);
  }
};

const handleReviewEditStart = (review) => {
  if (!canManageReview(review)) return;
  removeReviewEditForm();
  activeEditReviewId = review.id;

  const form = document.createElement('form');
  form.className = 'review-edit-form';
  form.dataset.reviewId = review.id;

  const titleField = document.createElement('label');
  titleField.textContent = 'Titre';
  const titleInput = document.createElement('input');
  titleInput.type = 'text';
  titleInput.name = 'title';
  titleInput.required = true;
  titleInput.minLength = 3;
  titleInput.value = review.title || '';
  titleField.appendChild(titleInput);

  const ratingField = document.createElement('label');
  ratingField.textContent = 'Note';
  const ratingSelect = document.createElement('select');
  ratingSelect.name = 'rating';
  ratingSelect.required = true;
  const ratingOptions = [
    { value: '', label: 'Sélectionner' },
    { value: '1', label: '1 - Peut mieux faire' },
    { value: '2', label: '2 - En dessous des attentes' },
    { value: '3', label: '3 - Bien' },
    { value: '4', label: '4 - Superbe' },
    { value: '5', label: '5 - Exceptionnel' },
  ];
  ratingOptions.forEach((option) => {
    const opt = document.createElement('option');
    opt.value = option.value;
    opt.textContent = option.label;
    if (String(review.rating) === option.value) {
      opt.selected = true;
    }
    ratingSelect.appendChild(opt);
  });
  ratingField.appendChild(ratingSelect);

  const contentField = document.createElement('label');
  contentField.textContent = 'Avis';
  const contentArea = document.createElement('textarea');
  contentArea.name = 'content';
  contentArea.rows = 4;
  contentArea.required = true;
  contentArea.minLength = 10;
  contentArea.value = review.content || '';
  contentField.appendChild(contentArea);

  const visitField = document.createElement('label');
  visitField.textContent = 'Date de visite';
  const visitInput = document.createElement('input');
  visitInput.type = 'date';
  visitInput.name = 'visit_date';
  if (review.visit_date) {
    visitInput.value = review.visit_date;
  }
  visitField.appendChild(visitInput);

  const actionsRow = document.createElement('div');
  actionsRow.className = 'review-edit-actions';
  const saveBtn = document.createElement('button');
  saveBtn.type = 'submit';
  saveBtn.className = 'primary-btn';
  saveBtn.textContent = 'Enregistrer';
  const cancelBtn = document.createElement('button');
  cancelBtn.type = 'button';
  cancelBtn.className = 'secondary-btn';
  cancelBtn.textContent = 'Annuler';
  cancelBtn.addEventListener('click', () => {
    removeReviewEditForm();
    showReviewDetail(review.id);
  });
  actionsRow.append(saveBtn, cancelBtn);

  form.append(titleField, ratingField, contentField, visitField, actionsRow);
  form.addEventListener('submit', handleReviewEditSubmit);

  reviewDetailBody.appendChild(form);
  form.scrollIntoView({ behavior: 'smooth', block: 'center' });
};

const handleReviewEditSubmit = async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const reviewId = form.dataset.reviewId;
  if (!reviewId) return;

  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = typeof value === 'string' ? value.trim() : value;
  });

  const rating = Number(payload.rating);
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    setFeedback(reviewFeedback, 'Merci de sélectionner une note entre 1 et 5.', true);
    return;
  }

  if (!payload.title || payload.title.length < 3) {
    setFeedback(reviewFeedback, 'Le titre doit contenir au moins 3 caractères.', true);
    return;
  }

  if (!payload.content || payload.content.length < 10) {
    setFeedback(reviewFeedback, 'Votre avis doit contenir au moins 10 caractères.', true);
    return;
  }

  const updateData = {
    title: payload.title,
    content: payload.content,
    rating,
  };

  if (payload.visit_date) {
    updateData.visit_date = payload.visit_date;
  } else {
    updateData.visit_date = null;
  }

  try {
    setFeedback(reviewFeedback, 'Mise à jour de votre avis…');
    await fetchJson(
      `/reviews/${reviewId}`,
      {
        method: 'PUT',
        body: JSON.stringify(updateData),
      },
      { requiresAuth: true }
    );

    removeReviewEditForm();
    setFeedback(reviewFeedback, 'Avis mis à jour avec succès.');
    await loadFeed();
    await showReviewDetail(reviewId);
  } catch (error) {
    setFeedback(reviewFeedback, error.message || "Impossible de mettre à jour l'avis", true);
  }
};

const renderReviewDetailContent = (review) => {
  if (!reviewDetailPanel || !reviewDetailBody) return;
  reviewDetailPanel.classList.remove('hidden');
  clearDetailPanel();
  removeReviewEditForm();

  const place = review.place || {};
  const author = review.user?.username ? `Par ${review.user.username}` : 'Voyageur anonyme';
  const visitDate = review.visit_date ? formatDate(review.visit_date) : null;
  const createdAt = review.created_at ? formatDate(review.created_at) : null;

  if (reviewDetailTitle) {
    reviewDetailTitle.textContent = review.title || 'Avis sans titre';
  }

  if (reviewDetailMeta) {
    const bits = [buildRatingLabel(review.rating), author];
    if (visitDate) bits.push(`Visité le ${visitDate}`);
    else if (createdAt) bits.push(`Publié le ${createdAt}`);
    reviewDetailMeta.textContent = bits.filter(Boolean).join(' • ');
  }

  const hero = document.createElement('div');
  hero.className = 'detail-hero';

  const ratingBadge = document.createElement('span');
  ratingBadge.className = 'rating';
  ratingBadge.textContent = buildRatingLabel(review.rating);

  const tagsContainer = document.createElement('div');
  tagsContainer.className = 'detail-tags';

  if (place.city || place.country) {
    const tag = document.createElement('span');
    tag.className = 'detail-tag';
    tag.textContent = [place.city, place.country].filter(Boolean).join(', ');
    tagsContainer.appendChild(tag);
  }

  if (place.name && (!place.city || place.name.toLowerCase() !== place.city.toLowerCase())) {
    const tag = document.createElement('span');
    tag.className = 'detail-tag';
    tag.textContent = place.name;
    tagsContainer.appendChild(tag);
  }

  if (visitDate) {
    const tag = document.createElement('span');
    tag.className = 'detail-tag';
    tag.textContent = `Séjour : ${visitDate}`;
    tagsContainer.appendChild(tag);
  }

  hero.append(ratingBadge, tagsContainer);

  const contentBlock = document.createElement('p');
  contentBlock.textContent = review.content || "Cet avis n'a pas encore de contenu détaillé.";

  const placeBlock = document.createElement('div');
  placeBlock.className = 'detail-place';
  const placeTitle = document.createElement('strong');
  placeTitle.textContent = place.name || 'Lieu non spécifié';
  const placeLocation = document.createElement('span');
  placeLocation.textContent = [place.city, place.country].filter(Boolean).join(', ') || 'Localisation inconnue';
  placeBlock.append(placeTitle, placeLocation);
  if (place.description) {
    const placeDescription = document.createElement('p');
    placeDescription.textContent = place.description;
    placeBlock.appendChild(placeDescription);
  }

  reviewDetailBody.append(hero, contentBlock, placeBlock);

  if (photoForm?.review_id) {
    photoForm.review_id.value = review.id || '';
  }

  if (canManageReview(review)) {
    const actions = document.createElement('div');
    actions.className = 'detail-actions';

    const editBtn = document.createElement('button');
    editBtn.type = 'button';
    editBtn.className = 'secondary-btn';
    editBtn.textContent = 'Modifier cet avis';
    editBtn.addEventListener('click', () => handleReviewEditStart(review));

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'danger-btn';
    deleteBtn.textContent = 'Supprimer cet avis';
    deleteBtn.addEventListener('click', () => handleReviewDelete(review.id));

    actions.append(editBtn, deleteBtn);
    reviewDetailBody.appendChild(actions);
  }

  const photos = Array.isArray(review.photos) ? review.photos.filter((photo) => photo?.file_url) : [];
  if (photos.length) {
    const gallery = document.createElement('div');
    gallery.className = 'detail-gallery';
    photos.forEach((photo) => {
      const figure = document.createElement('figure');
      const img = document.createElement('img');
      img.src = photo.file_url;
      img.alt = photo.caption || `Photo de ${review.title || "l'avis"}`;
      img.loading = 'lazy';
      figure.appendChild(img);
      const captionBlock = document.createElement('figcaption');
      if (photo.caption) {
        const caption = document.createElement('span');
        caption.textContent = photo.caption;
        captionBlock.appendChild(caption);
      }
      if (photo.user?.username) {
        const owner = document.createElement('span');
        owner.className = 'photo-owner';
        owner.textContent = `Partagée par ${photo.user.username}`;
        captionBlock.appendChild(owner);
      }
      if (captionBlock.childNodes.length) {
        figure.appendChild(captionBlock);
      }
      if (canManagePhoto(photo)) {
        const photoActions = document.createElement('div');
        photoActions.className = 'photo-actions';
        const deletePhotoBtn = document.createElement('button');
        deletePhotoBtn.type = 'button';
        deletePhotoBtn.className = 'photo-delete-btn';
        deletePhotoBtn.textContent = 'Supprimer';
        deletePhotoBtn.addEventListener('click', () => handlePhotoDelete(photo.id));
        photoActions.appendChild(deletePhotoBtn);
        figure.appendChild(photoActions);
      }
      gallery.appendChild(figure);
    });
    reviewDetailBody.appendChild(gallery);
  } else {
    const noPhotos = document.createElement('p');
    noPhotos.className = 'detail-placeholder';
    noPhotos.textContent = 'Aucune photo pour le moment. Ajoutez-en une via le formulaire ci-dessous.';
    reviewDetailBody.appendChild(noPhotos);
  }
};

const showReviewDetail = async (reviewId) => {
  if (!reviewId || !reviewDetailPanel) return;

  currentDetailReviewId = reviewId;
  reviewDetailPanel.classList.remove('hidden');

  if (reviewDetailTitle) {
    reviewDetailTitle.textContent = 'Chargement de l’avis…';
  }
  if (reviewDetailMeta) {
    reviewDetailMeta.textContent = 'Merci de patienter pendant que nous ouvrons les détails.';
  }
  clearDetailPanel();

  try {
    const response = await fetchJson(`/reviews/${reviewId}`);
    const review = response?.data || response;

    if (!review) {
      throw new Error('Avis introuvable');
    }

    const index = lastReviews.findIndex((item) => String(item.id) === String(reviewId));
    if (index !== -1) {
      lastReviews[index] = review;
    }

    renderReviewDetailContent(review);
  } catch (error) {
    setFeedback(feedFeedback, error.message || 'Impossible de charger le détail de cet avis', true);
    hideReviewDetail();
  }
};

const loadFeed = async (query = {}) => {
  try {
    setFeedback(feedFeedback, 'Chargement des aventures…');
    const qs = buildQueryString(query);
    const data = await fetchJson(`/reviews${qs}`);
    lastReviews = data.reviews || [];
    renderReviews(lastReviews);
    setFeedback(feedFeedback, lastReviews.length ? '' : '');
  } catch (error) {
    console.error(error);
    setFeedback(feedFeedback, error.message || 'Impossible de charger les avis', true);
    updateHeroStats([]);
    renderMapFeed([]);
    hideReviewDetail();
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
    profileUsername.textContent = profile.username || 'Voyageur';
    profileEmail.textContent = profile.email || '—';
    profileCreated.textContent = formatDate(profile.created_at);
    profileReviewCount.textContent = stats.reviews_count ?? '0';

    profileForm.username.value = profile.username || '';
    profileForm.bio.value = profile.bio || '';
  } catch (error) {
    console.error(error);
    setFeedback(profileFeedback, error.message || 'Échec du chargement du profil', true);
  }
};

const saveAuthState = (token, user, refresh, { silent = false } = {}) => {
  authToken = token || null;
  currentUser = user || null;

  if (token) {
    safeStorageSet('naya-token', token);
  } else {
    safeStorageRemove('naya-token');
  }

  if (refresh !== undefined) {
    refreshToken = refresh || null;
    if (refreshToken) {
      safeStorageSet(REFRESH_TOKEN_KEY, refreshToken);
    } else {
      safeStorageRemove(REFRESH_TOKEN_KEY);
    }
  }

  if (!silent) {
    updateLayoutForAuth();
  }
};

const clearAuthState = () => {
  saveAuthState(null, null, null);
};

const updateLayoutForAuth = () => {
  const isAuthenticated = Boolean(authToken);
  if (mainNav) {
    mainNav.classList.toggle('hidden', !isAuthenticated);
  }
  logoutBtn.classList.toggle('hidden', !isAuthenticated);
  if (isAuthenticated) {
    showView('feed-view');
    loadFeed();
    loadProfile();
  } else {
    showView('auth-view');
    hideReviewDetail();
  }
};

const showView = (viewId) => {
  views.forEach((view) => {
    view.classList.toggle('hidden', view.id !== viewId);
  });
  navButtons.forEach((button) => {
    const isActive = button.dataset.target === viewId;
    button.classList.toggle('active', isActive);
  });

  if (viewId === 'map-view') {
    const source = mapReviews.length ? mapReviews : lastReviews;
    renderMapFeed(source);
    setMapFeedback('');
  }
};

const handleThemeToggle = () => {
  const currentTheme = document.body.getAttribute('data-theme') || getPreferredTheme();
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  setTheme(nextTheme);
};

const handleLogin = async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = {
    login: formData.get('login').trim(),
    password: formData.get('password').trim(),
  };

  try {
    setFeedback(authFeedback, 'Connexion en cours…');
    const data = await fetchJson('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    saveAuthState(data.access_token, data.user, data.refresh_token);
    setFeedback(authFeedback, 'Ravi de vous revoir ! Redirection vers votre fil.');
    loginForm.reset();
  } catch (error) {
    setFeedback(authFeedback, error.message || 'Impossible de se connecter', true);
  }
};

const handleRegister = async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const password = formData.get('password').trim();
  const confirmPassword = formData.get('confirmPassword').trim();

  if (password !== confirmPassword) {
    setFeedback(authFeedback, 'Les mots de passe ne correspondent pas. Veuillez réessayer.', true);
    return;
  }

  const payload = {
    username: formData.get('username').trim(),
    email: formData.get('email').trim(),
    password,
  };

  try {
    setFeedback(authFeedback, 'Création de votre compte…');
    await fetchJson('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    setFeedback(authFeedback, 'Compte créé ! Vous pouvez maintenant vous connecter.', false);
    registerForm.reset();
    tabs.forEach((tab) => tab.classList.remove('active'));
    tabs.find((tab) => tab.dataset.tab === 'login').classList.add('active');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  } catch (error) {
    setFeedback(authFeedback, error.message || 'Impossible de créer un compte', true);
  }
};

const handleSearch = (event) => {
  event.preventDefault();
  const term = new FormData(searchForm).get('search').trim();
  loadFeed(term ? { search: term } : {});
  if (term && mapFrame) {
    const query = encodeURIComponent(term);
    mapFrame.src = `https://maps.google.com/maps?q=${query}&z=6&output=embed`;
  }
};

const handleMapSearch = async (event) => {
  if (event) {
    event.preventDefault();
  }
  if (!mapSearchInput) return;

  const term = mapSearchInput.value.trim();
  if (!term) {
    setMapFeedback('Indiquez un mot-clé pour la recherche.', true);
    return;
  }

  try {
    setMapFeedback('Recherche en cours…');
    const data = await fetchJson(`/reviews${buildQueryString({ search: term })}`);
    const results = data.reviews || [];
    renderMapFeed(results);
    if (results.length) {
      setMapFeedback(`${results.length} avis trouvé(s).`);
      highlightOnMap(results[0]);
      await showReviewDetail(results[0].id);
    } else {
      setMapFeedback('Aucun avis trouvé pour ce mot-clé.', true);
    }
  } catch (error) {
    setMapFeedback(error.message || 'Impossible de lancer la recherche.', true);
  }
};

const handleReviewSubmit = async (event) => {
  event.preventDefault();
  if (!authToken) {
    setFeedback(reviewFeedback, 'Vous devez être connecté pour partager un avis.', true);
    return;
  }

  const formData = new FormData(reviewForm);
  const photoFile = formData.get('photo_file');
  const captionValue = formData.get('caption');
  const photoCaption = typeof captionValue === 'string' ? captionValue.trim() : '';

  const payload = {};
  formData.forEach((value, key) => {
    if (key === 'photo_file' || key === 'caption') {
      return;
    }
    if (typeof value === 'string') {
      payload[key] = value.trim();
    } else {
      payload[key] = value;
    }
  });

  let placeId;
  try {
    placeId = await ensurePlaceId(payload);
  } catch (error) {
    setFeedback(reviewFeedback, error.message || 'Impossible de déterminer le lieu.', true);
    return;
  }

  const rating = Number(payload.rating);
  if (Number.isNaN(rating) || rating < 1 || rating > 5) {
    setFeedback(reviewFeedback, 'Merci de sélectionner une note entre 1 et 5.', true);
    return;
  }

  if (!payload.title) {
    setFeedback(reviewFeedback, 'Le titre de votre avis est requis.', true);
    return;
  }

  if (!payload.content || payload.content.length < 10) {
    setFeedback(reviewFeedback, 'Votre avis doit contenir au moins 10 caractères.', true);
    return;
  }

  payload.rating = rating;
  payload.place_id = placeId;

  if (!payload.visit_date) {
    delete payload.visit_date;
  }

  delete payload.place_name;
  delete payload.place_city;
  delete payload.place_country;
  delete payload.place_description;

  try {
    setFeedback(reviewFeedback, 'Publication de votre avis…');
    const response = await fetchJson(
      '/reviews',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      { requiresAuth: true }
    );

    const createdReview = response?.data?.review;
    const createdReviewId = createdReview?.id || null;

    let photoError = null;
    const hasPhotoToUpload = photoFile instanceof File && Boolean(photoFile?.name);

    if (hasPhotoToUpload && createdReviewId) {
      const photoPayload = new FormData();
      photoPayload.append('photo_file', photoFile, photoFile.name);
      photoPayload.append('review_id', createdReviewId);
      if (photoCaption) {
        photoPayload.append('caption', photoCaption);
      }

      setFeedback(reviewFeedback, 'Avis publié. Téléversement de la photo…');
      try {
        await fetchJson(
          '/photos',
          {
            method: 'POST',
            body: photoPayload,
          },
          { requiresAuth: true }
        );
      } catch (uploadError) {
        console.error(uploadError);
        photoError = uploadError;
      }
    }

    reviewForm.reset();

    await loadFeed();
    await loadProfile();

    if (hasPhotoToUpload && !createdReviewId) {
      setFeedback(
        reviewFeedback,
        "Avis publié, mais impossible d'associer la photo à cet avis.",
        true
      );
    } else if (photoError) {
      const errorMessage = photoError?.message || 'erreur inconnue';
      setFeedback(
        reviewFeedback,
        `Avis publié, mais échec du téléversement de la photo : ${errorMessage}`,
        true
      );
    } else if (hasPhotoToUpload) {
      setFeedback(reviewFeedback, 'Avis et photo publiés avec succès !');
    } else {
      setFeedback(reviewFeedback, 'Avis publié avec succès !');
    }
  } catch (error) {
    setFeedback(reviewFeedback, error.message || 'Impossible de publier cet avis', true);
  }
};

const handleProfileUpdate = async (event) => {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    setFeedback(profileFeedback, 'Mise à jour du profil…');
    const result = await fetchJson('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Profil mis à jour !');
    await loadProfile();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Impossible de mettre le profil à jour', true);
  }
};

const handlePasswordChange = async (event) => {
  event.preventDefault();
  const formData = new FormData(passwordForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    setFeedback(profileFeedback, 'Mise à jour du mot de passe…');
    const result = await fetchJson('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Mot de passe mis à jour.');
    passwordForm.reset();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Impossible de mettre à jour le mot de passe', true);
  }
};

const handleDeactivate = async (event) => {
  event.preventDefault();
  if (!confirm('Voulez-vous vraiment désactiver votre compte NAYA ?')) {
    return;
  }

  try {
    setFeedback(profileFeedback, 'Désactivation du compte…');
    const result = await fetchJson('/auth/deactivate', {
      method: 'PUT',
    }, { requiresAuth: true });

    setFeedback(profileFeedback, result.message || 'Compte désactivé.');
    clearAuthState();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Impossible de désactiver le compte', true);
  }
};

const handleLogout = () => {
  clearAuthState();
  setFeedback(authFeedback, 'Vous êtes déconnecté. À très vite !');
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
        updateHeroStats(lastReviews);
        renderMapFeed(lastReviews);
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
  profileForm.addEventListener('submit', handleProfileUpdate);
  passwordForm.addEventListener('submit', handlePasswordChange);
  deactivateForm.addEventListener('submit', handleDeactivate);
  logoutBtn.addEventListener('click', handleLogout);
  if (closeDetailBtn) {
    closeDetailBtn.addEventListener('click', hideReviewDetail);
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      hideReviewDetail();
    }
  });
  if (apiConfigBtn) {
    apiConfigBtn.addEventListener('click', handleApiConfigClick);
  }
  if (themeToggle) {
    themeToggle.addEventListener('click', handleThemeToggle);
  }
  if (mapSearchForm) {
    mapSearchForm.addEventListener('submit', handleMapSearch);
  }
};

const initApp = () => {
  initTheme();
  yearEl.textContent = new Date().getFullYear();
  initRevealAnimations();
  updateApiIndicator();
  if (window.location.protocol === 'https:' && apiBaseUrl.startsWith('http://')) {
    showGlobalMessage(
      "Cette page est servie en HTTPS. Assurez-vous que l'API répond en HTTPS pour éviter les requêtes bloquées.",
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
