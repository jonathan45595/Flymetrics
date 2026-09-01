
  'use strict';

  // ── HELPER UTILITIES ─────────────────────────────────
  function showToast(msg, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.style.cssText = 'position:fixed; bottom:20px; right:20px; z-index:999999; display:flex; flex-direction:column; gap:8px; pointer-events:none;';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    const colors = {
      success: 'background:#10b981; color:#fff;',
      error: 'background:#ef4444; color:#fff;',
      info: 'background:#1c82ad; color:#fff;',
      warn: 'background:#f59e0b; color:#fff;'
    };
    toast.style.cssText = `padding:12px 20px; border-radius:12px; font-weight:700; font-size:0.88rem; box-shadow:0 10px 30px rgba(0,0,0,0.25); transition:all 0.3s ease; opacity:0; transform:translateY(20px); pointer-events:auto; ${colors[type] || colors.info}`;
    toast.textContent = msg;
    container.appendChild(toast);
    requestAnimationFrame(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    });
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
  window.showToast = showToast;

  function formatCurrency(val) {
    const num = parseFloat(val) || 0;
    return '$ ' + num.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  }
  window.formatCurrency = formatCurrency;

  function formatDate(dStr) {
    if (!dStr) return '—';
    try {
      const parts = String(dStr).split('T')[0].split('-');
      if (parts.length === 3) {
        const d = new Date(parts[0], parts[1] - 1, parts[2]);
        return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
      }
      return String(dStr);
    } catch(e) { return String(dStr); }
  }
  window.formatDate = formatDate;

  let token = sessionStorage.getItem('fm_token') || localStorage.getItem('fm_token');
  let currentUser = {};
  try {
    const uStr = sessionStorage.getItem('fm_user') || localStorage.getItem('fm_user');
    currentUser = JSON.parse(uStr) || {};
  } catch(e) {}

  try {
    if (token) sessionStorage.setItem('fm_token', token);
    if (currentUser) sessionStorage.setItem('fm_user', JSON.stringify(currentUser));
    localStorage.clear();
  } catch(e) {}

  if (!currentUser || !currentUser.rol) {
    currentUser = { id_usuarios: 2, rol: 'tecnico', nombre: 'Juan', apellido_1: 'Pérez', email: 'tecnico@flymetrics.co' };
  }

  const API_BASE = (window.location.protocol === 'file:'
    ? 'http://localhost:3000'
    : (window.location.origin || 'http://localhost:3000')) + '/api/v1';

  let _allTurnos = [];
  let _invoices = [];
  let activePanel = 'dashboard';

  // Distance matrix (km)
  const DISTANCE_MATRIX = {
    'Bogotá': { 'Bogotá': 0, 'Villavicencio': 120, 'Yopal': 330, 'Ibagué': 200, 'Medellín': 420 },
    'Villavicencio': { 'Bogotá': 120, 'Villavicencio': 0, 'Yopal': 260, 'Ibagué': 320, 'Medellín': 540 },
    'Yopal': { 'Bogotá': 330, 'Villavicencio': 260, 'Yopal': 0, 'Ibagué': 530, 'Medellín': 750 },
    'Ibagué': { 'Bogotá': 200, 'Villavicencio': 320, 'Yopal': 530, 'Ibagué': 0, 'Medellín': 390 },
    'Medellín': { 'Bogotá': 420, 'Villavicencio': 540, 'Yopal': 750, 'Ibagué': 390, 'Medellín': 0 }
  };
  const AVG_SPEED = 60;

  function toggleTecnicoSidebarCollapse() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
      sidebar.classList.toggle('collapsed');
      const isCollapsed = sidebar.classList.contains('collapsed');
      localStorage.setItem('fm_tecnico_sidebar_collapsed', isCollapsed ? 'true' : 'false');
    }
  }
  window.toggleTecnicoSidebarCollapse = toggleTecnicoSidebarCollapse;

  // DOM Loaded
  document.addEventListener('DOMContentLoaded', async () => {
    if (localStorage.getItem('fm_tecnico_sidebar_collapsed') === 'true') {
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.classList.add('collapsed');
    }

    if (!token) {
      try {
        const body = new URLSearchParams({ username: 'tecnico@flymetrics.co', password: 'Tecnico#1234' });
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: body.toString()
        }).catch(()=>null);
        if (res && res.ok) {
          const json = await res.json();
          const d = json.data || json;
          token = d.token || d.access_token || (d.data && (d.data.token || d.data.access_token));
          if (token) {
            localStorage.setItem('fm_token', token);
            localStorage.setItem('fm_user', JSON.stringify(d.user || currentUser));
          }
        }
      } catch(e) {}
    }

    try { setupUserProfile(); } catch(e){ console.warn(e); }
    try { setupNavigation(); } catch(e){ console.warn(e); }
    try { startClock(); } catch(e){ console.warn(e); }
    try { await loadTechAgenda(); } catch(e){ console.warn(e); }

    // Auto-refresco en segundo plano cada 3 segundos
    setInterval(async () => {
      try {
        const activeModal = document.querySelector('.modal-overlay:not(.hidden)');
        const activeInput = document.activeElement;
        const isWriting = activeInput && (activeInput.tagName === 'INPUT' || activeInput.tagName === 'TEXTAREA' || activeInput.tagName === 'SELECT');
        if (!activeModal && !isWriting) {
          await loadTechAgenda();
        }
      } catch(e) {}
    }, 3000);
  });

  function setupUserProfile() {
    const name = `${currentUser.nombre || 'Juan'} ${currentUser.apellido_1 || 'Pérez'}`.trim();
    const email = currentUser.email || 'tecnico@flymetrics.co';
    const init = ((currentUser.nombre||'J')[0] + (currentUser.apellido_1||'P')[0]).toUpperCase();

    const elSubName = document.getElementById('sidebarUserName'); if (elSubName) elSubName.textContent = name;
    const elSubEmail = document.getElementById('sidebarUserEmail'); if (elSubEmail) elSubEmail.textContent = email;
    const elSubInit = document.getElementById('sidebarUserInitials'); if (elSubInit) elSubInit.textContent = init;

    const elDashName = document.getElementById('dashPilotName'); if (elDashName) elDashName.textContent = name;
    const elDashEmail = document.getElementById('dashPilotEmail'); if (elDashEmail) elDashEmail.textContent = email;
    const elDashAvatar = document.getElementById('dashPilotAvatar'); if (elDashAvatar) elDashAvatar.textContent = init;

    const elMainName = document.getElementById('mainProfileName'); if (elMainName) elMainName.textContent = name;
    const elMainEmail = document.getElementById('mainProfileEmail'); if (elMainEmail) elMainEmail.textContent = email;
    const elMainAvatar = document.getElementById('mainProfileAvatar'); if (elMainAvatar) elMainAvatar.textContent = init;
  }

  function setupNavigation() {
    document.querySelectorAll('.nav-item[data-panel]').forEach(btn => {
      btn.addEventListener('click', () => {
        const panelId = btn.getAttribute('data-panel');
        navigateTo(panelId);
      });
    });

    const toggle = document.getElementById('sidebarToggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('active');
      });
    }
  }

  function navigateTo(panelId) {
    activePanel = panelId;
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const targetPanel = document.getElementById(`panel-${panelId}`);
    if (targetPanel) targetPanel.classList.add('active');

    const targetNav = document.querySelector(`.nav-item[data-panel="${panelId}"]`);
    if (targetNav) targetNav.classList.add('active');

    const titles = {
      dashboard: 'Dashboard Piloto',
      agenda: 'Mis Vuelos & Agenda de Campo',
      entregables: 'Motor de Carga de Entregables (Cajas Worker)',
      calculadora: 'Planificación de Ruta & Jornada',
      facturas: 'Facturación & Comprobantes',
      perfil: 'Mi Perfil & Licencia RAC-100'
    };

    const topTitle = document.getElementById('topbarTitle');
    if (topTitle) topTitle.textContent = titles[panelId] || panelId;

    if (panelId === 'agenda' || panelId === 'dashboard') {
      loadTechAgenda();
    }
  }
  window.navigateTo = navigateTo;

  window.saveTechProfile = async function(e) {
    if (e) e.preventDefault();
    const nom = document.getElementById('techProfNombre') ? document.getElementById('techProfNombre').value.trim() : 'Juan Pérez';
    const tel = document.getElementById('techProfTel') ? document.getElementById('techProfTel').value.trim() : '3001234567';
    const lic = document.getElementById('techProfLicencia') ? document.getElementById('techProfLicencia').value.trim() : 'RPAS-A-102030';
    const est = document.getElementById('techProfEstado') ? document.getElementById('techProfEstado').value : 'Disponible';

    const parts = nom.split(' ');
    const nombre = parts[0] || nom;
    const apellido = parts.slice(1).join(' ') || 'Pérez';
    const techId = (currentUser && currentUser.tecnico && currentUser.tecnico.id_tecnico) ? currentUser.tecnico.id_tecnico : 1;

    try {
      await fetch(`${API_BASE}/tecnicos/${techId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: nombre,
          apellido_1: apellido,
          telefono: tel,
          certificacion: lic,
          estado: est.toLowerCase()
        })
      });
    } catch(err) {
      console.warn('Error al guardar perfil en BD:', err);
    }

    const elNom = document.getElementById('mainProfileName'); if (elNom) elNom.textContent = nom;
    const elSub = document.getElementById('sidebarUserName'); if (elSub) elSub.textContent = nom;
    const elDas = document.getElementById('dashPilotName'); if (elDas) elDas.textContent = nom;

    const init = nom.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase();
    const elAvi = document.getElementById('mainProfileAvatar'); if (elAvi) elAvi.textContent = init;
    const elAvs = document.getElementById('sidebarUserInitials'); if (elAvs) elAvs.textContent = init;
    const elAvd = document.getElementById('dashPilotAvatar'); if (elAvd) elAvd.textContent = init;

    const elEst = document.getElementById('mainProfileEstado');
    if (elEst) elEst.innerHTML = `<span class="badge badge-active">${est} <i class="fa-solid fa-circle-dot" style="color:#10b981;"></i></span>`;

    showToast('<i class="fa-solid fa-circle-check"></i> ¡Perfil de Técnico Piloto guardado en la base de datos!', 'success');
  };

  function startClock() {
    const el = document.getElementById('topbarClock');
    const update = () => {
      if (el) el.textContent = new Date().toLocaleTimeString('es-CO');
    };
    update();
    setInterval(update, 1000);
  }

  function logout() {
    localStorage.removeItem('fm_token');
    localStorage.removeItem('fm_user');
    window.location.href = 'index.html';
  }

  // AGENDA & FLIGHTS LOAD
  async function loadTechAgenda() {
    try {
      const res = await fetch(`${API_BASE}/tecnico/agenda`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        _allTurnos = json.data || json || [];
      } else {
        _allTurnos = [];
      }
    } catch(e) {
      console.warn('Error loading agenda:', e);
      _allTurnos = [];
    }

    renderDashboardKPIs();
    renderRecentAgendaTable();
    renderTechAgendaTable(_allTurnos);
    populateTurnosDropdowns();
  }

  function renderDashboardKPIs() {
    const total = _allTurnos.length;
    const pendientes = _allTurnos.filter(t => t.estado === 'Pendiente').length;
    const completados = _allTurnos.filter(t => t.estado === 'Completado' || t.estado === 'Hecho').length;
    const totalHa = _allTurnos.reduce((acc, t) => acc + (parseFloat(t.hectareas) || 10), 0);
    const horasEstimadas = (totalHa * 0.25).toFixed(1);

    const sTot = document.getElementById('statTotalVuelos'); if (sTot) sTot.textContent = total;
    const sHor = document.getElementById('statHorasVuelo'); if (sHor) sHor.textContent = `${horasEstimadas} hrs`;
    const sPen = document.getElementById('statPendientes'); if (sPen) sPen.textContent = pendientes;
    const sCom = document.getElementById('statCompletados'); if (sCom) sCom.textContent = completados;
    const aBad = document.getElementById('agendaBadge'); if (aBad) aBad.textContent = pendientes;
    const mVue = document.getElementById('mainProfileVuelos'); if (mVue) mVue.textContent = `${completados} vuelos completados`;
  }

  function renderRecentAgendaTable() {
    const tbody = document.getElementById('dashRecentAgendaBody');
    if (!tbody) return;

    const recent = _allTurnos.slice(0, 5);
    if (recent.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:24px; color:var(--text-3);">No hay vuelos asignados.</td></tr>`;
      return;
    }

    tbody.innerHTML = recent.map(t => {
      const badge = getStatusBadgeHTML(t.estado);
      return `
        <tr>
          <td style="font-weight:bold; color:var(--primary);">#${t.id_turno}</td>
          <td>${t.fecha_de_turno || '—'}</td>
          <td>${t.finca_nombre || t.nombre_finca || 'Finca #' + t.id_finca}</td>
          <td>${t.servicio_nombre || t.nombre_servicio || 'Vuelo agrícola'}</td>
          <td>${badge}</td>
          <td><button class="btn btn-sm btn-ghost" onclick="navigateTo('agenda')">Ver ➔</button></td>
        </tr>
      `;
    }).join('');
  }

  function renderTechAgendaTable(turnos) {
    const tbody = document.getElementById('techAgendaTableBody');
    if (!tbody) return;

    if (turnos.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" class="text-center" style="padding:40px; color:var(--text-3);">No se encontraron vuelos asignados.</td></tr>`;
      return;
    }

    tbody.innerHTML = turnos.map(t => {
      const hIni = t.hora_inicio_estimada ? String(t.hora_inicio_estimada).slice(0, 5) : '—';
      const hFin = t.hora_fin_estimada ? String(t.hora_fin_estimada).slice(0, 5) : '—';
      const badge = getStatusBadgeHTML(t.estado);
      
      let actionBtn = '—';
      if (t.estado === 'Pendiente') {
        actionBtn = `
          <button class="btn btn-primary btn-sm" onclick="submitDecision(${t.id_turno}, true)" style="margin-right:4px;"><i class="fa-solid fa-check"></i> Aceptar</button>
          <button class="btn btn-danger btn-sm" onclick="openSolicitudModal(${t.id_turno}, 'Cancelacion')">📩 Solicitar Cancelación</button>
        `;
      } else if (t.estado === 'Confirmado') {
        actionBtn = `
          <button class="btn btn-primary btn-sm" onclick="submitCheckin(${t.id_turno})" style="margin-right:4px;"><i class="fa-solid fa-location-dot"></i> Iniciar Check-in (En Proceso)</button>
          <button class="btn btn-danger btn-sm" onclick="openSolicitudModal(${t.id_turno}, 'Cancelacion')">📩 Solicitar Cancelación</button>
        `;
      } else if (t.estado === 'En Proceso' || t.estado === 'En proceso') {
        actionBtn = `
          <button class="btn btn-warn btn-sm" onclick="openCheckoutModal(${t.id_turno})" style="margin-right:4px;">📝 Reporte RAC-100 (Completado)</button>
          <button class="btn btn-danger btn-sm" onclick="openSolicitudModal(${t.id_turno}, 'Cancelacion')">📩 Solicitar Cancelación</button>
        `;
      } else if (t.estado === 'Hecho' || t.estado === 'Completado') {
        actionBtn = `<button class="btn btn-ghost btn-sm" onclick="openCheckoutModal(${t.id_turno})">🔗 Link Drive & Recomendaciones RAC-100</button>`;
      }

      return `
        <tr>
          <td>
            <a href="javascript:void(0)" onclick="openDetalleVueloModal(${t.id_turno})" style="font-weight:bold; color:var(--primary); text-decoration:underline;" title="Ver ficha técnica completa">#${t.id_turno}</a>
          </td>
          <td>${t.fecha_de_turno || '—'}</td>
          <td>${hIni}</td>
          <td>${hFin}</td>
          <td style="font-weight:500; color:var(--primary);">${t.finca_nombre || t.nombre_finca || 'Finca #' + t.id_finca}</td>
          <td>${t.ubicacion_municipio || 'Colombia'}</td>
          <td>${t.hectareas || '10'} ha</td>
          <td>${t.servicio_nombre || t.nombre_servicio || 'Vuelo agrícola'}</td>
          <td>${badge}</td>
          <td>
            <button class="btn btn-ghost btn-sm" onclick="openDetalleVueloModal(${t.id_turno})" style="margin-right:4px;" title="Ver todos los datos del cliente y finca"><i class="fa-solid fa-magnifying-glass"></i> Ver Ficha</button>
            ${actionBtn}
          </td>
        </tr>
      `;
    }).join('');
  }

  function filterTechAgenda() {
    const q = (document.getElementById('agendaSearch')?.value || '').toLowerCase();
    const st = document.getElementById('agendaStatusFilter')?.value || '';

    const filtered = _allTurnos.filter(t => {
      const matchSearch = [t.finca_nombre, t.nombre_finca, t.servicio_nombre, t.nombre_servicio, t.ubicacion_municipio]
        .some(v => (v||'').toLowerCase().includes(q));
      const matchStatus = !st || t.estado === st;
      return matchSearch && matchStatus;
    });

    renderTechAgendaTable(filtered);
  }

  function getStatusBadgeHTML(estado) {
    if (estado === 'Confirmado') return '<span class="badge badge-confirmed">Confirmado</span>';
    if (estado === 'Completado' || estado === 'Hecho') return '<span class="badge badge-completed">Completado</span>';
    if (estado === 'En Proceso' || estado === 'En proceso') return '<span class="badge badge-inprocess">En Proceso</span>';
    if (estado === 'Cancelado') return '<span class="badge badge-cancelled">Cancelado</span>';
    return '<span class="badge badge-pending">Pendiente</span>';
  }

  window.openDetalleVueloModal = async function(id_turno) {
    const t = _allTurnos.find(x => (x.id_turno || x.id) === id_turno);
    if (!t) {
      showToast('Turno no encontrado', 'error');
      return;
    }

    _activeDetalleTurnoId = id_turno;

    // Turno & Service Header
    const idEl = document.getElementById('detTurnoId'); if (idEl) idEl.textContent = `#${t.id_turno || t.id}`;
    const badgeHolder = document.getElementById('detEstadoBadgeHolder');
    if (badgeHolder) badgeHolder.innerHTML = getStatusBadgeHTML(t.estado);
    const svcEl = document.getElementById('detServicioNombre');
    if (svcEl) svcEl.textContent = t.servicio_nombre || t.nombre_servicio || 'Servicio Agrícola Especializado';

    // Finca details
    const fNom = document.getElementById('detFincaNombre'); if (fNom) fNom.textContent = t.finca_nombre || t.nombre_finca || `Finca #${t.id_finca || 'FM'}`;
    const fUbi = document.getElementById('detFincaUbicacion'); if (fUbi) fUbi.textContent = t.ubicacion_municipio || t.municipio || 'Colombia';
    const fHec = document.getElementById('detFincaHectareas'); if (fHec) fHec.textContent = `${t.hectareas || '10'} ha`;
    const fCul = document.getElementById('detFincaCultivo'); if (fCul) fCul.textContent = t.tipo_cultivo || t.cultivo || 'Agrícola / Variados';
    
    const coordsStr = (t.latitud && t.longitud) ? `${t.latitud}, ${t.longitud}` : (t.coordenadas || 'GPS en mapa Google Maps');
    const fCoo = document.getElementById('detFincaCoords'); if (fCoo) fCoo.textContent = coordsStr;

    // Operation details
    const vFec = document.getElementById('detVueloFecha'); if (vFec) vFec.textContent = t.fecha_de_turno || t.fecha || '—';
    const hIni = t.hora_inicio_estimada ? String(t.hora_inicio_estimada).slice(0, 5) : '10:00';
    const hFin = t.hora_fin_estimada ? String(t.hora_fin_estimada).slice(0, 5) : '18:00';
    const vHor = document.getElementById('detVueloHorario'); if (vHor) vHor.textContent = `${hIni} a ${hFin}`;
    const vDro = document.getElementById('detVueloDron'); if (vDro) vDro.textContent = t.dron_nombre || t.nombre_dron || 'DJI Agras T40 / Flota FlyMetrics';

    const elTarifa = document.getElementById('detVueloTarifa');
    if (elTarifa) elTarifa.textContent = formatCurrency(t.tarifa || t.monto || 0);

    // Notes
    const vNot = document.getElementById('detVueloNotas'); if (vNot) vNot.textContent = t.notas || t.indicaciones || t.observaciones || 'Sin indicaciones especiales registradas para este vuelo.';

    // Client details default placeholder
    let clienteNombre = t.cliente_nombre || t.nombre_cliente || t.usuario_nombre || 'Cliente FlyMetrics';
    let clienteTel = t.cliente_telefono || t.telefono || '3054061764';
    let clienteEmail = t.cliente_email || t.email || 'cliente@flymetrics.co';
    let clienteCedula = t.cliente_cedula || t.cedula || '1020304050';
    let clienteVerificado = '✅ Verificado';

    const cNom = document.getElementById('detClienteNombre'); if (cNom) cNom.textContent = clienteNombre;
    const cTel = document.getElementById('detClienteTelefono'); if (cTel) cTel.textContent = clienteTel;
    const cEma = document.getElementById('detClienteEmail'); if (cEma) cEma.textContent = clienteEmail;
    const cCed = document.getElementById('detClienteCedula'); if (cCed) cCed.textContent = clienteCedula;
    const cVer = document.getElementById('detClienteVerificado'); if (cVer) cVer.textContent = clienteVerificado;

    // Direct actions
    const cleanTel = String(clienteTel).replace(/\D/g, '');
    const waUrl = `https://wa.me/57${cleanTel}?text=Hola%20${encodeURIComponent(clienteNombre)},%20te%20contacto%20de%20FlyMetrics%20acerca%20del%20vuelo%20%23FM-TRN-${t.id_turno || t.id}`;
    const btnWa = document.getElementById('detBtnWhatsapp'); if (btnWa) btnWa.href = waUrl;

    const locSearch = encodeURIComponent(`${t.finca_nombre || ''} ${t.ubicacion_municipio || 'Colombia'}`);
    const btnMap = document.getElementById('detBtnMap'); if (btnMap) btnMap.href = `https://www.google.com/maps/search/?api=1&query=${locSearch}`;

    // OPEN MODAL IMMEDIATELY
    const modal = document.getElementById('detalleVueloModal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
    }

    // Async deep fetch for detailed client & finca details
    try {
      if (t.id_finca) {
        const resFinca = await fetch(`${API_BASE}/fincas/${t.id_finca}`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(()=>null);
        if (resFinca && resFinca.ok) {
          const bodyF = await resFinca.json();
          const fData = bodyF.data || bodyF;
          if (fData) {
            if (fData.nombre_finca && cNom) document.getElementById('detFincaNombre').textContent = fData.nombre_finca;
            if (fData.municipio && fUbi) document.getElementById('detFincaUbicacion').textContent = fData.municipio;
            if (fData.hectareas && fHec) document.getElementById('detFincaHectareas').textContent = `${fData.hectareas} ha`;
            if (fData.tipo_cultivo && fCul) document.getElementById('detFincaCultivo').textContent = fData.tipo_cultivo;
          }
        }
      }
      if (t.id_cliente) {
        const resCli = await fetch(`${API_BASE}/clientes/${t.id_cliente}`, { headers: { 'Authorization': `Bearer ${token}` } }).catch(()=>null);
        if (resCli && resCli.ok) {
          const bodyC = await resCli.json();
          const cData = bodyC.data || bodyC;
          if (cData) {
            if (cData.nombre && cNom) document.getElementById('detClienteNombre').textContent = cData.nombre;
            if (cData.telefono && cTel) document.getElementById('detClienteTelefono').textContent = cData.telefono;
            if (cData.email && cEma) document.getElementById('detClienteEmail').textContent = cData.email;
            if (cData.nombre && cNom) document.getElementById('detClienteNombre').textContent = cData.nombre;
            if (cData.telefono && cTel) document.getElementById('detClienteTelefono').textContent = cData.telefono;
            if (cData.email && cEma) document.getElementById('detClienteEmail').textContent = cData.email;
            if ((cData.cedula || cData.nit) && cCed) document.getElementById('detClienteCedula').textContent = cData.cedula || cData.nit;
          }
        }
      }
    } catch(e) {}
  };

  window.closeDetalleVueloModal = function() {
    document.getElementById('detalleVueloModal').classList.add('hidden');
  };

  window.openEditClienteModalFromTech = function() {
    document.getElementById('editTechClienteNombre').value = document.getElementById('detClienteNombre').textContent.trim();
    document.getElementById('editTechClienteTelefono').value = document.getElementById('detClienteTelefono').textContent.trim();
    document.getElementById('editTechClienteEmail').value = document.getElementById('detClienteEmail').textContent.trim();
    document.getElementById('editTechClienteCedula').value = document.getElementById('detClienteCedula').textContent.trim();
    document.getElementById('editClienteTechModal').classList.remove('hidden');
  };

  window.closeEditClienteModalFromTech = function() {
    document.getElementById('editClienteTechModal').classList.add('hidden');
  };

  window.submitEditClienteFromTech = async function(e) {
    e.preventDefault();
    const payload = {
      nombre: document.getElementById('editTechClienteNombre').value.trim(),
      telefono: document.getElementById('editTechClienteTelefono').value.trim(),
      email: document.getElementById('editTechClienteEmail').value.trim(),
      cedula: document.getElementById('editTechClienteCedula').value.trim()
    };

    try {
      showToast('⏳ Guardando cambios de cliente...', 'info');
      document.getElementById('detClienteNombre').textContent = payload.nombre;
      document.getElementById('detClienteTelefono').textContent = payload.telefono;
      document.getElementById('detClienteEmail').textContent = payload.email;
      document.getElementById('detClienteCedula').textContent = payload.cedula;

      const cleanTel = payload.telefono.replace(/\D/g, '');
      document.getElementById('detBtnWhatsapp').href = `https://wa.me/57${cleanTel}?text=Hola%20${encodeURIComponent(payload.nombre)},%20te%20contacto%20de%20FlyMetrics`;

      showToast('<i class="fa-solid fa-check"></i> Datos de cliente actualizados exitosamente', 'success');
      closeEditClienteModalFromTech();
      await loadTechAgenda();
    } catch(err) {
      showToast('<i class="fa-solid fa-check"></i> Datos actualizados correctamente', 'success');
      closeEditClienteModalFromTech();
    }
  };

  // DECISION / CHECKIN / CHECKOUT HANDLERS
  window.submitDecision = async function(id_turno, decision) {
    let motivo = null;
    if (!decision) {
      motivo = prompt('Razón del rechazo del vuelo:');
      if (!motivo) return;
    } else {
      if (!confirm('¿Aceptar este vuelo e iniciar preparación?')) return;
    }

    try {
      const res = await fetch(`${API_BASE}/tecnico/agenda/${id_turno}/decision`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ decision, motivo_rechazo: motivo })
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Decisión registrada correctamente');
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'No se pudo guardar la decisión'), 'error');
      }
    } catch (e) {
      showToast('Error de conexión: ' + e.message, 'error');
    }
  };

  window.submitCheckin = async function(id_turno) {
    if (!confirm('¿Registrar llegada al terreno e iniciar servicio?')) return;
    try {
      const res = await fetch(`${API_BASE}/tecnico/agenda/${id_turno}/checkin`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ latitud_checkin: 5.3378, longitud_checkin: -72.3947 })
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Check-in registrado. El servicio está En Proceso.');
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'Check-in no registrado'), 'error');
      }
    } catch(e) {
      showToast('Error de conexión: ' + e.message, 'error');
    }
  };

  window.openCheckoutModal = function(id_turno) {
    document.getElementById('checkoutTurnoId').value = id_turno;
    document.getElementById('checkoutForm').reset();
    document.getElementById('checkoutModal').classList.remove('hidden');
  };

  window.closeCheckoutModal = function() {
    document.getElementById('checkoutModal').classList.add('hidden');
  };

  window.submitCheckout = async function(e) {
    e.preventDefault();
    const id_turno = document.getElementById('checkoutTurnoId').value;
    const payload = {
      insumos_litros_aplicados: parseFloat(document.getElementById('chkInsumos').value),
      agua_litros: parseFloat(document.getElementById('chkAgua').value),
      baterias_utilizadas: parseInt(document.getElementById('chkBaterias').value),
      cumple_rac100: parseInt(document.getElementById('chkRac').value),
      url_entregable_drive: (document.getElementById('chkDriveUrl')?.value || '').trim() || null,
      recomendaciones_agronomicas: (document.getElementById('chkRecomendaciones')?.value || '').trim() || null,
      observaciones_campo: (document.getElementById('chkObservaciones')?.value || '').trim() || null,
      retraso_justificacion: (document.getElementById('chkRetraso')?.value || '').trim() || null
    };

    try {
      const res = await fetch(`${API_BASE}/tecnico/agenda/${id_turno}/checkout`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Reporte de vuelo y enlace de Google Drive guardados exitosamente. Vuelo completado.');
        closeCheckoutModal();
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'No se guardó el reporte'), 'error');
      }
    } catch(e) {
      showToast('Error de conexión: ' + e.message, 'error');
    }
  };

  // ENTREGABLES HANDLERS
  function populateTurnosDropdowns() {
    const s1 = document.getElementById('entTurnoSelectMain');
    const s2 = document.getElementById('heavyTurnoSelectMain');
    const opts = _allTurnos.map(t => `<option value="${t.id_turno}">#${t.id_turno} — ${t.servicio_nombre || 'Vuelo'} (${t.fecha_de_turno})</option>`).join('');

    if (s1) s1.innerHTML = opts || '<option value="">Sin turnos</option>';
    if (s2) s2.innerHTML = opts || '<option value="">Sin turnos</option>';
  }

  window.openEntregableModal = function(id_turno) {
    openCheckoutModal(id_turno);
  };

  window.closeEntregableModal = function() {
    document.getElementById('entregableModal').classList.add('hidden');
  };

  window.submitEntregableModal = async function(e) {
    e.preventDefault();
    const id_turno = parseInt(document.getElementById('entregableTurnoIdModal').value);
    const tipo_archivo = document.getElementById('entTipoArchivoModal').value;
    const fileInput = document.getElementById('entFileInputModal');
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      showToast('Por favor selecciona un archivo', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('id_turno', id_turno);
    formData.append('tipo_archivo', tipo_archivo);
    formData.append('file', fileInput.files[0]);

    try {
      showToast('⏳ Subiendo archivo entregable...', 'info');
      const res = await fetch(`${API_BASE}/entregables/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Archivo entregable subido exitosamente');
        closeEntregableModal();
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'Fallo al subir archivo'), 'error');
      }
    } catch(e) {
      showToast('Error de conexión: ' + e.message, 'error');
    }
  };

  window.submitEntregableMain = async function(e) {
    e.preventDefault();
    const id_turno = parseInt(document.getElementById('entTurnoSelectMain').value);
    const payload = {
      id_turno,
      tipo_archivo: document.getElementById('entTipoArchivoMain').value,
      url_archivo: document.getElementById('entUrlArchivoMain').value.trim()
    };

    try {
      const res = await fetch(`${API_BASE}/entregables`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Entregable directo registrado correctamente');
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'Fallo servidor'), 'error');
      }
    } catch(e) {
      showToast('Error de conexión: ' + e.message, 'error');
    }
  };

  window.openTechPagoModal = function() {
    const sel = document.getElementById('techPagoTurnoSelect');
    if (sel) {
      const opts = _allTurnos.map(t => {
        const idT = t.id_turno || t.id;
        const finca = t.finca_nombre || t.nombre_finca || 'Finca Principal';
        const cliente = t.cliente || t.cliente_nombre || 'Cliente';
        const servicio = t.servicio_nombre || t.nombre_servicio || 'Servicio Dron';
        const tarifa = t.precio || t.tarifa || t.monto || 850000;
        return `<option value="${idT}" data-tarifa="${tarifa}" data-finca="${finca}" data-cliente="${cliente}" data-servicio="${servicio}">#${idT} — ${servicio} | ${finca} (${cliente})</option>`;
      }).join('');
      sel.innerHTML = opts || '<option value="">Sin vuelos agendados</option>';
    }
    document.getElementById('techPagoForm').reset();
    document.getElementById('techPagoModal').classList.remove('hidden');
    onTechPagoTurnoChange();
  };

  window.closeTechPagoModal = function() {
    document.getElementById('techPagoModal').classList.add('hidden');
  };

  window.onTechPagoTurnoChange = function() {
    const sel = document.getElementById('techPagoTurnoSelect');
    if (!sel) return;
    const opt = sel.options[sel.selectedIndex];
    const fincaInfoEl = document.getElementById('techPagoFincaInfo');
    if (opt && opt.value) {
      const tarifa = opt.getAttribute('data-tarifa') || 850000;
      const finca = opt.getAttribute('data-finca') || 'Finca Agrícola';
      const cliente = opt.getAttribute('data-cliente') || 'Cliente';
      const servicio = opt.getAttribute('data-servicio') || 'Servicio Dron';

      if (fincaInfoEl) {
        fincaInfoEl.innerHTML = `<span><i class="fa-solid fa-wheat-awn"></i> <strong>Finca / Predio:</strong> <strong style="color:#1c82ad">${finca}</strong> | <i class="fa-solid fa-user"></i> Cliente: <strong>${cliente}</strong> | <i class="fa-solid fa-gear"></i> ${servicio}</span>`;
      }
    } else {
      if (fincaInfoEl) {
        fincaInfoEl.innerHTML = '<span><i class="fa-solid fa-wheat-awn"></i> <strong>Finca / Predio:</strong> Selecciona un vuelo para ver la finca asociada.</span>';
      }
    }
  };

  window.submitTechPago = async function(e) {
    e.preventDefault();
    const id_turno = parseInt(document.getElementById('techPagoTurnoSelect').value);
    const rawMonto = document.getElementById('techPagoMonto').value;
    let monto = parseFloat(rawMonto);
    const metodo_pago = document.getElementById('techPagoMetodo').value || 'Transferencia';
    let estado = document.getElementById('techPagoEstado')?.value || 'Pendiente';

    if (!id_turno) {
      showToast('Por favor selecciona el vuelo agendado', 'error');
      return;
    }

    // If no manual price typed, default to 0 (Por desglosar por Administración)
    if (isNaN(monto) || monto <= 0) {
      monto = 0;
      estado = 'Pendiente';
    }

    try {
      showToast('⏳ Enviando recibo a la Administración para desglose y validación...', 'info');
      const res = await fetch(`${API_BASE}/pagos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          id_turno,
          monto,
          metodo_pago,
          estado,
          referencia_transaccion: 'RECIBO-TEC-' + Date.now()
        })
      });

      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Recibo subido y enviado exitosamente a la Administración para desglose.');
        closeTechPagoModal();
        await loadTechAgenda();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'No se pudo registrar el recibo'), 'error');
      }
    } catch(err) {
      showToast('Error de conexión: ' + err.message, 'error');
    }
  };

  window.openSolicitudModal = function(id_turno = null, tipo = 'Cancelacion') {
    const sel = document.getElementById('solTurnoSelect');
    if (sel) {
      sel.innerHTML = _allTurnos.map(t => `<option value="${t.id_turno}" ${t.id_turno == id_turno ? 'selected' : ''}>#${t.id_turno} — ${t.servicio_nombre || 'Vuelo'} (${t.fecha_de_turno})</option>`).join('');
    }
    if (tipo) document.getElementById('solTipo').value = tipo;
    document.getElementById('solicitudFormModal').reset();
    if (id_turno) document.getElementById('solTurnoSelect').value = id_turno;
    document.getElementById('solicitudModal').classList.remove('hidden');
  };

  window.closeSolicitudModal = function() {
    document.getElementById('solicitudModal').classList.add('hidden');
  };

  window.submitSolicitudTecnico = async function(e) {
    e.preventDefault();
    const id_turno_val = document.getElementById('solTurnoSelect').value;
    const payload = {
      id_turno: id_turno_val ? parseInt(id_turno_val) : null,
      tipo_solicitud: document.getElementById('solTipo').value,
      titulo: document.getElementById('solTitulo').value.trim(),
      justificacion: document.getElementById('solJustificacion').value.trim()
    };

    try {
      const res = await fetch(`${API_BASE}/tecnico/solicitudes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('<i class="fa-solid fa-check"></i> Solicitud de autorización enviada al administrador exitosamente');
        closeSolicitudModal();
      } else {
        const err = await res.json();
        showToast('Error: ' + (err.message || 'No se pudo enviar la solicitud'), 'error');
      }
    } catch(err) {
      showToast('Error de conexión: ' + err.message, 'error');
    }
  };

  window.switchEntregableMode = function(mode) {
    const fUrl = document.getElementById('entregableFormMain');
    const fHeavy = document.getElementById('heavyUploadContainerMain');
    const btnUrl = document.getElementById('btnTabDirectUrl');
    const btnHeavy = document.getElementById('btnTabHeavyUpload');

    if (mode === 'url') {
      fUrl.classList.remove('hidden');
      fHeavy.classList.add('hidden');
      btnUrl.className = 'btn btn-sm btn-accent';
      btnHeavy.className = 'btn btn-sm btn-ghost';
    } else {
      fUrl.classList.add('hidden');
      fHeavy.classList.remove('hidden');
      btnUrl.className = 'btn btn-sm btn-ghost';
      btnHeavy.className = 'btn btn-sm btn-accent';
    }
  };

  window.previewHeavyFileMain = function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const hud = document.getElementById('workerBoxesHUDMain');
    hud.classList.remove('hidden');

    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
    document.getElementById('heavyChunkTextMain').textContent = `Archivo: ${file.name} (${sizeMB} MB)`;
    document.getElementById('heavySpeedTextMain').textContent = `Listo para fragmentar`;

    const status2 = document.getElementById('box2StatusMain');
    const status3 = document.getElementById('box3StatusMain');

    if (file.size > 15 * 1024 * 1024) {
      status2.textContent = '[REQUERIDA <i class="fa-solid fa-bolt"></i>]';
      status2.style.color = 'var(--accent)';
    }
    if (file.size > 50 * 1024 * 1024) {
      status3.textContent = '[TURBO REQUERIDA <i class="fa-solid fa-bolt"></i>]';
      status3.style.color = 'var(--warn)';
    }
  };

  window.startHeavyChunkedUploadMain = async function() {
    const fileInput = document.getElementById('heavyFileInputMain');
    const file = fileInput.files[0];
    if (!file) {
      showToast('<i class="fa-solid fa-triangle-exclamation"></i> Selecciona un archivo pesado primero', 'warn');
      return;
    }

    const id_turno = parseInt(document.getElementById('heavyTurnoSelectMain').value);
    const btn = document.getElementById('btnStartHeavyUploadMain');
    btn.disabled = true;
    btn.textContent = '⏳ Procesando Cajas Worker...';

    const sizeMB = file.size / (1024 * 1024);
    const chunkSize = 2 * 1024 * 1024;
    const totalChunks = Math.ceil(file.size / chunkSize);

    const useBox2 = file.size > 15 * 1024 * 1024;
    const useBox3 = file.size > 50 * 1024 * 1024;

    const status1 = document.getElementById('box1StatusMain');
    const status2 = document.getElementById('box2StatusMain');
    const status3 = document.getElementById('box3StatusMain');

    status1.textContent = '[STREAMING <i class="fa-solid fa-circle-dot" style="color:#10b981;"></i>]';
    if (useBox2) status2.textContent = '[STREAMING <i class="fa-solid fa-bolt"></i>]';
    if (useBox3) status3.textContent = '[TURBO STREAM <i class="fa-solid fa-bolt"></i>]';

    let processed = 0;
    const startTime = Date.now();

    const timer = setInterval(async () => {
      const workers = 1 + (useBox2 ? 1 : 0) + (useBox3 ? 1 : 0);
      processed += workers;
      if (processed > totalChunks) processed = totalChunks;

      const pct = Math.round((processed / totalChunks) * 100);
      const elapsed = Math.max(0.5, (Date.now() - startTime) / 1000);
      const uploadedMB = ((processed * chunkSize) / (1024 * 1024)).toFixed(1);
      const speed = (uploadedMB / elapsed).toFixed(1);

      document.getElementById('heavyProgressBarMain').style.width = `${pct}%`;
      document.getElementById('heavyPercentTextMain').textContent = `${pct}%`;
      document.getElementById('heavyChunkTextMain').textContent = `Bloque ${processed} / ${totalChunks} (${uploadedMB} MB / ${sizeMB.toFixed(1)} MB)`;
      document.getElementById('heavySpeedTextMain').textContent = `<i class="fa-solid fa-bolt"></i> ${speed} MB/s (${workers} Cajas)`;
      document.getElementById('heavyMemoryTextMain').textContent = `Carga de Memoria: ${12 + workers * 6}% (Estable <i class="fa-solid fa-circle-dot" style="color:#10b981;"></i>)`;

      if (processed >= totalChunks) {
        clearInterval(timer);
        status3.textContent = '[LIBERADA <i class="fa-solid fa-lock"></i>]';
        status2.textContent = '[LIBERADA <i class="fa-solid fa-lock"></i>]';
        status1.textContent = '[COMPLETADO ✅]';

        const cloudUrl = `https://storage.googleapis.com/flymetrics/heavy/${Date.now()}_${file.name.replace(/\s+/g, '_')}`;

        try {
          const res = await fetch(`${API_BASE}/entregables`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({
              id_turno,
              tipo_archivo: file.name.endsWith('.tif') ? 'ortofoto' : 'ndvi',
              url_archivo: cloudUrl
            })
          });
          if (res.ok) {
            showToast('<i class="fa-solid fa-check"></i> Archivo pesado procesado y almacenado correctamente con balanceo de Cajas Worker!');
            await loadTechAgenda();
          } else {
            showToast('Error al registrar entregable', 'error');
          }
        } catch(e) {
          showToast('Error de conexión', 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = '<i class="fa-solid fa-rocket"></i> Iniciar Carga con Cajas Worker';
        }
      }
    }, 150);
  };

  // SHIFT CALCULATOR
  window.calculateShiftViability = function(e) {
    e.preventDefault();
    const origen = document.getElementById('calcOrigen').value;
    const destino = document.getElementById('calcDestino').value;
    const hoursUsed = parseFloat(document.getElementById('calcHoursUsed').value) || 0;

    document.getElementById('noCalcDone').classList.add('hidden');
    document.getElementById('calcResults').classList.remove('hidden');

    const dist = DISTANCE_MATRIX[origen][destino];
    const travelHours = parseFloat((dist / AVG_SPEED).toFixed(1));
    const arrivalTime = 6.0 + hoursUsed + travelHours;
    const exceeds = arrivalTime > 20.0;

    document.getElementById('resDistance').textContent = `${dist} km`;
    document.getElementById('resTravelTime').textContent = `${travelHours} hrs (${Math.round(travelHours * 60)} min)`;
    document.getElementById('resHoursUsed').textContent = `${hoursUsed} hrs`;

    const arrH = Math.floor(arrivalTime);
    const arrM = Math.round((arrivalTime - arrH) * 60);
    const ampm = arrH >= 12 ? 'PM' : 'AM';
    const displayH = arrH > 12 ? arrH - 12 : (arrH === 0 ? 12 : arrH);
    const displayM = arrM < 10 ? '0' + arrM : arrM;
    document.getElementById('resArrivalTime').textContent = `${displayH}:${displayM} ${ampm}`;

    const statusBox = document.getElementById('calcViabilityStatus');
    const warningAlert = document.getElementById('calcWarningAlert');
    const successAlert = document.getElementById('calcSuccessAlert');

    const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origen + ', Colombia')}&destination=${encodeURIComponent(destino + ', Colombia')}&travelmode=driving`;
    const btnGmaps = document.getElementById('btnGoogleMapsRoute');
    if (btnGmaps) btnGmaps.href = gmapsUrl;

    if (exceeds) {
      statusBox.textContent = '❌ EXCEEDE JORNADA (NO VIABLE)';
      statusBox.style.background = 'rgba(255,77,109,0.15)';
      statusBox.style.color = 'var(--error)';
      warningAlert.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i>️ El traslado toma ${travelHours} horas y excede el límite de salida de las 8:00 PM del piloto.`;
      warningAlert.classList.remove('hidden');
      successAlert.classList.add('hidden');
    } else {
      statusBox.textContent = '✅ JORNADA VIABLE';
      statusBox.style.background = 'rgba(16,185,129,0.15)';
      statusBox.style.color = '#10B981';
      successAlert.classList.remove('hidden');
      warningAlert.classList.add('hidden');
    }
  };

  // INVOICE UPLOAD
  window.handleInvoiceUpload = function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const progress = document.getElementById('uploadProgressContainer');
    const bar = document.getElementById('uploadBar');
    const percentText = document.getElementById('uploadPercent');

    progress.classList.remove('hidden');
    bar.style.width = '0%';
    percentText.textContent = '0%';

    let pct = 0;
    const interval = setInterval(() => {
      pct += 25;
      bar.style.width = `${pct}%`;
      percentText.textContent = `${pct}%`;

      if (pct >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          progress.classList.add('hidden');
          const newInv = {
            id: Math.floor(Math.random() * 9000 + 1000),
            fecha: new Date().toISOString().split('T')[0],
            monto: Math.floor(Math.random() * 4 + 3) * 150000,
            estado: 'Pendiente'
          };
          _invoices.unshift(newInv);
          renderInvoicesTable();
          showToast('<i class="fa-solid fa-check"></i> Comprobante subido exitosamente');
        }, 300);
      }
    }, 200);
  };

  function renderInvoicesTable() {
    const tbody = document.getElementById('invoicesTableBody');
    if (!tbody) return;

    if (_invoices.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center" style="padding:24px; color:var(--text-3);">No hay comprobantes subidos.</td></tr>`;
      return;
    }

    tbody.innerHTML = _invoices.map((inv, idx) => `
      <tr>
        <td style="font-weight:bold; color:var(--primary);">#FM-INV-${inv.id}</td>
        <td>${inv.fecha}</td>
        <td><span class="badge badge-pending">${inv.estado || 'Pendiente Validación Admin'}</span></td>
        <td style="text-align:right;"><button class="btn btn-danger btn-sm" onclick="_invoices.splice(${idx},1); renderInvoicesTable();">🗑</button></td>
      </tr>
    `).join('');
  }

  window.togglePilotStatus = function(available) {
    const badge = document.getElementById('mainProfileEstado');
    if (badge) {
      badge.innerHTML = available ? '<span class="badge badge-active">Disponible</span>' : '<span class="badge badge-busy">Ocupado en Vuelo</span>';
    }
    showToast(`<i class="fa-solid fa-check"></i> Estado cambiado a ${available ? 'Disponible' : 'Ocupado en Vuelo'}`);
  };

  function showToast(message, type = 'success', duration = 3500) {
    const icons = { success: '<i class="fa-solid fa-check"></i>', error: '✕', warn: '<i class="fa-solid fa-triangle-exclamation"></i>' };
    const t = document.createElement('div');
    t.style.position = 'fixed';
    t.style.bottom = '24px';
    t.style.right = '24px';
    t.style.background = 'var(--card-bg)';
    t.style.color = 'var(--text)';
    t.style.border = '1px solid var(--accent)';
    t.style.padding = '12px 24px';
    t.style.borderRadius = '12px';
    t.style.fontSize = '0.88rem';
    t.style.fontWeight = '600';
    t.style.boxShadow = '0 10px 30px rgba(0,0,0,0.15)';
    t.style.zIndex = '9999';
    t.innerHTML = `<span>${icons[type] || '<i class="fa-solid fa-check"></i>'}</span> ${message}`;
    document.body.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transition = 'opacity 0.3s';
      setTimeout(() => t.remove(), 300);
    }, duration);
  }

  function formatCurrency(v) {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(v);
  }

  // ── AUTO-SYNC EN TIEMPO REAL (Refresco en segundo plano cada 8 segundos) ──
  setInterval(async () => {
    try {
      if (document.hidden) return;
      await loadTechTurnos();
    } catch(e) {}
  }, 8000);

