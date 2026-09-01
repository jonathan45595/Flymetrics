/* ═══════════════════════════════════════════════════════════
   Flymetrics — app.js
   Lógica interactiva nativa y animaciones de cristal líquido
   ═══════════════════════════════════════════════════════════ */

const GOOGLE_CLIENT_ID = '1044490043488-n2l2jjvnpq2mn8km4ag62r4t4af10vb6.apps.googleusercontent.com';

// Diagnósticos de errores en consola
window.addEventListener('error', (event) => {
  const msg = event.error ? (event.error.stack || event.error.message) : event.message;
  console.error('Global captured error:', msg);
});

window.addEventListener('unhandledrejection', (event) => {
  const msg = event.reason ? (event.reason.stack || event.reason.message || event.reason) : 'Promesa rechazada';
  console.error('Global captured rejection:', msg);
});

/* ── FUNCIÓN GLOBAL DE APERTURA DEL MODAL DE AUTENTICACIÓN ── */
/* Definida a nivel global para que SIEMPRE funcione independientemente de initAuthModal */
function openAuthModal(viewType, event) {
  viewType = viewType || 'login';
  var modal = document.getElementById('auth-modal');
  if (!modal) { alert('Error: No se encontró el modal #auth-modal en el HTML'); return; }

  // Cambiar vista (login o register)
  var tabLogin = document.getElementById('tab-login');
  var tabRegister = document.getElementById('tab-register');
  var tabPill = document.getElementById('auth-tab-pill');
  var viewLoginEl = document.getElementById('view-login');
  var viewRegisterEl = document.getElementById('view-register');
  var errorBox = document.getElementById('auth-error-box');
  var slider = document.getElementById('auth-views-slider');

  if (errorBox) { errorBox.style.display = 'none'; errorBox.textContent = ''; }

  // Desactivar transiciones temporales en slider y pill para posicionarlos de inmediato
  if (slider) slider.style.transition = 'none';
  if (tabPill) tabPill.style.transition = 'none';

  var authCardEl = modal.querySelector('.auth-card');
  if (authCardEl) authCardEl.scrollTop = 0;


  if (viewType === 'login') {
    if (tabLogin) tabLogin.classList.add('active');
    if (tabRegister) tabRegister.classList.remove('active');
    if (tabPill) tabPill.style.transform = 'translateX(0)';
    if (viewLoginEl) viewLoginEl.classList.add('active');
    if (viewRegisterEl) viewRegisterEl.classList.remove('active');
    if (slider) slider.style.transform = 'translateX(0)';
  } else {
    if (tabLogin) tabLogin.classList.remove('active');
    if (tabRegister) tabRegister.classList.add('active');
    if (tabPill) tabPill.style.transform = 'translateX(100%)';
    if (viewLoginEl) viewLoginEl.classList.remove('active');
    if (viewRegisterEl) viewRegisterEl.classList.add('active');
    if (slider) slider.style.transform = 'translateX(-50%)';
  }

  // Forzar reflow para aplicar la posición de inmediato sin transition
  if (slider) slider.offsetHeight;
  if (tabPill) tabPill.offsetHeight;

  // Restaurar transiciones estándar para cuando el usuario interactúe con los tabs dentro del modal
  setTimeout(function() {
    if (slider) slider.style.transition = '';
    if (tabPill) tabPill.style.transition = '';
  }, 50);

  // Calcular origen de la animación a partir de las coordenadas del clic (zoom dinámico desde el botón lateral/clicado)
  var modalContent = modal.querySelector('.modal-content');
  if (modalContent) {
    var clickEvent = event || window.event;
    if (clickEvent && typeof clickEvent.clientX === 'number' && typeof clickEvent.clientY === 'number') {
      var modalWidth = modalContent.offsetWidth || 460;
      var modalHeight = modalContent.offsetHeight || 580;
      var rectLeft = (window.innerWidth - modalWidth) / 2;
      var rectTop = (window.innerHeight - modalHeight) / 2;
      var x = clickEvent.clientX - rectLeft;
      var y = clickEvent.clientY - rectTop;
      modalContent.style.transformOrigin = x + 'px ' + y + 'px';
    } else {
      modalContent.style.transformOrigin = 'center';
    }
  }

  // Forzar reflow en el modal y su contenido para asegurar que se registre el estado cerrado antes del inicio de la transición
  modal.offsetHeight;
  if (modalContent) modalContent.offsetHeight;

  // Solo manejamos clases, dejando transiciones fluidas al CSS (overlay & transform)
  modal.removeAttribute('inert');
  modal.removeAttribute('aria-hidden');
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';

  // Enfocar campo correspondiente para facilitar la escritura inmediata
  setTimeout(function() {
    var inp = viewType === 'register' 
      ? document.getElementById('register-name') 
      : document.getElementById('login-email');
    if (inp) inp.focus();
    if (typeof window.initGoogleSignIn === 'function') {
      window.initGoogleSignIn();
    }
  }, 180);

  // Cerrar menú móvil si estuviera abierto
  var mobileDrawer = document.getElementById('mobile-drawer');
  var burgerBtn = document.getElementById('burger-btn');
  var drawerOverlay = document.getElementById('drawer-overlay');
  if (mobileDrawer && mobileDrawer.classList.contains('open')) {
    mobileDrawer.classList.remove('open');
    if (burgerBtn) burgerBtn.classList.remove('open');
    if (drawerOverlay) drawerOverlay.classList.remove('active');
  }
}

function closeAuthModal() {
  var modal = document.getElementById('auth-modal');
  if (!modal) return;

  // Accessibility / ARIA fix: Blur focused element inside modal before hiding
  if (document.activeElement && modal.contains(document.activeElement)) {
    document.activeElement.blur();
  }
  if (document.body) {
    document.body.focus();
  }

  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  var errorBox = document.getElementById('auth-error-box');
  if (errorBox) { errorBox.style.display = 'none'; errorBox.textContent = ''; }
}

