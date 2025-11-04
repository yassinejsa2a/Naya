
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
  if (profilePhotoForm) {
    profilePhotoForm.addEventListener('submit', handleProfilePhotoUpdate);
  }
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
  if (profileThemeToggle) {
    profileThemeToggle.addEventListener('click', handleThemeToggle);
  }
  if (mapSearchForm) {
    mapSearchForm.addEventListener('submit', handleMapSearch);
  }
  if (publicProfileBackBtn) {
    publicProfileBackBtn.addEventListener('click', () => {
      setFeedback(publicProfileFeedback, '');
      publicProfileReviewsList.innerHTML = '';
      publicProfileReviews = [];
      publicProfileUserId = null;
      const destination = authToken ? 'feed-view' : 'auth-view';
      showView(destination);
      if (destination === 'feed-view') {
        updateHeroStats(lastReviews);
        renderMapFeed(lastReviews);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
};

const initApp = () => {
  initTheme();
  yearEl.textContent = new Date().getFullYear();
  initRevealAnimations();
  updateApiIndicator();
  setProfileAvatar(null);
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
