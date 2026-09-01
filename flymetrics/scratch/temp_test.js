
  // Update live clock
  function updateClock() {
    const el = document.getElementById('topbarTime');
    if (el) {
      const now = new Date();
      el.textContent = now.toLocaleString('es-CO', {
        weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
      });
    }
  }
  updateClock();
  setInterval(updateClock, 60000);

  // Update dashboard date
  const dashDateEl = document.getElementById('dashboardDate');
  if (dashDateEl) {
    dashDateEl.textContent = new Date().toLocaleDateString('es-CO', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // Session start time for config
  const cfgSessEl = document.getElementById('cfgSessionTime');
  if (cfgSessEl) {
    cfgSessEl.textContent = new Date().toLocaleString('es-CO');
  }

  // Update agenda badge with pending count
  async function updateBadge() {
    try {
      const agenda = await apiFetch('/agenda') || [];
      const pending = Array.isArray(agenda) ? agenda.filter(a => a.estado === 'Pendiente').length : 0;
      const badge = document.getElementById('agendaBadge');
      if (badge) badge.textContent = pending;
    } catch(e) {
      const badge = document.getElementById('agendaBadge');
      if (badge) badge.textContent = '0';
    }
  }
  setTimeout(updateBadge, 1000);
  // Sidebar toggle for mobile responsive view
  window.toggleAdminSidebar = function(e) {
    if (e) e.stopPropagation();
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('adminSidebarOverlay');
    if (sidebar) {
      const isOpen = sidebar.classList.toggle('open');
      if (overlay) {
        if (isOpen) {
          overlay.classList.remove('hidden');
          setTimeout(() => overlay.style.opacity = '1', 10);
        } else {
          overlay.style.opacity = '0';
          setTimeout(() => overlay.classList.add('hidden'), 300);
        }
      }
    }
  };

  // Close sidebar when clicking a nav item on mobile
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      if (sidebar && sidebar.classList.contains('open')) {
        toggleAdminSidebar();
      }
    });
  });