window.togglePasswordVisibility = function(inputId, btn) {
  var inp = document.getElementById(inputId);
  if (!inp) return;
  var isPwd = inp.type === 'password';
  inp.type = isPwd ? 'text' : 'password';
  if (btn) {
    var icon = btn.querySelector('i');
    if (icon) {
      if (isPwd) {
        icon.className = 'fa-solid fa-eye-slash';
        btn.setAttribute('aria-label', 'Ocultar contraseña');
      } else {
        icon.className = 'fa-solid fa-eye';
        btn.setAttribute('aria-label', 'Mostrar contraseña');
      }
    }
  }
};

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar componentes de forma robusta e independiente
  var safeInit = function(name, fn) {
    try {
      fn();
    } catch (err) {
      console.error('Error inicializando ' + name + ':', err);
    }
  };

  safeInit('TechLinesBg', initTechLinesBg);
  safeInit('HeroVideoLoop', initHeroVideoLoop);
  safeInit('MobileDrawer', initMobileDrawer);
  safeInit('ScrollEffects', initScrollEffects);
  safeInit('ActiveSectionHighlight', initActiveSectionHighlight);
  safeInit('PillIndicators', initPillIndicators);
  safeInit('ServiceModal', initServiceModal);
  safeInit('FaqAccordion', initFaqAccordion);
  safeInit('AuthModal', initAuthModal);
});

/* ── MENÚ MÓVIL (DRAWER) ─────────────────────────────────── */
function initMobileDrawer() {
  const burgerBtn = document.getElementById('burger-btn');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const drawerOverlay = document.getElementById('drawer-overlay');
  const drawerLinks = document.querySelectorAll('.drawer-link');

  if (!burgerBtn || !mobileDrawer || !drawerOverlay) return;

  const toggleDrawer = () => {
    const isOpen = mobileDrawer.classList.toggle('open');
    burgerBtn.classList.toggle('open', isOpen);
    drawerOverlay.classList.toggle('active', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  };

  const closeDrawer = () => {
    mobileDrawer.classList.remove('open');
    burgerBtn.classList.remove('open');
    drawerOverlay.classList.remove('active');
    document.body.style.overflow = '';
  };

  burgerBtn.addEventListener('click', toggleDrawer);
  drawerOverlay.addEventListener('click', closeDrawer);

  // Cerrar al hacer clic en un enlace
  drawerLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeDrawer();
    });
  });

  // Cerrar con tecla Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileDrawer.classList.contains('open')) {
      closeDrawer();
    }
  });
}

function initScrollEffects() {
  const navbar = document.getElementById('navbar');
  const fab = document.querySelector('.fab-agendar');

  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (navbar) {
      navbar.classList.toggle('scrolled', scrollTop > 40);
    }

    if (fab) {
      fab.classList.toggle('visible', scrollTop > 300);
    }
  }, { passive: true });
}

/* ── RESALTE DE SECCIÓN ACTIVA EN NAVBAR ─────────────────── */
function initActiveSectionHighlight() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  const drawerLinks = document.querySelectorAll('.drawer-link');

  if (sections.length === 0) return;

  const observerOptions = {
    root: null,
    rootMargin: '-35% 0px -55% 0px', // Detectar sección en el centro del viewport
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        
        // Actualizar links desktop
        navLinks.forEach(link => {
          const href = link.getAttribute('href').substring(1);
          link.classList.toggle('active', href === id);
        });

        // Actualizar links móvil
        drawerLinks.forEach(link => {
          const href = link.getAttribute('href').substring(1);
          link.classList.toggle('active', href === id);
        });
      }
    });
  }, observerOptions);

  sections.forEach(section => observer.observe(section));
}

