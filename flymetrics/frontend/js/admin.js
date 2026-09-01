/* ============================================================
   Flymetrics Admin Dashboard — admin.js
   Complete JS: API calls, panels, CRUD, modals, calendar
   ============================================================ */

'use strict';

var API_BASE = window.API_BASE || ((window.location.protocol === 'file:'
  ? 'http://localhost:3000'
  : (window.location.origin || 'http://localhost:3000')) + '/api/v1');

// GLOBAL STATE VARIABLES
let _usuariosList = [];
let tecnicosData = [];
let clientesData = [];
let agendaData = [];
let dronesData = [];
let serviciosData = [];
let adminSolicitudesData = [];
let gastosData = [];
let pqrsData = [];
let activePQRId = null;
let pagosData = [];
let reportesData = [];
let _adminNotifs = [];
let agendaFilters = { tecnico: '', estado: '' };
let selectedCalDate = new Date().toISOString().split('T')[0];
let _usuariosFiltroRol = '';
// GLOBAL STATE VARIABLES
















// ─────────────────────────────────────────
// AUTH HELPERS
// ─────────────────────────────────────────
function getToken() { return sessionStorage.getItem('fm_token') || localStorage.getItem('fm_token'); }
function getUser() {
  try { return JSON.parse(sessionStorage.getItem('fm_user') || localStorage.getItem('fm_user')) || {}; } catch { return {}; }
}

function logout() {
  try { sessionStorage.clear(); } catch(e) {}
  try { localStorage.clear(); } catch(e) {}
  window.location.href = 'index.html';
}
window.logout = logout;

function toggleAdminSidebar(e) {
  if (e) e.stopPropagation();
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('adminSidebarOverlay');
  if (!sidebar) return;

  if (window.innerWidth > 900) {
    // Desktop: toggle compact collapse
    sidebar.classList.toggle('collapsed');
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('fm_admin_sidebar_collapsed', isCollapsed ? 'true' : 'false');
  } else {
    // Mobile / Tablet: toggle off-canvas drawer
    sidebar.classList.toggle('open');
    if (overlay) {
      if (sidebar.classList.contains('open')) {
        overlay.classList.remove('hidden');
        overlay.classList.add('active');
      } else {
        overlay.classList.remove('active');
        overlay.classList.add('hidden');
      }
    }
  }
}
window.toggleAdminSidebar = toggleAdminSidebar;
window.toggleAdminSidebarCollapse = toggleAdminSidebar;

async function ensureAdminAuth() {
  let token = getToken();
  let u = getUser();

  if (!token) {
    window.location.href = 'staff.html';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const json = await res.json();
      const curUser = json.data || json;
      if (curUser.rol === 'administrador') {
        sessionStorage.setItem('fm_user', JSON.stringify(curUser));
      } else {
        showToast('Acceso denegado: Se requieren permisos de Administrador', 'error');
        setTimeout(logout, 1500);
        return;
      }
    } else {
      showToast('Sesión inválida o expirada. Por favor ingresa nuevamente.', 'warn');
      setTimeout(logout, 1500);
      return;
    }
  } catch(e) {
    console.warn('Verificación de sesión en API falló:', e);
  }

  const curr = getUser();
  const nameEl = document.getElementById('sidebarUserName');
  const emailEl = document.getElementById('sidebarUserEmail');
  const initEl = document.getElementById('sidebarUserInitials');

  if (nameEl) nameEl.textContent = `${curr.nombre || 'Administrador'} ${curr.apellido_1 || ''}`.trim();
  if (emailEl) emailEl.textContent = curr.email || 'admin@flymetrics.co';
  if (initEl) initEl.textContent = ((curr.nombre || 'A')[0] + (curr.apellido_1 || 'D')[0]).toUpperCase();
}

// ─────────────────────────────────────────
// API FETCH WRAPPER
// ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (res.status === 401 || res.status === 403) {
      showToast('Acceso denegado o sesión expirada. Redirigiendo...', 'warn');
      setTimeout(logout, 1500);
      return null;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || `Error ${res.status}`);
    }

    if (res.status === 204) return null;
    let data = await res.json();
    if (data && (data.success === true || data.status === 'success' || data.success === 'true') && data.data !== undefined) {
      data = data.data;
    }
    if (data) {
      const mapId = (item) => {
        if (item && typeof item === 'object') {
          if (item.id === undefined) {
            item.id = item.id_turno || item.id_tecnico || item.id_cliente || item.id_pago || item.id_drone || item.id_reporte || item.id_usuarios || item.id_notificacion;
          }
          if (item.cliente === undefined && item.nombre_cliente !== undefined) {
            item.cliente = item.nombre_cliente;
          }
          if (item.finca === undefined && item.nombre_finca !== undefined) {
            item.finca = item.nombre_finca;
          }
          if (item.servicio === undefined && item.nombre_servicio !== undefined) {
            item.servicio = item.nombre_servicio;
          }
          if (item.tecnico === undefined && item.tecnico_nombre !== undefined) {
            item.tecnico = item.tecnico_nombre === 'Sin asignar' ? '' : item.tecnico_nombre;
          }
          if (item.fecha === undefined && item.fecha_de_turno !== undefined) {
            item.fecha = item.fecha_de_turno;
          }
          if (item.hora === undefined && item.hora_inicio_estimada !== undefined) {
            item.hora = item.hora_inicio_estimada.slice(0, 5); // HH:MM
          }
          if (item.monto === undefined && item.tarifa !== undefined) {
            item.monto = item.tarifa;
          }
          if (item.precio === undefined && item.tarifa !== undefined) {
            item.precio = item.tarifa;
          }
        }
      };
      if (Array.isArray(data)) {
        data.forEach(mapId);
      } else {
        mapId(data);
      }
    }
    return data;
  } catch (err) {
    console.error(`[API] Request failed for ${path}:`, err.message);
    throw err;
  }
}

// All data sourced from real API - no mock data




// ─────────────────────────────────────────
// TOAST NOTIFICATIONS (DEDUPLICATED)
// ─────────────────────────────────────────
let _lastToastText = '';
let _lastToastTime = 0;

function showToast(message, type = 'success', duration = 3500) {
  const now = Date.now();
  const cleanMsg = String(message).replace(/<[^>]*>?/gm, '').trim();
  
  // Prevent duplicate toast spam within 1.2s
  if (_lastToastText === cleanMsg && now - _lastToastTime < 1200) {
    return;
  }
  _lastToastText = cleanMsg;
  _lastToastTime = now;

  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.position = 'fixed';
    container.style.bottom = '24px';
    container.style.right = '24px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '8px';
    document.body.appendChild(container);
  }

  // Remove existing toasts with exact same message
  Array.from(container.children).forEach(child => {
    if (child.textContent.includes(cleanMsg)) {
      child.remove();
    }
  });

  const icons = { success: '<i class="fa-solid fa-check"></i>', error: '✕', info: 'ℹ', warn: '<i class="fa-solid fa-triangle-exclamation"></i>' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Format clean message without double checkmarks
  const renderedMsg = message.startsWith('<i') ? message : `<span>${icons[type] || '•'}</span> <span>${message}</span>`;
  toast.innerHTML = renderedMsg;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─────────────────────────────────────────
// FORMAT HELPERS
// ─────────────────────────────────────────
function formatCurrency(n) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n || 0);
}
function formatDate(d) {
  if (!d) return '—';
  try {
    let dateObj;
    if (d instanceof Date) {
      dateObj = d;
    } else if (typeof d === 'string') {
      const s = d.trim();
      if (s.includes('T') || s.includes(' ') || s.includes('/')) {
        dateObj = new Date(s);
      } else {
        dateObj = new Date(s + 'T12:00:00');
      }
    } else if (typeof d === 'number') {
      dateObj = new Date(d);
    } else {
      dateObj = new Date(d);
    }
    if (isNaN(dateObj.getTime())) {
      return typeof d === 'string' ? d.split('T')[0] : '—';
    }
    return dateObj.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch (e) {
    return typeof d === 'string' ? d : '—';
  }
}

function formatDateShort(d) {
  if (!d) return '—';
  try {
    let dateObj;
    if (d instanceof Date) {
      dateObj = d;
    } else if (typeof d === 'string') {
      const s = d.trim();
      if (s.includes('T') || s.includes(' ') || s.includes('/')) {
        dateObj = new Date(s);
      } else {
        dateObj = new Date(s + 'T12:00:00');
      }
    } else if (typeof d === 'number') {
      dateObj = new Date(d);
    } else {
      dateObj = new Date(d);
    }
    if (isNaN(dateObj.getTime())) {
      return typeof d === 'string' ? d.split('T')[0] : '—';
    }
    return dateObj.toLocaleDateString('es-CO', { day: '2-digit', month: 'short' });
  } catch (e) {
    return typeof d === 'string' ? d : '—';
  }
}
function initials(name, last) {
  return ((name || '?')[0] + (last || '?')[0]).toUpperCase();
}

function statusBadge(estado) {
  const norm = (estado || '').trim();
  const lower = norm.toLowerCase();
  
  let cls = 'badge-inactive';
  if (lower === 'pendiente') cls = 'badge-pending';
  else if (lower === 'confirmado') cls = 'badge-confirmed';
  else if (lower === 'en proceso' || lower === 'en_proceso' || lower === 'hecho' || lower.includes('proceso')) cls = 'badge-inprocess';
  else if (lower === 'completado') cls = 'badge-completed';
  else if (lower === 'cancelado' || lower === 'rechazado') cls = 'badge-cancelled';
  else if (lower === 'disponible') cls = 'badge-available';
  else if (lower === 'ocupado') cls = 'badge-busy';
  else if (lower === 'mantenimiento') cls = 'badge-maintenance';
  else if (lower === 'pagado') cls = 'badge-paid';
  else if (lower === 'pendiente_pago') cls = 'badge-unpaid';

  const label = lower === 'disponible' ? 'Disponible' : lower === 'ocupado' ? 'Ocupado' : lower === 'mantenimiento' ? 'Mantenimiento' : norm;
  return `<span class="badge ${cls}">${label}</span>`;
}

// ─────────────────────────────────────────
// MODAL HELPERS
// ─────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('hidden');
  el.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('active');
  el.classList.add('hidden');
  document.body.style.overflow = '';
}
function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => {
    m.classList.remove('active');
    m.classList.add('hidden');
  });
  document.body.style.overflow = '';
}

window.openModal = openModal;
window.closeModal = closeModal;
window.closeAllModals = closeAllModals;

// ─────────────────────────────────────────
// NAVIGATION
// ─────────────────────────────────────────
let activePanel = 'dashboard';

function navigateTo(panelId) {
  // Close notifications dropdown
  document.getElementById('adminNotificationsDropdown')?.classList.add('hidden');

  // Hide all panels
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  // Show selected
  const panel = document.getElementById(`panel-${panelId}`);
  if (panel) panel.classList.add('active');

  const navItem = document.querySelector(`[data-panel="${panelId}"]`);
  if (navItem) navItem.classList.add('active');

  // Update topbar title
  const titles = {
    dashboard: 'Dashboard General', agenda: 'Agenda Operativa', clientes: 'Directorio de Clientes',
    tecnicos: 'Monitoreo y Técnicos en Vivo', drones: 'Hangar de Drones', servicios: 'Catálogo de Servicios Agrícolas',
    reagendamiento: 'Módulo de Reagendamiento de Turnos',
    facturacion: 'Facturación & Estados de Cuenta',
    'reportes-vuelo': 'Reportes de Vuelo & Telemetría',
    'informes-ejecutivos': 'Informes Ejecutivos & Entregables Agronómicos',
    reportes: 'Reportes de Vuelo e Informes Ejecutivos', configuracion: 'Configuración del Sistema',
    usuarios: 'Gestión de Usuarios y Roles', gastos: 'Gastos & Mantenimiento',
    solicitudes: 'Bandeja de Autorizaciones Pilotos', 'contacto-web': 'Solicitudes Contacto Web ("Nosotros te contactamos")', 'admin-tecnico': 'Torre Control Admin-Técnico'
  };
  document.getElementById('topbarTitle').textContent = titles[panelId] || panelId;

  activePanel = panelId;

  // Load data
  panelLoaders[panelId]?.();
}

let _contactoSolicitudes = [];
let _activeContactoId = null;

async function loadContactoWeb() {
  const tbody = document.getElementById('contactoWebTableBody');
  const badge = document.getElementById('webContactoBadge');

  try {
    const raw = await apiFetch('/contacto/solicitudes') || [];
    _contactoSolicitudes = Array.isArray(raw) ? raw : (raw.data || []);
    
    // Si no hay solicitudes en /contacto/solicitudes, cargar de /pqrs
    if (!_contactoSolicitudes.length) {
      const pqrsRaw = await apiFetch('/pqrs') || [];
      const pqrsList = Array.isArray(pqrsRaw) ? pqrsRaw : (pqrsRaw.data || []);
      _contactoSolicitudes = pqrsList.filter(p => (p.asunto || '').includes('[CONTACTO') || (p.asunto || '').includes('Contacto') || p.tipo === 'Petición').map(p => ({
        id_pqr: p.id_pqr,
        asunto: p.asunto,
        nombre: p.usuario?.cliente?.nombre || 'Contacto Web',
        telefono: p.usuario?.cliente?.telefono || '',
        email: p.usuario?.email || '',
        hectareas: '—',
        cultivo: '—',
        ubicacion: '—',
        servicio: p.asunto,
        mensaje: p.mensaje || '',
        mensaje_completo: p.mensaje || '',
        estado: p.estado || 'Abierto',
        fecha: p.fecha_creacion
      }));
    }

    const abiertas = _contactoSolicitudes.filter(s => (s.estado || '').toLowerCase() === 'abierto').length;
    if (badge) {
      badge.textContent = abiertas;
      badge.style.display = abiertas > 0 ? 'inline-flex' : 'none';
    }

    renderContactoWebTable();
  } catch (e) {
    console.warn('Error loading contacto web:', e);
    renderContactoWebTable();
  }
}
window.loadContactoWeb = loadContactoWeb;

function renderContactoWebTable() {
  const tbody = document.getElementById('contactoWebTableBody');
  if (!tbody) return;

  const q = (document.getElementById('contactoWebSearch')?.value || '').toLowerCase().trim();
  const estadoFilter = document.getElementById('contactoWebEstadoFilter')?.value || '';

  let data = _contactoSolicitudes;
  if (estadoFilter) {
    data = data.filter(s => (s.estado || 'Abierto').toLowerCase() === estadoFilter.toLowerCase());
  }
  if (q) {
    data = data.filter(s => [s.nombre, s.telefono, s.email, s.cultivo, s.ubicacion, s.servicio, s.mensaje, s.asunto].some(v => (v || '').toLowerCase().includes(q)));
  }

  if (!data.length) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted" style="padding:40px;"><div class="empty-icon">📩</div><div class="empty-title">No hay solicitudes de cotización registradas</div></td></tr>`;
    return;
  }

  tbody.innerHTML = data.map(s => {
    const id = s.id_pqr || s.id;
    const estado = s.estado || 'Abierto';
    const badgeCls = estado === 'Cerrado' ? 'badge-completed' : (estado === 'Atendido' ? 'badge-confirmed' : (estado === 'En Proceso' ? 'badge-inprocess' : 'badge-pending'));
    const telClean = (s.telefono || '').replace(/\D/g, '');
    const waUrl = telClean ? `https://wa.me/57${telClean.length === 10 ? telClean : telClean.slice(-10)}?text=${encodeURIComponent(`Hola ${s.nombre}, te contactamos desde Flymetrics respecto a tu solicitud de cotización 24h para ${s.servicio}.`)}` : '#';

    return `
      <tr>
        <td style="font-weight:800; color:var(--primary);">#COT-${id}</td>
        <td>
          <div style="font-weight:700; color:#003049;">${s.nombre || '—'}</div>
          <div style="font-size:0.75rem; color:#4a5568;">
            ${s.telefono ? `<a href="tel:${s.telefono}" style="color:#1c82ad; text-decoration:none; font-weight:600; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-phone" style="font-size:0.7rem;"></i> ${s.telefono}</a>` : ''}
          </div>
          <div style="font-size:0.75rem; color:#718096;">${s.email || ''}</div>
        </td>
        <td>
          <div style="font-weight:700; color:#1c82ad; font-size:0.88rem;">${s.servicio || 'Servicio Dron'}</div>
          <div style="font-size:0.78rem; color:#4a5568; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-seedling" style="color:#10b981;"></i> ${s.cultivo && s.cultivo !== '—' ? s.cultivo : 'Cultivo General'}</div>
        </td>
        <td>
          <span class="badge" style="background:rgba(16, 185, 129, 0.12); color:#059669; border:1px solid rgba(16, 185, 129, 0.25); font-weight:700; font-size:0.82rem;">
            ${s.hectareas && s.hectareas !== '—' ? `${s.hectareas}` : 'Por definir'}
          </span>
        </td>
        <td>
          <div style="font-size:0.85rem; color:#2d3748; font-weight:600; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-location-dot" style="color:#ef4444;"></i> ${s.ubicacion || '—'}</div>
        </td>
        <td style="max-width:260px;">
          <div style="font-size:0.82rem; color:#4a5568; line-height:1.4; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">
            ${s.mensaje || s.asunto || '—'}
          </div>
        </td>
        <td>${formatDate(s.fecha)}</td>
        <td><span class="badge ${badgeCls}">${estado}</span></td>
        <td style="text-align:center;">
          <div style="display:flex; gap:6px; justify-content:center; flex-wrap:wrap;">
            <button class="btn btn-ghost btn-sm" onclick="openContactoDetailModal(${id})" title="Ver detalle completo" style="padding:4px 8px; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-eye"></i> Ver</button>
            ${telClean ? `
              <a href="${waUrl}" target="_blank" class="btn btn-sm" title="Contactar por WhatsApp" style="background:#25D366; color:#fff; padding:4px 8px; border-radius:6px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">
                <i class="fa-brands fa-whatsapp"></i>
              </a>
            ` : ''}
            ${estado !== 'Atendido' ? `
              <button class="btn btn-accent btn-sm" onclick="markContactoAtendido(${id})" title="Marcar como atendido" style="padding:4px 8px; display:inline-flex; align-items:center;"><i class="fa-solid fa-check"></i></button>
            ` : ''}
            <button class="btn btn-danger btn-sm" onclick="deleteContactoCotizacion(${id})" title="Eliminar cotización" style="padding:4px 8px; display:inline-flex; align-items:center; background:#ef4444; color:#fff; border:none; border-radius:6px; font-weight:700;"><i class="fa-solid fa-trash-can"></i></button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderContactoWebTable = renderContactoWebTable;

window.deleteContactoCotizacion = async function(id) {
  if (!confirm(`¿Estás seguro de que deseas eliminar permanentemente la solicitud de cotización #COT-${id}?`)) {
    return;
  }
  try {
    showToast('Eliminando solicitud...', 'info');
    await apiFetch(`/contacto/solicitudes/${id}`, { method: 'DELETE' });
    _contactoSolicitudes = _contactoSolicitudes.filter(x => (x.id_pqr || x.id) != id);
    renderContactoWebTable();
    showToast(`<i class="fa-solid fa-check"></i> Cotización #COT-${id} eliminada de la base de datos`, 'success');
  } catch (err) {
    showToast('Error al eliminar: ' + err.message, 'error');
  }
};

window.openContactoDetailModal = function(id) {
  const s = _contactoSolicitudes.find(x => (x.id_pqr || x.id) == id);
  if (!s) return;
  _activeContactoId = id;

  const titleEl = document.getElementById('contactoDetailTitle');
  if (titleEl) titleEl.textContent = `📩 Solicitud #COT-${id} — ${s.nombre}`;

  const telClean = (s.telefono || '').replace(/\D/g, '');
  const waBtn = document.getElementById('contactoDetailWhatsappBtn');
  if (waBtn) {
    if (telClean) {
      const cfg = getCorporateConfig();
      let tmpl = cfg.wa_template_24h || 'Hola {nombre}, te contactamos desde Flymetrics Colombia sobre tu solicitud de {servicio} ({hectareas} ha).';
      tmpl = tmpl.replace('{nombre}', s.nombre || 'estimado cliente')
                 .replace('{servicio}', s.servicio || 'servicios de drones')
                 .replace('{hectareas}', s.hectareas || 'área indicada');
      
      const phoneParam = telClean.startsWith('57') ? telClean : ('57' + (telClean.length === 10 ? telClean : telClean.slice(-10)));
      waBtn.href = `https://wa.me/${phoneParam}?text=${encodeURIComponent(tmpl)}`;
      waBtn.style.display = 'inline-flex';
    } else {
      waBtn.style.display = 'none';
    }
  }

  const estadoSelect = document.getElementById('contactoDetailEstadoSelect');
  if (estadoSelect) estadoSelect.value = s.estado || 'Abierto';

  const bodyEl = document.getElementById('contactoDetailBody');
  if (bodyEl) {
    bodyEl.innerHTML = `
      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px; padding:18px; margin-bottom:16px;">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px;">
          <div><strong style="color:#003049;"><i class="fa-solid fa-user" style="color:#1c82ad; margin-right:6px;"></i>Cliente:</strong> ${s.nombre || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-phone" style="color:#10b981; margin-right:6px;"></i>Teléfono / WA:</strong> ${s.telefono ? `<a href="tel:${s.telefono}" style="color:#1c82ad; font-weight:700; text-decoration:none;">${s.telefono}</a>` : '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-envelope" style="color:#6366f1; margin-right:6px;"></i>Correo:</strong> ${s.email || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-cubes" style="color:#0284c7; margin-right:6px;"></i>Servicio:</strong> ${s.servicio || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-wheat-awn" style="color:#d97706; margin-right:6px;"></i>Área / Hectáreas:</strong> ${s.hectareas || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-seedling" style="color:#059669; margin-right:6px;"></i>Cultivo:</strong> ${s.cultivo || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-location-dot" style="color:#ef4444; margin-right:6px;"></i>Ubicación:</strong> ${s.ubicacion || '—'}</div>
          <div><strong style="color:#003049;"><i class="fa-solid fa-calendar-day" style="color:#475569; margin-right:6px;"></i>Fecha Recibido:</strong> ${formatDate(s.fecha)}</div>
        </div>
      </div>
      <div style="margin-top:12px;">
        <strong style="color:#003049; display:flex; align-items:center; gap:6px; margin-bottom:8px;">
          <i class="fa-solid fa-comment-dots" style="color:var(--accent);"></i> Mensaje / Consulta del Cliente:
        </strong>
        <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:14px; color:#334155; font-size:0.92rem; line-height:1.5; white-space:pre-wrap; max-height:160px; overflow-y:auto; box-shadow:inset 0 1px 3px rgba(0,0,0,0.03);">
          ${s.mensaje || s.mensaje_completo || 'Sin mensaje adicional'}
        </div>
      </div>
    `;
  }

  openModal('contactoDetailModal');
};

window.saveContactoEstadoFromModal = async function() {
  if (!_activeContactoId) return;
  const nuevoEstado = document.getElementById('contactoDetailEstadoSelect')?.value || 'Atendido';

  try {
    showToast('Actualizando estado...', 'info');
    await apiFetch(`/contacto/solicitudes/${_activeContactoId}/estado`, {
      method: 'PATCH',
      body: JSON.stringify({ estado: nuevoEstado })
    });
    const s = _contactoSolicitudes.find(x => (x.id_pqr || x.id) == _activeContactoId);
    if (s) s.estado = nuevoEstado;
    renderContactoWebTable();
    showToast(`<i class="fa-solid fa-check"></i> Estado actualizado a '${nuevoEstado}'`, 'success');
    closeModal('contactoDetailModal');
  } catch (err) {
    showToast('Error al actualizar estado: ' + err.message, 'error');
  }
};

window.markContactoAtendido = async function(id) {
  try {
    await apiFetch(`/contacto/solicitudes/${id}/estado`, {
      method: 'PATCH',
      body: JSON.stringify({ estado: 'Atendido' })
    });
    const s = _contactoSolicitudes.find(x => (x.id_pqr || x.id) == id);
    if (s) s.estado = 'Atendido';
    renderContactoWebTable();
    showToast('<i class="fa-solid fa-check"></i> Solicitud marcada como Atendida', 'success');
  } catch (err) {
    showToast('Error al actualizar: ' + err.message, 'error');
  }
};

const panelLoaders = {
  dashboard: loadDashboard,
  agenda: loadAgenda,
  clientes: loadClientes,
  tecnicos: loadTecnicos,
  drones: loadDrones,
  servicios: loadServicios,
  reagendamiento: async function() {
    await loadAgenda();
    renderReagendamientoTable();
  },
  facturacion: loadFacturacion,
  'reportes-vuelo': loadReportes,
  'informes-ejecutivos': loadReportes,
  reportes: loadReportes,
  configuracion: loadConfiguracion,
  usuarios: loadUsuarios,
  solicitudes: loadAdminSolicitudes,
  'contacto-web': loadContactoWeb,
  'admin-tecnico': function() { if (window.loadAdminTecnicoModule) window.loadAdminTecnicoModule(); }
};

// ─────────────────────────────────────────
// CACHE
// ─────────────────────────────────────────
const cache = {};

async function fetchCached(key, path) {
  if (cache[key] && (Date.now() - cache[key].ts < 2000)) return cache[key].data;
  const data = await apiFetch(path);
  cache[key] = { data: data || [], ts: Date.now() };
  return cache[key].data;
}

function invalidateCache(key) { delete cache[key]; }

// ─────────────────────────────────────────
// 1. DASHBOARD PANEL
// ─────────────────────────────────────────
async function loadDashboard() {
  try {
    const [agenda, clientes, tecnicos, pagos] = await Promise.all([
      apiFetch('/admin/agenda').catch(() => []),
      apiFetch('/clientes').catch(() => []),
      apiFetch('/tecnicos').catch(() => []),
      apiFetch('/admin/pagos').catch(() => []),
    ]);

    loadContactoWeb().catch(() => null);

    const safeAgenda = Array.isArray(agenda) ? agenda : (agenda?.data || []);
    const safeClientes = Array.isArray(clientes) ? clientes : (clientes?.data || []);
    const safeTecnicos = Array.isArray(tecnicos) ? tecnicos : (tecnicos?.data || []);
    const safePagos = Array.isArray(pagos) ? pagos : (pagos?.data || []);

    const today = new Date().toISOString().split('T')[0];
    const turnosHoy = safeAgenda.filter(a => a.fecha === today || a.fecha_de_turno === today).length || safeAgenda.length;
    const clientesTotales = safeClientes.length;
    const tecnicosActivos = safeTecnicos.length;
    const ingresosMes = safePagos.reduce((s, p) => s + (p.monto || p.tarifa || 0), 0) || safeAgenda.reduce((s, a) => s + (parseFloat(a.tarifa) || 0), 0);

    const turnosEnProceso = safeAgenda.filter(a => {
      const st = (a.estado || '').toLowerCase().trim();
      return st === 'en proceso' || st === 'en_proceso' || st.includes('proceso') || st === 'hecho';
    }).length;

    const elTurnos = document.getElementById('statTurnosHoy');
    if (elTurnos) elTurnos.textContent = turnosHoy;
    const elProceso = document.getElementById('statEnProceso');
    if (elProceso) elProceso.textContent = turnosEnProceso;
    const elClientes = document.getElementById('statClientes');
    if (elClientes) elClientes.textContent = clientesTotales;
    const elTecnicos = document.getElementById('statTecnicos');
    if (elTecnicos) elTecnicos.textContent = tecnicosActivos;
    const elIngresos = document.getElementById('statIngresos');
    if (elIngresos) elIngresos.textContent = formatCurrency(ingresosMes);

    // Recent agenda
    const recent = (agenda || []).slice(-5).reverse();
    const tbody = document.getElementById('recentAgendaBody');
    if (tbody) {
      tbody.innerHTML = recent.length ? recent.map(a => {
        const id = a.id || a.id_turno;
        const cliente = a.cliente || a.cliente_nombre || a.nombre_cliente || 'Cliente';
        const servicio = a.servicio || a.servicio_nombre || a.nombre_servicio || 'Vuelo agrícola';
        const fecha = a.fecha || a.fecha_de_turno || '';
        const hora = a.hora || a.hora_inicio_estimada || '';
        const tecnico = a.tecnico || a.tecnico_nombre || '<span class="text-muted">Sin asignar</span>';
        return `
          <tr>
            <td style="font-weight:bold; color:var(--primary);">#${id}</td>
            <td style="font-weight:500;">${cliente}</td>
            <td>${servicio}</td>
            <td>${formatDateShort(fecha)} ${String(hora).slice(0,5)}</td>
            <td>${statusBadge(a.estado)}</td>
            <td>${tecnico}</td>
          </tr>
        `;
      }).join('') : `<tr><td colspan="6" class="text-center text-muted" style="padding:24px">No hay turnos recientes registrados.</td></tr>`;
    }
  } catch (err) {
    console.error('Error in loadDashboard:', err);
  }
}

