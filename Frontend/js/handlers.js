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
    const data = await api.auth.login(payload);

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
    await api.auth.register(payload);

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
    const data = await api.reviews.list({ search: term });
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
    const response = await api.reviews.create(payload);

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
        await api.photos.upload(photoPayload);
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
    const result = await api.auth.updateProfile(payload);

    setFeedback(profileFeedback, result.message || 'Profil mis à jour !');
    await loadProfile();
  } catch (error) {
    setFeedback(profileFeedback, error.message || 'Impossible de mettre le profil à jour', true);
  }
};

const handleProfilePhotoUpdate = async (event) => {
  event.preventDefault();
  if (!profilePhotoForm) return;
  if (!authToken) {
    setFeedback(profileFeedback, 'Vous devez être connecté pour changer votre photo de profil.', true);
    return;
  }

  const formData = new FormData(profilePhotoForm);
  const avatarFile = formData.get('avatar');
  if (!(avatarFile instanceof File) || !avatarFile.name) {
    setFeedback(profileFeedback, 'Sélectionnez une image avant de téléverser.', true);
    return;
  }

  try {
    setFeedback(profileFeedback, 'Téléversement de votre photo…');
    const result = await api.auth.updateAvatar(formData);
    const updatedUser = result?.user || currentUser;
    if (updatedUser) {
      saveAuthState(authToken, updatedUser, refreshToken, { silent: true });
      setProfileAvatar(updatedUser.profile_photo_url, updatedUser.username || '');
    } else if (result?.profile_photo_url) {
      setProfileAvatar(result.profile_photo_url, currentUser?.username || '');
    }
    profilePhotoForm.reset();
    setFeedback(profileFeedback, result?.message || 'Photo de profil mise à jour !');
    await loadProfile();
  } catch (error) {
    setFeedback(
      profileFeedback,
      error.message || 'Impossible de mettre à jour la photo de profil',
      true
    );
  }
};

const handlePasswordChange = async (event) => {
  event.preventDefault();
  const formData = new FormData(passwordForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    setFeedback(profileFeedback, 'Mise à jour du mot de passe…');
    const result = await api.auth.changePassword(payload);
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
    const result = await api.auth.deactivate();

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