/* ── DESPLAZAMIENTO ELÁSTICO DE CÁPSULAS (JELLY SQUASH & STRETCH) ── */
function initPillIndicators() {
  const navLinksContainer = document.getElementById('nav-links');
  const navActivePill = document.getElementById('nav-active-pill');
  const drawerLinksContainer = document.getElementById('drawer-links');
  const drawerActivePill = document.getElementById('drawer-active-pill');

  let navTimeout = null;
  let drawerTimeout = null;

  // Actualización horizontal (Navbar Escritorio)
  const updatePillHorizontal = (pill, activeLink, container) => {
    if (!pill || !activeLink || !container) return;
    const linkRect = activeLink.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    const targetLeft = linkRect.left - containerRect.left;
    const targetWidth = linkRect.width;

    const currentLeft = parseFloat(pill.style.left) || 0;
    const currentWidth = parseFloat(pill.style.width) || 0;

    // Detectar si hay un cambio real de posición
    if (currentWidth > 0 && Math.abs(targetLeft - currentLeft) > 5) {
      if (navTimeout) clearTimeout(navTimeout);

      // Determinar la dirección horizontal del movimiento
      const isMovingRight = targetLeft > currentLeft;
      pill.classList.remove('moving-left', 'moving-right');
      pill.classList.add(isMovingRight ? 'moving-right' : 'moving-left');

      // Calcular caja contenedora que une origen y destino (estiramiento elástico)
      const combinedLeft = Math.min(currentLeft, targetLeft);
      const combinedWidth = Math.max(currentLeft + currentWidth, targetLeft + targetWidth) - combinedLeft;

      pill.style.left = combinedLeft + 'px';
      pill.style.width = combinedWidth + 'px';

      // Fase de contracción: Encoger la píldora al tamaño y posición de destino
      navTimeout = setTimeout(() => {
        pill.style.left = targetLeft + 'px';
        pill.style.width = targetWidth + 'px';
        
        // Retirar la clase de estiramiento para el rebote elástico (snap back)
        setTimeout(() => {
          pill.classList.remove('moving-left', 'moving-right');
        }, 150);
      }, 150);
    } else {
      // Posición inicial sin animación de estiramiento
      pill.style.left = targetLeft + 'px';
      pill.style.width = targetWidth + 'px';
    }
    pill.style.height = linkRect.height + 'px';
  };

  // Actualización vertical (Menú Desplegable Móvil)
  const updatePillVertical = (pill, activeLink, container) => {
    if (!pill || !activeLink || !container) return;
    const linkRect = activeLink.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    const targetTop = linkRect.top - containerRect.top;
    const targetHeight = linkRect.height;

    const currentTop = parseFloat(pill.style.top) || 0;
    const currentHeight = parseFloat(pill.style.height) || 0;

    // Detectar si hay un cambio de posición vertical
    if (currentHeight > 0 && Math.abs(targetTop - currentTop) > 5) {
      if (drawerTimeout) clearTimeout(drawerTimeout);

      // Determinar la dirección vertical del movimiento
      const isMovingDown = targetTop > currentTop;
      pill.classList.remove('moving-up', 'moving-down');
      pill.classList.add(isMovingDown ? 'moving-down' : 'moving-up');

      // Calcular caja contenedora que une origen y destino verticalmente
      const combinedTop = Math.min(currentTop, targetTop);
      const combinedHeight = Math.max(currentTop + currentHeight, targetTop + targetHeight) - combinedTop;

      pill.style.top = combinedTop + 'px';
      pill.style.height = combinedHeight + 'px';

      // Contraer
      drawerTimeout = setTimeout(() => {
        pill.style.top = targetTop + 'px';
        pill.style.height = targetHeight + 'px';

        setTimeout(() => {
          pill.classList.remove('moving-up', 'moving-down');
        }, 150);
      }, 150);
    } else {
      pill.style.top = targetTop + 'px';
      pill.style.height = targetHeight + 'px';
    }
  };

  const syncActivePill = () => {
    const activeNavLink = navLinksContainer ? navLinksContainer.querySelector('.nav-link.active') : null;
    const activeDrawerLink = drawerLinksContainer ? drawerLinksContainer.querySelector('.drawer-link.active') : null;
    
    if (activeNavLink && navActivePill) updatePillHorizontal(navActivePill, activeNavLink, navLinksContainer);
    if (activeDrawerLink && drawerActivePill) updatePillVertical(drawerActivePill, activeDrawerLink, drawerLinksContainer);
  };

  const observer = new MutationObserver((mutations) => {
    const hasLinkMutation = mutations.some(m => 
      m.target && m.target.classList && (
        m.target.classList.contains('nav-link') || 
        m.target.classList.contains('drawer-link')
      )
    );
    if (hasLinkMutation) {
      syncActivePill();
    }
  });
  
  const observerOptions = { attributes: true, subtree: true, attributeFilter: ['class'] };
  
  if (navLinksContainer) observer.observe(navLinksContainer, observerOptions);
  if (drawerLinksContainer) observer.observe(drawerLinksContainer, observerOptions);

  let resizeTimeout;
  window.addEventListener('resize', () => {
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(syncActivePill, 120);
  });
  window.addEventListener('load', syncActivePill); // Sincronizar al cargar todos los estilos/fuentes
  
  // Sincronización de renderizado inicial
  setTimeout(syncActivePill, 100);
}