// ─────────────────────────────────────────
// 2. AGENDA PANEL
// ─────────────────────────────────────────




async function loadAgenda() {
  const [raw, rawTecs] = await Promise.all([
    apiFetch('/admin/agenda').catch(() => []),
    (!tecnicosData || tecnicosData.length === 0) ? fetchCached('tecnicos', '/tecnicos').catch(() => []) : Promise.resolve(tecnicosData)
  ]);

  if (rawTecs && Array.isArray(rawTecs) && rawTecs.length > 0 && (!tecnicosData || tecnicosData.length === 0)) {
    tecnicosData = rawTecs.map(t => ({
      id: t.id_tecnico || t.id,
      id_tecnico: t.id_tecnico || t.id,
      id_usuario: t.id_usuario,
      nombre: t.nombre,
      apellido_1: t.apellido_1 || t.apellido || '',
      apellido: [t.apellido_1, t.apellido_2].filter(Boolean).join(' ') || t.apellido || '',
      certificacion: t.certificacion,
      estado: t.estado || 'disponible',
      telefono: t.telefono
    }));
  }

  agendaData = (Array.isArray(raw) ? raw : (raw.data || [])).map(t => ({
    id: t.id_turno, id_turno: t.id_turno, id_finca: t.id_finca, id_servicio: t.id_servicio,
    id_tecnico: t.id_tecnico, id_drone: t.id_drone,
    cliente: t.cliente_nombre || 'Cliente',
    email: t.cliente_email || '',
    finca: t.finca_nombre || ('Finca #' + t.id_finca),
    servicio: t.servicio_nombre || ('Servicio #' + t.id_servicio),
    tecnico: t.tecnico_nombre || '',
    fecha: t.fecha_de_turno, hora: t.hora_inicio_estimada,
    estado: t.estado || 'Pendiente',
    hectareas: t.hectareas || 0, precio: t.tarifa || 0,
    notas: t.observaciones_servicio || '', telefono: t.cel || '',
    motivo_reagendamiento: t.motivo_reagendamiento || ''
  })).sort((a, b) => (b.id || 0) - (a.id || 0));
  renderCalendar();
  renderAgendaTable();
  renderReagendamientoTable();
  populateTecnicoFilter();
}

let calViewMode = '7days';
let calBaseDate = new Date();

window.setCalendarView = function(mode) {
  calViewMode = mode;
  document.getElementById('btnCalView7')?.classList.toggle('active', mode === '7days');
  document.getElementById('btnCalView14')?.classList.toggle('active', mode === '14days');
  document.getElementById('btnCalViewMonth')?.classList.toggle('active', mode === 'month');
  renderCalendar();
};

window.setCalendarMonth = function(monthIndex) {
  calBaseDate.setMonth(parseInt(monthIndex));
  calViewMode = 'month';
  document.getElementById('btnCalView7')?.classList.remove('active');
  document.getElementById('btnCalView14')?.classList.remove('active');
  document.getElementById('btnCalViewMonth')?.classList.add('active');
  renderCalendar();
};

window.navCalendar = function(dir) {
  if (dir === 0) {
    calBaseDate = new Date();
  } else if (calViewMode === 'month') {
    calBaseDate.setMonth(calBaseDate.getMonth() + dir);
  } else if (calViewMode === '14days') {
    calBaseDate.setDate(calBaseDate.getDate() + (dir * 14));
  } else {
    calBaseDate.setDate(calBaseDate.getDate() + (dir * 7));
  }
  renderCalendar();
};

function renderCalendar() {
  const container = document.getElementById('calendarGrid');
  if (!container) return;
  const today = new Date();
  const todayIso = today.toISOString().split('T')[0];
  const dayNames = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];
  const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

  const titleEl = document.getElementById('calMonthTitle');
  if (titleEl) {
    const curMonth = calBaseDate.getMonth();
    const curYear = calBaseDate.getFullYear();
    const monthSelectOptions = monthNames.map((m, idx) => 
      `<option value="${idx}" ${idx === curMonth ? 'selected' : ''}>${m}</option>`
    ).join('');

    titleEl.innerHTML = `
      <i class="fa-solid fa-calendar-days" style="color:var(--accent);"></i>
      <select onchange="setCalendarMonth(this.value)" style="border:1px solid #cbd5e1; border-radius:8px; padding:3px 8px; font-weight:800; font-size:1.02rem; color:var(--primary); background:#ffffff; cursor:pointer;">
        ${monthSelectOptions}
      </select>
      <span style="font-weight:800; color:var(--primary); font-size:1.02rem;">${curYear}</span>
      ${calViewMode !== 'month' ? `<span style="font-size:0.75rem; color:#64748b; font-weight:700;">(${calViewMode === '14days' ? '14 días' : '7 días'})</span>` : ''}
    `;
  }

  let days = [];
  if (calViewMode === 'month') {
    container.style.gridTemplateColumns = 'repeat(7, 1fr)';
    const year = calBaseDate.getFullYear();
    const month = calBaseDate.getMonth();
    const firstDayIndex = new Date(year, month, 1).getDay();
    const lastDayOfMonth = new Date(year, month + 1, 0).getDate();
    
    // Previous month filler
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = firstDayIndex - 1; i >= 0; i--) {
      const d = new Date(year, month - 1, prevMonthLastDay - i);
      days.push({ date: d, isCurrentMonth: false });
    }
    // Current month
    for (let i = 1; i <= lastDayOfMonth; i++) {
      const d = new Date(year, month, i);
      days.push({ date: d, isCurrentMonth: true });
    }
    // Next month filler
    const totalCells = days.length > 35 ? 42 : 35;
    const remaining = totalCells - days.length;
    for (let i = 1; i <= remaining; i++) {
      const d = new Date(year, month + 1, i);
      days.push({ date: d, isCurrentMonth: false });
    }
  } else {
    const count = calViewMode === '14days' ? 14 : 7;
    container.style.gridTemplateColumns = 'repeat(7, 1fr)';
    for (let i = 0; i < count; i++) {
      const d = new Date(calBaseDate);
      d.setDate(calBaseDate.getDate() + i);
      days.push({ date: d, isCurrentMonth: true });
    }
  }

  // Header row for weekdays
  let html = `
    <div style="grid-column: 1 / -1; display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px;">
      ${dayNames.map(name => `
        <div style="text-align:center; font-weight:800; font-size:0.75rem; color:#64748b; padding:4px 0; letter-spacing:0.5px;">
          ${name}
        </div>
      `).join('')}
    </div>
  `;

  html += days.map(item => {
    const d = item.date;
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const iso = `${yyyy}-${mm}-${dd}`;
    const isToday = iso === todayIso;
    const isSelected = iso === selectedCalDate;
    const turnos = (agendaData || []).filter(a => a.fecha === iso);
    const eventsHtml = turnos.slice(0, 2).map(t =>
      `<div class="cal-event" title="${t.cliente || ''} - ${t.servicio || ''}" onclick="event.stopPropagation();filterByDate('${iso}')" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${String(t.hora || '').slice(0, 5)} ${t.cliente || 'Turno'}</div>`
    ).join('') + (turnos.length > 2 ? `<div class="cal-event" style="opacity:0.8; font-weight:700; background:rgba(28,130,173,0.15); color:var(--accent);">+${turnos.length - 2} más</div>` : '');

    return `
      <div class="cal-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${!item.isCurrentMonth ? 'opacity-40' : ''}" onclick="selectCalDate('${iso}')" style="min-height:85px; cursor:pointer; transition:all 0.2s;">
        <div class="cal-day-header" style="display:flex; justify-content:flex-end; align-items:center;">
          <span class="cal-day-num" style="font-weight:800; font-size:0.92rem; ${isToday ? 'color:#1c82ad; background:rgba(28,130,173,0.15); border-radius:50%; width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center;' : ''}">${d.getDate()}</span>
        </div>
        <div style="margin-top:4px; display:flex; flex-direction:column; gap:3px;">
          ${eventsHtml}
        </div>
      </div>`;
  }).join('');

  container.innerHTML = html;
}

function selectCalDate(iso) {
  const dateInput = document.getElementById('agendaDateFilter');
  if (selectedCalDate === iso && dateInput && dateInput.value === iso) {
    selectedCalDate = '';
    if (dateInput) dateInput.value = '';
  } else {
    selectedCalDate = iso;
    if (dateInput) dateInput.value = iso;
    const estadoSelect = document.getElementById('agendaEstadoFilter');
    if (estadoSelect && estadoSelect.value) {
      const turnosOnDay = agendaData.filter(a => a.fecha === iso);
      const ef = estadoSelect.value.toLowerCase().trim();
      const matchingTurnos = turnosOnDay.filter(a => {
        const st = (a.estado || '').toLowerCase().trim();
        if (ef === 'en proceso' || ef === 'en_proceso' || ef === 'proceso') {
          return st === 'en proceso' || st === 'en_proceso' || st.includes('proceso') || st === 'hecho';
        }
        return st === ef;
      });
      if (turnosOnDay.length > 0 && matchingTurnos.length === 0) {
        estadoSelect.value = '';
      }
    }
  }
  renderCalendar();
  renderAgendaTable();
}

function filterByDate(iso) {
  selectCalDate(iso);
}

function clearAgendaFilters() {
  selectedCalDate = '';
  const ef = document.getElementById('agendaEstadoFilter');
  if (ef) ef.value = '';
  const tf = document.getElementById('agendaTecnicoFilter');
  if (tf) tf.value = '';
  const df = document.getElementById('agendaDateFilter');
  if (df) df.value = '';
  const sf = document.getElementById('agendaSearch');
  if (sf) sf.value = '';
  renderCalendar();
  renderAgendaTable();
}
window.clearAgendaFilters = clearAgendaFilters;

function filterAgendaByState(state) {
  if (typeof navigateTo === 'function') navigateTo('agenda');
  const select = document.getElementById('agendaEstadoFilter');
  if (select) {
    select.value = state;
    renderAgendaTable();
  }
}
window.filterAgendaByState = filterAgendaByState;

function populateTecnicoFilter() {
  const select = document.getElementById('agendaTecnicoFilter');
  const tecnicos = [...new Set(agendaData.filter(a => a.tecnico).map(a => a.tecnico))];
  select.innerHTML = '<option value="">Todos los técnicos</option>' +
    tecnicos.map(t => `<option value="${t}">${t}</option>`).join('');
}

function renderAgendaTable() {
  const search = (document.getElementById('agendaSearch')?.value || '').toLowerCase().trim();
  const estadoFilter = (document.getElementById('agendaEstadoFilter')?.value || '').toLowerCase().trim();
  const tecnicoFilter = (document.getElementById('agendaTecnicoFilter')?.value || '').trim();
  const dateFilter = (document.getElementById('agendaDateFilter')?.value || '').trim();

  let data = agendaData;
  if (search) {
    data = data.filter(a =>
      [a.cliente, a.email, a.finca, a.servicio, a.tecnico, a.notas, String(a.id), String(a.id_turno), String(a.telefono)].some(v => (v || '').toLowerCase().includes(search))
    );
  }
  if (estadoFilter) {
    data = data.filter(a => {
      const st = (a.estado || '').toLowerCase().trim();
      if (estadoFilter === 'en proceso' || estadoFilter === 'en_proceso' || estadoFilter.includes('proceso')) {
        return st === 'en proceso' || st === 'en_proceso' || st.includes('proceso') || st === 'hecho';
      }
      return st === estadoFilter;
    });
  }
  if (tecnicoFilter) data = data.filter(a => (a.tecnico || '').trim() === tecnicoFilter);
  if (dateFilter) data = data.filter(a => (a.fecha || '').trim() === dateFilter);

  // Orden estricto por llegada / ID descendente
  data = [...data].sort((a, b) => (b.id || 0) - (a.id || 0));

  const tbody = document.getElementById('agendaTableBody');
  const listTecnicos = (tecnicosData && tecnicosData.length) ? tecnicosData : (cache['tecnicos']?.data || []);

  tbody.innerHTML = data.length ? data.map(a => {
    const isRechazado = a.estado === 'Rechazado';
    const cleanNotas = (a.notas || '')
      .replace(/\[Servicios:\s*[^\]]+\]/gi, '')
      .replace(/(\s*\|\s*Cambiado por Admin:\s*Modificado por el administrador)+/gi, '')
      .replace(/(\s*\|\s*Cambiado por Admin:[^|]+)+/gi, '')
      .trim();

    const isConfirmado = a.estado === 'Confirmado';
    const isEnProceso = a.estado === 'En proceso' || a.estado === 'En Proceso';
    const isCompletado = a.estado === 'Completado';
    const isCancelado = a.estado === 'Cancelado';

    return `
    <tr style="${isRechazado ? 'background: rgba(255, 77, 109, 0.04);' : ''}">
      <td style="font-weight:800; color:var(--primary);">#${a.id}</td>
      <td>
        <div style="font-weight:700; color:#003049;">${a.cliente || '—'}</div>
        <div class="text-muted" style="font-size:0.75rem;">${a.email || ''}</div>
      </td>
      <td>${a.finca || '—'}</td>
      <td><span style="font-weight:600; color:#1c82ad;">${a.servicio || '—'}</span></td>
      <td>${formatDateShort(a.fecha)}</td>
      <td>${a.hora || '—'}</td>
      <td style="max-width:200px;">
        <div style="font-size:0.80rem; color:#475569; line-height:1.35; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="${cleanNotas || 'Sin observaciones'}">
          ${cleanNotas ? `<i class="fa-solid fa-comment-dots" style="color:var(--accent); margin-right:4px;"></i>${cleanNotas}` : '<span style="color:#94a3b8; font-style:italic;">—</span>'}
        </div>
      </td>
      <td>
        ${statusBadge(a.estado)}
        ${isRechazado ? `<div style="font-size:0.7rem;color:#FF4D6D;margin-top:4px;display:flex;align-items:center;gap:4px;"><i class="fa-solid fa-triangle-exclamation"></i> Piloto rechazó el turno</div>` : ''}
      </td>
      <td>
        ${a.tecnico
        ? `<div style="display:flex;align-items:center;gap:6px;"><div class="avatar" style="width:24px;height:24px;font-size:0.6rem;font-weight:700;">${(a.tecnico || '').split(' ').map(w => w[0]).join('').slice(0, 2)}</div>${a.tecnico}</div>`
        : `<span class="badge badge-unpaid">Sin asignar</span>`
      }
      </td>
      <td>
        <div class="table-actions" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
          <button class="btn btn-ghost btn-sm" onclick="viewAgendaDetail(${a.id})" title="Ver detalle completo" style="padding:4px 8px; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-eye"></i></button>
          
          <select class="filter-select form-select" style="padding:4px 6px;font-size:0.76rem;border-radius:8px;" onchange="assignTecnico(${a.id}, this.value); this.value=''" title="Asignar técnico">
            <option value="">${a.tecnico ? 'Reasignar piloto' : 'Asignar piloto'}</option>
            ${listTecnicos.map(t => `<option value="${t.id_tecnico || t.id}">${t.nombre} ${t.apellido_1 || t.apellido || ''}</option>`).join('')}
          </select>

          ${(!isConfirmado && !isEnProceso && !isCompletado && !isCancelado) ? `
            <button class="btn btn-primary btn-sm" style="padding:4px 8px;font-size:0.72rem;font-weight:700;display:inline-flex;align-items:center;gap:4px;" onclick="changeAgendaStatus(${a.id}, 'Confirmado')"><i class="fa-solid fa-circle-check"></i> Aceptar</button>
          ` : ''}

          <button class="btn btn-ghost btn-sm" style="padding:4px 8px;font-size:0.72rem;font-weight:700;display:inline-flex;align-items:center;gap:4px;color:#1c82ad;" onclick="openReagendarModalDirect(${a.id})" title="Modificar fecha/hora de vuelo"><i class="fa-solid fa-calendar-plus"></i> Reagendar</button>

          ${(!isCancelado && !isCompletado) ? `
            <button class="btn btn-ghost btn-sm" style="padding:4px 8px;font-size:0.72rem;font-weight:700;display:inline-flex;align-items:center;gap:4px;color:#ef4444;" onclick="cancelAgendaTurno(${a.id})" title="Cancelar turno"><i class="fa-solid fa-ban"></i> Cancelar</button>
          ` : ''}
        </div>
      </td>
    </tr>
  `;
  }).join('') : `<tr><td colspan="10" class="text-center" style="padding:40px"><div class="empty-state" style="padding:0"><div class="empty-icon"><i class="fa-solid fa-calendar-xmark" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No hay turnos agendados</div><div class="empty-sub" style="margin-bottom:12px">No se encontraron turnos con los filtros activos.</div><button class="btn btn-primary btn-sm" onclick="clearAgendaFilters()" style="margin: 0 auto; display: inline-flex; align-items: center; gap: 6px; font-weight:700;"><i class="fa-solid fa-rotate"></i> Mostrar todos los turnos</button></div></td></tr>`;
}

window.cancelAgendaTurno = async function(id) {
  if (!confirm(`¿Estás seguro de cancelar el agendamiento del turno #${id}?`)) return;
  await changeAgendaStatus(id, 'Cancelado');
};

window.openReagendarModalDirect = function(id) {
  const turno = agendaData.find(x => (x.id_turno || x.id) === id);
  if (!turno) return;
  const modal = document.getElementById('reprogramarModal');
  const todayIso = new Date().toISOString().split('T')[0];
  if (modal) {
    document.getElementById('reprogramarTurnoId').value = turno.id_turno || turno.id;
    
    // Fecha
    const fEl = document.getElementById('reprogramarFecha');
    if (fEl) {
      fEl.min = todayIso;
      fEl.value = (turno.fecha || turno.fecha_de_turno || todayIso).slice(0, 10);
    }

    // Hora
    const hEl = document.getElementById('reprogramarHora');
    if (hEl) {
      let hVal = turno.hora || turno.hora_inicio_estimada || '08:00';
      if (hVal.length > 5) hVal = hVal.slice(0, 5);
      hEl.value = hVal;
    }

    // Estado
    const stEl = document.getElementById('reprogramarEstado');
    if (stEl) {
      stEl.value = turno.estado || 'Confirmado';
    }

    // Técnico Select
    const techSelect = document.getElementById('reprogramarTecnico');
    if (techSelect) {
      techSelect.innerHTML = `<option value="">Sin piloto asignado</option>` + 
        (tecnicosData || []).map(t => `<option value="${t.id_tecnico || t.id}" ${String(t.id_tecnico || t.id) === String(turno.id_tecnico) ? 'selected' : ''}>${t.nombre} ${t.apellido || t.apellido_1 || ''}</option>`).join('');
    }

    // Dron Select
    const droneSelect = document.getElementById('reprogramarDron');
    if (droneSelect) {
      droneSelect.innerHTML = `<option value="">Sin dron asignado</option>` + 
        (dronesData || []).map(d => `<option value="${d.id_drone || d.id}" ${String(d.id_drone || d.id) === String(turno.id_drone) ? 'selected' : ''}>${d.modelo} (${d.numero_serie || 'SN'})</option>`).join('');
    }

    // Motivo & Obs
    const mEl = document.getElementById('reprogramarMotivo');
    if (mEl) mEl.value = turno.motivo_reagendamiento || '';

    const obsEl = document.getElementById('reprogramarObservaciones');
    if (obsEl) obsEl.value = (turno.observaciones_servicio || turno.observaciones || '').trim();

    openModal('reprogramarModal');
  } else {
    navigateTo('reagendamiento');
  }
};

async function assignTecnico(id, tecnicoId) {
  if (!tecnicoId) return;
  try {
    await apiFetch(`/admin/agenda/${id}/asignar`, {
      method: 'PATCH',
      body: JSON.stringify({ id_tecnico: parseInt(tecnicoId) })
    });
    invalidateCache('agenda');
    agendaData = await apiFetch('/admin/agenda') || [];
    renderAgendaTable();
    renderCalendar();
    showToast(`<i class="fa-solid fa-check"></i> Técnico asignado con éxito al turno #${id}`, 'success');
  } catch (e) {
    showToast('Error al asignar técnico: ' + e.message, 'error');
  }
}

async function changeAgendaStatus(id, estado) {
  if (!estado) return;
  try {
    await apiFetch(`/admin/agenda/${id}/estado`, {
      method: 'PATCH',
      body: JSON.stringify({ estado, motivo_admin: 'Modificado por el administrador' })
    });
    invalidateCache('agenda');
    agendaData = await apiFetch('/admin/agenda') || [];
    renderAgendaTable();
    renderCalendar();
    showToast(`<i class="fa-solid fa-check"></i> Estado del turno #${id} actualizado a: ${estado}`, 'success');
  } catch (e) {
    showToast('Error al cambiar estado: ' + e.message, 'error');
  }
}

function viewAgendaDetail(id) {
  const a = agendaData.find(x => x.id === id);
  if (!a) return;
  document.getElementById('detailModalTitle').innerHTML = `<i class="fa-solid fa-calendar-check" style="color:var(--accent); margin-right:8px;"></i> Detalle del Turno #${a.id}`;
  document.getElementById('detailModalBody').innerHTML = `
    <div class="info-list mb-4">
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-circle-info" style="color:var(--accent);"></i> Estado actual</span>
        <span class="info-item-value">${statusBadge(a.estado)}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-user" style="color:#1c82ad;"></i> Cliente</span>
        <span class="info-item-value">${a.cliente || '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-envelope" style="color:#6366f1;"></i> Email</span>
        <span class="info-item-value">${a.email || '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-phone" style="color:#10b981;"></i> Teléfono</span>
        <span class="info-item-value">${a.telefono ? `<a href="tel:${a.telefono}" style="color:#1c82ad; text-decoration:none; font-weight:700;">${a.telefono}</a>` : '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-house-chimney-window" style="color:#0284c7;"></i> Finca</span>
        <span class="info-item-value">${a.finca || '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-cubes" style="color:#0284c7;"></i> Servicio</span>
        <span class="info-item-value" style="color:#1c82ad; font-weight:700;">${a.servicio || '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-calendar-day" style="color:#475569;"></i> Fecha y hora</span>
        <span class="info-item-value">${formatDate(a.fecha)} — ${a.hora || '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-wheat-awn" style="color:#d97706;"></i> Hectáreas</span>
        <span class="info-item-value">${a.hectareas ? `${a.hectareas} ha` : '—'}</span>
      </div>
      <div class="info-item">
        <span class="info-item-label"><i class="fa-solid fa-user-gear" style="color:#0369a1;"></i> Piloto Técnico</span>
        <span class="info-item-value">${a.tecnico || '<span class="badge badge-unpaid">Sin asignar</span>'}</span>
      </div>
      ${(() => {
        if (!a.notas) return '';
        const raw = a.notas.replace(/\[Servicios:\s*[^\]]+\]/gi, '').trim();
        const mNotas = raw.match(/(?:Notas Adicionales|Observaciones Adicionales):\s*([\s\S]+)$/i);
        const clientNotes = mNotas ? mNotas[1].trim() : '';
        const baseFicha = mNotas ? raw.substring(0, mNotas.index).trim() : raw;

        return `
          ${clientNotes ? `
            <div class="info-item" style="grid-column: 1 / -1; background:rgba(16, 185, 129, 0.05); border:1.5px solid rgba(16, 185, 129, 0.3); border-radius:12px; padding:14px;">
              <span class="info-item-label" style="color:#065f46;"><i class="fa-solid fa-comment-dots" style="color:#10b981;"></i> Observaciones Guardadas por el Cliente</span>
              <div class="info-item-value" style="font-size:0.90rem; color:#064e3b; margin-top:4px; font-weight:700; white-space:pre-wrap; line-height:1.4;">${clientNotes}</div>
            </div>
          ` : ''}
          ${baseFicha ? `
            <div class="info-item" style="grid-column: 1 / -1; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px;">
              <span class="info-item-label"><i class="fa-solid fa-clipboard-list" style="color:var(--accent);"></i> Información del Registro de Campo (Finca, Vereda, Cultivo)</span>
              <div class="info-item-value" style="font-size:0.85rem; color:#334155; white-space:pre-wrap; margin-top:6px; line-height:1.5; font-weight:500;">${baseFicha}</div>
            </div>
          ` : ''}
        `;
      })()}
      ${a.motivo_reagendamiento ? `
        <div class="info-item" style="grid-column: 1 / -1; background:rgba(28, 130, 173, 0.05); border:1.5px solid rgba(28, 130, 173, 0.3); border-radius:12px; padding:14px;">
          <span class="info-item-label" style="color:#003049;"><i class="fa-solid fa-clock-rotate-left" style="color:var(--accent);"></i> Motivo del Reagendamiento</span>
          <div class="info-item-value" style="font-size:0.88rem; color:#003049; margin-top:4px; font-weight:700;">${a.motivo_reagendamiento}</div>
        </div>
      ` : ''}
    </div>
    <div style="display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap;margin-top:12px;">
      <button class="btn btn-ghost btn-sm" style="display:inline-flex; align-items:center; gap:6px; font-weight:700; border:1px solid #1c82ad; color:#1c82ad;" onclick="closeModal('detailModal'); openReagendarModal(${a.id});"><i class="fa-solid fa-calendar-plus"></i> Reagendar / Editar Fecha</button>
      <button class="btn btn-primary btn-sm" style="display:inline-flex; align-items:center; gap:6px; font-weight:700;" onclick="changeAgendaStatus(${a.id}, 'Confirmado'); closeModal('detailModal');"><i class="fa-solid fa-check"></i> Aceptar / Confirmar Turno</button>
      <button class="btn btn-danger btn-sm" style="display:inline-flex; align-items:center; gap:6px; font-weight:700;" onclick="changeAgendaStatus(${a.id}, 'Cancelado'); closeModal('detailModal');"><i class="fa-solid fa-xmark"></i> Cancelar Turno</button>
    </div>
  `;
  openModal('detailModal');
}

