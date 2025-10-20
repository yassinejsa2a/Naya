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
const photoFeedback = document.getElementById('photo-feedback');
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
let revealObserver = null;

const getStoredTheme = () => {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
  } catch (error) {
    console.warn('NAYA : impossible de lire le thème stocké.', error);
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
    try {
      window.localStorage.removeItem(THEME_STORAGE_KEY);
    } catch (error) {
      console.warn('NAYA : impossible de nettoyer le thème stocké.', error);
    }
    return;
  }
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme === 'dark' ? 'dark' : 'light');
  } catch (error) {
    console.warn('NAYA : impossible de stocker le thème.', error);
  }
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
  const stored = getStoredTheme();
  if (stored) {
    setTheme(stored);
  } else {
    applyTheme(getPreferredTheme());
  }
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
      console.warn('NAYA : URL de base API invalide définie dans <meta name="naya-api-base">.', error);
    }
  }

  if (window.location.origin && window.location.origin.startsWith('http')) {
    try {
      return normaliseApiBaseUrl(window.location.origin);
    } catch (error) {
      console.warn("NAYA : impossible de déterminer l'URL de base de l'API depuis window.location.origin.", error);
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
  console.warn("NAYA : URL de base API stockée invalide, retour à la valeur par défaut.", error);
  window.localStorage.removeItem('naya-api-base');
  apiBaseUrl = defaultApiBaseUrl;
}

let authToken = window.localStorage.getItem('naya-token');
let currentUser = null;
let lastReviews = [];
let highlightedReviewId = null;
let globalMessageTimeoutId;
let lastCreatedReviewId = null;
let currentDetailReviewId = null;

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
    window.localStorage.setItem('naya-api-base', value);
  } else {
    window.localStorage.removeItem('naya-api-base');
  }
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

    return matchingPlace?.id ?? null;
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
      return createdPlace.id;
    }

    // Certains endpoints renvoient la place sous data.place
    if (createdPlace?.place?.id) {
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

const fetchJson = async (endpoint, options = {}, { requiresAuth = false } = {}) => {
  const url = `${apiBaseUrl}${endpoint}`;
  const headers = options.headers ? { ...options.headers } : {};

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (requiresAuth) {
    if (!authToken) throw new Error('Authentification requise');
    headers.Authorization = `Bearer ${authToken}`;
  }

  let response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (networkError) {
    console.error("NAYA : erreur réseau lors de l'appel à l'API.", networkError);
    showGlobalMessage(
      `Impossible de joindre l'API à ${apiBaseUrl}. Vérifiez l'adresse dans « Paramètres API » ainsi que votre connexion.`,
      true,
      8000
    );
    throw new Error(
      `Impossible de joindre l'API à ${apiBaseUrl}. Merci de vérifier votre connexion ou vos paramètres API.`
    );
  }
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMessage = data.error || data.message || 'La requête a échoué';
    throw new Error(errorMessage);
  }

  return data;
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
  mapFeedList.innerHTML = '';

  if (!reviews.length) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'map-feed-empty';
    emptyItem.textContent = 'Aucun avis à afficher pour le moment.';
    mapFeedList.appendChild(emptyItem);
    highlightReviewItems();
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

        if (photo.caption) {
          const caption = document.createElement('figcaption');
          caption.textContent = photo.caption;
          figure.appendChild(caption);
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
    mapUrl = `https://maps.google.com/maps?q=${place.latitude},${place.longitude}&z=12&output=embed`;
  } else if (place.city || place.name) {
    const query = encodeURIComponent(`${place.name || ''} ${place.city || ''} ${place.country || ''}`.trim());
    mapUrl = `https://maps.google.com/maps?q=${query}&z=10&output=embed`;
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
};

const buildRatingLabel = (rating) => {
  if (typeof rating !== 'number' || Number.isNaN(rating)) return 'Note indisponible';
  const stars = '★'.repeat(Math.round(rating));
  return `${stars} (${rating}/5)`;
};

const renderReviewDetailContent = (review) => {
  if (!reviewDetailPanel || !reviewDetailBody) return;
  reviewDetailPanel.classList.remove('hidden');
  clearDetailPanel();

  if (photoForm?.review_id) {
    photoForm.review_id.value = review.id || '';
  }

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
      if (photo.caption) {
        const figcaption = document.createElement('figcaption');
        figcaption.textContent = photo.caption;
        figure.appendChild(figcaption);
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

  let review = lastReviews.find((item) => String(item.id) === String(reviewId));
  if (!review) {
    try {
      const response = await fetchJson(`/reviews/${reviewId}`);
      review = response?.data || response;
    } catch (error) {
      setFeedback(feedFeedback, error.message || 'Impossible de charger le détail de cet avis', true);
      hideReviewDetail();
      return;
    }
  }

  renderReviewDetailContent(review);
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

    saveAuthState(data.access_token, data.user);
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

const handleReviewSubmit = async (event) => {
  event.preventDefault();
  if (!authToken) {
    setFeedback(reviewFeedback, 'Vous devez être connecté pour partager un avis.', true);
    return;
  }

  const formData = new FormData(reviewForm);
  const payload = Object.fromEntries(formData.entries());
  Object.keys(payload).forEach((key) => {
    if (typeof payload[key] === 'string') {
      payload[key] = payload[key].trim();
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
    lastCreatedReviewId = createdReview?.id || lastCreatedReviewId;

    setFeedback(reviewFeedback, 'Avis publié avec succès !');
    reviewForm.reset();

    if (photoForm?.review_id && lastCreatedReviewId) {
      photoForm.review_id.value = lastCreatedReviewId;
    }

    await loadFeed();
    await loadProfile();
  } catch (error) {
    setFeedback(reviewFeedback, error.message || 'Impossible de publier cet avis', true);
  }
};

const handlePhotoSubmit = async (event) => {
  event.preventDefault();
  if (!authToken) {
    setFeedback(photoFeedback, 'Veuillez vous connecter pour ajouter une photo.', true);
    return;
  }

  const formData = new FormData(photoForm);
  const file = formData.get('photo_file');

  if (!(file instanceof File) || !file.name) {
    setFeedback(photoFeedback, 'Sélectionnez un fichier image à téléverser.', true);
    return;
  }

  const caption = formData.get('caption');
  if (typeof caption === 'string' && !caption.trim()) {
    formData.delete('caption');
  }

  let reviewId = formData.get('review_id');
  if (typeof reviewId === 'string') {
    reviewId = reviewId.trim();
  }

  if (!reviewId && lastCreatedReviewId) {
    formData.set('review_id', lastCreatedReviewId);
  } else if (!reviewId) {
    formData.delete('review_id');
  } else {
    formData.set('review_id', reviewId);
  }

  try {
    setFeedback(photoFeedback, 'Téléversement de la photo en cours…');
    const response = await fetchJson(
      '/photos',
      {
        method: 'POST',
        body: formData,
      },
      { requiresAuth: true }
    );

    const uploadedPhoto = response?.data;
    const targetReviewId = uploadedPhoto?.review_id || formData.get('review_id');
    if (targetReviewId) {
      lastCreatedReviewId = targetReviewId;
    }

    const photoUrl = uploadedPhoto?.file_url;
    setFeedback(
      photoFeedback,
      photoUrl ? `Photo téléversée avec succès ! (${photoUrl})` : 'Photo téléversée avec succès !'
    );
    photoForm.reset();
    if (targetReviewId && photoForm.review_id) {
      photoForm.review_id.value = targetReviewId;
    }
    await loadFeed();
  } catch (error) {
    setFeedback(photoFeedback, error.message || "Impossible d'enregistrer la photo", true);
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
    saveAuthState(null, null);
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Impossible de désactiver le compte', true);
  }
};

const handleLogout = () => {
  saveAuthState(null, null);
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
  photoForm.addEventListener('submit', handlePhotoSubmit);
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
};

const initApp = () => {
  initTheme();
  yearEl.textContent = new Date().getFullYear();
  initRevealAnimations();
  updateApiIndicator();
  if (window.location.protocol === 'https:' && apiBaseUrl.startsWith('http://')) {
    showGlobalMessage(
      'Cette page est servie en HTTPS. Configurez une URL d\'API en HTTPS via « Paramètres API » pour éviter les requêtes bloquées.',
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