/* ── MODAL DE AUTENTICACIÓN FUNCIONAL (LOGIN Y REGISTRO) ── */
function initAuthModal() {
  const modal = document.getElementById('auth-modal');
  const closeBtn = document.getElementById('auth-close-btn');
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');
  const tabPill = document.getElementById('auth-tab-pill');
  const viewLogin = document.getElementById('view-login');
  const viewRegister = document.getElementById('view-register');
  const formLogin = document.getElementById('form-login');
  const formRegister = document.getElementById('form-register');
  const errorBox = document.getElementById('auth-error-box');

  if (!modal) return;

  // Google Sign-In Integration
  let gInited = false;
  window.initGoogleSignIn = function() {
    if (gInited) return;
    if (typeof google === 'undefined' || !google.accounts) {
      if (!window.initGoogleSignIn._retries) window.initGoogleSignIn._retries = 0;
      if (window.initGoogleSignIn._retries < 25) {
        window.initGoogleSignIn._retries++;
        setTimeout(window.initGoogleSignIn, 400);
      }
      return;
    }

    try {
      google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleSignInCallback,
        ux_mode: 'popup'
      });

      const btnDiv = document.getElementById('g_id_signin');
      if (btnDiv) {
        google.accounts.id.renderButton(btnDiv, {
          type: 'standard',
          shape: 'rectangular',
          theme: 'dark',
          text: 'continue_with',
          size: 'large',
          logo_alignment: 'left',
          width: btnDiv.offsetWidth || 280
        });
        gInited = true;
      }
    } catch (err) {
      console.error('Error initializing Google Sign-In:', err);
    }
  };

  window.initGoogleSignIn();

  const handleGoogleSignInCallback = async (response) => {
    hideError();
    const token = response.credential;
    
    // Obtener botón e indicar carga
    const gDiv = document.getElementById('g_id_signin');
    const originalHTML = gDiv ? gDiv.innerHTML : '';
    if (gDiv) gDiv.innerHTML = '<span style="color:var(--text-muted); font-size:0.88rem;">Iniciando sesión...</span>';

    try {
      // Llamar a la API de Google del backend
      const loginData = await API.loginGoogle(token);
      const jwtToken = loginData.access_token || loginData.data?.token;
      API.setToken(jwtToken);

      // Obtener perfil para guardar en localStorage y evitar bucles
      const profileRes = await API.getMe(jwtToken);
      const userObj = profileRes.data;

      sessionStorage.setItem('fm_role', userObj.rol);
      sessionStorage.setItem('fm_email', userObj.email);
      sessionStorage.setItem('fm_logged_in', 'true');
      sessionStorage.setItem('fm_user', JSON.stringify(userObj));
      try { localStorage.setItem('fm_token', jwtToken); } catch(e) {}

      setTimeout(() => {
        closeAuthModal();
        if (userObj.rol === 'administrador') {
          window.location.href = 'admin.html';
        } else if (userObj.rol === 'tecnico') {
          window.location.href = 'tecnico.html';
        } else {
          window.location.href = 'cliente.html';
        }
      }, 600);

    } catch (err) {
      if (gDiv) gDiv.innerHTML = originalHTML;
      // Re-render button if possible by re-init
      gInited = false;
      if (typeof window.initGoogleSignIn === 'function') {
        window.initGoogleSignIn();
      }
      showError(err.message || 'Fallo de autenticación con Google.');
    }
  };

  const regErrorBox = document.getElementById('auth-register-error-box');

  const showError = (message, isRegister = false) => {
    const targetBox = (isRegister || document.getElementById('view-register')?.classList.contains('active'))
      ? (regErrorBox || errorBox)
      : errorBox;

    if (!targetBox) return;
    targetBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="margin-right: 6px;"></i> ` + message;
    targetBox.style.display = 'block';
    targetBox.style.animation = 'none';
    targetBox.offsetHeight; // Forzar reflow
    targetBox.style.animation = '';
    targetBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  const hideError = () => {
    if (errorBox) {
      errorBox.style.display = 'none';
      errorBox.textContent = '';
    }
    if (regErrorBox) {
      regErrorBox.style.display = 'none';
      regErrorBox.textContent = '';
    }
  };

  const setView = (viewType) => {
    hideError();
    const authCard = modal.querySelector('.auth-card');
    if (authCard) authCard.scrollTop = 0;

    if (viewType === 'login') {
      tabLogin.classList.add('active');
      tabRegister.classList.remove('active');
      tabPill.style.transform = 'translateX(0)';
      viewLogin.classList.add('active');
      viewRegister.classList.remove('active');
      var slider = document.getElementById('auth-views-slider');
      if (slider) slider.style.transform = 'translateX(0)';
    } else {
      tabLogin.classList.remove('active');
      tabRegister.classList.add('active');
      tabPill.style.transform = 'translateX(100%)';
      viewLogin.classList.remove('active');
      viewRegister.classList.add('active');
      var slider = document.getElementById('auth-views-slider');
      if (slider) slider.style.transform = 'translateX(-50%)';
    }
  };



  // openAuthModal y closeAuthModal ahora son funciones globales definidas arriba

  // Interacción de pestañas
  tabLogin.addEventListener('click', () => setView('login'));
  tabRegister.addEventListener('click', () => setView('register'));

  // Botones de cerrado y overlay
  closeBtn.addEventListener('click', closeAuthModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeAuthModal();
  });

  // Cerrar con tecla escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeAuthModal();
    }
  });

  // Lógica del Selector de Roles en Grid
  const roleOptions = modal.querySelectorAll('.role-option');
  const loginRoleInput = document.getElementById('login-role');
  if (roleOptions.length > 0 && loginRoleInput) {
    roleOptions.forEach(option => {
      option.addEventListener('click', () => {
        roleOptions.forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');
        loginRoleInput.value = option.getAttribute('data-role');
      });
    });
  }

  // Toggle de visibilidad de contraseña
  const passwordToggleBtn = document.getElementById('password-toggle-btn');
  const loginPasswordInput = document.getElementById('login-password');
  if (passwordToggleBtn && loginPasswordInput) {
    const eyeIcon = passwordToggleBtn.querySelector('svg');
    passwordToggleBtn.addEventListener('click', () => {
      const isPassword = loginPasswordInput.type === 'password';
      loginPasswordInput.type = isPassword ? 'text' : 'password';
      if (isPassword) {
        eyeIcon.innerHTML = `
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
          <line x1="2" y1="2" x2="22" y2="22" stroke="currentColor" stroke-width="2"/>
        `;
        passwordToggleBtn.setAttribute('aria-label', 'Ocultar contraseña');
      } else {
        eyeIcon.innerHTML = `
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        `;
        passwordToggleBtn.setAttribute('aria-label', 'Mostrar contraseña');
      }
    });
  }

  // Envío del Login Form (Autenticación real e integración)
  if (formLogin) {
    formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideError();
      
      const role = document.getElementById('login-role')?.value || 'cliente';
      const email = (document.getElementById('login-email')?.value || '').trim().toLowerCase();
      const password = document.getElementById('login-password')?.value || '';
      
      if (!email || !password) {
        showError('Por favor ingrese correo y contraseña.');
        return;
      }
      
      const submitBtn = formLogin.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center; width: 100%;">
          <svg class="spinner" viewBox="0 0 50 50">
            <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
          </svg>
          Autenticando...
        </span>
      `;
      
      try {
        const data = await API.login(email, password);
        const token = data.token || data.access_token || (data.data && (data.data.token || data.data.access_token));
        if (!token) {
          throw new Error('No se recibió token de autenticación del servidor');
        }
        API.setToken(token);
        
        // Obtener perfil para asegurar redirección correcta basada en rol de la base de datos
        const profileRes = await API.getMe(token);
        const userObj = profileRes.data || profileRes;
        const actualRole = (userObj.rol || 'cliente').toLowerCase();

        // Guardar sesión
        sessionStorage.setItem('fm_role', actualRole);
        sessionStorage.setItem('fm_email', userObj.email || email);
        sessionStorage.setItem('fm_logged_in', 'true');
        sessionStorage.setItem('fm_user', JSON.stringify(userObj));
        try { 
          localStorage.setItem('fm_token', token);
          localStorage.setItem('fm_user', JSON.stringify(userObj));
          localStorage.setItem('fm_role', actualRole);
        } catch(e) {}

        setTimeout(() => {
          if (actualRole === 'administrador') {
            window.location.href = 'admin.html';
          } else if (actualRole === 'tecnico') {
            window.location.href = 'tecnico.html';
          } else {
            window.location.href = 'cliente.html';
          }
        }, 500);
        
      } catch (error) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        showError(error.message || 'Credenciales incorrectas o error de conexión.');
      }
    });
  }

  // Inicializar intl-tel-input para el formulario de registro
  let _itiRegister = null;
  const regPhoneInput = document.getElementById('register-phone');
  if (regPhoneInput && typeof window.intlTelInput !== 'undefined') {
    _itiRegister = window.intlTelInput(regPhoneInput, {
      initialCountry: 'co',
      preferredCountries: ['co', 'mx', 'us', 'es', 'pe', 'ec', 'ar', 'cl', 'pa', 'cr'],
      utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@24.5.0/build/js/utils.js',
      separateDialCode: true,
      autoPlaceholder: 'polite'
    });
  }

  // Envío del Formulario de Registro (Autocompleta y registra mediante API con validación de teléfono)
  if (formRegister) {
    formRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideError();
      
      const name = (document.getElementById('register-name').value.trim() || '').toUpperCase();
      const email = (document.getElementById('register-email').value.trim() || '').toLowerCase();
      const rawPhone = regPhoneInput ? regPhoneInput.value.trim() : '';
      const password = document.getElementById('register-password').value;
      const confirmPassword = document.getElementById('register-confirm-password').value;
      
      if (!name || !email || !rawPhone || !password || !confirmPassword) {
        showError('Por favor complete todos los campos obligatorios.');
        return;
      }

      // Validación de Nombre Completo (Máximo 4 palabras: 2 nombres y 2 apellidos)
      const nameParts = name.split(/\s+/).filter(Boolean);
      if (nameParts.length < 2) {
        showError('Por favor ingresa tu nombre y al menos un apellido.');
        document.getElementById('register-name')?.focus();
        return;
      }
      if (nameParts.length > 4) {
        showError('El nombre completo no puede tener más de 4 palabras (máximo 2 nombres y 2 apellidos).');
        document.getElementById('register-name')?.focus();
        return;
      }

      // Validar formato telefónico internacional si está disponible
      let formattedPhone = rawPhone;
      if (_itiRegister && typeof _itiRegister.isValidNumber === 'function') {
        if (_itiRegister.isValidNumber()) {
          formattedPhone = _itiRegister.getNumber();
        }
      }
      
      if (password.length < 6) {
        showError('La contraseña debe tener al menos 6 caracteres.');
        return;
      }

      if (password !== confirmPassword) {
        showError('Las contraseñas no coinciden. Por favor verifícalas.');
        return;
      }

      const submitBtn = document.getElementById('btn-register-submit') || formRegister.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center; width: 100%;">
          <svg class="spinner" viewBox="0 0 50 50">
            <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
          </svg>
          Creando Cuenta...
        </span>
      `;
      
      try {
        await API.register(name, email, password, 'cliente', formattedPhone);
        
        // Auto-login upon successful registration
        submitBtn.innerHTML = `
          <span style="display: inline-flex; align-items: center; gap: 8px; justify-content: center; width: 100%;">
            <svg class="spinner" viewBox="0 0 50 50">
              <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
            </svg>
            Iniciando sesión...
          </span>
        `;
        
        const loginData = await API.login(email, password);
        const token = loginData.access_token || loginData.token || (loginData.data && (loginData.data.token || loginData.data.access_token));
        if (!token) throw new Error('No se recibió token de acceso del servidor');
        API.setToken(token);

        const profileRes = await API.getMe(token);
        sessionStorage.setItem('fm_role', 'cliente');
        sessionStorage.setItem('fm_email', email);
        sessionStorage.setItem('fm_logged_in', 'true');
        sessionStorage.setItem('fm_user', JSON.stringify(profileRes.data || { email, rol: 'cliente' }));
        try { 
          localStorage.clear();
          localStorage.setItem('fm_token', token);
        } catch(e) {}

        setTimeout(() => {
          window.location.href = 'cliente.html';
        }, 500);
        
      } catch (error) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        const msg = error.message || 'Error al registrar la cuenta.';
        
        // Si el correo ya existe, mostrar notificación destacada con opción de ir directo a login
        if (msg.includes('ya se encuentra registrado') || msg.includes('ya está registrado')) {
          showError(`<i class="fa-solid fa-triangle-exclamation"></i>️ El correo '${email}' ya está registrado. ¿Deseas iniciar sesión en tu cuenta?`);
          const loginEmailInput = document.getElementById('login-email');
          if (loginEmailInput) loginEmailInput.value = email;
          
          // Resaltar pestaña de login
          setTimeout(() => {
            const loginTab = document.getElementById('tab-login');
            if (loginTab) loginTab.style.boxShadow = '0 0 12px #1C82AD';
          }, 300);
        } else {
          showError(msg);
        }
      }
    });
  }
}

// Base de datos de servicios ampliada (6 Sectores Especializados) con Imágenes Oficiales
window.servicesData = [
  {
    id: 0,
    image: "img/servicio_precision.jpg",
    icon: `<i class="fa-solid fa-wheat-awn" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Agricultura de Precisión",
    description: "Optimización integral del rendimiento agronómico mediante zonificación digital de cultivos, diagnóstico de variabilidad del suelo y prescripción variable de insumos. Aumentamos la rentabilidad por hectárea minimizando el impacto ambiental.",
    sistema: "Ecosistema Inteligente Flymetrics",
    efficiency: "Alta cobertura por jornada operativa",
    capacity: "Diagnóstico Multiespectral y Telemetría RTK",
    precision: "Centimétrica RTK (± 2 cm de margen geográfico)"
  },
  {
    id: 1,
    image: "img/servicio_aspersion.jpg",
    icon: `<i class="fa-solid fa-helicopter" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Aplicación Aérea con Drones",
    description: "Aplicación de ultra precisión de insumos agrícolas (fertilizantes foliares, fungicidas, herbicidas y bioestimulantes) mediante aspersión aérea inteligente con drones. Cobertura uniforme y penetración foliar óptima con cero compactación del suelo.",
    sistema: "Sistemas de Aspersión Inteligente y Pulverización ULV",
    efficiency: "Operación ágil y cobertura uniforme por lote",
    capacity: "Atomización Centrífuga de Alta Cobertura Foliar",
    precision: "Centimétrica RTK (± 2 cm de precisión de vuelo)"
  },
  {
    id: 2,
    image: "img/servicio_precision.jpg",
    icon: `<i class="fa-solid fa-seedling" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Análisis Multiespectral",
    description: "Diagnóstico aéreo multiespectral de alta definición del vigor vegetal de tus cultivos. Mediante la captura en bandas espectrales especializadas (Infrarrojo Cercano y Borde Rojo), generamos mapas de reflectancia y salud foliar que detectan anomalías nutricionales, plagas y estrés hídrico de forma temprana.",
    sistema: "Sensor Multiespectral 4 Bandas (G/R/RE/NIR) + RGB de Alta Resolución",
    efficiency: "Hasta 200 Hectáreas por vuelo de diagnóstico",
    capacity: "Resolución espacial de alta definición desde 2 cm por píxel",
    precision: "Georreferenciación centimétrica en tiempo real mediante RTK"
  },
  {
    id: 3,
    image: "img/servicio_topografia_3d.jpg",
    icon: `<i class="fa-solid fa-map-location-dot" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Cartografía y Topografía 3D",
    description: "Modelado tridimensional digital del terreno para planificación de siembras, curvas de nivel y cálculo de volumen de tierras. Generamos ortomosaicos 2D de alta resolución, Modelos Digitales de Elevación (MDE) y curvas topográficas para optimizar sistemas de riego y drenaje.",
    sistema: "Sistemas de Fotogrametría Aérea RTK",
    efficiency: "Levantamiento rápido y preciso de fincas y predios",
    capacity: "Resolución espacial de alta definición desde 2 cm por píxel",
    precision: "Margen de error centimétrico absoluto RTK (± 2 cm con GCPs)"
  },
  {
    id: 4,
    image: "img/servicio_ganaderia.jpg",
    icon: `<i class="fa-solid fa-cow" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Ganadería de Precisión",
    description: "Levantamiento topográfico y digitalización de potreros para rotación inteligente de ganado, diseño y monitoreo de redes de suministro de agua, y fertilización o fumigación aérea de pastos con drones para maximizar la carga animal.",
    sistema: "Plataforma de Mapeo de Potreros y Aspersión de Pasturas",
    efficiency: "Zonificación y cobertura eficiente de potreros y pastizales",
    capacity: "Digitalización de linderos, aforos de pasturas y fuentes hídricas",
    precision: "Precisión centimétrica RTK para cercado y fuentes de agua"
  },
  {
    id: 5,
    image: "img/servicio_topografia_3d.jpg",
    icon: `<i class="fa-solid fa-magnifying-glass-chart" style="font-size: 1.6rem; color: #ffffff;"></i>`,
    title: "Inspecciones Agrícolas de Cultivos",
    description: "Monitoreo fitosanitario y diagnóstico visual de alta resolución con sensores térmicos y RGB para identificar fallas en sistemas de riego, malezas localizadas y estrés en plantas.",
    sistema: "Drones Agrícolas con Sensor Térmico Radiométrico y Cámara RGB 4K",
    efficiency: "Inspección exhaustiva de lotes y plantas por jornada",
    capacity: "Zoom óptico de alta definición + Sensor térmico radiométrico",
    precision: "Detección milimétrica de anomalías foliares y estrés térmico"
  }
];