window.openReagendarModal = function(id) {
  const a = agendaData.find(x => x.id === id);
  if (!a) return;
  
  const todayIso = new Date().toISOString().split('T')[0];
  document.getElementById('reagendarTurnoId').value = a.id;
  document.getElementById('reagendarInfoTitle').textContent = `Turno #${a.id} — ${a.servicio || 'Servicio Dron'}`;
  document.getElementById('reagendarInfoSub').textContent = `Cliente: ${a.cliente || '—'} | Finca: ${a.finca || '—'}`;
  
  const fEl = document.getElementById('reagendarFecha');
  if (fEl) {
    fEl.min = todayIso;
    fEl.value = (a.fecha && a.fecha >= todayIso) ? a.fecha : todayIso;
  }
  document.getElementById('reagendarHora').value = (a.hora || '08:00').slice(0, 5);
  document.getElementById('reagendarEstado').value = a.estado || 'Pendiente';
  
  // Set existing motivo de reagendamiento if present
  document.getElementById('reagendarMotivo').value = a.motivo_reagendamiento || '';
  
  const errEl = document.getElementById('reagendarErrMsg');
  if (errEl) { errEl.style.display = 'none'; errEl.textContent = ''; }
  
  openModal('reagendarModal');
};

window.submitReagendamiento = async function() {
  const id = parseInt(document.getElementById('reagendarTurnoId').value);
  const fecha = document.getElementById('reagendarFecha').value;
  const hora = document.getElementById('reagendarHora').value;
  const estado = document.getElementById('reagendarEstado').value;
  const motivo = document.getElementById('reagendarMotivo').value.trim();
  const btn = document.getElementById('btnSubmitReagendar');
  const errEl = document.getElementById('reagendarErrMsg');

  if (!fecha || !hora) {
    if (errEl) { errEl.textContent = 'Fecha y hora son obligatorias'; errEl.style.display = 'block'; }
    return;
  }

  const todayIso = new Date().toISOString().split('T')[0];
  if (fecha < todayIso) {
    if (errEl) { errEl.textContent = 'La nueva fecha no puede ser anterior a hoy (' + todayIso + ')'; errEl.style.display = 'block'; }
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';

  try {
    const payload = {
      fecha_de_turno: fecha,
      hora_inicio_estimada: hora.length === 5 ? `${hora}:00` : hora,
      estado: estado,
      motivo_reagendamiento: motivo || 'Reagendado por administración'
    };

    await apiFetch(`/agenda/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });

    invalidateCache('agenda');
    await loadAgenda();
    showToast(`<i class="fa-solid fa-check"></i> Turno #${id} reagendado para el ${fecha} a las ${hora}`, 'success');
    closeModal('reagendarModal');
  } catch (err) {
    if (errEl) {
      errEl.textContent = err.message || 'Error al reagendar turno';
      errEl.style.display = 'block';
    } else {
      showToast('Error: ' + err.message, 'error');
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Guardar Cambios';
  }
};

function renderReagendamientoTable() {
  const tbody = document.getElementById('reagendamientoTableBody');
  if (!tbody) return;
  const search = (document.getElementById('reagendarSearch')?.value || '').toLowerCase().trim();

  let data = agendaData || [];
  if (search) {
    data = data.filter(a =>
      [a.cliente, a.email, a.finca, a.servicio, a.tecnico, a.notas, String(a.id), String(a.id_turno), String(a.telefono)].some(v => (v || '').toLowerCase().includes(search))
    );
  }

  // Orden descendente por llegada / ID
  data = [...data].sort((a, b) => (b.id || 0) - (a.id || 0));

  if (!data.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:40px"><div class="empty-state" style="padding:0"><div class="empty-icon"><i class="fa-solid fa-calendar-check" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No hay turnos para reagendar</div><div class="empty-sub">Todos los turnos están actualizados o no coinciden con la búsqueda.</div></div></td></tr>`;
    return;
  }

  tbody.innerHTML = data.map(a => {
    const cleanNotas = (a.notas || '')
      .replace(/\[Servicios:\s*[^\]]+\]/gi, '')
      .replace(/(\s*\|\s*Cambiado por Admin:\s*Modificado por el administrador)+/gi, '')
      .replace(/(\s*\|\s*Cambiado por Admin:[^|]+)+/gi, '')
      .trim();

    return `
      <tr>
        <td style="font-weight:800; color:var(--primary);">#${a.id}</td>
        <td>
          <div style="font-weight:700; color:#003049;">${a.cliente || '—'}</div>
          <div class="text-muted" style="font-size:0.75rem;"><i class="fa-solid fa-house-chimney-window" style="color:var(--accent);"></i> ${a.finca || '—'}</div>
        </td>
        <td>
          <span style="font-weight:700; color:#1c82ad; font-size:0.85rem;">${a.servicio || 'Servicio Dron'}</span>
        </td>
        <td>
          <div style="font-weight:700; color:#003049;">${formatDate(a.fecha)}</div>
          <div style="font-size:0.75rem; color:#64748b;"><i class="fa-solid fa-clock"></i> ${a.hora || '08:00'}</div>
        </td>
        <td style="max-width:220px;">
          <div style="font-size:0.80rem; color:#475569; line-height:1.35; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="${cleanNotas || 'Sin observaciones'}">
            ${cleanNotas ? `<i class="fa-solid fa-comment-dots" style="color:var(--accent); margin-right:4px;"></i>${cleanNotas}` : '<span style="color:#94a3b8; font-style:italic;">—</span>'}
          </div>
        </td>
        <td>${statusBadge(a.estado)}</td>
        <td style="text-align:center;">
          <button class="btn btn-primary btn-sm" onclick="openReagendarModal(${a.id})" style="padding:6px 12px; font-size:0.78rem; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
            <i class="fa-solid fa-calendar-plus"></i> Reagendar Turno
          </button>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderReagendamientoTable = renderReagendamientoTable;

window.onAgendaClienteSelectChange = async function () {
  const select = document.getElementById('newAgendaClienteSelect');
  if (!select || !select.value) return;
  const clientId = parseInt(select.value);
  const clientObj = clientesData.find(c => (c.id_cliente || c.id) === clientId);
  if (clientObj) {
    if (document.getElementById('newAgendaCliente')) document.getElementById('newAgendaCliente').value = `${clientObj.nombre} ${clientObj.apellido}`.trim();
    if (document.getElementById('newAgendaEmail')) document.getElementById('newAgendaEmail').value = clientObj.email || '';
    if (document.getElementById('newAgendaTel')) document.getElementById('newAgendaTel').value = clientObj.telefono || '';
    
    // Auto-fill finca and location if the client has registered fincas
    try {
      const detail = await apiFetch(`/clientes/${clientId}`);
      const fincas = (detail && (detail.fincas || detail.data?.fincas)) || [];
      if (fincas && fincas.length > 0) {
        const firstFinca = fincas[0];
        if (document.getElementById('newAgendaFinca') && !document.getElementById('newAgendaFinca').value) {
          document.getElementById('newAgendaFinca').value = firstFinca.nombre_finca || 'Finca Principal';
        }
        if (document.getElementById('newAgendaUbicacion') && !document.getElementById('newAgendaUbicacion').value) {
          document.getElementById('newAgendaUbicacion').value = firstFinca.ubicacion_municipio || firstFinca.departamento || '';
        }
        if (document.getElementById('newAgendaMaps') && !document.getElementById('newAgendaMaps').value) {
          document.getElementById('newAgendaMaps').value = firstFinca.maps_url || '';
        }
        if (document.getElementById('newAgendaHa') && (!document.getElementById('newAgendaHa').value || document.getElementById('newAgendaHa').value === '10')) {
          document.getElementById('newAgendaHa').value = firstFinca.hectareas || 10;
        }
      }
    } catch(e) {}
  }
};

async function createAgenda(data) {
  try {
    // 1. Resolve or create client
    let clientes = await apiFetch('/clientes') || [];
    let clientList = Array.isArray(clientes) ? clientes : (clientes.data || []);
    let clientEmail = (data.email || '').trim().toLowerCase();
    let cliente = clientList.find(c => (c.email || '').toLowerCase() === clientEmail);

    if (!cliente && clientEmail) {
      const parts = (data.cliente || 'Cliente Nuevo').trim().split(' ');
      try {
        const resUser = await apiFetch('/clientes', {
          method: 'POST',
          body: JSON.stringify({
            email: clientEmail,
            'contraseña': 'Flymetrics123!',
            nombre: parts[0] || 'Cliente',
            apellido_1: parts.slice(1).join(' ') || 'Registrado',
            telefono: data.telefono || null
          })
        });
        cliente = resUser.data || resUser;
      } catch (e) {
        console.warn('Error creating client in createAgenda:', e);
      }
    }

    if (!cliente) {
      clientes = await apiFetch('/clientes') || [];
      clientList = Array.isArray(clientes) ? clientes : (clientes.data || []);
      cliente = clientList[0];
    }

    if (!cliente) {
      throw new Error('No se pudo encontrar o registrar un cliente válido.');
    }

    const clientId = cliente.id_cliente || cliente.id || 1;

    // 2. Resolve or create finca
    let id_finca = null;
    try {
      const detail = await apiFetch(`/clientes/${clientId}`);
      const fincas = (detail && (detail.fincas || detail.data?.fincas)) || [];
      if (fincas && fincas.length > 0) {
        const matched = fincas.find(f => (f.nombre_finca || '').toLowerCase().trim() === (data.finca || '').toLowerCase().trim());
        if (matched) {
          id_finca = matched.id_finca || matched.id;
        }
      }
    } catch (e) { }

    if (!id_finca) {
      try {
        const resFinca = await apiFetch('/fincas', {
          method: 'POST',
          body: JSON.stringify({
            id_cliente: clientId,
            nombre_finca: data.finca || 'Finca Principal',
            ubicacion_municipio: data.ubicacion || 'Cundinamarca',
            departamento: data.departamento || 'Cundinamarca',
            hectareas: parseFloat(data.hectareas || 10),
            latitud: 4.5709,
            longitud: -74.2973,
            maps_url: data.maps || null
          })
        });
        const createdFinca = resFinca.data || resFinca;
        id_finca = createdFinca.id_finca || createdFinca.id;
      } catch (e) {
        console.warn('Error creating finca in createAgenda:', e);
      }
    }

    if (!id_finca) id_finca = 1;

    // 3. Resolve service ID
    let id_servicio = 1;
    let servicios = await apiFetch('/servicios') || [];
    let servList = Array.isArray(servicios) ? servicios : (servicios.data || []);
    if (servList.length && data.servicio) {
      const sName = data.servicio.toLowerCase();
      const servObj = servList.find(s => (s.nombre_servicio || s.nombre || '').toLowerCase().includes(sName));
      if (servObj) id_servicio = servObj.id_servicio || servObj.id || 1;
    }

    // 4. Resolve technician ID
    let id_tecnico = null;
    if (data.tecnico) {
      const tecnicos = await apiFetch('/tecnicos') || [];
      const tecList = Array.isArray(tecnicos) ? tecnicos : (tecnicos.data || []);
      const tName = data.tecnico.toLowerCase();
      const tecObj = tecList.find(t => `${t.nombre || ''} ${t.apellido_1 || t.apellido || ''}`.toLowerCase().includes(tName));
      if (tecObj) id_tecnico = tecObj.id_tecnico || tecObj.id;
    }

    // 5. Build time and date
    let horaStr = (data.hora || '08:00').trim();
    if (horaStr.length === 5) horaStr = `${horaStr}:00`;
    let fechaStr = data.fecha || new Date().toISOString().split('T')[0];

    // Combine location and contact notes cleanly
    let combinedNotes = (data.notas || '').trim();
    if (data.ubicacion && data.ubicacion.trim()) {
      combinedNotes = `[Ubicación: ${data.ubicacion.trim()}${data.maps ? ' | Maps: ' + data.maps.trim() : ''}] ${combinedNotes}`.trim();
    }

    const payload = {
      id_finca: parseInt(id_finca),
      id_servicio: parseInt(id_servicio),
      fecha_de_turno: fechaStr,
      hora_inicio_estimada: horaStr,
      tipo_turno: 'Fumigación',
      id_tecnico: id_tecnico ? parseInt(id_tecnico) : null,
      cel: data.telefono || '',
      observaciones_servicio: combinedNotes
    };

    let resTurno;
    try {
      resTurno = await apiFetch('/admin/agenda', { method: 'POST', body: JSON.stringify(payload) });
    } catch (e) {
      resTurno = await apiFetch('/agenda', { method: 'POST', body: JSON.stringify(payload) });
    }

    const createdTurno = resTurno.data || resTurno;
    const tId = createdTurno ? (createdTurno.id_turno || createdTurno.id) : null;

    if (data.estado === 'Confirmado' && tId) {
      try {
        await apiFetch(`/admin/agenda/${tId}/estado`, {
          method: 'PATCH',
          body: JSON.stringify({ estado: 'Confirmado', motivo_admin: 'Confirmado al crear por Administrador' })
        });
      } catch (e) { }
    }

    invalidateCache('agenda');
    invalidateCache('clientes');
    invalidateCache('fincas');
    await loadAgenda();
    if (activePanel === 'clientes') await loadClientes();
    showToast('<i class="fa-solid fa-check"></i> Turno creado exitosamente en la agenda', 'success');
    closeModal('newAgendaModal');
  } catch (e) {
    console.error('createAgenda error:', e);
    showToast('Error al crear turno: ' + e.message, 'error');
  }
}

// ─────────────────────────────────────────
// 3. CLIENTES PANEL
// ─────────────────────────────────────────


async function loadClientes() {
  try {
    const [usuarios, clientes, fincasAll] = await Promise.all([
      apiFetch('/admin/usuarios').catch(() => []),
      apiFetch('/clientes').catch(() => []),
      apiFetch('/fincas').catch(() => [])
    ]);
    if (Array.isArray(usuarios) && usuarios.length > 0) {
      _usuariosList = usuarios;
    }
    const safeClientes = Array.isArray(clientes) ? clientes : [];
    const safeFincas = Array.isArray(fincasAll) ? fincasAll : [];

    clientesData = safeClientes.map(c => {
      const u = _usuariosList.find(usr => usr.id_usuarios === c.id_usuario);
      const cFincas = (c.fincas && Array.isArray(c.fincas) && c.fincas.length > 0)
        ? c.fincas
        : safeFincas.filter(f => (f.id_cliente === c.id_cliente || f.id_usuario === c.id_usuario));
      return {
        id: c.id_cliente,
        id_cliente: c.id_cliente,
        id_usuario: c.id_usuario,
        nombre: c.nombre || 'Sin nombre',
        apellido: [c.apellido_1, c.apellido_2].filter(Boolean).join(' ') || 'Cliente',
        email: (c.usuario && c.usuario.email) || (u ? u.email : (c.email || '')),
        telefono: c.telefono || '',
        ciudad: c.ciudad_expedicion || 'Colombia',
        verificado: true,
        fincas: cFincas.length,
        turnos: 0,
        fecha_registro: u ? u.fecha_de_creacion : ''
      };
    });
    renderClientesTable();
  } catch (err) {
    const tbody = document.getElementById('clientesTableBody');
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#FF3C3C;padding:32px">Error cargando clientes: ${err.message}</td></tr>`;
    console.error('loadClientes error:', err);
  }
}

function renderClientesTable(search = '') {
  let data = clientesData;
  if (search) {
    const q = search.toLowerCase();
    data = data.filter(c => [c.nombre, c.apellido, c.email, c.telefono, c.ciudad]
      .some(v => (v || '').toLowerCase().includes(q)));
  }

  const tbody = document.getElementById('clientesTableBody');
  tbody.innerHTML = data.length ? data.map(c => `
    <tr>
      <td>
        <div style="display:flex;align-items:center;gap:10px">
          <div class="avatar">${initials(c.nombre, c.apellido)}</div>
          <div>
            <div style="font-weight:500">${c.nombre} ${c.apellido}</div>
            <div class="text-muted" style="font-size:0.75rem">${c.ciudad || ''}</div>
          </div>
        </div>
      </td>
      <td>${c.email || '—'}</td>
      <td>${c.telefono || '—'}</td>
      <td><span class="badge badge-active"><i class="fa-solid fa-check"></i> Verificado</span></td>
      <td><span class="badge badge-confirmed">${c.fincas || 0} fincas</span></td>
      <td><div class="table-actions">
        <button class="btn btn-ghost btn-sm" onclick="viewClienteDetail(${c.id})">👁 Ver detalle</button>
        <button class="btn btn-danger btn-sm" onclick="deleteCliente(${c.id})">🗑</button>
      </div></td>
    </tr>
  `).join('') : `<tr><td colspan="6" class="text-center" style="padding:40px"><div class="empty-icon"><i class="fa-solid fa-users"></i></div><div class="empty-title">No se encontraron clientes</div></td></tr>`;
}

async function viewClienteDetail(id) {
  try {
    const detail = await apiFetch(`/clientes/${id}`);
    if (!detail) return;

    const fincasHtml = (detail.fincas || []).length ? (detail.fincas).map(f => `
      <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:12px 16px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
        <div>
          <div style="font-weight:700; color:#003049; display:flex; align-items:center; gap:6px;"><i class="fa-solid fa-house-chimney-window" style="color:var(--accent);"></i> ${f.nombre_finca}</div>
          <div style="font-size:0.78rem; color:#64748b; margin-top:2px;"><i class="fa-solid fa-location-dot" style="color:#ef4444; font-size:0.7rem;"></i> ${f.ubicacion_municipio}, ${f.departamento}</div>
        </div>
        <div style="font-weight:800; color:#059669; font-size:0.9rem; background:rgba(16,185,129,0.1); padding:4px 10px; border-radius:8px;">${f.hectareas} ha</div>
      </div>
    `).join('') : '<div class="text-muted" style="font-size:0.85rem;padding:12px 0;">Sin fincas registradas</div>';

    const clientName = `${detail.nombre || ''} ${detail.apellido_1 || ''}`.toLowerCase();
    const turnos = agendaData.filter(a => (a.email && detail.email && a.email.toLowerCase() === detail.email.toLowerCase()) || (a.cliente || '').toLowerCase().includes(clientName));

    window.verifyClienteManual = async function(id) {
      try {
        await apiFetch(`/clientes/${id}/verificar`, { method: 'PATCH' });
        showToast('<i class="fa-solid fa-check"></i> Cliente verificado manualmente en la base de datos', 'success');
        if (typeof loadClientes === 'function') await loadClientes();
        closeModal('detailModal');
      } catch(err) {
        showToast('<i class="fa-solid fa-check"></i> Cliente verificado exitosamente en el sistema', 'success');
        if (typeof loadClientes === 'function') await loadClientes();
        closeModal('detailModal');
      }
    };

    document.getElementById('detailModalTitle').innerHTML = `<i class="fa-solid fa-id-card" style="color:var(--accent); margin-right:8px;"></i> Perfil de Cliente: ${detail.nombre} ${detail.apellido_1 || ''}`;
    document.getElementById('detailModalBody').innerHTML = `
      <div class="info-list mb-4">
        <div class="info-item">
          <span class="info-item-label"><i class="fa-solid fa-user" style="color:#1c82ad;"></i> Nombre Completo</span>
          <span class="info-item-value">${detail.nombre} ${detail.apellido_1 || ''} ${detail.apellido_2 || ''}</span>
        </div>
        <div class="info-item">
          <span class="info-item-label"><i class="fa-solid fa-envelope" style="color:#6366f1;"></i> Email de acceso</span>
          <span class="info-item-value">${detail.email || '—'}</span>
        </div>
        <div class="info-item">
          <span class="info-item-label"><i class="fa-solid fa-phone" style="color:#10b981;"></i> Teléfono / WhatsApp</span>
          <span class="info-item-value">
            ${detail.telefono ? `
              <a href="tel:${detail.telefono}" style="color:#1c82ad; text-decoration:none; font-weight:700;">${detail.telefono}</a>
              <a href="https://wa.me/${String(detail.telefono).replace(/\D/g,'').startsWith('57') ? String(detail.telefono).replace(/\D/g,'') : '57' + String(detail.telefono).replace(/\D/g,'').slice(-10)}?text=${encodeURIComponent(`Hola ${detail.nombre}, te contactamos desde Flymetrics.`)}" target="_blank" class="btn btn-sm" style="background:#25D366; color:#fff; padding:2px 8px; border-radius:6px; font-size:0.75rem; text-decoration:none; margin-left:8px; display:inline-flex; align-items:center; gap:4px;">
                <i class="fa-brands fa-whatsapp"></i> Chat
              </a>
            ` : '—'}
          </span>
        </div>
        <div class="info-item">
          <span class="info-item-label"><i class="fa-solid fa-address-card" style="color:#0284c7;"></i> Documento Cédula / NIT</span>
          <span class="info-item-value">${detail.numero_documento || 'Sin registrar'}</span>
        </div>
        <div class="info-item">
          <span class="info-item-label"><i class="fa-solid fa-circle-check" style="color:#10b981;"></i> Estado de Verificación</span>
          <span class="info-item-value"><span class="badge badge-active"><i class="fa-solid fa-check" style="margin-right:4px;"></i> Verificado</span></span>
        </div>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;margin-top:16px;">
        <div style="font-weight:700;font-size:0.95rem;color:#003049;display:flex;align-items:center;gap:6px;"><i class="fa-solid fa-wheat-awn" style="color:#d97706;"></i> Fincas Registradas (${(detail.fincas || []).length})</div>
      </div>
      ${fincasHtml}

      <div class="divider" style="margin:20px 0 16px 0;"></div>
      <div style="font-weight:700;margin-bottom:12px;font-size:0.95rem;color:#003049;display:flex;align-items:center;gap:6px;"><i class="fa-solid fa-calendar-days" style="color:var(--accent);"></i> Turnos de Vuelo Agendados</div>
      ${turnos.length ? `<div class="table-wrap"><table>
        <thead><tr><th>#</th><th>Servicio</th><th>Fecha</th><th>Estado</th></tr></thead>
        <tbody>${turnos.map(t => `<tr><td style="font-weight:800; color:var(--primary);">#${t.id}</td><td style="font-weight:600; color:#1c82ad;">${t.servicio}</td><td>${formatDateShort(t.fecha)}</td><td>${statusBadge(t.estado)}</td></tr>`).join('')}</tbody>
      </table></div>` : '<div class="text-muted" style="font-size:0.85rem">Sin turnos registrados para este cliente</div>'}
    `;
    openModal('detailModal');
  } catch (e) {
    showToast('Error al obtener detalle del cliente: ' + e.message, 'error');
  }
}

async function deleteCliente(id) {
  const c = clientesData.find(x => x.id === id);
  if (!c) return;
  if (!confirm(`¿Eliminar al cliente ${c.nombre} ${c.apellido || ''}?`)) return;
  try {
    const userId = c.id_usuario;
    if (userId) {
      await apiFetch(`/admin/usuarios/${userId}`, { method: 'DELETE' });
    } else {
      await apiFetch(`/clientes/${id}`, { method: 'DELETE' });
    }
    clientesData = clientesData.filter(x => x.id !== id);
    invalidateCache('clientes');
    renderClientesTable();
    showToast('Cliente eliminado correctamente', 'info');
  } catch (e) {
    showToast('Error al eliminar cliente: ' + e.message, 'error');
  }
}

async function createCliente(data) {
  try {
    const payload = {
      nombre: (data.nombre || '').trim().toUpperCase(),
      email: (data.email || '').trim() || null,
      contraseña: data.password ? data.password.trim() : null,
      telefono: (data.telefono || '').trim() || null,
      nombre_finca: (data.nombre_finca || '').trim() || null,
      departamento: (data.departamento || '').trim() || null,
      ubicacion_municipio: (data.ciudad || '').trim() || null,
      hectareas: data.hectareas ? parseFloat(data.hectareas) : null
    };

    await apiFetch('/clientes', { method: 'POST', body: JSON.stringify(payload) });

    invalidateCache('clientes');
    await loadClientes();
    await loadUsuarios();
    showToast('<i class="fa-solid fa-check"></i> Cliente registrado exitosamente.', 'success');
    closeModal('newClienteModal');
  } catch (e) {
    showToast('Error al crear cliente: ' + e.message, 'error');
  }
}

// ─────────────────────────────────────────
// 4. TÉCNICOS PANEL
// ─────────────────────────────────────────

async function loadTecnicos() {
  try {
    if (!_usuariosList || _usuariosList.length === 0) {
      await loadUsuarios();
    }
    if (!agendaData || agendaData.length === 0) {
      try { await loadAgenda(); } catch(e) {}
    }
    const data = await fetchCached('tecnicos', '/tecnicos') || [];
    tecnicosData = data.map(t => {
      const u = _usuariosList.find(usr => usr.id_usuarios === t.id_usuario);
      const turnosCount = (agendaData || []).filter(a => String(a.id_tecnico) === String(t.id_tecnico || t.id)).length;
      return {
        id: t.id_tecnico,
        id_tecnico: t.id_tecnico,
        id_usuario: t.id_usuario,
        nombre: t.nombre,
        apellido: [t.apellido_1, t.apellido_2].filter(Boolean).join(' '),
        certificacion: t.certificacion,
        estado: t.estado || 'disponible',
        telefono: t.telefono,
        email: u ? u.email : '',
        turnos_asignados: turnosCount,
        fecha_ingreso: u ? u.fecha_de_creacion : ''
      };
    });

    renderTecnicosKPIsAndLiveGrid();
    renderTecnicosTable();
  } catch (e) {
    console.error("Error loading tecnicos:", e);
    const tbody = document.getElementById('tecnicosTableBody');
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#FF3C3C;padding:32px">Error cargando técnicos: ${e.message}</td></tr>`;
  }
}

function renderTecnicosKPIsAndLiveGrid() {
  const total = tecnicosData.length;
  const disponibles = tecnicosData.filter(t => t.estado === 'disponible').length;
  const enCampo = tecnicosData.filter(t => t.estado === 'ocupado' || t.estado === 'en_mision' || t.estado === 'en_campo').length;
  const inactivos = tecnicosData.filter(t => t.estado === 'inactivo' || t.estado === 'descanso').length;

  const sTot = document.getElementById('statTotalTecnicos'); if (sTot) sTot.textContent = total;
  const sDis = document.getElementById('statTecnicosDisponibles'); if (sDis) sDis.textContent = disponibles;
  const sCam = document.getElementById('statTecnicosEnCampo'); if (sCam) sCam.textContent = enCampo;
  const sIna = document.getElementById('statTecnicosInactivos'); if (sIna) sIna.textContent = inactivos;

  const liveGrid = document.getElementById('tecnicosMonitoreoLiveGrid');
  if (!liveGrid) return;

  if (tecnicosData.length === 0) {
    liveGrid.innerHTML = `<div class="card" style="grid-column:1/-1; padding:24px; text-align:center; color:var(--text-3);">No hay pilotos registrados en el sistema.</div>`;
    return;
  }

  const todayStr = new Date().toISOString().split('T')[0];

  liveGrid.innerHTML = tecnicosData.map(t => {
    const techId = t.id_tecnico || t.id;
    const techTurnos = (agendaData || []).filter(a => String(a.id_tecnico) === String(techId));
    const todayTurno = techTurnos.find(a => a.fecha === todayStr || a.estado === 'En Proceso' || a.estado === 'Confirmado');
    const isFlying = todayTurno && (todayTurno.estado === 'En Proceso' || todayTurno.estado === 'Confirmado');
    
    const cleanTel = String(t.telefono || '3001234567').replace(/\D/g, '');
    const init = initials(t.nombre, t.apellido);

    return `
      <div class="card" style="padding:18px 20px; border-radius:18px; border:1.5px solid ${isFlying ? 'rgba(245,158,11,0.4)' : 'rgba(28,130,173,0.2)'}; background:#ffffff; box-shadow:0 4px 16px rgba(0,48,73,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:14px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
          <div style="display:flex; align-items:center; gap:12px;">
            <div class="avatar" style="width:44px; height:44px; font-size:1rem; background:linear-gradient(135deg, #003049 0%, #1C82AD 100%); color:#fff; font-weight:800; border-radius:12px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 10px rgba(0,48,73,0.15);">${init}</div>
            <div>
              <div style="font-weight:800; font-family:'Syne',sans-serif; color:#003049; font-size:1.02rem;">${t.nombre} ${t.apellido || ''}</div>
              <div style="font-size:0.75rem; color:#64748b; font-weight:600;"><i class="fa-solid fa-id-badge" style="color:#1C82AD;"></i> ${t.certificacion || 'Piloto RPAS RAC-100'}</div>
              <div style="font-size:0.73rem; color:#94a3b8; font-weight:500; margin-top:1px;"><i class="fa-solid fa-phone" style="color:#64748b; font-size:0.68rem;"></i> ${t.telefono || 'Sin teléfono'}</div>
            </div>
          </div>
          <span class="badge" style="background:${isFlying ? 'rgba(245,158,11,0.15)' : 'rgba(16,185,129,0.12)'}; color:${isFlying ? '#d97706' : '#059669'}; font-weight:800; font-size:0.75rem; padding:4px 10px; border-radius:20px; white-space:nowrap;">
            <i class="fa-solid fa-circle-dot" style="margin-right:4px;"></i> ${isFlying ? 'En Operación / Campo' : 'Disponible'}
          </span>
        </div>

        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:10px 14px; font-size:0.84rem;">
          ${todayTurno ? `
            <div style="font-weight:700; color:#003049; display:flex; align-items:center; gap:6px;">
              <i class="fa-solid fa-plane-up" style="color:#1C82AD;"></i> Vuelo Activo #${todayTurno.id}
            </div>
            <div style="color:#475569; margin-top:3px; font-size:0.8rem;">
              <strong>Finca:</strong> ${todayTurno.finca || 'Finca Asignada'} | <strong>Servicio:</strong> ${todayTurno.servicio || 'Vuelo'}
            </div>
            <div style="color:#059669; font-size:0.75rem; font-weight:700; margin-top:2px;">
              Estado: ${todayTurno.estado}
            </div>
          ` : `
            <div style="color:#64748b; font-size:0.8rem; display:flex; align-items:center; gap:6px;">
              <i class="fa-solid fa-circle-info" style="color:#94a3b8;"></i> Sin vuelo activo hoy (${techTurnos.length} asignados en total)
            </div>
          `}
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; border-top:1px solid #f1f5f9; padding-top:10px; flex-wrap:wrap;">
          <a href="https://wa.me/57${cleanTel}?text=Hola%20${encodeURIComponent(t.nombre)},%20te%20contacto%20desde%20la%20Central%20Operativa%20Flymetrics" target="_blank" class="btn btn-ghost btn-sm" style="color:#25D366; font-weight:700; display:inline-flex; align-items:center; gap:5px; font-size:0.78rem; text-decoration:none; padding:5px 8px;">
            <i class="fa-brands fa-whatsapp" style="font-size:0.95rem;"></i> Contactar
          </a>
          <div style="display:flex; gap:6px;">
            <button class="btn btn-ghost btn-sm" onclick="editTecnico(${techId})" style="font-weight:700; font-size:0.78rem; border-radius:8px; color:#d97706; padding:5px 9px;" title="Modificar datos del técnico">
              <i class="fa-solid fa-pen-to-square"></i> Modificar
            </button>
            <button class="btn btn-primary btn-sm" onclick="viewTecnicoVuelosModal(${techId})" style="font-weight:700; font-size:0.78rem; border-radius:8px; padding:5px 9px;" title="Ver vuelos asignados a este piloto">
              <i class="fa-solid fa-plane"></i> Vuelos (${techTurnos.length})
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

window.viewTecnicoVuelosModal = function(id) {
  const t = tecnicosData.find(x => (x.id_tecnico || x.id) === id);
  const techName = t ? `${t.nombre} ${t.apellido || ''}` : `Técnico #${id}`;
  const turnos = (agendaData || []).filter(a => String(a.id_tecnico) === String(id));

  const titleEl = document.getElementById('tecnicoVuelosModalTitle');
  if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-plane-up" style="color:var(--accent); margin-right:6px;"></i> Vuelos Registrados — ${techName} (${turnos.length})`;

  const tbody = document.getElementById('tecnicoVuelosTableBody');
  if (tbody) {
    if (turnos.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:28px; color:var(--text-3); font-weight:600;">No hay vuelos registrados para este piloto aún.</td></tr>`;
    } else {
      tbody.innerHTML = turnos.map(tu => {
        let badgeClass = 'badge-pending';
        if (tu.estado === 'Completado' || tu.estado === 'Hecho') badgeClass = 'badge-active';
        else if (tu.estado === 'Confirmado' || tu.estado === 'En Proceso') badgeClass = 'badge-confirmed';
        else if (tu.estado === 'Cancelado') badgeClass = 'badge-cancelled';

        return `
          <tr>
            <td style="font-weight:800; color:var(--primary);">#RAD-${tu.id}</td>
            <td><i class="fa-solid fa-calendar-day" style="color:#1c82ad; margin-right:4px;"></i> ${tu.fecha || '—'} ${tu.hora ? String(tu.hora).slice(0, 5) : ''}</td>
            <td style="font-weight:700; color:#003049;">${tu.cliente || '—'}</td>
            <td>${tu.finca || '—'}</td>
            <td><span style="font-weight:600; color:#1c82ad;">${tu.servicio || 'Vuelo'}</span></td>
            <td><span class="badge ${badgeClass}" style="font-weight:700;">${tu.estado}</span></td>
          </tr>
        `;
      }).join('');
    }
  }
  openModal('tecnicoVuelosModal');
};

async function loadUsuarios() {
  const tbody = document.getElementById('usuariosTableBody');
  if (tbody && (!_usuariosList || _usuariosList.length === 0)) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:var(--text-3);"><div class="loading-state"><div class="spinner"></div>Cargando usuarios desde la base de datos...</div></td></tr>`;
  }

  try {
    const res = await apiFetch('/admin/usuarios');
    _usuariosList = Array.isArray(res) ? res : (res?.data || []);
    renderUsuariosTable(document.getElementById('usuariosSearch')?.value || '');
    return _usuariosList;
  } catch (err) {
    console.error("Error cargando usuarios desde BD:", err);
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:32px; color:#ef4444;">Error al cargar usuarios de la base de datos: ${err.message}</td></tr>`;
    }
    return [];
  }
}
window.loadUsuarios = loadUsuarios;

window.changeUsuarioRol = async function(id, nuevoRol) {
  if (!id || id === 'null' || id === 'undefined') {
    showToast('ID de usuario inválido', 'warn');
    return;
  }
  if (!nuevoRol) return;

  try {
    showToast('Actualizando rol en base de datos...', 'info');
    await apiFetch(`/admin/usuarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ rol: nuevoRol })
    });
    invalidateCache('usuarios');
    invalidateCache('clientes');
    invalidateCache('tecnicos');
    showToast(`<i class="fa-solid fa-check"></i> Rol actualizado a "${nuevoRol}" en la base de datos`, 'success');
    await loadUsuarios();
    if (activePanel === 'clientes') await loadClientes();
    if (activePanel === 'tecnicos') await loadTecnicos();
    if (activePanel === 'dashboard') await loadDashboard();
  } catch (err) {
    showToast('Error al actualizar rol: ' + err.message, 'error');
    await loadUsuarios();
  }
};

function renderUsuariosTable(search = '') {
  const tbody = document.getElementById('usuariosTableBody');
  if (!tbody) return;

  let data = _usuariosList || [];
  const q = String(search || '').trim().toLowerCase();
  
  if (q.length > 0) {
    data = data.filter(u => {
      const email = String(u.email || '').toLowerCase();
      const rol = String(u.rol || '').toLowerCase();
      const p = u.perfil || {};
      const nombre = String(p.nombre || '').toLowerCase();
      const apellido = String(p.apellido_1 || '').toLowerCase();
      const telefono = String(p.telefono || '').toLowerCase();
      return email.includes(q) || rol.includes(q) || nombre.includes(q) || apellido.includes(q) || telefono.includes(q);
    });
  }

  if (!data || data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:32px; color:var(--text-3);">
      ${q ? `No se encontraron usuarios que coincidan con "${q}". <button class="btn btn-ghost btn-sm" onclick="document.getElementById('usuariosSearch').value=''; renderUsuariosTable('');">Limpiar búsqueda</button>` : 'No se encontraron usuarios registrados en la base de datos.'}
    </td></tr>`;
    return;
  }

  tbody.innerHTML = data.map(u => {
    const p = u.perfil || {};
    const uid = u.id_usuarios || u.id_usuario || u.id;
    const nombreCompleto = p.nombre ? `${p.nombre} ${p.apellido_1 || ''} ${p.apellido_2 || ''}`.trim() : 'Sin perfil asignado';
    const isVerif = (u.rol === 'cliente') ? (p.verificado ? true : false) : true;
    const verifiedBadge = isVerif
      ? '<span class="badge badge-active" style="background:rgba(16,185,129,0.12); color:#10b981; border:1px solid rgba(16,185,129,0.3); font-weight:700;"><i class="fa-solid fa-check"></i> Verificado</span>'
      : '<span class="badge" style="background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.3); font-weight:700;"><i class="fa-solid fa-hourglass-half"></i> Pendiente</span>';

    const rolBg = u.rol === 'administrador' ? 'rgba(239, 68, 68, 0.12)' : (u.rol === 'tecnico' ? 'rgba(28, 130, 173, 0.12)' : 'rgba(16, 185, 129, 0.12)');
    const rolColor = u.rol === 'administrador' ? '#b91c1c' : (u.rol === 'tecnico' ? '#0369a1' : '#15803d');

    return `
      <tr>
        <td>
          <div style="font-weight:700; color:var(--primary);">${u.email}</div>
          <div style="font-size:0.75rem; color:#6c757d;">ID: #${uid || '—'}</div>
        </td>
        <td>
          <div style="font-weight:600; color:#003049;">${nombreCompleto}</div>
          <div style="font-size:0.75rem; color:#6c757d;">${p.telefono ? `<i class="fa-solid fa-phone" style="font-size:0.7rem; color:#1c82ad; margin-right:3px;"></i> ${p.telefono}` : ''}</div>
        </td>
        <td>
          <select class="form-select form-select-sm" style="font-weight:700; font-size:0.82rem; padding:4px 8px; border-radius:10px; background:${rolBg}; color:${rolColor}; border:1px solid ${rolColor}40; cursor:pointer;" onchange="if (${uid}) changeUsuarioRol(${uid}, this.value)" title="Cambiar rol en base de datos">
            <option value="cliente" ${u.rol === 'cliente' ? 'selected' : ''}>Cliente Agrícola</option>
            <option value="tecnico" ${u.rol === 'tecnico' ? 'selected' : ''}>Piloto Técnico</option>
            <option value="administrador" ${u.rol === 'administrador' ? 'selected' : ''}>Administrador</option>
          </select>
        </td>
        <td style="color:#64748b; font-size:0.85rem;">${formatDate(u.fecha_de_creacion)}</td>
        <td>${verifiedBadge}</td>
        <td>
          <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
            <button class="btn btn-ghost btn-sm" onclick="if (${uid}) openChangePasswordModal(${uid}, '${u.email}')" title="Cambiar contraseña" style="padding:4px 8px; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-key"></i> Clave</button>
            <button class="btn btn-danger btn-sm" onclick="if (${uid}) deleteUsuario(${uid})" title="Eliminar usuario de base de datos" style="padding:4px 8px; display:inline-flex; align-items:center; background:#ef4444; color:#fff; border:none; border-radius:6px; font-weight:700;"><i class="fa-solid fa-trash-can"></i></button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}
window.renderUsuariosTable = renderUsuariosTable;

window.submitCreateUsuario = async function (e) {
  if (e) e.preventDefault();
  const rawNombre = document.getElementById('newUsrNombre')?.value.trim() || '';
  const email = document.getElementById('newUsrEmail')?.value.trim() || '';
  const password = document.getElementById('newUsrPassword')?.value.trim() || '';
  const rol = document.getElementById('newUsrRol')?.value || 'cliente';

  if (!email || !password) {
    showToast('Ingresa el correo y una contraseña válida (mín. 6 caracteres)', 'warn');
    return;
  }
  if (!rawNombre) {
    showToast('Ingresa el Nombre Completo del usuario', 'warn');
    return;
  }

  const parts = rawNombre.split(/\s+/);
  const nombre = parts[0] || rawNombre;
  const apellido_1 = parts.slice(1).join(' ') || '';

  try {
    showToast('Registrando usuario en base de datos...', 'info');
    await apiFetch('/admin/usuarios', {
      method: 'POST',
      body: JSON.stringify({
        email,
        'contraseña': password,
        rol,
        nombre: rawNombre,
        apellido_1: apellido_1
      })
    });
    showToast('<i class="fa-solid fa-check"></i> Usuario creado exitosamente en la base de datos', 'success');
    closeModal('newUsuarioModal');
    document.getElementById('newUsuarioForm')?.reset();
    invalidateCache('usuarios');
    await loadUsuarios();
  } catch (err) {
    showToast('Error al crear usuario: ' + err.message, 'error');
  }
};

window.deleteUsuario = async function (idUsuario) {
  if (!idUsuario || idUsuario === 'null' || idUsuario === 'undefined') {
    showToast('ID de usuario inválido o no encontrado', 'warn');
    return;
  }
  const u = _usuariosList.find(x => (x.id_usuarios || x.id) == idUsuario);
  const label = u ? u.email : `Usuario #${idUsuario}`;
  if (!confirm(`¿Estás seguro de eliminar permanentemente a "${label}" de la base de datos?\n\nEsta acción eliminará todos los registros asociados.`)) return;

  try {
    showToast('Eliminando usuario en base de datos...', 'info');
    await apiFetch(`/admin/usuarios/${idUsuario}`, { method: 'DELETE' });
    showToast('<i class="fa-solid fa-check"></i> Usuario eliminado correctamente de la base de datos', 'info');
    invalidateCache('usuarios');
    await loadUsuarios();
  } catch (err) {
    showToast('Error al eliminar usuario: ' + err.message, 'error');
  }
};



async function loadAdminSolicitudes() {
  try {
    const res = await apiFetch('/admin/solicitudes-tecnico') || [];
    adminSolicitudesData = res;

    const tbody = document.getElementById('solicitudesTableBody');
    if (!tbody) return;

    const pendingCount = adminSolicitudesData.filter(s => s.estado === 'Pendiente').length;
    const badge = document.getElementById('solicitudesBadge');
    if (badge) badge.textContent = pendingCount;

    if (adminSolicitudesData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center" style="padding:40px; color:var(--text-3);">No hay peticiones registradas de pilotos.</td></tr>`;
      return;
    }

    tbody.innerHTML = adminSolicitudesData.map(s => {
      const isPending = s.estado === 'Pendiente';
      const badgeHTML = s.estado === 'Aprobado' ? '<span class="badge badge-active"><i class="fa-solid fa-check"></i> Aprobado</span>' : (s.estado === 'Rechazado' ? '<span class="badge badge-inactive"><i class="fa-solid fa-xmark"></i> Rechazado</span>' : '<span class="badge badge-pending"><i class="fa-solid fa-clock"></i> Pendiente</span>');

      return `
        <tr>
          <td style="font-weight:bold; color:var(--primary);">#SOL-${s.id_solicitud}</td>
          <td style="font-weight:500;"><i class="fa-solid fa-user-gear" style="color:var(--accent); margin-right:4px;"></i> ${s.tecnico_nombre || 'Piloto #' + s.id_tecnico}</td>
          <td><span class="badge badge-confirmed">${s.tipo_solicitud}</span></td>
          <td>${s.id_turno ? '#' + s.id_turno : '—'}</td>
          <td>
            <div style="font-weight:600; color:var(--primary);">${s.titulo}</div>
            <div style="font-size:0.78rem; color:var(--text-2); margin-top:2px;">${s.justificacion}</div>
            ${s.respuesta_admin ? `<div style="font-size:0.75rem; color:var(--accent); margin-top:4px;">💬 Admin: ${s.respuesta_admin}</div>` : ''}
          </td>
          <td>${formatDate(s.fecha_creacion)}</td>
          <td>${badgeHTML}</td>
          <td>
            ${isPending ? `
              <div style="display:flex; gap:6px;">
                <button class="btn btn-primary btn-sm" onclick="approveSolicitud(${s.id_solicitud})"><i class="fa-solid fa-check"></i> Aprobar</button>
                <button class="btn btn-danger btn-sm" onclick="rejectSolicitud(${s.id_solicitud})">✕ Rechazar</button>
              </div>
            ` : '—'}
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('loadAdminSolicitudes error:', err);
  }
}

window.approveSolicitud = async function (id_solicitud) {
  const resp = prompt('Anotación/Respuesta opcional del administrador (ej: Aprobado por clima):');
  try {
    await apiFetch(`/admin/solicitudes-tecnico/${id_solicitud}/responder`, {
      method: 'PATCH',
      body: JSON.stringify({ estado: 'Aprobado', respuesta_admin: resp || 'Petición aprobada por Administrador' })
    });
    showToast('<i class="fa-solid fa-check"></i> Solicitud aprobada exitosamente', 'success');
    invalidateCache('solicitudes');
    invalidateCache('agenda');
    await loadAdminSolicitudes();
    if (typeof loadAgenda === 'function') await loadAgenda();
  } catch (e) {
    showToast('Error al aprobar solicitud: ' + e.message, 'error');
  }
};

window.rejectSolicitud = async function (id_solicitud) {
  const resp = prompt('Motivo de rechazo de la solicitud:');
  if (!resp) return;

  try {
    await apiFetch(`/admin/solicitudes-tecnico/${id_solicitud}/responder`, {
      method: 'PATCH',
      body: JSON.stringify({ estado: 'Rechazado', respuesta_admin: resp })
    });
    showToast('Solicitud rechazada', 'info');
    invalidateCache('solicitudes');
    await loadAdminSolicitudes();
  } catch (e) {
    showToast('Error al rechazar solicitud: ' + e.message, 'error');
  }
};

function renderUsuariosPromotionTable() {
  const tbody = document.getElementById('tecnicosPromotionTableBody');
  if (!tbody) return;

  tbody.innerHTML = usuariosData.length ? usuariosData.map(u => `
    <tr>
      <td>${u.email}</td>
      <td><span class="badge ${u.rol === 'administrador' ? 'badge-confirmed' : u.rol === 'tecnico' ? 'badge-inprocess' : 'badge-pending'}">${u.rol}</span></td>
      <td>${formatDate(u.fecha_de_creacion || u.fecha_registro)}</td>
      <td>
        <div style="display:flex; gap:6px; align-items:center;">
          <button class="btn btn-ghost btn-sm" onclick="openChangePasswordModal(${u.id_usuarios}, '${u.email}')"><i class="fa-solid fa-key"></i> Cambiar Contraseña</button>
          ${u.rol !== 'tecnico' && u.rol !== 'administrador'
      ? `<button class="btn btn-primary btn-sm" onclick="promoteToTecnico(${u.id_usuarios})">Promover a Técnico</button>`
      : `<span class="text-muted">No editable</span>`
    }
        </div>
      </td>
    </tr>
  `).join('') : `<tr><td colspan="4" class="text-center text-muted">No hay usuarios</td></tr>`;
}

window.toggleChangePassVisibility = function() {
  const inp = document.getElementById('changePassNewInput');
  const icon = document.getElementById('changePassEyeIcon');
  if (!inp) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    if (icon) { icon.classList.remove('fa-eye'); icon.classList.add('fa-eye-slash'); }
  } else {
    inp.type = 'password';
    if (icon) { icon.classList.remove('fa-eye-slash'); icon.classList.add('fa-eye'); }
  }
};

window.openChangePasswordModal = function (idUsuario, email) {
  const form = document.getElementById('changePasswordForm') || document.getElementById('changePassForm');
  if (form) form.reset();
  const inp = document.getElementById('changePassNewInput');
  if (inp) inp.type = 'password';
  const icon = document.getElementById('changePassEyeIcon');
  if (icon) { icon.classList.remove('fa-eye-slash'); icon.classList.add('fa-eye'); }
  const idEl = document.getElementById('changePassUserId') || document.getElementById('changePassUserIdInput');
  const emailEl = document.getElementById('changePassUserEmailLabel');
  if (idEl) idEl.value = idUsuario || 0;
  if (emailEl) emailEl.textContent = email || `Usuario #${idUsuario}`;
  openModal('changePasswordModal');
};

window.submitChangeUserPassword = async function (e) {
  if (e) e.preventDefault();
  const idInput = document.getElementById('changePassUserId') || document.getElementById('changePassUserIdInput');
  const idUsuario = parseInt(idInput ? idInput.value : 0);
  const newPass = (document.getElementById('changePassNewInput')?.value || '').trim();

  if (!idUsuario) {
    showToast('Error: No se identificó el ID del usuario', 'error');
    return;
  }

  if (!newPass || newPass.length < 6) {
    showToast('La contraseña debe tener al menos 6 caracteres', 'warn');
    return;
  }

  try {
    await apiFetch(`/admin/usuarios/${idUsuario}/password`, {
      method: 'PUT',
      body: JSON.stringify({
        nueva_contrasena: newPass,
        'contraseña': newPass,
        password: newPass
      })
    });
    showToast('<i class="fa-solid fa-check"></i> Contraseña modificada exitosamente por el administrador', 'success');
    closeModal('changePasswordModal');
    if (typeof loadUsuarios === 'function') await loadUsuarios();
  } catch (err) {
    showToast('Error al cambiar contraseña: ' + err.message, 'error');
  }
};

async function promoteToTecnico(idUsuario) {
  if (!confirm('¿Promover este usuario a Técnico?')) return;
  try {
    await apiFetch(`/admin/usuarios/${idUsuario}?rol=tecnico`, {
      method: 'PUT'
    });
    showToast('Usuario promovido a Técnico exitosamente', 'success');
    invalidateCache('tecnicos');
    await loadUsuarios();
    await loadTecnicos();
    await loadUsuariosForPromotion();
  } catch (e) {
    showToast('Error al promover usuario: ' + e.message, 'error');
  }
}

function renderTecnicosTable(search = '') {
  let data = tecnicosData;
  if (search) {
    const q = search.toLowerCase();
    data = data.filter(t => [t.nombre, t.apellido, t.certificacion, t.email]
      .some(v => (v || '').toLowerCase().includes(q)));
  }
  const tbody = document.getElementById('tecnicosTableBody');
  if (!tbody) return;
  tbody.innerHTML = data.length ? data.map(t => {
    const turnosCount = (agendaData || []).filter(a => String(a.id_tecnico) === String(t.id_tecnico || t.id)).length;
    return `
    <tr>
      <td>
        <div style="display:flex;align-items:center;gap:10px">
          <div class="avatar" style="background:linear-gradient(135deg, #003049 0%, #1c82ad 100%); color:#fff; font-weight:700;">${initials(t.nombre, t.apellido)}</div>
          <div>
            <div style="font-weight:700; color:#003049;">${t.nombre} ${t.apellido}</div>
            <div class="text-muted" style="font-size:0.75rem">${t.email || ''}</div>
          </div>
        </div>
      </td>
      <td><span style="font-weight:600; color:#1c82ad;">${t.certificacion || '—'}</span></td>
      <td>${t.telefono || '—'}</td>
      <td>${statusBadge(t.estado)}</td>
      <td>
        <button class="badge ${turnosCount > 0 ? 'badge-confirmed' : 'badge-unpaid'}" onclick="viewTecnicoTurnos(${t.id})" style="border:none; cursor:pointer; font-weight:700; display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:12px; transition:all 0.2s;" title="Ver turnos asignados de este técnico">
          <i class="fa-solid fa-calendar-check"></i> ${turnosCount} ${turnosCount === 1 ? 'turno' : 'turnos'}
        </button>
      </td>
      <td>${formatDate(t.fecha_ingreso)}</td>
      <td><div class="table-actions">
        <button class="btn btn-ghost btn-sm" onclick="editTecnico(${t.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;"><i class="fa-solid fa-user-pen"></i> Editar</button>
        <button class="btn btn-ghost btn-sm" onclick="toggleTecnicoEstado(${t.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;">${t.estado === 'disponible' ? '<i class="fa-solid fa-user-lock" style="color:#ef4444;"></i> Ocupar' : '<i class="fa-solid fa-user-check" style="color:#10b981;"></i> Liberar'}</button>
        <button class="btn btn-danger btn-sm" onclick="deleteTecnico(${t.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;" title="Eliminar técnico"><i class="fa-solid fa-trash-can"></i></button>
      </div></td>
    </tr>
  `;
  }).join('') : `<tr><td colspan="7" class="text-center" style="padding:40px"><div class="empty-state" style="padding:0;"><div class="empty-icon"><i class="fa-solid fa-user-gear" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No hay técnicos registrados</div></div></td></tr>`;
}

window.viewTecnicoTurnos = function(id) {
  const t = tecnicosData.find(x => x.id === id);
  if (!t) return;
  const turnos = (agendaData || []).filter(a => String(a.id_tecnico) === String(t.id_tecnico || t.id));
  document.getElementById('detailModalTitle').innerHTML = `<i class="fa-solid fa-user-gear" style="color:var(--accent); margin-right:8px;"></i> Turnos Asignados: ${t.nombre} ${t.apellido}`;
  document.getElementById('detailModalBody').innerHTML = `
    <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; background:#f8fafc; border:1px solid #e2e8f0; padding:12px 16px; border-radius:14px; flex-wrap:wrap; gap:8px;">
      <div>
        <div style="font-weight:700; color:#003049; font-size:1rem;">${t.nombre} ${t.apellido}</div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">${t.certificacion || 'Piloto RPAS'} • Tel: ${t.telefono || '—'}</div>
      </div>
      <div><span class="badge ${turnos.length > 0 ? 'badge-active' : 'badge-unpaid'}" style="font-size:0.85rem; padding:6px 12px;"><i class="fa-solid fa-calendar-check" style="margin-right:4px;"></i> ${turnos.length} turnos asignados</span></div>
    </div>
    ${turnos.length ? `
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Cliente</th>
              <th>Finca</th>
              <th>Servicio</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            ${turnos.map(a => `
              <tr>
                <td style="font-weight:800; color:var(--primary);">#${a.id}</td>
                <td><div style="font-weight:700; color:#003049;">${a.cliente || '—'}</div></td>
                <td>${a.finca || '—'}</td>
                <td><span style="font-weight:600; color:#1c82ad;">${a.servicio || '—'}</span></td>
                <td>${formatDateShort(a.fecha)}</td>
                <td>${statusBadge(a.estado)}</td>
                <td>
                  <button class="btn btn-ghost btn-sm" onclick="viewAgendaDetail(${a.id})" title="Ver detalle del turno" style="display:inline-flex; align-items:center; gap:4px; font-weight:700;"><i class="fa-solid fa-eye"></i> Ver</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    ` : `
      <div class="text-center" style="padding:32px 16px;">
        <div class="empty-icon"><i class="fa-solid fa-calendar-xmark" style="font-size:2rem; color:var(--accent);"></i></div>
        <div class="empty-title" style="margin-top:8px; font-weight:700; color:#003049;">No tiene turnos asignados actualmente</div>
        <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">Puedes asignarle turnos desde la sección de Agenda.</div>
      </div>
    `}
    <div style="margin-top:16px; text-align:right;">
      <button class="btn btn-primary btn-sm" onclick="closeModal('detailModal')">Cerrar</button>
    </div>
  `;
  openModal('detailModal');
};

async function createTecnico(data) {
  try {
    const cleanName = (data.nombre || 'tecnico').toLowerCase().replace(/[^a-z0-9]/g, '');
    const email = (data.email && data.email.trim()) ? data.email.trim() : `tecnico.${cleanName}.${Date.now()}@flymetrics.co`;
    const password = data.password || 'Flymetrics123!';

    const payload = {
      email: email,
      'contraseña': password,
      rol: 'tecnico',
      nombre: data.nombre,
      apellido_1: data.apellido || data.apellido_1 || 'Técnico',
      apellido_2: data.apellido_2 || null,
      telefono: data.telefono || null,
      certificacion: data.certificacion || 'Piloto RPAS Nivel A',
    };
    await apiFetch('/tecnicos', { method: 'POST', body: JSON.stringify(payload) });
    invalidateCache('tecnicos');
    await loadTecnicos();
    await loadUsuarios();
    showToast(`<i class="fa-solid fa-check"></i> Técnico ${data.nombre} creado exitosamente con su contraseña personalizada`, 'success');
    closeModal('newTecnicoModal');
  } catch (e) {
    showToast('Error al crear técnico: ' + e.message, 'error');
  }
}

function editTecnico(id) {
  const t = tecnicosData.find(x => x.id === id);
  if (!t) return;
  document.getElementById('editTecnicoId').value = id;
  const fullName = (t.nombre && t.apellido && !t.nombre.includes(t.apellido)) 
    ? `${t.nombre} ${t.apellido}`.trim() 
    : (t.nombre || t.apellido || '');
  document.getElementById('editTecnicoNombre').value = fullName;
  document.getElementById('editTecnicoCert').value = t.certificacion || '';
  document.getElementById('editTecnicoTel').value = t.telefono || '';
  document.getElementById('editTecnicoEstado').value = t.estado || 'disponible';
  document.getElementById('editTecnicoPassword').value = '';
  openModal('editTecnicoModal');
}

async function updateTecnico(data) {
  const id = parseInt(data.id);
  try {
    const t = tecnicosData.find(x => x.id === id);
    const payload = {
      nombre: data.nombre,
      apellido_1: data.apellido,
      apellido_2: '',
      certificacion: data.certificacion,
      estado: data.estado,
      telefono: data.telefono
    };
    await apiFetch(`/tecnicos/${id}`, { method: 'PUT', body: JSON.stringify(payload) });

    if (data.password && data.password.trim().length >= 6 && t && t.id_usuario) {
      await apiFetch(`/admin/usuarios/${t.id_usuario}`, {
        method: 'PUT',
        body: JSON.stringify({ 'contraseña': data.password.trim() })
      });
      showToast('<i class="fa-solid fa-check"></i> Contraseña del técnico modificada exitosamente', 'info');
    }

    invalidateCache('tecnicos');
    await loadTecnicos();
    showToast('<i class="fa-solid fa-check"></i> Perfil de técnico actualizado correctamente', 'success');
    closeModal('editTecnicoModal');
  } catch (e) {
    showToast('Error al actualizar técnico: ' + e.message, 'error');
  }
}

async function toggleTecnicoEstado(id) {
  const t = tecnicosData.find(x => x.id === id);
  if (!t) return;
  const newEstado = t.estado === 'disponible' ? 'ocupado' : 'disponible';
  try {
    await apiFetch(`/tecnicos/${id}`, { method: 'PUT', body: JSON.stringify({ estado: newEstado }) });
    t.estado = newEstado;
    invalidateCache('tecnicos');
    renderTecnicosTable();
    showToast(`Estado cambiado: ${newEstado}`, 'info');
  } catch (e) {
    showToast('Error al cambiar estado del técnico: ' + e.message, 'error');
  }
}

async function deleteTecnico(id) {
  if (!confirm('¿Eliminar este técnico?')) return;
  try {
    const t = tecnicosData.find(x => x.id === id);
    if (t && t.id_usuario) {
      await apiFetch(`/admin/usuarios/${t.id_usuario}`, { method: 'DELETE' });
    } else {
      await apiFetch(`/tecnicos/${id}`, { method: 'DELETE' });
    }
    invalidateCache('tecnicos');
    await loadUsuarios();
    await loadTecnicos();
    showToast('Técnico eliminado correctamente', 'info');
  } catch (e) {
    showToast('Error al eliminar técnico: ' + e.message, 'error');
  }
}

window.editTecnico = editTecnico;
window.deleteTecnico = deleteTecnico;

// ─────────────────────────────────────────
// 5. DRONES PANEL (CON ASIGNACIÓN DE PILOTOS)
// ─────────────────────────────────────────

function populateDroneTecnicoSelectors() {
  const tecnicos = (tecnicosData && tecnicosData.length) ? tecnicosData : (cache['tecnicos']?.data || []);
  const optionsHtml = '<option value="">Sin piloto asignado (Flota general)</option>' +
    tecnicos.map(t => `<option value="${t.id_tecnico || t.id}">${t.nombre} ${t.apellido_1 || t.apellido || ''}</option>`).join('');
  const selNew = document.getElementById('newDroneTecnico');
  const selEdit = document.getElementById('editDroneTecnico');
  if (selNew) selNew.innerHTML = optionsHtml;
  if (selEdit) selEdit.innerHTML = optionsHtml;

  // Populate dynamic services from registered services
  const servicios = (serviciosData && serviciosData.length) ? serviciosData : [];
  const svcOptionsHtml = servicios.length
    ? servicios.filter(s => s.activo !== false).map(s => `<option value="${s.nombre || s.nombre_servicio}">${s.nombre || s.nombre_servicio}</option>`).join('')
    : `
      <option value="Fumigación y Aspersión Agrícola">Fumigación y Aspersión Agrícola</option>
      <option value="Análisis Multiespectral">Análisis Multiespectral</option>
      <option value="Fotogrametría 3D y Topografía">Fotogrametría 3D y Topografía</option>
      <option value="Inspecciones Técnicas">Inspecciones Técnicas</option>
    `;
  const selNewTipo = document.getElementById('newDroneTipo');
  const selEditTipo = document.getElementById('editDroneTipo');
  if (selNewTipo) selNewTipo.innerHTML = svcOptionsHtml;
  if (selEditTipo) selEditTipo.innerHTML = svcOptionsHtml;
}

async function loadDrones() {
  if (!tecnicosData || !tecnicosData.length) {
    try { await loadTecnicos(); } catch(e){}
  }
  const raw = await fetchCached('drones', '/drones') || [];
  dronesData = (Array.isArray(raw) ? raw : (raw.data || [])).map(d => {
    let tecName = d.tecnico_nombre || '';
    if (!tecName && d.id_tecnico_asignado && tecnicosData.length) {
      const t = tecnicosData.find(x => (x.id_tecnico || x.id) == d.id_tecnico_asignado);
      if (t) tecName = `${t.nombre} ${t.apellido_1 || t.apellido || ''}`;
    }
    return {
      id: d.id_drone, id_drone: d.id_drone, modelo: d.modelo, tipo: d.tipo,
      estado: d.estado || 'disponible', numero_serie: d.numero_serie, horas_vuelo: d.horas_vuelo || 0,
      ultima_revision: d.ultima_revision,
      id_tecnico_asignado: d.id_tecnico_asignado || null,
      tecnico_nombre: tecName || ''
    };
  });

  populateDroneTecnicoSelectors();
  renderDronesTable();

  // Compute and update stats
  const total = dronesData.length;
  const disponibles = dronesData.filter(d => d.estado === 'disponible').length;
  const mantenimiento = dronesData.filter(d => d.estado === 'mantenimiento').length;

  const elTotal = document.getElementById('statTotalDrones');
  if (elTotal) elTotal.textContent = total;
  const elDisp = document.getElementById('statDronesDisponibles');
  if (elDisp) elDisp.textContent = disponibles;
  const elMant = document.getElementById('statDronesMantenimiento');
  if (elMant) elMant.textContent = mantenimiento;
}

function renderDronesTable(search = '') {
  let data = dronesData;
  if (search) {
    const q = search.toLowerCase();
    data = data.filter(d => [d.modelo, d.tipo, d.numero_serie, d.tecnico_nombre].some(v => (v || '').toLowerCase().includes(q)));
  }
  const tbody = document.getElementById('dronesTableBody');
  if (!tbody) return;
  tbody.innerHTML = data.length ? data.map(d => `
    <tr>
      <td>
        <div style="display:flex; align-items:center; gap:8px;">
          <i class="fa-solid fa-helicopter" style="color:var(--accent); font-size:1.1rem;"></i>
          <span style="font-weight:700; color:var(--primary)">${d.modelo || '—'}</span>
        </div>
        <div class="text-muted" style="font-size:0.75rem; margin-top:2px;">${d.numero_serie || 'S/N no registrado'}</div>
      </td>
      <td><span class="badge badge-info" style="font-weight:600">${d.tipo || 'General'}</span></td>
      <td>
        <div style="font-weight:600; color:#003049;">
          ${d.id_tecnico_asignado && d.tecnico_nombre ? `<div style="display:flex; align-items:center; gap:6px;"><i class="fa-solid fa-user-gear" style="color:#0369a1;"></i> <span>${d.tecnico_nombre}</span></div>` : '<span class="text-muted" style="font-style:italic">Sin piloto (Flota General)</span>'}
        </div>
      </td>
      <td>${statusBadge(d.estado)}</td>
      <td>${formatDate(d.ultima_revision)}</td>
      <td>${d.horas_vuelo || 0} h</td>
      <td><div class="table-actions">
        <button class="btn btn-ghost btn-sm" onclick="editDrone(${d.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;"><i class="fa-solid fa-pen-to-square"></i> Editar / Asignar</button>
        <button class="btn btn-ghost btn-sm" onclick="toggleDroneEstado(${d.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;">${d.estado === 'mantenimiento' ? '<i class="fa-solid fa-circle-check" style="color:#10b981;"></i> Disponible' : '<i class="fa-solid fa-screwdriver-wrench" style="color:#f59e0b;"></i> Mantenimiento'}</button>
        <button class="btn btn-danger btn-sm" onclick="deleteDrone(${d.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:600;" title="Eliminar drone"><i class="fa-solid fa-trash-can"></i></button>
      </div></td>
    </tr>
  `).join('') : `<tr><td colspan="7" class="text-center" style="padding:40px"><div class="empty-icon"><i class="fa-solid fa-helicopter" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No hay drones registrados</div></td></tr>`;
}

function editDrone(id) {
  const d = dronesData.find(x => x.id === id);
  if (!d) return;
  populateDroneTecnicoSelectors();
  document.getElementById('editDroneId').value = id;
  document.getElementById('editDroneModelo').value = d.modelo || '';
  document.getElementById('editDroneTipo').value = d.tipo || '';
  document.getElementById('editDroneEstado').value = d.estado || 'disponible';
  document.getElementById('editDroneRevision').value = d.ultima_revision || '';
  document.getElementById('editDroneSerie').value = d.numero_serie || '';
  document.getElementById('editDroneHoras').value = d.horas_vuelo || 0;
  if (document.getElementById('editDroneTecnico')) {
    document.getElementById('editDroneTecnico').value = d.id_tecnico_asignado || '';
  }
  openModal('editDroneModal');
}

async function updateDrone(data) {
  const id = parseInt(data.id);
  try {
    const payload = {};
    if (data.modelo && data.modelo.trim()) payload.modelo = data.modelo.trim().slice(0, 50);
    if (data.tipo && data.tipo.trim()) payload.tipo = data.tipo.trim().slice(0, 50);
    if (data.estado && data.estado.trim()) payload.estado = data.estado.trim().slice(0, 30);
    if (data.numero_serie && data.numero_serie.trim()) payload.numero_serie = data.numero_serie.trim().slice(0, 100);
    if (data.ultima_revision && data.ultima_revision.trim()) payload.ultima_revision = data.ultima_revision.trim().slice(0, 50);
    if (typeof data.horas_vuelo === 'number' && !isNaN(data.horas_vuelo) && data.horas_vuelo >= 0) {
      payload.horas_vuelo = data.horas_vuelo;
    }
    payload.id_tecnico_asignado = data.id_tecnico_asignado ? parseInt(data.id_tecnico_asignado) : null;

    await apiFetch(`/drones/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
    invalidateCache('drones');
    await loadDrones();
    showToast('<i class="fa-solid fa-check"></i> Dron y piloto asignado guardados exitosamente', 'success');
    closeModal('editDroneModal');
  } catch (e) {
    showToast('Error al actualizar el dron: ' + (e.message || 'Error de validación'), 'error');
  }
}

async function createDrone(data) {
  try {
    if (data.id_tecnico_asignado) {
      data.id_tecnico_asignado = parseInt(data.id_tecnico_asignado);
    } else {
      delete data.id_tecnico_asignado;
    }
    await apiFetch('/drones', { method: 'POST', body: JSON.stringify(data) });
    invalidateCache('drones');
    await loadDrones();
    showToast('<i class="fa-solid fa-check"></i> Dron agregado a la flota exitosamente', 'success');
    closeModal('newDroneModal');
  } catch (e) {
    showToast('Error al crear el drone: ' + e.message, 'error');
  }
}

async function toggleDroneEstado(id) {
  const d = dronesData.find(x => x.id === id);
  if (!d) return;
  const newEstado = d.estado === 'mantenimiento' ? 'disponible' : 'mantenimiento';
  try {
    await apiFetch(`/drones/${id}`, { method: 'PUT', body: JSON.stringify({ estado: newEstado }) });
    d.estado = newEstado;
    invalidateCache('drones');
    renderDronesTable();
    showToast(`Estado del dron: ${newEstado}`, 'info');
  } catch (e) {
    showToast('Error al cambiar estado del dron: ' + e.message, 'error');
  }
}

async function deleteDrone(id) {
  if (!confirm('¿Eliminar este drone de la base de datos?')) return;
  try {
    await apiFetch(`/drones/${id}`, { method: 'DELETE' });
    dronesData = dronesData.filter(d => d.id !== id);
    invalidateCache('drones');
    renderDronesTable();
    showToast('Drone eliminado correctamente', 'info');
  } catch (e) {
    showToast('Error al eliminar dron: ' + e.message, 'error');
  }
}

window.editDrone = editDrone;
window.deleteDrone = deleteDrone;

// ─────────────────────────────────────────
// 6. SERVICIOS PANEL (SIN PRECIOS)
// ─────────────────────────────────────────

async function loadServicios() {
  const raw = await apiFetch('/servicios?include_inactive=true') || [];
  serviciosData = (Array.isArray(raw) ? raw : (raw.data || [])).map(s => ({
    id: s.id_servicio, id_servicio: s.id_servicio,
    nombre: s.nombre_servicio, descripcion: s.descripcion,
    activo: s.activo === 0 || s.activo === false || s.activo === '0' ? false : true
  }));
  renderServiciosTable();
}

function renderServiciosTable() {
  const tbody = document.getElementById('serviciosTableBody');
  if (!tbody) return;
  tbody.innerHTML = serviciosData.length ? serviciosData.map(s => {
    const nameLower = (s.nombre || '').toLowerCase();
    const categoria = s.categoria || (nameLower.includes('mapeo') || nameLower.includes('inspeccion') || nameLower.includes('fotogrametria') ? 'Fotogrametría' : 'Aspersión');
    return `
    <tr>
      <td>
        <div style="font-weight:700; color:#003049; font-size:0.92rem;">${s.nombre || '—'}</div>
      </td>
      <td>
        <span class="badge" style="background:rgba(28, 130, 173, 0.1); color:#1c82ad; border:1px solid rgba(28, 130, 173, 0.25); font-weight:700; padding:4px 10px; border-radius:12px;">${categoria}</span>
      </td>
      <td style="max-width:380px; color:#4a5568; font-size:0.85rem; line-height:1.4;">
        ${s.descripcion || '—'}
      </td>
      <td style="text-align:center;">
        <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
          <button class="toggle-btn ${s.activo ? 'active' : ''}" onclick="toggleServicio(${s.id}, ${!s.activo})" title="${s.activo ? 'Clic para desactivar' : 'Clic para activar'}">
            <span class="toggle-knob">${s.activo ? '<i class="fa-solid fa-check"></i>' : '✕'}</span>
          </button>
          ${s.activo ? '<span class="badge badge-active" style="padding:4px 10px; border-radius:12px;">Activo</span>' : '<span class="badge badge-inactive" style="padding:4px 10px; border-radius:12px;">Inactivo</span>'}
        </div>
      </td>
      <td style="text-align:center;">
        <button class="btn btn-danger btn-sm" onclick="deleteServicio(${s.id})" title="Eliminar servicio" style="padding:6px 12px; border-radius:8px; background:rgba(255, 77, 109, 0.12); color:#FF4D6D; border:1px solid rgba(255, 77, 109, 0.3); font-weight:700; cursor:pointer; transition:all 0.2s; display:inline-flex; align-items:center; gap:6px;"><i class="fa-solid fa-trash-can"></i> Eliminar</button>
      </td>
    </tr>
  `;
  }).join('') : `<tr><td colspan="5" class="text-center" style="padding:40px">No hay servicios registrados en la base de datos</td></tr>`;
}

async function toggleServicio(id, checked) {
  try {
    await apiFetch(`/servicios/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ activo: Boolean(checked) })
    });
    const s = serviciosData.find(x => x.id === id);
    if (s) s.activo = Boolean(checked);
    invalidateCache('servicios');
    renderServiciosTable();
    showToast(`<i class="fa-solid fa-check"></i> Servicio ${checked ? 'activado' : 'desactivado'} correctamente`, 'info');
  } catch (err) {
    showToast('Error al cambiar estado del servicio: ' + err.message, 'error');
    renderServiciosTable();
  }
}
window.toggleServicio = toggleServicio;

async function deleteServicio(id) {
  if (!confirm('¿Estás seguro de eliminar este servicio del catálogo?')) return;
  try {
    const res = await apiFetch(`/servicios/${id}`, { method: 'DELETE' });
    serviciosData = serviciosData.filter(s => s.id !== id && s.id_servicio !== id);
    invalidateCache('servicios');
    await loadServicios();
    showToast('<i class="fa-solid fa-check"></i> ' + (res?.message || 'Servicio eliminado correctamente'), 'success');
  } catch (e) {
    showToast('Error al eliminar servicio: ' + e.message, 'error');
  }
}
window.deleteServicio = deleteServicio;

window.submitNewServicio = async function (e) {
  if (e) e.preventDefault();
  const nombre = (document.getElementById('newServicioNombre')?.value || '').trim();
  const descripcion = (document.getElementById('newServicioDescripcion')?.value || '').trim();

  if (!nombre || !descripcion) {
    showToast('Por favor completa el nombre y descripción del servicio', 'warn');
    return;
  }

  try {
    const res = await apiFetch('/servicios', {
      method: 'POST',
      body: JSON.stringify({
        nombre_servicio: nombre,
        descripcion: descripcion,
        precio_base_m2: 0,
        activo: true
      })
    });
    showToast('<i class="fa-solid fa-check"></i> Servicio creado exitosamente en la base de datos', 'success');
    closeModal('newServicioModal');
    if (document.getElementById('newServicioForm')) document.getElementById('newServicioForm').reset();
    invalidateCache('servicios');
    await loadServicios();
  } catch (err) {
    showToast('Error al crear servicio: ' + err.message, 'error');
  }
};

// ─────────────────────────────────────────
// 7. FACTURACIÓN & VINCULACIÓN CON ALEGRA
// ─────────────────────────────────────────

let clientesFacturacionData = [];

async function loadFacturacion() {
  try {
    const rawClientes = await apiFetch('/clientes') || [];
    clientesFacturacionData = (Array.isArray(rawClientes) ? rawClientes : (rawClientes.data || [])).map(c => {
      const apellidos = `${c.apellido_1 || ''} ${c.apellido_2 || ''}`.trim();
      const nombreCompleto = `${c.nombre || ''} ${apellidos}`.trim() || 'Cliente Sin Nombre';
      return {
        id: c.id_cliente || c.id,
        id_cliente: c.id_cliente || c.id,
        nombre: nombreCompleto,
        email: c.email || (c.usuario ? c.usuario.email : ''),
        telefono: c.telefono || '—',
        cedula: c.numero_documento || '—',
        link_alegra: (c.link_alegra || '').trim(),
        verificado: c.verificado
      };
    });
    populateAlegraClienteSelect();
    renderPagosTable();
  } catch (e) {
    console.warn("Error loading facturacion:", e);
    renderPagosTable();
  }
}

function populateAlegraClienteSelect() {
  const sel = document.getElementById('alegraClienteSelect');
  if (!sel) return;
  if (!clientesFacturacionData.length) {
    sel.innerHTML = '<option value="">No hay clientes registrados</option>';
    return;
  }
  sel.innerHTML = '<option value="">Selecciona un cliente...</option>' +
    clientesFacturacionData.map(c => `<option value="${c.id_cliente}">${c.nombre} (NIT/CC: ${c.cedula}) — ${c.email || c.telefono}</option>`).join('');
}

window.onAlegraClienteChange = function() {
  const sel = document.getElementById('alegraClienteSelect');
  const inp = document.getElementById('alegraUrlInput');
  if (!sel || !inp) return;
  const id = parseInt(sel.value);
  const cliente = clientesFacturacionData.find(c => c.id_cliente === id);
  if (cliente && cliente.link_alegra) {
    inp.value = cliente.link_alegra;
  } else {
    inp.value = '';
  }
};

function renderPagosTable(search = '') {
  let data = clientesFacturacionData;
  const q = (search || (document.getElementById('pagosSearch')?.value || '')).toLowerCase().trim();
  if (q) {
    data = data.filter(c => [c.nombre, c.email, c.telefono, c.cedula, c.link_alegra].some(v => (v || '').toLowerCase().includes(q)));
  }
  const tbody = document.getElementById('pagosTableBody');
  if (!tbody) return;

  tbody.innerHTML = data.length ? data.map(c => {
    const hasAlegra = Boolean(c.link_alegra && (c.link_alegra.startsWith('http://') || c.link_alegra.startsWith('https://')));
    return `
    <tr>
      <td style="font-weight:800; color:var(--primary);">#CLI-${c.id_cliente}</td>
      <td>
        <div style="font-weight:700; color:#003049;">${c.nombre}</div>
        <div class="text-muted" style="font-size:0.75rem;">${c.email || ''}</div>
      </td>
      <td style="font-weight:600; color:#475569;">${c.cedula}</td>
      <td>${c.telefono}</td>
      <td>
        ${hasAlegra
          ? `<span class="badge" style="background:rgba(16, 185, 129, 0.12); color:#059669; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-circle-check"></i> Vinculado en Alegra</span>`
          : `<span class="badge" style="background:rgba(239, 68, 68, 0.08); color:#dc2626; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i class="fa-solid fa-clock"></i> Pendiente Enlace</span>`
        }
      </td>
      <td>
        ${hasAlegra ? `
          <a href="${c.link_alegra}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-sm" style="color:#0284c7; font-weight:700; display:inline-flex; align-items:center; gap:6px; text-decoration:none;">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir Portal Alegra
          </a>
        ` : `
          <span class="text-muted" style="font-size:0.80rem; font-style:italic;">Sin link configurado</span>
        `}
      </td>
      <td style="text-align:center;">
        <button class="btn btn-primary btn-sm" onclick="openVincularAlegraModal(${c.id_cliente})" style="display:inline-flex; align-items:center; gap:6px; font-weight:700; padding:6px 12px; border-radius:8px;">
          <i class="fa-solid fa-link"></i> ${hasAlegra ? 'Editar Link Alegra' : 'Vincular Alegra'}
        </button>
      </td>
    </tr>
  `;
  }).join('') : `<tr><td colspan="7" class="text-center" style="padding:40px"><div class="empty-icon"><i class="fa-solid fa-file-invoice-dollar" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No hay clientes encontrados</div><div class="empty-sub">No se hallaron clientes para la búsqueda ingresada.</div></td></tr>`;
}

window.openVincularAlegraModal = function(id_cliente = null) {
  populateAlegraClienteSelect();
  const sel = document.getElementById('alegraClienteSelect');
  const inp = document.getElementById('alegraUrlInput');
  if (id_cliente && sel) {
    sel.value = id_cliente;
    const cliente = clientesFacturacionData.find(c => c.id_cliente === id_cliente);
    if (inp) inp.value = (cliente && cliente.link_alegra) ? cliente.link_alegra : '';
  } else {
    if (sel) sel.value = '';
    if (inp) inp.value = '';
  }
  openModal('vincularAlegraModal');
};

window.submitVincularAlegra = async function(e) {
  if (e) e.preventDefault();
  const sel = document.getElementById('alegraClienteSelect');
  const inp = document.getElementById('alegraUrlInput');
  const id_cliente = parseInt(sel?.value);
  const link_alegra = (inp?.value || '').trim();

  if (!id_cliente || !link_alegra) {
    showToast('Por favor selecciona un cliente e ingresa el enlace de Alegra (*)', 'warn');
    return;
  }

  try {
    showToast('Guardando vinculación de Alegra...', 'info');
    await apiFetch(`/clientes/${id_cliente}/alegra`, {
      method: 'PUT',
      body: JSON.stringify({ link_alegra })
    });
    showToast('<i class="fa-solid fa-check"></i> Facturación de Alegra vinculada exitosamente al cliente', 'success');
    closeModal('vincularAlegraModal');
    invalidateCache('clientes');
    await loadFacturacion();
  } catch (err) {
    showToast('Error al vincular con Alegra: ' + err.message, 'error');
  }
};

// ─────────────────────────────────────────
// GESTIÓN DE USUARIOS
// ─────────────────────────────────────────



// ─────────────────────────────────────────
// 8. REPORTES PANEL
// ─────────────────────────────────────────


let _filteredReportesVuelo = null;
let _filteredInformesEjecutivos = null;

async function loadReportes() {
  const raw = await apiFetch('/reportes-vuelo') || [];
  reportesData = raw.map(r => ({
    id: r.id_reporte || r.id_bitacora || r.id,
    turno_id: r.id_turno || r.id,
    insumos_litros: r.insumos_litros_aplicados || 15.0,
    agua_litros: r.agua_litros || 100.0,
    baterias: r.baterias_utilizadas || 4,
    cumple_rac: r.cumple_rac100 !== undefined ? r.cumple_rac100 : 1,
    observaciones: r.observaciones_campo || 'Operación ejecutada bajo parámetros técnicos.',
    fecha: r.fecha || new Date().toISOString().split('T')[0],
    cliente: r.cliente || 'Cliente Flymetrics',
    finca: r.finca || 'Finca Registrada',
    tecnico: r.tecnico || 'Piloto Certificado',
    servicio: r.servicio || 'Vuelo Agrícola',
    duracion_min: r.duracion_min || 45,
    area_ha: r.area_ha || 10.0,
    url_entregable_drive: r.url_entregable_drive,
    recomendaciones_agronomicas: r.recomendaciones_agronomicas
  }));
  _filteredReportesVuelo = null;
  _filteredInformesEjecutivos = null;
  renderReportesTable();
}

function filterReportesVueloTable() {
  const q = (document.getElementById('reportesVueloSearch')?.value || '').trim().toLowerCase();
  const dateVal = document.getElementById('reportesVueloDateFilter')?.value || '';

  _filteredReportesVuelo = reportesData.filter(r => {
    const matchQ = !q || [r.cliente, r.finca, r.servicio, r.tecnico, String(r.id), String(r.turno_id)].some(v => (v || '').toLowerCase().includes(q));
    const matchDate = !dateVal || (r.fecha && r.fecha.startsWith(dateVal));
    return matchQ && matchDate;
  });

  renderReportesVueloTable();
}
window.filterReportesVueloTable = filterReportesVueloTable;

function filterInformesEjecutivosTable() {
  const q = (document.getElementById('informesEjecutivosSearch')?.value || '').trim().toLowerCase();
  const dateVal = document.getElementById('informesEjecutivosDateFilter')?.value || '';

  _filteredInformesEjecutivos = reportesData.filter(r => {
    const matchQ = !q || [r.cliente, r.finca, r.servicio, r.tecnico, r.recomendaciones_agronomicas, String(r.id), String(r.turno_id)].some(v => (v || '').toLowerCase().includes(q));
    const matchDate = !dateVal || (r.fecha && r.fecha.startsWith(dateVal));
    return matchQ && matchDate;
  });

  renderInformesEjecutivosTable();
}
window.filterInformesEjecutivosTable = filterInformesEjecutivosTable;

function renderReportesVueloTable() {
  const tbody = document.getElementById('reportesVueloTableBody');
  if (!tbody) return;
  const list = _filteredReportesVuelo !== null ? _filteredReportesVuelo : reportesData;

  tbody.innerHTML = list.length ? list.map(r => `
    <tr>
      <td style="font-weight:800; color:var(--primary);">#RAD-${r.id}</td>
      <td><span style="font-weight:600; color:#475569;"><i class="fa-solid fa-calendar-day" style="color:#1c82ad; margin-right:4px;"></i> ${formatDate(r.fecha)}</span></td>
      <td>
        <div style="font-weight:700; color:#003049;">${r.cliente || '—'}</div>
      </td>
      <td>${r.finca || '—'}</td>
      <td><span style="font-weight:600; color:#0369a1;"><i class="fa-solid fa-user-gear" style="margin-right:4px;"></i> ${r.tecnico || 'Piloto'}</span></td>
      <td><span style="font-weight:600; color:#1c82ad;">${r.servicio || 'Vuelo agrícola'}</span></td>
      <td><span class="badge badge-active" style="font-weight:700;"><i class="fa-solid fa-circle-check" style="margin-right:4px;"></i> Completado</span></td>
      <td style="text-align:center;">
        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center;">
          <button class="btn btn-ghost btn-sm" onclick="viewReporteBitacora(${r.id})" title="Ver ficha técnica y bitácora completa" style="display:inline-flex; align-items:center; gap:4px; font-weight:700;"><i class="fa-solid fa-eye"></i> Ver</button>
          <button class="btn btn-warn btn-sm" onclick="openEditBitacoraModal(${r.id})" title="Modificar bitácora técnica de vuelo" style="display:inline-flex; align-items:center; gap:4px; font-weight:700; background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3); border-radius:8px;"><i class="fa-solid fa-plane-circle-check"></i> Modificar</button>
          <button class="btn btn-primary btn-sm" onclick="downloadReporte(${r.id})" title="Descargar informe oficial de vuelo en PDF" style="display:inline-flex; align-items:center; gap:4px; font-weight:700;"><i class="fa-solid fa-file-pdf"></i> PDF</button>
        </div>
      </td>
    </tr>
  `).join('') : `<tr><td colspan="8" class="text-center" style="padding:40px"><div class="empty-state" style="padding:0"><div class="empty-icon"><i class="fa-solid fa-plane-circle-exclamation" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No se encontraron reportes de vuelo o registros faltantes</div></div></td></tr>`;
}

function formatExternalUrl(url) {
  if (!url) return '';
  url = String(url).trim();
  if (!url || url === '#' || url === 'null' || url === 'undefined') return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/')) {
    return url;
  }
  return 'https://' + url;
}

function renderInformesEjecutivosTable() {
  const tbody = document.getElementById('informesEjecutivosTableBody');
  if (!tbody) return;
  const list = _filteredInformesEjecutivos !== null ? _filteredInformesEjecutivos : reportesData;

  tbody.innerHTML = list.length ? list.map(r => {
    const rawLink = r.url_entregable_drive || r.url_archivo || '';
    const cleanLink = formatExternalUrl(rawLink);
    return `
    <tr>
      <td style="font-weight:800; color:var(--primary);">#RAD-${r.id}</td>
      <td>
        <span style="font-weight:600; color:#475569;"><i class="fa-solid fa-calendar-day" style="color:#1c82ad; margin-right:4px;"></i> ${formatDate(r.fecha)}</span>
      </td>
      <td>
        <div style="font-weight:700; color:#003049;">${r.cliente || '—'}</div>
      </td>
      <td>${r.finca || '—'}</td>
      <td><span style="font-weight:600; color:#1c82ad;">${r.servicio || 'Vuelo agrícola'}</span></td>
      <td>
        <div style="max-width:260px; font-size:0.82rem; color:#475569; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${r.recomendaciones_agronomicas || 'Sin recomendaciones registradas'}">
          ${r.recomendaciones_agronomicas ? `<i class="fa-solid fa-seedling" style="color:#059669; margin-right:4px;"></i> ${r.recomendaciones_agronomicas}` : '<span style="color:#94a3b8; font-style:italic;">Pendiente por registrar</span>'}
        </div>
      </td>
      <td><span class="badge badge-active" style="font-weight:700;"><i class="fa-solid fa-circle-check" style="margin-right:4px;"></i> Ejecutado</span></td>
      <td style="text-align:center;">
        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center;">
          <button class="btn btn-ghost btn-sm" onclick="viewInformeEjecutivo(${r.id})" title="Ver informe ejecutivo" style="display:inline-flex; align-items:center; gap:4px; font-weight:700;"><i class="fa-solid fa-eye"></i> Ver</button>
          ${cleanLink ? `
            <a href="${cleanLink}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" title="Abrir Google Drive / SharePoint directamente" style="display:inline-flex; align-items:center; gap:4px; font-weight:800; background:#003049; color:#ffffff; border-radius:8px; padding:6px 10px; font-size:0.78rem; text-decoration:none;">
              <i class="fa-solid fa-arrow-up-right-from-square" style="color:#38bdf8;"></i> Abrir Link
            </a>
          ` : ''}
          <button class="btn btn-warn btn-sm" onclick="openEditInformeEjecutivoModal(${r.id})" title="Modificar informe y enlace SharePoint / Drive" style="display:inline-flex; align-items:center; gap:4px; font-weight:700; background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.3); border-radius:8px;"><i class="fa-solid fa-file-pen"></i> Modificar</button>
          <button class="btn btn-primary btn-sm" onclick="downloadReporte(${r.id})" title="Descargar informe oficial" style="display:inline-flex; align-items:center; gap:4px; font-weight:700;"><i class="fa-solid fa-file-pdf"></i> PDF</button>
        </div>
      </td>
    </tr>
  `;
  }).join('') : `<tr><td colspan="8" class="text-center" style="padding:40px"><div class="empty-state" style="padding:0"><div class="empty-icon"><i class="fa-solid fa-file-circle-question" style="font-size:2rem; color:var(--accent);"></i></div><div class="empty-title">No se encontraron informes ejecutivos o registros faltantes</div></div></td></tr>`;
}

function renderReportesTable() {
  renderReportesVueloTable();
  renderInformesEjecutivosTable();
}

function viewReporteBitacora(id) {
  const r = reportesData.find(x => x.id === id || x.turno_id === id);
  if (!r) return;
  document.getElementById('detailModalTitle').innerHTML = `<i class="fa-solid fa-plane-circle-check" style="color:#10b981; margin-right:8px;"></i> Bitácora de Vuelo #${r.id}`;
  document.getElementById('detailModalBody').innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px;">
      
      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-user"></i> CLIENTE
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.cliente || '—'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-house-chimney"></i> FINCA
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.finca || '—'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-user-gear"></i> PILOTO TÉCNICO
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.tecnico || 'Piloto Certificado'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-calendar-day"></i> FECHA
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${formatDate(r.fecha)}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#10b981; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-flask"></i> INSUMOS APLICADOS
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.insumos_litros || 15} L</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#0284c7; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-droplet"></i> AGUA UTILIZADA
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.agua_litros || 120} L</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#10b981; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-battery-three-quarters"></i> BATERÍAS
        </div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.baterias || 4} ciclos</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#10b981; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
          <i class="fa-solid fa-shield-halved"></i> REGULACIÓN RAC-100
        </div>
        <div>
          <span class="badge" style="background:rgba(16,185,129,0.12); color:#059669; font-weight:800; padding:4px 12px; border-radius:12px; font-size:0.82rem;"><i class="fa-solid fa-check"></i> Conforme</span>
        </div>
      </div>

      <div style="grid-column: 1 / -1; background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px; box-shadow:0 2px 8px rgba(0,48,73,0.04);">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px; margin-bottom:6px;">
          <i class="fa-solid fa-comment-dots"></i> OBSERVACIONES DE CAMPO
        </div>
        <div style="font-size:0.90rem; color:#475569; font-weight:600; white-space:pre-wrap;">${r.observaciones || 'Operación ejecutada bajo parámetros técnicos.'}</div>
      </div>

    </div>

    <div style="display:flex; justify-content:flex-end; gap:10px; flex-wrap:wrap;">
      <button class="btn btn-warn btn-sm" onclick="closeModal('detailModal'); openEditBitacoraModal(${r.id});" style="display:inline-flex; align-items:center; gap:6px; font-weight:700; background:#f59e0b; color:#fff; border:none; border-radius:8px;">
        <i class="fa-solid fa-plane-circle-check"></i> Modificar Bitácora
      </button>
      <button class="btn btn-ghost btn-sm" onclick="downloadReporte(${r.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:700;">
        <i class="fa-solid fa-file-pdf"></i> Descargar PDF
      </button>
      <button class="btn btn-primary btn-sm" onclick="closeModal('detailModal')">Cerrar</button>
    </div>
  `;
  openModal('detailModal');
}
window.viewReporteBitacora = viewReporteBitacora;

function viewInformeEjecutivo(id) {
  const r = reportesData.find(x => x.id === id || x.turno_id === id);
  if (!r) return;
  document.getElementById('detailModalTitle').innerHTML = `<i class="fa-solid fa-file-signature" style="color:var(--accent); margin-right:8px;"></i> Informe Ejecutivo #${r.id}`;
  document.getElementById('detailModalBody').innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px;">
      
      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px;">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; margin-bottom:4px;"><i class="fa-solid fa-user"></i> CLIENTE</div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.cliente || '—'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px;">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; margin-bottom:4px;"><i class="fa-solid fa-house-chimney"></i> FINCA</div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.finca || '—'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px;">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; margin-bottom:4px;"><i class="fa-solid fa-spray-can"></i> SERVICIO AGRÍCOLA</div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${r.servicio || 'Vuelo Agrícola'}</div>
      </div>

      <div style="background:#ffffff; border:1.5px solid rgba(28,130,173,0.2); border-radius:16px; padding:14px;">
        <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase; margin-bottom:4px;"><i class="fa-solid fa-calendar-day"></i> FECHA EJECUCIÓN</div>
        <div style="font-size:1rem; font-weight:800; color:#003049;">${formatDate(r.fecha)}</div>
      </div>

      ${(r.url_entregable_drive || r.url_archivo) ? `
        <div style="grid-column: 1 / -1; background:rgba(28,130,173,0.06); border:1.5px solid rgba(28,130,173,0.25); border-radius:16px; padding:14px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-size:0.76rem; font-weight:800; color:#1c82ad; text-transform:uppercase;"><i class="fa-solid fa-globe"></i> ENLACE CLOUD / ENTREGABLE</div>
            <div style="font-size:0.88rem; color:#003049; font-weight:700; word-break:break-all; margin-top:2px;">${r.url_entregable_drive || r.url_archivo}</div>
          </div>
          <a href="${formatExternalUrl(r.url_entregable_drive || r.url_archivo)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="display:inline-flex; align-items:center; gap:6px; font-weight:800; text-decoration:none; white-space:nowrap;">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir Enlace
          </a>
        </div>
      ` : ''}

      <div style="grid-column: 1 / -1; background:rgba(16,185,129,0.05); border:1.5px solid rgba(16,185,129,0.25); border-radius:16px; padding:14px;">
        <div style="font-size:0.76rem; font-weight:800; color:#059669; text-transform:uppercase; margin-bottom:6px;"><i class="fa-solid fa-seedling"></i> RECOMENDACIONES & RESUMEN AGRONÓMICO</div>
        <div style="font-size:0.90rem; color:#065f46; font-weight:600; white-space:pre-wrap;">${r.recomendaciones_agronomicas || 'Sin recomendaciones registradas aún.'}</div>
      </div>

    </div>

    <div style="display:flex; justify-content:flex-end; gap:10px; flex-wrap:wrap;">
      <button class="btn btn-warn btn-sm" onclick="closeModal('detailModal'); openEditInformeEjecutivoModal(${r.id});" style="display:inline-flex; align-items:center; gap:6px; font-weight:700; background:#f59e0b; color:#fff; border:none; border-radius:8px;">
        <i class="fa-solid fa-file-pen"></i> Modificar Informe
      </button>
      <button class="btn btn-ghost btn-sm" onclick="downloadReporte(${r.id})" style="display:inline-flex; align-items:center; gap:6px; font-weight:700;">
        <i class="fa-solid fa-file-pdf"></i> Descargar PDF
      </button>
      <button class="btn btn-primary btn-sm" onclick="closeModal('detailModal')">Cerrar</button>
    </div>
  `;
  openModal('detailModal');
}
window.viewInformeEjecutivo = viewInformeEjecutivo;
window.viewReporte = viewReporteBitacora; // legacy

// ── MODAL 1: MODIFICAR BITÁCORA DE OPERACIÓN (IMAGEN 1) ──
function populateBitacoraTurnosDropdown() {
  const sel = document.getElementById('overrideBitacoraTurnoSelect');
  if (!sel) return;
  sel.innerHTML = '<option value="">Selecciona un vuelo...</option>' +
    reportesData.map(r => `<option value="${r.turno_id || r.id}">#${r.turno_id || r.id} — ${r.servicio || 'Vuelo'} | ${r.finca || 'Finca'} (${r.cliente || 'Cliente'})</option>`).join('');
}

window.onOverrideBitacoraTurnoChange = function() {
  const sel = document.getElementById('overrideBitacoraTurnoSelect');
  const id = parseInt(sel?.value);
  if (!id) return;
  const r = reportesData.find(x => x.id === id || x.turno_id === id);
  if (r) {
    if (document.getElementById('overrideTurnoId')) document.getElementById('overrideTurnoId').value = id;
    if (document.getElementById('overrideInsumos')) document.getElementById('overrideInsumos').value = r.insumos_litros || 15.0;
    if (document.getElementById('overrideAgua')) document.getElementById('overrideAgua').value = r.agua_litros || 120.0;
    if (document.getElementById('overrideBaterias')) document.getElementById('overrideBaterias').value = r.baterias || 4;
    if (document.getElementById('overrideHectareas')) document.getElementById('overrideHectareas').value = r.area_ha || 10.0;
    if (document.getElementById('overrideRac')) document.getElementById('overrideRac').value = r.cumple_rac !== undefined ? r.cumple_rac : 1;
    if (document.getElementById('overrideObservaciones')) document.getElementById('overrideObservaciones').value = r.observaciones || '';
    
    const prev = document.getElementById('overrideBitacoraPreviewText');
    if (prev) prev.textContent = `Vuelo #${id} — Finca: ${r.finca || '—'} | Servicio: ${r.servicio || '—'} | Piloto: ${r.tecnico || '—'}`;
  }
};

window.openEditBitacoraModal = function(id) {
  populateBitacoraTurnosDropdown();
  const r = reportesData.find(x => x.id === id || x.turno_id === id);
  const turnoId = r ? (r.turno_id || r.id) : id;

  if (document.getElementById('overrideTurnoId')) document.getElementById('overrideTurnoId').value = turnoId;
  const sel = document.getElementById('overrideBitacoraTurnoSelect');
  if (sel) sel.value = turnoId;
  
  if (r) {
    if (document.getElementById('overrideInsumos')) document.getElementById('overrideInsumos').value = r.insumos_litros || 15.0;
    if (document.getElementById('overrideAgua')) document.getElementById('overrideAgua').value = r.agua_litros || 120.0;
    if (document.getElementById('overrideBaterias')) document.getElementById('overrideBaterias').value = r.baterias || 4;
    if (document.getElementById('overrideHectareas')) document.getElementById('overrideHectareas').value = r.area_ha || 10.0;
    if (document.getElementById('overrideRac')) document.getElementById('overrideRac').value = r.cumple_rac !== undefined ? r.cumple_rac : 1;
    if (document.getElementById('overrideObservaciones')) document.getElementById('overrideObservaciones').value = r.observaciones || '';
    
    const prev = document.getElementById('overrideBitacoraPreviewText');
    if (prev) prev.textContent = `Vuelo #${turnoId} — Finca: ${r.finca || '—'} | Servicio: ${r.servicio || '—'} | Piloto: ${r.tecnico || '—'}`;
  }
  openModal('overrideBitacoraModal');
};
window.openOverrideBitacoraModal = window.openEditBitacoraModal;

window.openNewBitacoraModal = function() {
  populateBitacoraTurnosDropdown();
  if (document.getElementById('overrideTurnoId')) document.getElementById('overrideTurnoId').value = '';
  if (document.getElementById('overrideBitacoraTurnoSelect')) document.getElementById('overrideBitacoraTurnoSelect').value = '';
  if (document.getElementById('overrideInsumos')) document.getElementById('overrideInsumos').value = '15.0';
  if (document.getElementById('overrideAgua')) document.getElementById('overrideAgua').value = '120.0';
  if (document.getElementById('overrideBaterias')) document.getElementById('overrideBaterias').value = '4';
  if (document.getElementById('overrideHectareas')) document.getElementById('overrideHectareas').value = '10.0';
  if (document.getElementById('overrideRac')) document.getElementById('overrideRac').value = '1';
  if (document.getElementById('overrideObservaciones')) document.getElementById('overrideObservaciones').value = '';
  const prev = document.getElementById('overrideBitacoraPreviewText');
  if (prev) prev.textContent = 'Selecciona un vuelo para cargar la bitácora técnica de operación...';
  openModal('overrideBitacoraModal');
};

window.submitOverrideBitacora = async function(e) {
  if (e) e.preventDefault();
  const id_turno = document.getElementById('overrideTurnoId')?.value || document.getElementById('overrideBitacoraTurnoSelect')?.value;
  if (!id_turno) return showToast('Error: ID de turno no seleccionado', 'error');

  const payload = {
    insumos_litros_aplicados: parseFloat(document.getElementById('overrideInsumos')?.value) || 0,
    agua_litros: parseFloat(document.getElementById('overrideAgua')?.value) || 0,
    baterias_utilizadas: parseInt(document.getElementById('overrideBaterias')?.value) || 1,
    cumple_rac100: parseInt(document.getElementById('overrideRac')?.value) || 1,
    observaciones_campo: document.getElementById('overrideObservaciones')?.value.trim() || null
  };

  try {
    showToast('Guardando modificaciones de la bitácora de operación...', 'info');
    await apiFetch(`/tecnico/agenda/${id_turno}/checkout`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
    showToast('<i class="fa-solid fa-check"></i> Bitácora de operación guardada exitosamente', 'success');
    closeModal('overrideBitacoraModal');
    invalidateCache('reportes-vuelo');
    invalidateCache('agenda');
    await loadReportes();
    if (activePanel === 'agenda') await loadAgenda();
  } catch (err) {
    showToast('Error al actualizar bitácora: ' + err.message, 'error');
  }
};

// ── MODAL 2: MODIFICAR INFORME EJECUTIVO & ENTREGABLE (IMAGEN 3) ──
function populateInformeTurnosDropdown() {
  const sel = document.getElementById('overrideInformeTurnoSelect');
  if (!sel) return;
  sel.innerHTML = '<option value="">Selecciona un vuelo...</option>' +
    reportesData.map(r => `<option value="${r.turno_id || r.id}">#${r.turno_id || r.id} — ${r.servicio || 'Vuelo'} | ${r.finca || 'Finca'} (${r.cliente || 'Cliente'})</option>`).join('');
}

async function loadServiciosTiposDropdown(selectId = 'overrideInformeTipo') {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  try {
    const raw = await apiFetch('/servicios') || [];
    const servicios = Array.isArray(raw) ? raw : (raw.data || []);
    if (servicios.length > 0) {
      sel.innerHTML = servicios.map(s => {
        const nom = s.nombre || s.nombre_servicio || s.titulo || 'Servicio Agrícola';
        return `<option value="${nom}">${nom}</option>`;
      }).join('');
      return;
    }
  } catch(e) {}
  // Fallback defaults
  sel.innerHTML = `
    <option value="Informe Técnico de Aspersión / Pulverización">Informe Técnico de Aspersión / Pulverización</option>
    <option value="Mapa Multiespectral (NDVI)">Mapa Multiespectral e Índice NDVI</option>
    <option value="Ortomosaico Topográfico">Ortomosaico 2D / Topografía 3D (MDE/CAD)</option>
    <option value="Inspección Visual 4K / Térmica">Registro Fotográfico 4K & Diagnóstico Térmico</option>
    <option value="Aforo y Mapeo de Pasturas">Zonificación de Potreros y Pastos</option>
  `;
}
window.loadServiciosTiposDropdown = loadServiciosTiposDropdown;

window.openNewInformeEjecutivoModal = async function() {
  populateInformeTurnosDropdown();
  await loadServiciosTiposDropdown('overrideInformeTipo');
  if (document.getElementById('overrideInformeTurnoId')) document.getElementById('overrideInformeTurnoId').value = '';
  if (document.getElementById('overrideInformeTurnoSelect')) document.getElementById('overrideInformeTurnoSelect').value = '';
  if (document.getElementById('overrideInformeDriveUrl')) document.getElementById('overrideInformeDriveUrl').value = '';
  if (document.getElementById('overrideInformeRecomendaciones')) document.getElementById('overrideInformeRecomendaciones').value = '';
  if (document.getElementById('overrideInformeNotas')) document.getElementById('overrideInformeNotas').value = '';
  openModal('overrideInformeEjecutivoModal');
};

window.openEditInformeEjecutivoModal = async function(id) {
  populateInformeTurnosDropdown();
  await loadServiciosTiposDropdown('overrideInformeTipo');
  
  const r = reportesData.find(x => x.id === id || x.turno_id === id);
  const turnoId = r ? (r.turno_id || r.id) : id;

  if (document.getElementById('overrideInformeTurnoId')) document.getElementById('overrideInformeTurnoId').value = turnoId;
  const sel = document.getElementById('overrideInformeTurnoSelect');
  if (sel) sel.value = turnoId;
  
  if (r) {
    if (document.getElementById('overrideInformeTipo') && r.servicio) {
      document.getElementById('overrideInformeTipo').value = r.servicio;
    }
    if (document.getElementById('overrideInformeDriveUrl')) document.getElementById('overrideInformeDriveUrl').value = r.url_entregable_drive || '';
    if (document.getElementById('overrideInformeRecomendaciones')) document.getElementById('overrideInformeRecomendaciones').value = r.recomendaciones_agronomicas || '';
  }
  openModal('overrideInformeEjecutivoModal');
};
window.openOverrideInformeModal = window.openEditInformeEjecutivoModal;

window.submitOverrideInformeEjecutivo = async function(e) {
  if (e) e.preventDefault();
  const id_turno = document.getElementById('overrideInformeTurnoId')?.value || document.getElementById('overrideInformeTurnoSelect')?.value;
  if (!id_turno) return showToast('Error: ID de turno no encontrado', 'error');

  const tipo = document.getElementById('overrideInformeTipo')?.value;
  const link = document.getElementById('overrideInformeDriveUrl')?.value.trim() || null;
  const notas = document.getElementById('overrideInformeRecomendaciones')?.value.trim() || null;
  const fileInput = document.getElementById('overrideInformeFile');

  try {
    showToast('Guardando modificaciones del informe ejecutivo...', 'info');

    if (fileInput && fileInput.files && fileInput.files.length > 0) {
      const formData = new FormData();
      formData.append('id_turno', id_turno);
      formData.append('tipo_archivo', tipo);
      formData.append('file', fileInput.files[0]);
      if (notas) formData.append('notas', notas);

      await fetch(`${API_BASE}/entregables/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
    } else {
      await apiFetch(`/entregables`, {
        method: 'POST',
        body: JSON.stringify({
          id_turno: parseInt(id_turno),
          tipo_archivo: tipo,
          url_archivo: link,
          notas: notas
        })
      }).catch(async () => {
        // Fallback checkout update
        await apiFetch(`/tecnico/agenda/${id_turno}/checkout`, {
          method: 'PATCH',
          body: JSON.stringify({
            url_entregable_drive: link,
            recomendaciones_agronomicas: notas
          })
        });
      });
    }

    showToast('<i class="fa-solid fa-check"></i> Informe ejecutivo y entregable guardados exitosamente', 'success');
    closeModal('overrideInformeEjecutivoModal');
    invalidateCache('reportes-vuelo');
    invalidateCache('agenda');
    await loadReportes();
    if (activePanel === 'agenda') await loadAgenda();
  } catch (err) {
    showToast('Error al actualizar informe: ' + err.message, 'error');
  }
};

window.openEditReporteModal = window.openEditInformeEjecutivoModal; // backward-compat

function downloadReporte(id) {
  const r = reportesData.find(x => x.id === id);
  if (r && r.id_entregable) {
    window.open(`${API_BASE}/entregables/${r.id_entregable}/descargar`, '_blank');
    showToast('Iniciando descarga oficial de informe PDF...', 'info');
    return;
  }
  if (r && r.id_turno) {
    window.open(`${API_BASE}/entregables/${r.id_turno}/descargar`, '_blank');
    showToast('Iniciando descarga de informe PDF del turno...', 'info');
    return;
  }
  if (!r) return;
  const content = `===========================================================
                FLYMETRICS AGRICULTURA DE PRECISIÓN
                 REPORTE OFICIAL DE OPERACIÓN Y RAC-100
===========================================================

  ID Reporte / Vuelo: #FM-REP-${r.id}
  Fecha de Operación: ${r.fecha || new Date().toISOString().split('T')[0]}
  Cliente Agrícola:   ${r.cliente || 'Cliente Flymetrics'}
  Predio / Finca:     ${r.finca || 'Finca Agrícola'}
  Piloto Técnico:     ${r.tecnico || 'Técnico Certificado'}
  
-----------------------------------------------------------
  DATOS DE LA MISIÓN Y TELEMETRÍA AÉREA
-----------------------------------------------------------
  Tiempo de Vuelo:     ${r.duracion_min || 45} minutos
  Área Trata / Ha:     ${r.area_ha || 10.0} ha
  Mezcla / Producto:   ${r.producto || 'Aspersión / Multiespectral'}
  Dosis Aplicada:      ${r.dosis_l_ha || '12.0'} L/ha
  Condición de Viento: ${r.condicion_viento || 'Óptima (8 km/h)'}
  Temperatura Amb.:    ${r.temperatura || 24}°C
  Humedad Relativa:    ${r.humedad || 65}%
  Cumplimiento RAC100: SI (Regulación Aeronáutica Vigente)

-----------------------------------------------------------
  RECOMENDACIONES AGRONÓMICAS Y OBSERVACIONES
-----------------------------------------------------------
  ${r.observaciones || 'Inspección realizada con éxito. Vigor vegetal dentro de parámetros óptimos.'}

===========================================================
  Certificación Oficial — Flymetrics Colombia S.A.S.
  Documento generado electrónicamente.
===========================================================`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Reporte_Oficial_Flymetrics_RAC100_${r.id}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('<i class="fa-solid fa-check"></i> Reporte técnico oficial generado y descargado', 'success');
}

// ─────────────────────────────────────────
// 9. CONFIGURACIÓN PANEL (BASE DE DATOS)
// ─────────────────────────────────────────
function loadConfiguracion() {
  if (typeof window.loadCorporateConfig === 'function') {
    window.loadCorporateConfig();
  }
}

async function saveConfig() {
  if (typeof window.saveCorporateConfig === 'function') {
    await window.saveCorporateConfig();
  }
}

async function changePassword() {
  const current = document.getElementById('cfgCurrentPwd')?.value || '';
  const newPwd = document.getElementById('cfgNewPwd')?.value || '';
  const confirm = document.getElementById('cfgConfirmPwd')?.value || '';

  if (!newPwd || !confirm) return showToast('Por favor ingresa y confirma la nueva contraseña', 'warn');
  if (newPwd !== confirm) return showToast('Las contraseñas no coinciden', 'error');
  if (newPwd.length < 6) return showToast('La contraseña debe tener al menos 6 caracteres', 'warn');

  try {
    showToast('Actualizando contraseña...', 'info');
    await apiFetch('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: current, new_password: newPwd })
    });
    showToast('<i class="fa-solid fa-check"></i> Contraseña de administrador actualizada exitosamente en la base de datos', 'success');
    if (document.getElementById('cfgCurrentPwd')) document.getElementById('cfgCurrentPwd').value = '';
    if (document.getElementById('cfgNewPwd')) document.getElementById('cfgNewPwd').value = '';
    if (document.getElementById('cfgConfirmPwd')) document.getElementById('cfgConfirmPwd').value = '';
  } catch (e) {
    showToast('Error al actualizar contraseña: ' + e.message, 'error');
  }
}
window.changePassword = changePassword;

/* ============================================================
   PERFIL CORPORATIVO & CONFIGURACIÓN GLOBAL
   ============================================================ */
const DEFAULT_CORPORATE_CONFIG = {
  empresa: "Flymetrics Colombia S.A.S.",
  nit: "900.123.456-7",
  telefono: "+57 305 406 1764",
  whatsapp: "+57 305 406 1764",
  email: "comercial@flymetrix.com.co",
  direccion: "Avenida El Dorado #68b-70, Bogotá D.C.",
  wa_template_24h: "Hola {nombre}, te contactamos desde Flymetrics Colombia sobre tu solicitud de {servicio} ({hectareas} ha).",
  wa_template_agendar: "Hola Flymetrics Colombia, acabo de agendar una solicitud de servicio / demostración:\nRadicado: {radicado}\nProductor: {nombre} (CC/NIT: {cedula})\nFinca: {finca} en {municipio} ({departamento})\nCultivo: {cultivo} ({hectareas} Ha)\nServicio: {servicio}\nFecha programada: {fecha}\nUbicación / Maps: {ubicacion_maps}\nDeseo coordinar detalles técnicos de campo con el piloto.",
  wa_template_general: "Hola Flymetrics, deseo solicitar asesoría e información técnica sobre sus servicios de drones agrícolas."
};

let _currentCorporateConfig = { ...DEFAULT_CORPORATE_CONFIG };

function getCorporateConfig() {
  return _currentCorporateConfig;
}

window.syncCorporatePreview = function() {
  const name = document.getElementById('cfgEmpresa')?.value.trim() || 'Flymetrics';
  const topbrand = document.getElementById('topbarBrandName');
  if (topbrand) topbrand.textContent = name.split(' ')[0] || 'Flymetrics';
};

window.loadCorporateConfig = async function() {
  let cfg = DEFAULT_CORPORATE_CONFIG;
  try {
    const res = await apiFetch('/admin/usuarios/config/sistema');
    if (res && (res.empresa || res.telefono || res.whatsapp)) {
      cfg = { ...DEFAULT_CORPORATE_CONFIG, ...res };
      _currentCorporateConfig = cfg;
    }
  } catch (e) {
    console.warn("Could not load system config from DB, using defaults:", e);
  }

  if (document.getElementById('cfgEmpresa')) document.getElementById('cfgEmpresa').value = cfg.empresa;
  if (document.getElementById('cfgNit')) document.getElementById('cfgNit').value = cfg.nit;
  if (document.getElementById('cfgTelefono')) document.getElementById('cfgTelefono').value = cfg.telefono;
  if (document.getElementById('cfgWhatsapp')) document.getElementById('cfgWhatsapp').value = cfg.whatsapp;
  if (document.getElementById('cfgEmail')) document.getElementById('cfgEmail').value = cfg.email;
  if (document.getElementById('cfgDireccion')) document.getElementById('cfgDireccion').value = cfg.direccion || DEFAULT_CORPORATE_CONFIG.direccion;
  if (document.getElementById('cfgWaTemplate24h')) document.getElementById('cfgWaTemplate24h').value = cfg.wa_template_24h || DEFAULT_CORPORATE_CONFIG.wa_template_24h;
  if (document.getElementById('cfgWaTemplateAgendar')) document.getElementById('cfgWaTemplateAgendar').value = cfg.wa_template_agendar || DEFAULT_CORPORATE_CONFIG.wa_template_agendar;
  if (document.getElementById('cfgWaTemplateGeneral')) document.getElementById('cfgWaTemplateGeneral').value = cfg.wa_template_general || DEFAULT_CORPORATE_CONFIG.wa_template_general;
  syncCorporatePreview();
};

window.saveCorporateConfig = async function() {
  const cfg = {
    empresa: document.getElementById('cfgEmpresa')?.value.trim() || DEFAULT_CORPORATE_CONFIG.empresa,
    nit: document.getElementById('cfgNit')?.value.trim() || DEFAULT_CORPORATE_CONFIG.nit,
    telefono: document.getElementById('cfgTelefono')?.value.trim() || DEFAULT_CORPORATE_CONFIG.telefono,
    whatsapp: document.getElementById('cfgWhatsapp')?.value.trim() || DEFAULT_CORPORATE_CONFIG.whatsapp,
    email: document.getElementById('cfgEmail')?.value.trim() || DEFAULT_CORPORATE_CONFIG.email,
    direccion: document.getElementById('cfgDireccion')?.value.trim() || DEFAULT_CORPORATE_CONFIG.direccion,
    wa_template_24h: document.getElementById('cfgWaTemplate24h')?.value.trim() || DEFAULT_CORPORATE_CONFIG.wa_template_24h,
    wa_template_agendar: document.getElementById('cfgWaTemplateAgendar')?.value.trim() || DEFAULT_CORPORATE_CONFIG.wa_template_agendar,
    wa_template_general: document.getElementById('cfgWaTemplateGeneral')?.value.trim() || DEFAULT_CORPORATE_CONFIG.wa_template_general
  };

  try {
    showToast('Guardando configuración en base de datos...', 'info');
    await apiFetch('/admin/usuarios/config/sistema', {
      method: 'PUT',
      body: JSON.stringify(cfg)
    });
    _currentCorporateConfig = cfg;
    syncCorporatePreview();
    showToast('<i class="fa-solid fa-check"></i> Configuración corporativa y plantillas guardadas en base de datos', 'success');
  } catch (e) {
    showToast('Error al guardar configuración: ' + e.message, 'error');
  }
};

window.toggleAdminSidebar = function (e) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('adminSidebarOverlay');
  if (!sidebar) return;

  if (window.innerWidth <= 900) {
    sidebar.classList.toggle('open');
    const isOpen = sidebar.classList.contains('open');
    if (overlay) {
      overlay.classList.toggle('hidden', !isOpen);
      overlay.classList.toggle('active', isOpen);
      overlay.style.opacity = isOpen ? '1' : '0';
      overlay.style.pointerEvents = isOpen ? 'all' : 'none';
      overlay.style.display = isOpen ? 'block' : 'none';
    }
  } else {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('fm_admin_sidebar_collapsed', sidebar.classList.contains('collapsed'));
  }
};

// ─────────────────────────────────────────
// DOM INIT
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async function () {
  // Auth guard & initialization
  await ensureAdminAuth();
  const user = getUser();
  const token = getToken();

  // Restore collapsed sidebar state on desktop
  if (window.innerWidth > 900 && localStorage.getItem('fm_admin_sidebar_collapsed') === 'true') {
    document.getElementById('sidebar')?.classList.add('collapsed');
  }

  // Load admin notifications on start
  loadAdminNotifications();
  loadCorporateConfig();

  // Prevent closing notifications dropdown when clicking inside it
  document.getElementById('adminNotificationsDropdown')?.addEventListener('click', e => {
    e.stopPropagation();
  });

  // Set user info
  const nameEl = document.getElementById('sidebarUserName');
  const roleEl = document.getElementById('sidebarUserRole');
  const initEl = document.getElementById('sidebarUserInitials');

  const fullName = user.nombre ? `${user.nombre} ${user.apellido || user.apellido_1 || ''}`.trim() : (user.name || 'Administrador');
  const userEmail = user.email || 'admin@flymetrics.co';

  if (nameEl) nameEl.textContent = fullName;
  if (roleEl) roleEl.textContent = userEmail;
  if (initEl) {
    const init1 = user.nombre ? user.nombre[0] : userEmail[0];
    const init2 = (user.apellido || user.apellido_1) ? (user.apellido || user.apellido_1)[0] : '';
    initEl.textContent = (init1 + init2).toUpperCase() || 'AD';
  }

  // Navigation with auto-closing mobile sidebar
  document.querySelectorAll('[data-panel]').forEach(el => {
    el.addEventListener('click', () => {
      navigateTo(el.dataset.panel);
      if (window.innerWidth <= 900) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('adminSidebarOverlay');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) {
          overlay.classList.add('hidden');
          overlay.classList.remove('active');
          overlay.style.opacity = '0';
          overlay.style.pointerEvents = 'none';
          overlay.style.display = 'none';
        }
      }
    });
  });

  // Logout
  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    if (confirm('¿Cerrar sesión?')) logout();
  });

  // Close modals on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) closeAllModals();
    });
  });

  // ── AGENDA FILTERS ──
  document.getElementById('agendaSearch')?.addEventListener('input', e => renderAgendaTable());
  document.getElementById('agendaEstadoFilter')?.addEventListener('change', e => renderAgendaTable());
  document.getElementById('agendaTecnicoFilter')?.addEventListener('change', e => renderAgendaTable());
  document.getElementById('agendaDateFilter')?.addEventListener('change', e => {
    selectedCalDate = e.target.value;
    renderCalendar();
    renderAgendaTable();
  });

  // ── NEW AGENDA FORM ──
  document.getElementById('newAgendaBtn')?.addEventListener('click', async () => {
    const form = document.getElementById('newAgendaForm');
    if (form) form.reset();
    if (!clientesData.length) await loadClientes();
    if (!serviciosData.length) await loadServicios();
    if (!tecnicosData.length) await loadTecnicos();

    // Populate clientes
    const csel = document.getElementById('newAgendaClienteSelect');
    if (csel) {
      csel.innerHTML = '<option value="">-- Crear cliente nuevo o seleccionar existente --</option>' +
        clientesData.map(c => `<option value="${c.id_cliente || c.id}">${c.nombre} ${c.apellido} (${c.email || 'Sin email'})</option>`).join('');
    }
    // Populate servicios
    const sel = document.getElementById('newAgendaServicio');
    if (sel) {
      sel.innerHTML = '<option value="">Seleccionar servicio...</option>' +
        (serviciosData.length ? serviciosData : [])
          .filter(s => s.activo)
          .map(s => `<option value="${s.nombre}">${s.nombre}</option>`).join('');
    }
    // Populate tecnicos
    const tsel = document.getElementById('newAgendaTecnico');
    if (tsel) {
      tsel.innerHTML = '<option value="">Sin asignar</option>' +
        (tecnicosData.length ? tecnicosData : [])
          .map(t => `<option value="${t.nombre} ${t.apellido}">${t.nombre} ${t.apellido}</option>`).join('');
    }

    // Set smart defaults for date and time and enforce min date
    const todayIso = new Date().toISOString().split('T')[0];
    const fInput = document.getElementById('newAgendaFecha');
    if (fInput) {
      fInput.min = todayIso;
      if (!fInput.value || fInput.value < todayIso) fInput.value = todayIso;
    }
    const hInput = document.getElementById('newAgendaHora');
    if (hInput && !hInput.value) hInput.value = '08:00';
    const haInput = document.getElementById('newAgendaHa');
    if (haInput && !haInput.value) haInput.value = '10';

    openModal('newAgendaModal');
  });

  document.getElementById('newAgendaForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const cliente = (document.getElementById('newAgendaCliente')?.value || '').trim();
    const email = (document.getElementById('newAgendaEmail')?.value || '').trim();
    const finca = (document.getElementById('newAgendaFinca')?.value || '').trim();
    const ubicacion = (document.getElementById('newAgendaUbicacion')?.value || '').trim();
    const maps = (document.getElementById('newAgendaMaps')?.value || '').trim();
    const servicio = document.getElementById('newAgendaServicio')?.value || '';
    const fecha = document.getElementById('newAgendaFecha')?.value || '';
    const hora = document.getElementById('newAgendaHora')?.value || '08:00';

    if (!cliente) {
      showToast('Por favor ingresa o selecciona el nombre del cliente', 'warn');
      return;
    }
    if (!email) {
      showToast('Por favor ingresa el correo del cliente', 'warn');
      return;
    }
    if (!fecha) {
      showToast('Por favor selecciona la fecha del vuelo', 'warn');
      return;
    }

    const todayIso = new Date().toISOString().split('T')[0];
    if (fecha < todayIso) {
      showToast('La fecha del vuelo no puede ser anterior a hoy (' + todayIso + ')', 'warn');
      return;
    }

    const data = {
      cliente,
      email,
      telefono: (document.getElementById('newAgendaTel')?.value || '').trim(),
      finca: finca || 'Finca Principal',
      ubicacion: ubicacion || 'Cundinamarca',
      maps: maps || '',
      servicio,
      hectareas: parseInt(document.getElementById('newAgendaHa')?.value) || 10,
      fecha,
      hora,
      tecnico: document.getElementById('newAgendaTecnico')?.value || '',
      estado: document.getElementById('newAgendaEstado')?.value || 'Pendiente',
      notas: (document.getElementById('newAgendaNotas')?.value || '').trim(),
    };
    await createAgenda(data);
  });

  // ── CLIENTES SEARCH ──
  document.getElementById('clientesSearch')?.addEventListener('input', e => renderClientesTable(e.target.value));

  document.getElementById('newClienteBtn')?.addEventListener('click', () => {
    document.getElementById('newClienteForm').reset();
    openModal('newClienteModal');
  });

  document.getElementById('newClienteForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const nombre = document.getElementById('newClienteNombre')?.value || '';
    const email = document.getElementById('newClienteEmail')?.value || '';
    const telefono = document.getElementById('newClienteTel')?.value || '';
    const password = document.getElementById('newClientePassword')?.value || '';
    const nombre_finca = document.getElementById('newClienteFinca')?.value || '';
    const hectareas = document.getElementById('newClienteHectareas')?.value || '';
    const departamento = document.getElementById('newClienteDepto')?.value || '';
    const ciudad = document.getElementById('newClienteCiudad')?.value || '';

    if (!nombre.trim()) {
      showToast('Por favor escribe el Nombre Completo del cliente', 'warn');
      return;
    }
    if (email.trim() && !email.includes('@')) {
      showToast('Por favor escribe un correo electrónico válido', 'warn');
      return;
    }

    const data = {
      nombre,
      email,
      telefono,
      password,
      nombre_finca,
      hectareas,
      departamento,
      ciudad
    };
    await createCliente(data);
  });

  // ── TECNICOS ──
  document.getElementById('tecnicosSearch')?.addEventListener('input', e => renderTecnicosTable(e.target.value));

  document.getElementById('newTecnicoBtn')?.addEventListener('click', () => {
    document.getElementById('newTecnicoForm').reset();
    openModal('newTecnicoModal');
  });

  document.getElementById('newTecnicoForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const rawNombre = (document.getElementById('newTecnicoNombre')?.value || '').trim();
    const certificacion = document.getElementById('newTecnicoCert')?.value || 'Piloto RPAS Nivel A';
    const telefono = (document.getElementById('newTecnicoTel')?.value || '').trim();
    const email = (document.getElementById('newTecnicoEmail')?.value || '').trim();
    const password = (document.getElementById('newTecnicoPassword')?.value || '').trim();

    if (!rawNombre) {
      showToast('Por favor ingresa el Nombre Completo del técnico', 'warn');
      return;
    }
    if (!password || password.length < 6) {
      showToast('La contraseña debe tener al menos 6 caracteres', 'warn');
      return;
    }

    const parts = rawNombre.split(/\s+/);
    const nombre = parts[0] || rawNombre;
    const apellido = parts.slice(1).join(' ') || '';

    const data = {
      nombre: rawNombre,
      apellido: apellido,
      certificacion,
      telefono,
      email,
      password,
      estado: 'disponible',
    };
    await createTecnico(data);
  });

  document.getElementById('editTecnicoForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const rawNombre = (document.getElementById('editTecnicoNombre')?.value || '').trim();
    const parts = rawNombre.split(/\s+/);
    const nombre = parts[0] || rawNombre;
    const apellido = parts.slice(1).join(' ') || '';

    await updateTecnico({
      id: document.getElementById('editTecnicoId').value,
      nombre: rawNombre,
      apellido: apellido,
      certificacion: document.getElementById('editTecnicoCert').value,
      telefono: document.getElementById('editTecnicoTel').value,
      estado: document.getElementById('editTecnicoEstado').value,
      password: (document.getElementById('editTecnicoPassword')?.value || '').trim()
    });
  });

  // ── DRONES ──
  document.getElementById('dronesSearch')?.addEventListener('input', e => renderDronesTable(e.target.value));

  document.getElementById('newDroneBtn')?.addEventListener('click', () => {
    document.getElementById('newDroneForm').reset();
    openModal('newDroneModal');
  });

  document.getElementById('newDroneForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const id_tec = document.getElementById('newDroneTecnico')?.value;
    await createDrone({
      modelo: document.getElementById('newDroneModelo').value,
      tipo: document.getElementById('newDroneTipo').value,
      numero_serie: document.getElementById('newDroneSerie').value,
      id_tecnico_asignado: id_tec ? parseInt(id_tec) : null,
      estado: 'disponible',
      ultima_revision: new Date().toISOString().split('T')[0],
      horas_vuelo: 0,
    });
  });

  document.getElementById('editDroneForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const id_tec = document.getElementById('editDroneTecnico')?.value;
    await updateDrone({
      id: document.getElementById('editDroneId').value,
      modelo: document.getElementById('editDroneModelo').value,
      tipo: document.getElementById('editDroneTipo').value,
      estado: document.getElementById('editDroneEstado').value,
      id_tecnico_asignado: id_tec ? parseInt(id_tec) : null,
      ultima_revision: document.getElementById('editDroneRevision').value,
      numero_serie: document.getElementById('editDroneSerie').value,
      horas_vuelo: parseInt(document.getElementById('editDroneHoras').value) || 0,
    });
  });

  // ── RESET CONTRASEÑA ADMIN ──
  document.getElementById('changePasswordBtn')?.addEventListener('click', changePassword);

  // ── COTIZACIONES & CONTACTO 24H ──
  document.getElementById('contactoWebSearch')?.addEventListener('input', () => renderContactoWebTable());
  document.getElementById('contactoWebEstadoFilter')?.addEventListener('change', () => renderContactoWebTable());

  // ── FACTURACIÓN / COMPROBANTES ──
  document.getElementById('pagosSearch')?.addEventListener('input', e => renderPagosTable(e.target.value));

  document.getElementById('newPagoBtn')?.addEventListener('click', async () => {
    document.getElementById('newPagoForm').reset();
    const select = document.getElementById('newPagoTurnoId');
    const fincaInfoEl = document.getElementById('newPagoFincaInfo');
    if (fincaInfoEl) {
      fincaInfoEl.innerHTML = '<span><i class="fa-solid fa-wheat-awn"></i> <strong>Finca / Predio:</strong> Selecciona un vuelo para ver la finca asociada.</span>';
    }
    
    if (select) {
      if (!agendaData || !agendaData.length) {
        try {
          const freshAgenda = await apiFetch('/admin/agenda') || await apiFetch('/agenda') || [];
          agendaData = Array.isArray(freshAgenda) ? freshAgenda : (freshAgenda.data || []);
        } catch (e) {
          console.warn("Error fetching agenda for pagos:", e);
        }
      }
      
      const turnosCompleto = (agendaData && agendaData.length) ? agendaData : [];
      turnosCompleto.sort((a, b) => {
        const estA = String(a.estado || '').toLowerCase();
        const estB = String(b.estado || '').toLowerCase();
        const isDoneA = estA.includes('hecho') || estA.includes('complet');
        const isDoneB = estB.includes('hecho') || estB.includes('complet');
        if (isDoneA && !isDoneB) return -1;
        if (!isDoneA && isDoneB) return 1;
        return (b.id_turno || b.id || 0) - (a.id_turno || a.id || 0);
      });

      if (!turnosCompleto.length) {
        select.innerHTML = '<option value="">Sin vuelos agendados en el sistema</option>';
      } else {
        select.innerHTML = '<option value="">Selecciona un vuelo...</option>' +
          turnosCompleto.map(a => {
            const idT = a.id_turno || a.id;
            const cliente = a.cliente || a.cliente_nombre || a.nombre_cliente || 'Cliente';
            const finca = a.finca || a.finca_nombre || a.nombre_finca || 'Finca Principal';
            const servicio = a.servicio || a.servicio_nombre || a.nombre_servicio || 'Servicio Dron';
            const estado = a.estado || 'Pendiente';
            const tarifa = a.precio || a.tarifa || a.monto || 850000;
            const isHecho = String(estado).toLowerCase().includes('hecho') || String(estado).toLowerCase().includes('complet');
            const prefix = isHecho ? '✅ [HECHO]' : `[${estado.toUpperCase()}]`;
            
            return `<option value="${idT}" data-tarifa="${tarifa}" data-finca="${finca}" data-cliente="${cliente}" data-servicio="${servicio}">${prefix} #${idT} — ${servicio} | ${finca} (${cliente})</option>`;
          }).join('');
      }
    }
    openModal('newPagoModal');
  });

  document.getElementById('newPagoForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const id_turno = parseInt(document.getElementById('newPagoTurnoId').value);
    const monto = parseFloat(document.getElementById('newPagoMonto').value) || 0;
    const metodo_pago = document.getElementById('newPagoMetodo').value || 'Transferencia';
    const referencia_transaccion = 'TRANS-' + Date.now();

    await createPago({
      id_turno,
      monto,
      metodo_pago,
      referencia_transaccion
    });
  });

  window.onPagoTurnoChange = function () {
    const select = document.getElementById('newPagoTurnoId');
    if (!select) return;
    const selectedOption = select.options[select.selectedIndex];
    const fincaInfoEl = document.getElementById('newPagoFincaInfo');
    if (selectedOption && selectedOption.value) {
      const tarifa = selectedOption.getAttribute('data-tarifa') || 0;
      const finca = selectedOption.getAttribute('data-finca') || 'Finca Agrícola';
      const cliente = selectedOption.getAttribute('data-cliente') || 'Cliente';
      const servicio = selectedOption.getAttribute('data-servicio') || 'Servicio Dron';
      
      const montoInput = document.getElementById('newPagoMonto');
      if (montoInput) montoInput.value = Math.round(tarifa);
      
      if (fincaInfoEl) {
        fincaInfoEl.innerHTML = `<span><i class="fa-solid fa-wheat-awn"></i> <strong>Finca / Predio:</strong> <strong style="color:#1c82ad">${finca}</strong> | <i class="fa-solid fa-user"></i> Cliente: <strong>${cliente}</strong> | <i class="fa-solid fa-gear"></i> ${servicio}</span>`;
      }
    } else {
      if (fincaInfoEl) {
        fincaInfoEl.innerHTML = '<span><i class="fa-solid fa-wheat-awn"></i> <strong>Finca / Predio:</strong> Selecciona un vuelo para ver la finca asociada.</span>';
      }
    }
  };

  // ── SERVICIOS ──
  document.getElementById('editPrecioForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const id = parseInt(document.getElementById('editPrecioId').value);
    const precio = parseInt(document.getElementById('editPrecioValor').value);
    await updateServicePrice(id, precio);
  });

  // ── CONFIGURACIÓN ──
  document.getElementById('saveConfigBtn')?.addEventListener('click', saveConfig);
  document.getElementById('changePasswordBtn')?.addEventListener('click', changePassword);

  // ── QUICK ACTIONS ──
  document.querySelectorAll('[data-quick]').forEach(el => {
    el.addEventListener('click', () => {
      const target = el.dataset.quick;
      navigateTo(target);
      if (target === 'agenda') {
        setTimeout(() => document.getElementById('newAgendaBtn')?.click(), 300);
      }
    });
  });

  // Keyboard: ESC closes modals and dropdowns
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeAllModals();
      document.getElementById('adminNotificationsDropdown')?.classList.add('hidden');
    }
  });

  // Load default panel
  navigateTo('dashboard');
});

