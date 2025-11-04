const loadFeed = async (query = {}) => {
  try {
    setFeedback(feedFeedback, 'Chargement des aventures…');
    const data = await api.reviews.list(query);
    lastReviews = data.reviews || [];
    reconcileLikedStateAcrossCollections();
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
    // Charge simultanément les informations du profil, les statistiques et les avis créés par l'utilisateur
    const [profile, stats, reviewsResponse] = await Promise.all([
      api.auth.profile(),
      api.auth.stats(),
      api.reviews.list({ user_id: currentUser?.id || 'me', limit: 50 }, { includeAuth: true }),
    ]);

    currentUser = profile;
    profileUsername.textContent = profile.username || 'Voyageur';
    profileEmail.textContent = profile.email || '—';
    profileCreated.textContent = formatDate(profile.created_at);
    profileReviewCount.textContent = stats.reviews_count ?? '0';
    setProfileAvatar(profile.profile_photo_url, profile.username || '');

    ensureLikedReviewsFromProfile(profile.liked_reviews || [], profile.liked_reviews_count ?? null);
    lastReviews.forEach((review) => {
      if (!review?.id) return;
      const liked = likedReviewIds.has(String(review.id));
      updateLikeButtonsInDOM(review.id, review.likes_count ?? 0, liked);
    });

    // Préfère la réponse API détaillée, sinon retombe sur les avis déjà présents dans le profil
    postedReviews = Array.isArray(reviewsResponse?.reviews) && reviewsResponse.reviews.length
      ? [...reviewsResponse.reviews]
      : Array.isArray(profile.reviews)
      ? profile.reviews
      : [];
    refreshPostedReviewsUI();

    profileForm.username.value = profile.username || '';
    profileForm.bio.value = profile.bio || '';
  } catch (error) {
    console.error(error);
    setFeedback(profileFeedback, error.message || 'Échec du chargement du profil', true);
  }
};

const showPublicProfile = async (userId) => {
  if (!userId) return;
  publicProfileUserId = userId;
  hideReviewDetail();
  showView('public-profile-view');
  setFeedback(publicProfileFeedback, 'Chargement du profil…');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  publicProfileReviewsList.innerHTML = '';
  if (publicProfileAvatar) {
    publicProfileAvatar.src = resolveAvatarUrl(null);
    publicProfileAvatar.alt = 'Photo de profil du voyageur';
  }
  if (publicProfileTitle) {
    publicProfileTitle.textContent = 'Chargement du profil';
  }
  if (publicProfileSubtitle) {
    publicProfileSubtitle.textContent = 'Merci de patienter pendant le chargement des informations.';
  }

  try {
    const [profilePayload, reviewsPayload] = await Promise.all([
      api.auth.publicProfile(userId),
      api.reviews.list({ user_id: userId, limit: 50 }),
    ]);

    const profileData = profilePayload?.user || profilePayload;
    const profile = { ...profileData, reviews: profileData?.reviews || [] };
    if (!profile) {
      throw new Error('Profil introuvable');
    }

    if (publicProfileTitle) {
      publicProfileTitle.textContent = profile.username
        ? `Profil de ${profile.username}`
        : 'Profil du voyageur';
    }
    if (publicProfileSubtitle) {
      const reviewCount = profile.reviews_count ?? 0;
      const reviewLabel = reviewCount === 1 ? 'avis partagé' : 'avis partagés';
      const reviewer = profile.username ? `par ${profile.username}` : 'par ce membre';
      publicProfileSubtitle.textContent = `${reviewCount.toLocaleString('fr-FR')} ${reviewLabel} ${reviewer}.`;
    }
    publicProfileUsername.textContent = profile.username || 'Voyageur';
    publicProfileBio.textContent = profile.bio?.trim() || 'Aucune biographie renseignée.';
    publicProfileCreated.textContent = profile.created_at ? formatDate(profile.created_at) : '—';
    publicProfileReviewsCount.textContent = (profile.reviews_count ?? 0).toLocaleString('fr-FR');
    publicProfilePhotosCount.textContent = (profile.photos_count ?? 0).toLocaleString('fr-FR');
    if (publicProfileAvatar) {
      publicProfileAvatar.src = resolveAvatarUrl(profile.profile_photo_url);
      publicProfileAvatar.alt = profile.username
        ? `Photo de profil de ${profile.username}`
        : 'Photo de profil du voyageur';
    }

    const reviews = reviewsPayload?.reviews || [];
    renderPublicProfileReviews(reviews);
  } catch (error) {
    console.error(error);
    setFeedback(publicProfileFeedback, error.message || 'Impossible de charger ce profil.', true);
    if (publicProfileAvatar) {
      publicProfileAvatar.src = resolveAvatarUrl(null);
      publicProfileAvatar.alt = 'Photo de profil du voyageur';
    }
    if (publicProfileTitle) {
      publicProfileTitle.textContent = 'Profil indisponible';
    }
    if (publicProfileSubtitle) {
      publicProfileSubtitle.textContent = 'Nous ne parvenons pas à afficher ce profil pour le moment.';
    }
    publicProfileUsername.textContent = 'Voyageur';
    publicProfileBio.textContent = 'Aucune biographie renseignée.';
    publicProfileCreated.textContent = '—';
    publicProfileReviewsCount.textContent = '0';
    publicProfilePhotosCount.textContent = '0';
  }
};

const saveAuthState = (token, user, refresh, { silent = false } = {}) => {
  authToken = token || null;
  currentUser = user || null;
  setProfileAvatar(user?.profile_photo_url, user?.username || '');

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
  likedReviews = [];
  likedReviewsTotal = 0;
  likedReviewIds.clear();
  refreshLikedReviewsUI();
  reviewCommentsCache.clear();
  commentSections.clear();
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