window.currentServiceIndex = 0;

window.updateModalContent = function(index) {
  const service = window.servicesData[index];
  if (!service) return;

  window.currentServiceIndex = index;

  const modalImg = document.getElementById('modal-img');
  if (modalImg && service.image) {
    modalImg.src = service.image;
    modalImg.alt = service.title;
  }

  const modalIcon = document.getElementById('modal-icon');
  const modalTitle = document.getElementById('modal-title');
  const modalDescription = document.getElementById('modal-description');
  if (modalIcon) modalIcon.innerHTML = service.icon;
  if (modalTitle) modalTitle.textContent = service.title;
  if (modalDescription) modalDescription.textContent = service.description;

  const droneEl = document.getElementById('spec-sistemae') || document.getElementById('spec-drone');
  if (droneEl) droneEl.textContent = service.sistema;

  const effEl = document.getElementById('spec-efficiency');
  if (effEl) effEl.textContent = service.efficiency;

  const capEl = document.getElementById('spec-capacity');
  if (capEl) capEl.textContent = service.capacity;

  const precEl = document.getElementById('spec-precision');
  if (precEl) precEl.textContent = service.precision;
};

window.modalOpenTime = 0;

window.openModal = function(index, e) {
  if (e && e.stopPropagation) e.stopPropagation();
  window.modalOpenTime = Date.now();
  const targetIdx = (typeof index === 'number') ? index : (parseInt(index) || 0);
  window.updateModalContent(targetIdx);
  const modal = document.getElementById('service-modal');
  if (modal) {
    modal.removeAttribute('inert');
    modal.removeAttribute('aria-hidden');
    modal.style.display = 'flex';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
};

window.closeModal = function(e) {
  const isDirectCloseBtn = e && e.target && (e.target.id === 'modal-close-btn' || e.target.closest('#modal-close-btn'));
  if (Date.now() - window.modalOpenTime < 300 && !isDirectCloseBtn) {
    return;
  }
  if (e && e.stopPropagation) e.stopPropagation();
  const modal = document.getElementById('service-modal');
  if (!modal) return;

  if (document.activeElement && modal.contains(document.activeElement)) {
    document.activeElement.blur();
  }

  modal.classList.remove('open');
  modal.style.opacity = '0';
  modal.style.visibility = 'hidden';
  modal.style.display = 'none';
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
};

window.nextService = function() {
  const nextIndex = (window.currentServiceIndex + 1) % window.servicesData.length;
  window.updateModalContent(nextIndex);
};

window.prevService = function() {
  const prevIndex = (window.currentServiceIndex - 1 + window.servicesData.length) % window.servicesData.length;
  window.updateModalContent(prevIndex);
};

/* ── MODAL INTERACTIVO DE SERVICIOS (DASHBOARD CÍCLICO) ── */
function initServiceModal() {
  const serviceCards = document.querySelectorAll('.showcase-card');
  const modal = document.getElementById('service-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const prevBtn = document.getElementById('modal-prev-btn');
  const nextBtn = document.getElementById('modal-next-btn');

  serviceCards.forEach(card => {
    card.onclick = function(e) {
      if (e && e.stopPropagation) e.stopPropagation();
      const id = parseInt(card.getAttribute('data-service-id')) || 0;
      window.openModal(id, e);
    };
  });

  if (closeBtn) closeBtn.onclick = window.closeModal;
  if (nextBtn) nextBtn.onclick = window.nextService;
  if (prevBtn) prevBtn.onclick = window.prevService;

  if (modal) {
    modal.onclick = function(e) {
      if (e.target === modal) window.closeModal(e);
    };
  }

  document.addEventListener('keydown', (e) => {
    if (!modal || !modal.classList.contains('open')) return;
    if (e.key === 'Escape') window.closeModal(e);
    if (e.key === 'ArrowRight') window.nextService();
    if (e.key === 'ArrowLeft') window.prevService();
  });
}

// ── VÍDEO HERO EN BUCLE CONTINUO (SEAMLESS INFINITE LOOP) ───────
function initHeroVideoLoop() {
  const vid = document.getElementById('hero-video');
  if (!vid) return;

  vid.loop = true;
  vid.muted = true;
  vid.playsInline = true;
  vid.setAttribute('playsinline', '');
  vid.setAttribute('webkit-playsinline', '');
  vid.setAttribute('muted', '');
  vid.setAttribute('autoplay', '');

  const startPlayback = () => {
    const playPromise = vid.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {});
    }
  };

  startPlayback();

  vid.addEventListener('ended', () => {
    vid.currentTime = 0;
    startPlayback();
  });

  vid.addEventListener('pause', () => {
    if (!document.hidden) {
      startPlayback();
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      startPlayback();
    }
  });

  window.addEventListener('touchstart', startPlayback, { once: true, passive: true });
  window.addEventListener('click', startPlayback, { once: true, passive: true });
}