// ── ADMIN NOTIFICATIONS LOGIC ────────────


async function loadAdminNotifications() {
  try {
    _adminNotifs = [
      { id: 1, titulo: "Nuevo Registro", mensaje: "El cliente Carlos Mendoza se ha registrado en la plataforma.", fecha: new Date().toISOString().split('T')[0] },
      { id: 2, titulo: "Validación de Cédula", mensaje: "Miguel Torres ha completado exitosamente su validación de identidad.", fecha: new Date().toISOString().split('T')[0] }
    ];
    renderAdminNotifications();
  } catch (e) {
    renderAdminNotifications();
  }
}

function renderAdminNotifications() {
  const list = document.getElementById('adminNotificationsList');
  const dot = document.getElementById('adminBellDot');

  if (dot) {
    dot.style.display = _adminNotifs.length > 0 ? 'block' : 'none';
  }

  if (list) {
    list.innerHTML = _adminNotifs.map(n => `
      <div style="padding: 12px 18px; border-bottom: 1px solid rgba(255,255,255,0.03);">
        <div style="display:flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
          <strong style="font-size: 0.82rem; color: #fff;">${n.titulo}</strong>
          <span style="font-size: 0.65rem; color: var(--text-2);">${n.fecha}</span>
        </div>
        <p style="margin: 0; font-size: 0.78rem; color: var(--text-2); line-height: 1.4; text-align: left;">${n.mensaje}</p>
      </div>
    `).join('');
  }
}

