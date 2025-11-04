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

const api = {
  reviews: {
    list: (params = {}) => fetchJson(`/reviews${buildQueryString(params)}`),
    get: (id) => fetchJson(`/reviews/${id}`),
    create: (payload) =>
      fetchJson(
        '/reviews',
        {
          method: 'POST',
          body: JSON.stringify(payload),
        },
        { requiresAuth: true }
      ),
    update: (id, payload) =>
      fetchJson(
        `/reviews/${id}`,
        {
          method: 'PUT',
          body: JSON.stringify(payload),
        },
        { requiresAuth: true }
      ),
    like: (id) => fetchJson(`/reviews/${id}/likes`, { method: 'POST' }, { requiresAuth: true }),
    unlike: (id) => fetchJson(`/reviews/${id}/likes`, { method: 'DELETE' }, { requiresAuth: true }),
    likes: (id) => fetchJson(`/reviews/${id}/likes`, { method: 'GET' }, { requiresAuth: Boolean(authToken) }),
    comments: {
      list: (id, params = {}) => fetchJson(`/reviews/${id}/comments${buildQueryString(params)}`, { method: 'GET' }, { requiresAuth: Boolean(authToken) }),
      create: (id, payload) =>
        fetchJson(
          `/reviews/${id}/comments`,
          {
            method: 'POST',
            body: JSON.stringify(payload),
          },
          { requiresAuth: true }
        ),
      delete: (reviewId, commentId) =>
        fetchJson(`/reviews/${reviewId}/comments/${commentId}`, { method: 'DELETE' }, { requiresAuth: true }),
    },
    delete: (id) => fetchJson(`/reviews/${id}`, { method: 'DELETE' }, { requiresAuth: true }),
  },
  auth: {
    login: (credentials) =>
      fetchJson('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      }),
    register: (payload) =>
      fetchJson('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    profile: () => fetchJson('/auth/profile', { method: 'GET' }, { requiresAuth: true }),
    updateProfile: (payload) =>
      fetchJson(
        '/auth/profile',
        {
          method: 'PUT',
          body: JSON.stringify(payload),
        },
        { requiresAuth: true }
      ),
    changePassword: (payload) =>
      fetchJson(
        '/auth/change-password',
        {
          method: 'PUT',
          body: JSON.stringify(payload),
        },
        { requiresAuth: true }
      ),
    updateAvatar: (formData) =>
      fetchJson('/auth/avatar', { method: 'PUT', body: formData }, { requiresAuth: true }),
    deactivate: () => fetchJson('/auth/deactivate', { method: 'PUT' }, { requiresAuth: true }),
    stats: () => fetchJson('/auth/stats', { method: 'GET' }, { requiresAuth: true }),
    publicProfile: (userId) => fetchJson(`/auth/users/${encodeURIComponent(userId)}`),
    refresh: () =>
      fetchJson(
        '/auth/refresh',
        { method: 'POST' },
        { requiresAuth: true, skipRefresh: true, useRefreshToken: true }
      ),
  },
  places: {
    search: (params = {}) => fetchJson(`/places${buildQueryString(params)}`),
    create: (payload) =>
      fetchJson(
        '/places',
        {
          method: 'POST',
          body: JSON.stringify(payload),
        },
        { requiresAuth: true }
      ),
  },
  photos: {
    upload: (formData) => fetchJson('/photos', { method: 'POST', body: formData }, { requiresAuth: true }),
    delete: (photoId) => fetchJson(`/photos/${photoId}`, { method: 'DELETE' }, { requiresAuth: true }),
  },
};

const refreshAccessToken = async () => {
  if (!refreshToken) {
    throw new Error('Session expirée. Merci de vous reconnecter.');
  }

  const response = await api.auth.refresh();

  const newToken = response?.access_token;
  if (!newToken) {
    throw new Error('Impossible de rafraîchir la session.');
  }

  saveAuthState(newToken, currentUser, refreshToken, { silent: true });
  return newToken;
};