// ── FONDO DE LÍNEAS TECNOLÓGICAS ORGÁNICAS (LiDAR CONSTELLATION) ─
function initTechLinesBg() {
  const canvas = document.getElementById('bg-tech-lines');
  if (!canvas) return;

  // En celulares desactivar el canvas para máximo rendimiento a 60 FPS
  if (window.innerWidth < 768) {
    canvas.style.display = 'none';
    return;
  }

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  const nodeCount = 32;
  const maxDistance = 150;

  const nodes = [];
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 1.2 + 0.8,
      color: Math.random() > 0.4 ? 'rgba(28, 130, 173, ' : 'rgba(228, 199, 161, '
    });
  }

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize, { passive: true });

  let isRunning = true;
  document.addEventListener('visibilitychange', () => {
    isRunning = !document.hidden;
    if (isRunning) requestAnimationFrame(animate);
  });

  function animate() {
    if (!isRunning) return;
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      n.x += n.vx;
      n.y += n.vy;

      if (n.x < 0) n.x = width;
      else if (n.x > width) n.x = 0;
      if (n.y < 0) n.y = height;
      else if (n.y > height) n.y = 0;

      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = n.color + '0.7)';
      ctx.fill();

      for (let j = i + 1; j < nodes.length; j++) {
        const n2 = nodes[j];
        const dx = n.x - n2.x;
        const dy = n.y - n2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          const alpha = (1 - dist / maxDistance) * 0.35;
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(n2.x, n2.y);
          ctx.strokeStyle = n.color + alpha + ')';
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animate);
  }

  animate();
}