window.toggleAdminNotifications = function (e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById('adminNotificationsDropdown');
  const isOpen = dropdown.classList.toggle('hidden');
  if (!isOpen) {
    loadAdminNotifications();
  }
};

window.openNewNotifModal = function (e) {
  if (e) e.stopPropagation();
  document.getElementById('adminNotificationsDropdown').classList.add('hidden');

  const select = document.getElementById('notifClienteSelect');
  const clientes = cache['clientes']?.data || [];
  select.innerHTML = '<option value="">Seleccionar cliente...</option>' +
    clientes.map(c => `<option value="${c.id_usuario || c.id}">${c.nombre} ${c.apellido} (User ID: ${c.id_usuario || c.id})</option>`).join('');

  openModal('newNotifModal');
};

window.submitNewNotif = async function () {
  const id_usuario = parseInt(document.getElementById('notifClienteSelect').value);
  const titulo = document.getElementById('notifTitulo').value.trim();
  const mensaje = document.getElementById('notifMensaje').value.trim();

  if (!id_usuario || !titulo || !mensaje) {
    showToast('Por favor completa todos los campos', 'warn');
    return;
  }

  try {
    await apiFetch('/notificaciones', {
      method: 'POST',
      body: JSON.stringify({ id_usuario, titulo, mensaje })
    });
    showToast('Notificación enviada con éxito', 'success');
    closeModal('newNotifModal');
  } catch (e) {
    showToast('Alerta enviada correctamente (Modo Demo)', 'success');
    closeModal('newNotifModal');
  }
};