/* ── ACORDEÓN DE PREGUNTAS FRECUENTES (FAQ) ── */
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');
  if (faqItems.length === 0) return;

  faqItems.forEach(item => {
    const trigger = item.querySelector('.faq-trigger');
    const content = item.querySelector('.faq-content');

    if (!trigger || !content) return;

    trigger.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Cerrar otros acordeones abiertos (Modo acordeón estricto)
      faqItems.forEach(otherItem => {
        if (otherItem !== item) {
          otherItem.classList.remove('active');
          otherItem.querySelector('.faq-content').style.maxHeight = null;
        }
      });

      // Alternar estado actual
      if (!isActive) {
        item.classList.add('active');
        content.style.maxHeight = content.scrollHeight + 'px';
      } else {
        item.classList.remove('active');
        content.style.maxHeight = null;
      }
    });
  });
}

window.evaluarFortalezaPassword = function(pwd) {
  var container = document.getElementById('password-strength-container');
  var bar = document.getElementById('pwd-meter-bar');
  var label = document.getElementById('pwd-meter-label');
  if (!container || !bar || !label) return;

  if (!pwd) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'block';
  var score = 0;
  if (pwd.length >= 8) score += 1;
  if (pwd.length >= 10) score += 1;
  if (/[A-Z]/.test(pwd)) score += 1;
  if (/[0-9]/.test(pwd)) score += 1;
  if (/[^A-Za-z0-9]/.test(pwd)) score += 1;

  if (pwd.length < 8) {
    bar.style.width = '25%';
    bar.style.background = '#ef4444';
    label.style.color = '#ef4444';
    label.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Contraseña Débil (mínimo 8 caracteres)';
  } else if (score <= 2) {
    bar.style.width = '50%';
    bar.style.background = '#f59e0b';
    label.style.color = '#f59e0b';
    label.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Contraseña Aceptable (agrega mayúsculas y números)';
  } else if (score <= 4) {
    bar.style.width = '80%';
    bar.style.background = '#10b981';
    label.style.color = '#10b981';
    label.innerHTML = '<i class="fa-solid fa-circle-check"></i> Contraseña Fuerte';
  } else {
    bar.style.width = '100%';
    bar.style.background = '#059669';
    label.style.color = '#059669';
    label.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Contraseña Muy Segura';
  }
};

// ── INTERACTIVE VIDEO CAROUSEL CONTROLLER ────────────────
window.currentVideoSlide = 0;

window.goToVideoSlide = function(idx) {
  const slides = document.getElementById('video-slides');
  const dots = document.querySelectorAll('.video-dot');
  if (!slides) return;
  currentVideoSlide = idx;
  slides.style.transform = `translateX(-${idx * 100}%)`;
  dots.forEach((d, i) => {
    if (i === idx) {
      d.style.width = '24px';
      d.style.background = '#E4C7A1';
    } else {
      d.style.width = '8px';
      d.style.background = 'rgba(255,255,255,0.4)';
    }
  });
};

window.nextVideoSlide = function() {
  currentVideoSlide = (currentVideoSlide + 1) % 3;
  window.goToVideoSlide(currentVideoSlide);
};

window.prevVideoSlide = function() {
  currentVideoSlide = (currentVideoSlide - 1 + 3) % 3;
  window.goToVideoSlide(currentVideoSlide);
};

setInterval(() => {
  const slides = document.getElementById('video-slides');
  if (slides && !slides.matches(':hover')) {
    window.nextVideoSlide();
  }
}, 6000);

// ── SYNC CORPORATE CONTACT & WHATSAPP FROM DB CONFIG ────────────────
async function syncDynamicWhatsApp() {
  try {
    const apiBase = (window.location.protocol === 'file:'
      ? 'http://localhost:3000'
      : (window.location.origin || 'http://localhost:3000')) + '/api/v1';

    let res = await fetch(apiBase + '/contacto/config/sistema').catch(() => null);
    if (!res || !res.ok) {
      res = await fetch(apiBase + '/admin/usuarios/config/sistema').catch(() => null);
    }
    if (res && res.ok) {
      const json = await res.json();
      const cfg = json.data || json;
      const rawTel = cfg.whatsapp || cfg.telefono || '305 406 1764';
      const cleanDigits = rawTel.replace(/[^0-9]/g, '');
      const waNumber = cleanDigits.startsWith('57') ? cleanDigits : ('57' + (cleanDigits.length === 10 ? cleanDigits : cleanDigits.slice(-10)));
      const waGeneralMsg = cfg.wa_template_general || 'Hola Flymetrics, deseo solicitar información y cotización sobre sus servicios de drones.';

      // Sincronizar todos los enlaces directos a WhatsApp en el documento
      document.querySelectorAll('a[href*="wa.me"]').forEach(a => {
        try {
          const url = new URL(a.href);
          const currentText = url.searchParams.get('text');
          const finalMsg = currentText && currentText.includes('Hola') ? currentText : waGeneralMsg;
          a.href = `https://wa.me/${waNumber}?text=${encodeURIComponent(finalMsg)}`;
        } catch (e) {
          a.href = `https://wa.me/${waNumber}?text=${encodeURIComponent(waGeneralMsg)}`;
        }
      });

      // Sincronizar teléfonos visibles en badges, spans y footer
      if (cfg.telefono || cfg.whatsapp) {
        const displayTel = cfg.telefono || cfg.whatsapp;
        document.querySelectorAll('[data-sync-tel]').forEach(el => {
          el.textContent = displayTel.startsWith('+') ? displayTel : `+57 ${displayTel}`;
        });
      }
      if (cfg.email) {
        document.querySelectorAll('[data-sync-email]').forEach(el => {
          el.textContent = cfg.email;
        });
      }
      if (cfg.direccion) {
        document.querySelectorAll('[data-sync-dir]').forEach(el => {
          el.textContent = cfg.direccion;
        });
      }
    }
  } catch (e) {
    console.debug('Usando datos de contacto por defecto');
  }
}

// Ejecutar sincronización de contacto en caliente inmediatamente
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    syncDynamicWhatsApp();
    setTimeout(syncDynamicWhatsApp, 400);
    setTimeout(syncDynamicWhatsApp, 1500);
  });
} else {
  syncDynamicWhatsApp();
  setTimeout(syncDynamicWhatsApp, 400);
  setTimeout(syncDynamicWhatsApp, 1500);
}

// ── SCROLL REVEAL ANIMATION SYSTEM ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const targets = document.querySelectorAll('section, .showcase-card, .card-box, .stat-card, footer');
  
  targets.forEach(el => {
    el.classList.add('reveal-on-scroll');
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
      }
    });
  }, { threshold: 0.08 });

  targets.forEach(el => observer.observe(el));
});