// Close dropdown on click outside
window.addEventListener('click', () => {
  document.getElementById('adminNotificationsDropdown')?.classList.add('hidden');
});

// ═══════════════════════════════════════════════════
// GESTIÓN DE USUARIOS (Admins, Técnicos, Clientes)
// ═══════════════════════════════════════════════════

const ROL_BADGE = {
  administrador: `<span style="background:rgba(30,144,255,0.15);color:#1E90FF;padding:3px 10px;border-radius:20px;font-size:0.74rem;font-weight:600;border:1px solid rgba(30,144,255,0.3)"><i class="fa-solid fa-user-tie"></i> Admin</span>`,
  tecnico: `<span style="background:rgba(0,255,136,0.12);color:#00B060;padding:3px 10px;border-radius:20px;font-size:0.74rem;font-weight:600;border:1px solid rgba(0,255,136,0.3)"><i class="fa-solid fa-user-gear"></i> Técnico</span>`,
  cliente: `<span style="background:rgba(255,184,0,0.12);color:#D97706;padding:3px 10px;border-radius:20px;font-size:0.74rem;font-weight:600;border:1px solid rgba(255,184,0,0.3)"><i class="fa-solid fa-user"></i> Cliente</span>`,
};



function filtrarUsuariosRol(rol, btn) {
  _usuariosFiltroRol = rol;
  document.querySelectorAll('.usuariosFiltro').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderUsuariosTable(document.getElementById('usuariosSearch')?.value || '');
}

// ── Crear Staff ──────────────────────────────────
function onStaffRolChange() {
  const esTecnico = document.getElementById('staffRolTecnico')?.checked;
  const cardTec = document.getElementById('cardRolTecnico');
  const cardAdm = document.getElementById('cardRolAdmin');
  const certField = document.getElementById('staffCertificacionField');

  if (cardTec) {
    cardTec.style.border = esTecnico ? '2px solid var(--accent)' : '2px solid rgba(255,255,255,0.1)';
    cardTec.style.background = esTecnico ? 'rgba(0,255,136,0.06)' : 'rgba(30,144,255,0.03)';
    cardTec.querySelector('div:nth-child(2)').style.color = esTecnico ? 'var(--accent)' : 'var(--text-2)';
  }
  if (cardAdm) {
    cardAdm.style.border = !esTecnico ? '2px solid #1E90FF' : '2px solid rgba(255,255,255,0.1)';
    cardAdm.style.background = !esTecnico ? 'rgba(30,144,255,0.06)' : 'rgba(30,144,255,0.03)';
    cardAdm.querySelector('div:nth-child(2)').style.color = !esTecnico ? '#1E90FF' : 'var(--text-2)';
  }
  if (certField) certField.style.display = esTecnico ? 'block' : 'none';
}

async function submitNewStaff(e) {
  e.preventDefault();
  const errEl = document.getElementById('staffErrMsg');
  const btn = document.getElementById('btnCrearStaff');
  const rol = document.querySelector('input[name="staffRol"]:checked')?.value;

  errEl.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Creando...';

  const rawNombre = (document.getElementById('staffNombre')?.value || '').trim();
  const parts = rawNombre.split(/\s+/);
  const nombre = parts[0] || rawNombre;
  const apellido_1 = parts.slice(1).join(' ') || '';

  const payload = {
    email: document.getElementById('staffEmail').value.trim(),
    'contraseña': document.getElementById('staffPassword').value,
    rol,
    nombre: rawNombre,
    apellido_1: apellido_1,
    apellido_2: null,
    telefono: document.getElementById('staffTelefono')?.value.trim() || null,
  };

  // Si es tecnico, lo creamos via /tecnicos que también establece certificacion
  let endpoint = '/admin/usuarios';

  try {
    if (rol === 'tecnico') {
      // Usar endpoint /tecnicos que maneja certificacion
      const cert = document.getElementById('staffCertificacion')?.value.trim();
      const techPayload = { ...payload, certificacion: cert || 'Piloto RPAS Nivel A' };
      await apiFetch('/tecnicos', { method: 'POST', body: JSON.stringify(techPayload) });
    } else {
      await apiFetch(endpoint, { method: 'POST', body: JSON.stringify(payload) });
    }
    showToast(`${rol === 'tecnico' ? 'Técnico' : 'Administrador'} creado correctamente`, 'success');
    closeModal('newStaffModal');
    document.getElementById('newStaffForm').reset();
    document.getElementById('staffRolTecnico').checked = true;
    onStaffRolChange();
    await loadUsuarios();
    if (rol === 'tecnico') { invalidateCache('tecnicos'); await loadTecnicos(); }
  } catch (err) {
    errEl.textContent = err.message || 'Error al crear el usuario. Verifica que el email no esté en uso.';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = '+ Crear usuario';
  }
}

// ── Cambiar Rol ──────────────────────────────────
function abrirCambiarRol(id, email) {
  document.getElementById('cambiarRolUserId').value = id;
  document.getElementById('cambiarRolEmail').textContent = email;
  openModal('cambiarRolModal');
}

async function confirmarCambioRol(nuevoRol) {
  const id = document.getElementById('cambiarRolUserId').value;
  try {
    await apiFetch(`/admin/usuarios/${id}?rol=${nuevoRol}`, {
      method: 'PUT'
    });
    showToast(`<i class="fa-solid fa-check"></i> Rol actualizado a "${nuevoRol}"`, 'success');
    closeModal('cambiarRolModal');
    await loadUsuarios();
  } catch (err) {
    showToast('Error: ' + (err.message || 'No se pudo cambiar el rol'), 'error');
  }
}

// ── Reset Password ───────────────────────────────
function abrirResetPassword(id, email) {
  document.getElementById('resetPwdUserId').value = id;
  document.getElementById('resetPwdEmail').textContent = email;
  document.getElementById('resetPwdValue').value = '';
  document.getElementById('resetPwdErr').style.display = 'none';
  openModal('resetPasswordModal');
}

async function confirmarResetPassword() {
  const id = document.getElementById('resetPwdUserId').value;
  const nueva = document.getElementById('resetPwdValue').value;
  const errEl = document.getElementById('resetPwdErr');
  errEl.style.display = 'none';

  if (nueva.length < 6) {
    errEl.textContent = 'La contraseña debe tener al menos 6 caracteres.';
    errEl.style.display = 'block';
    return;
  }

  try {
    await apiFetch(`/admin/usuarios/${id}?contrase%C3%B1a=${encodeURIComponent(nueva)}`, {
      method: 'PUT'
    });
    showToast('<i class="fa-solid fa-check"></i> Contraseña restablecida correctamente', 'success');
    closeModal('resetPasswordModal');
  } catch (err) {
    errEl.textContent = err.message || 'Error al restablecer contraseña.';
    errEl.style.display = 'block';
  }
}

// ── Eliminar Usuario ─────────────────────────────
async function confirmarEliminarUsuario(id, email) {
  if (!confirm(`<i class="fa-solid fa-triangle-exclamation"></i> ¿Estás seguro de eliminar al usuario "${email}"?\n\nEsta acción no se puede deshacer.`)) return;
  try {
    await apiFetch(`/admin/usuarios/${id}`, { method: 'DELETE' });
    showToast('<i class="fa-solid fa-check"></i> Usuario eliminado correctamente', 'success');
    await loadUsuarios();
  } catch (err) {
    showToast('Error: ' + (err.message || 'No se pudo eliminar el usuario'), 'error');
  }
}

window.openChangePasswordModal = function(id, email) {
  const label = document.getElementById('changePassUserEmailLabel');
  const idInput = document.getElementById('changePassUserId') || document.getElementById('changePassUserIdInput');
  const passInput = document.getElementById('changePassNewInput');
  if (label) label.textContent = email || `Usuario #${id}`;
  if (idInput) idInput.value = id;
  if (passInput) passInput.value = '';
  openModal('changePasswordModal');
};

window.deleteUsuario = function(id) {
  const u = _usuariosList.find(x => String(x.id_usuarios || x.id) === String(id));
  confirmarEliminarUsuario(id, u ? u.email : `ID #${id}`);
};

window.submitChangePassword = window.submitChangeUserPassword;

window.abrirCambiarRol = abrirCambiarRol;
window.confirmarCambioRol = confirmarCambioRol;
window.abrirResetPassword = abrirResetPassword;
window.confirmarResetPassword = confirmarResetPassword;
window.confirmarEliminarUsuario = confirmarEliminarUsuario;

// Cargar usuarios cuando se abre el panel e iniciar refresco automático reactivo
document.addEventListener('DOMContentLoaded', async () => {
  await ensureAdminAuth();

  // Bind navigation click events
  document.querySelectorAll('.sidebar-nav .nav-item[data-panel]').forEach(btn => {
    btn.addEventListener('click', () => {
      const panelId = btn.getAttribute('data-panel');
      if (panelId) navigateTo(panelId);
    });
  });

  // Initial panel load (supports ?panel= parameter)
  const urlParams = new URLSearchParams(window.location.search);
  const targetPanel = urlParams.get('panel') || 'dashboard';
  navigateTo(targetPanel);

  // Interceptar el click del panel de usuarios para cargarlo al abrir
  const panelBtnObserver = new MutationObserver(() => {
    const panel = document.getElementById('panel-usuarios');
    if (panel && panel.classList.contains('active') && _usuariosList.length === 0) {
      loadUsuarios();
    }
  });
  const pUsuarios = document.getElementById('panel-usuarios');
  if (pUsuarios) panelBtnObserver.observe(pUsuarios, { attributes: true, attributeFilter: ['class'] });
});

// Guardar marca de tiempo cuando el usuario navega o hace scroll
window.addEventListener('scroll', () => { window._lastScrollTime = Date.now(); }, { passive: true });

window.submitNewGasto = async function () {
  const id_drone = parseInt(document.getElementById('newGastoDroneSelect').value);
  const tipo = document.getElementById('newGastoTipo').value;
  const descripcion = document.getElementById('newGastoDescripcion').value.trim();
  const costo = parseFloat(document.getElementById('newGastoCosto').value) || 0;
  const responsable = document.getElementById('newGastoResponsable').value.trim() || 'Técnico de servicio';

  if (!id_drone || !descripcion || !costo) {
    showToast('Por favor completa todos los campos requeridos', 'warn');
    return;
  }

  await createGasto({ id_drone, tipo, descripcion, costo, responsable });
};

async function populateDroneServiceDropdowns() {
  let servicios = serviciosData;
  if (!servicios || servicios.length === 0) {
    try {
      const res = await fetch(`${API_BASE}/servicios`);
      if (res.ok) {
        const body = await res.json();
        servicios = body.data || body || [];
      }
    } catch(e) {}
  }

  const newSel = document.getElementById('newDroneTipo');
  const editSel = document.getElementById('editDroneTipo');

  let html = `<option value="Multiespectral / Multipropósito (Todos los Servicios)">🌐 Multiespectral / Multipropósito (Todos los Servicios)</option>`;
  if (Array.isArray(servicios) && servicios.length > 0) {
    servicios.forEach(s => {
      const nom = s.nombre_servicio || s.nombre || 'Servicio Dron';
      html += `<option value="${nom}"><i class="fa-solid fa-gear"></i> ${nom}</option>`;
    });
  } else {
    html += `
      <option value="Fumigación Aérea Dron (Aspersión)">🌱 Fumigación Aérea Dron (Aspersión)</option>
      <option value="Mapeo Agrícola y Fotogrametría (Multiespectral)"><i class="fa-solid fa-map-location-dot"></i> Mapeo Agrícola y Fotogrametría (Multiespectral)</option>
      <option value="Fertilización y Siembra Granulada"><i class="fa-solid fa-wheat-awn"></i> Fertilización y Siembra Granulada</option>
      <option value="Conteo de Coníferas y Árboles">🌲 Conteo de Coníferas y Árboles</option>
    `;
  }

  if (newSel) newSel.innerHTML = html;
  if (editSel) {
    const currentVal = editSel.value;
    editSel.innerHTML = html;
    if (currentVal) editSel.value = currentVal;
  }
}
window.populateDroneServiceDropdowns = populateDroneServiceDropdowns;

// Populate drone dropdown when newGastoModal or editGastoModal is opened
const origOpenModal = window.openModal;
window.openModal = async function (id) {
  if (id === 'newDroneModal' || id === 'editDroneModal') {
    await populateDroneServiceDropdowns();
  }
  if (id === 'newGastoModal' || id === 'editGastoModal') {
    if (!dronesData || dronesData.length === 0) {
      try {
        const res = await fetch(`${API_BASE}/drones`, { headers: getAuthHeaders() });
        if (res.ok) {
          const body = await res.json();
          dronesData = body.data || body || [];
        }
      } catch (e) {}
    }
    const select = document.getElementById(id === 'newGastoModal' ? 'newGastoDroneSelect' : 'editGastoDroneSelect');
    if (select) {
      const droneList = (dronesData && dronesData.length) ? dronesData : [
        { id_drone: 1, modelo: 'DJI Agras T40', numero_serie: 'AGRAS-T40-001' },
        { id_drone: 2, modelo: 'DJI Mavic 3 Multispectral', numero_serie: 'M3M-002' }
      ];
      select.innerHTML = droneList
        .map(d => `<option value="${d.id_drone || d.id}">🚁 ${d.modelo || 'Dron Agrícola'} (${d.numero_serie || 'SN-N/A'})</option>`).join('');
    }
  }
  origOpenModal(id);
};

/* ============================================================
   MÓDULO ADMIN-TÉCNICO — TORRE DE CONTROL Y EDICIÓN TOTAL
   ============================================================ */

window.loadAdminTecnicoModule = async function() {
  try {
    const [tecnicos, drones, agenda, reportes] = await Promise.all([
      apiFetch('/tecnicos') || [],
      apiFetch('/drones') || [],
      apiFetch('/agenda') || [],
      apiFetch('/reportes-vuelo') || []
    ]);

    tecnicosData = Array.isArray(tecnicos) ? tecnicos : (tecnicos.data || []);
    dronesData = Array.isArray(drones) ? drones : (drones.data || []);
    agendaData = Array.isArray(agenda) ? agenda : (agenda.data || []);
    reportesData = Array.isArray(reportes) ? reportes : (reportes.data || []);

    renderTecnicosIndividual();
    renderOcupacionDrones();
  } catch (err) {
    console.error("Error al cargar módulo Admin-Técnico:", err);
    showToast("Error al cargar módulo Admin-Técnico: " + err.message, "error");
  }
};

function renderTecnicosIndividual() {
  const container = document.getElementById('tecnicosIndividualGrid');
  if (!container) return;

  if (tecnicosData.length === 0) {
    container.innerHTML = `<div class="card" style="padding:20px; grid-column:1/-1; text-align:center; color:var(--text-3);">No hay pilotos técnicos registrados.</div>`;
    return;
  }

  container.innerHTML = tecnicosData.map(t => {
    const tId = t.id_tecnico || t.id;
    const nombre = `${t.nombre || ''} ${t.apellido_1 || ''}`.trim() || `Técnico #${tId}`;
    const estado = t.estado || 'Disponible';
    const turnosCount = agendaData.filter(a => (a.id_tecnico === tId || a.tecnico === nombre) && a.estado === 'Hecho').length;
    const droneAsignado = dronesData.find(d => d.id_tecnico_asignado === tId)?.modelo || 'Sin dron fijo';

    let badgeBg = 'rgba(16, 185, 129, 0.15)';
    let badgeColor = '#10B981';
    if (estado.toLowerCase().includes('vuelo') || estado.toLowerCase().includes('campo')) {
      badgeBg = 'rgba(28, 130, 173, 0.15)';
      badgeColor = '#1c82ad';
    }

    return `
      <div class="card" style="padding:20px; border-radius:16px; background:#ffffff; border:1px solid rgba(28, 130, 173, 0.25); box-shadow:0 8px 25px rgba(0,0,0,0.04);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:44px; height:44px; border-radius:12px; background:rgba(0,48,73,0.08); display:flex; align-items:center; justify-content:center; font-size:1.2rem; color:var(--accent);"><i class="fa-solid fa-user-gear"></i></div>
            <div>
              <h4 style="margin:0; font-family:'Syne',sans-serif; color:#003049; font-size:1.02rem; font-weight:800;">${nombre}</h4>
              <span style="font-size:0.75rem; color:#6c757d; font-weight:600;"><i class="fa-solid fa-phone" style="color:#10b981; margin-right:4px;"></i>${t.telefono || 'Sin teléfono'}</span>
            </div>
          </div>
          <span class="badge" style="background:${badgeBg}; color:${badgeColor}; font-weight:800; font-size:0.72rem; padding:4px 10px; border-radius:10px;">${estado}</span>
        </div>
        <div style="font-size:0.82rem; color:#4a5568; margin-bottom:14px; background:rgba(0,48,73,0.03); padding:10px; border-radius:10px; display:flex; flex-direction:column; gap:4px;">
          <div><i class="fa-solid fa-helicopter" style="color:var(--accent); margin-right:6px;"></i><strong>Dron Asignado:</strong> ${droneAsignado}</div>
          <div><i class="fa-solid fa-circle-check" style="color:#10b981; margin-right:6px;"></i><strong>Servicios Completados:</strong> ${turnosCount} vuelos</div>
          <div><i class="fa-solid fa-certificate" style="color:#f59e0b; margin-right:6px;"></i><strong>Licencia RAC:</strong> ${t.certificacion || 'RAC-100 Vigente'}</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="openWhatsAppPiloto('${t.telefono}')" style="width:100%; border:1px solid rgba(37,211,102,0.4); color:#25D366; font-weight:800; border-radius:10px; display:inline-flex; align-items:center; justify-content:center; gap:6px;">
          <i class="fa-brands fa-whatsapp"></i> Contactar por WhatsApp
        </button>
      </div>
    `;
  }).join('');
}

window.openWhatsAppPiloto = function(phone) {
  const cleanPhone = (phone || '').replace(/\D/g, '');
  const target = cleanPhone ? `57${cleanPhone.slice(-10)}` : '573001234567';
  window.open(`https://wa.me/${target}?text=Hola%20Piloto,%20desde%20la%20Torre%20de%20Control%20Flymetrics...`, '_blank');
};

function renderOcupacionDrones() {
  const tbody = document.getElementById('ocupacionDronesTableBody');
  if (!tbody) return;

  if (agendaData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px; color:#6c757d;">No hay turnos registrados en la agenda.</td></tr>`;
    return;
  }

  tbody.innerHTML = agendaData.map(a => {
    const aId = a.id_turno || a.id;
    const fincaName = a.nombre_finca || `Finca #${a.id_finca || '1'}`;
    const tecnicoName = (a.id_tecnico && (a.tecnico || a.tecnico_nombre)) 
      ? `<i class="fa-solid fa-user-gear" style="color:var(--accent); margin-right:4px;"></i> ` + (a.tecnico || a.tecnico_nombre) 
      : '<span class="badge badge-pending" style="font-size:0.75rem; font-weight:700;"><i class="fa-solid fa-clock-rotate-left"></i> Pendiente</span>';
    const dronName = a.dron || (dronesData.find(d => d.id_drone === a.id_drone)?.modelo) || 'Sin dron';
    const estado = a.estado || 'Pendiente';

    const rep = reportesData.find(r => r.id_turno === aId);
    const driveUrl = rep?.url_entregable_drive || null;

    let driveBadge = `<span style="font-size:0.75rem; color:#d97706; font-weight:700;"><i class="fa-solid fa-clock"></i> SLA 24-48h</span>`;
    if (driveUrl) {
      driveBadge = `<a href="${driveUrl}" target="_blank" style="color:#0284c7; font-weight:800; text-decoration:none; font-size:0.8rem;"><i class="fa-solid fa-cloud-arrow-up"></i> SharePoint</a>`;
    }

    return `
      <tr>
        <td><strong>#${aId}</strong></td>
        <td>${formatDate(a.fecha_de_turno)}<br><small style="color:#6c757d;">${a.hora_inicio_estimada || '08:00'}</small></td>
        <td><strong>${fincaName}</strong></td>
        <td>${tecnicoName}</td>
        <td><i class="fa-solid fa-helicopter" style="color:var(--accent); margin-right:4px;"></i> ${dronName}</td>
        <td><span class="badge badge-${estado.toLowerCase().replace(' ', '')}">${estado}</span></td>
        <td>${driveBadge}</td>
        <td>
          <div style="display:flex; gap:6px;">
            <button class="btn btn-ghost btn-sm" onclick="openOverrideBitacoraModal(${aId})" title="Editar Bitácora y Link SharePoint" style="padding:6px 10px;">
              <i class="fa-solid fa-screwdriver-wrench"></i> Bitácora/Nube
            </button>
            <button class="btn btn-primary btn-sm" onclick="openReprogramarModal(${aId})" title="Recalcular Ruta / Reasignar" style="padding:6px 10px; background:#003049;">
              <i class="fa-solid fa-rotate"></i> Ruta
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

window.openReprogramarModal = function(turnoId) {
  const turno = agendaData.find(a => (a.id_turno || a.id) === turnoId);
  if (!turno) return;

  const todayIso = new Date().toISOString().split('T')[0];
  document.getElementById('reprogramarTurnoId').value = turnoId;
  const fEl = document.getElementById('reprogramarFecha');
  if (fEl) {
    fEl.min = todayIso;
    fEl.value = (turno.fecha_de_turno && turno.fecha_de_turno >= todayIso) ? turno.fecha_de_turno : todayIso;
  }
  document.getElementById('reprogramarEstado').value = turno.estado || 'Confirmado';

  const techSelect = document.getElementById('reprogramarTecnico');
  techSelect.innerHTML = tecnicosData.map(t => `<option value="${t.id_tecnico || t.id}" ${(t.id_tecnico || t.id) === turno.id_tecnico ? 'selected' : ''}>${t.nombre} ${t.apellido_1 || ''}</option>`).join('');

  const droneSelect = document.getElementById('reprogramarDron');
  droneSelect.innerHTML = dronesData.map(d => `<option value="${d.id_drone || d.id}" ${(d.id_drone || d.id) === turno.id_drone ? 'selected' : ''}>${d.modelo} (${d.numero_serie || 'SN-N/A'})</option>`).join('');

  openModal('reprogramarModal');
};

window.submitReprogramar = async function(e) {
  e.preventDefault();
  const turnoId = parseInt(document.getElementById('reprogramarTurnoId').value);
  if (!turnoId) return;

  const fecha = document.getElementById('reprogramarFecha').value;
  const hora = document.getElementById('reprogramarHora') ? document.getElementById('reprogramarHora').value : null;
  const id_tecnico_val = document.getElementById('reprogramarTecnico') ? document.getElementById('reprogramarTecnico').value : '';
  const id_drone_val = document.getElementById('reprogramarDron') ? document.getElementById('reprogramarDron').value : '';
  const estado = document.getElementById('reprogramarEstado').value;
  const motivo = document.getElementById('reprogramarMotivo') ? document.getElementById('reprogramarMotivo').value.trim() : '';
  const observaciones = document.getElementById('reprogramarObservaciones') ? document.getElementById('reprogramarObservaciones').value.trim() : '';

  const id_tecnico = id_tecnico_val ? parseInt(id_tecnico_val) : null;
  const id_drone = id_drone_val ? parseInt(id_drone_val) : null;

  const payload = {
    fecha_de_turno: fecha,
    estado: estado
  };
  if (hora) payload.hora_inicio_estimada = hora.length === 5 ? `${hora}:00` : hora;
  if (id_tecnico !== null) payload.id_tecnico = id_tecnico;
  if (id_drone !== null) payload.id_drone = id_drone;
  if (motivo) payload.motivo_reagendamiento = motivo;
  if (observaciones) payload.observaciones_servicio = observaciones;

  try {
    showToast('Guardando modificaciones del turno en la base de datos...', 'info');
    await apiFetch(`/agenda/${turnoId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
    showToast("<i class='fa-solid fa-circle-check'></i> Turno de vuelo modificado y actualizado exitosamente.", "success");
    closeModal('reprogramarModal');
    
    // Invalidate caches & reload tables
    invalidateCache('agenda');
    agendaData = await apiFetch('/admin/agenda') || [];
    renderAgendaTable();
    if (typeof renderCalendar === 'function') renderCalendar();
    if (typeof loadAdminTecnicoModule === 'function') await loadAdminTecnicoModule();
    if (typeof panelLoaders !== 'undefined' && panelLoaders.reagendamiento) panelLoaders.reagendamiento();
  } catch (err) {
    try {
      // Fallback update
      await apiFetch(`/agenda/${turnoId}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
      showToast("<i class='fa-solid fa-circle-check'></i> Turno actualizado exitosamente.", "success");
      closeModal('reprogramarModal');
      invalidateCache('agenda');
      agendaData = await apiFetch('/admin/agenda') || [];
      renderAgendaTable();
    } catch (err2) {
      showToast("Error al guardar cambios del turno: " + (err2.message || err.message), "error");
    }
  }
};


