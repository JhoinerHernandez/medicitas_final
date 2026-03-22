/* ================================================================
   MediCitas — scripts.js
   Sistema de Gestión de Citas Médicas
   ================================================================ */

'use strict';

/* ──────────────────────────────────────────────────────────────
   1. NAVBAR SCROLL EFFECT
────────────────────────────────────────────────────────────── */
(function initNavbar() {
  const nav = document.querySelector('.med-navbar');
  if (!nav) return;
  const handler = () => nav.classList.toggle('scrolled', window.scrollY > 20);
  window.addEventListener('scroll', handler, { passive: true });
  handler();
})();

/* ──────────────────────────────────────────────────────────────
   2. MOBILE NAV TOGGLE
────────────────────────────────────────────────────────────── */
(function initMobileNav() {
  const toggler = document.getElementById('navToggler');
  const menu    = document.getElementById('navMenu');
  if (!toggler || !menu) return;
  toggler.addEventListener('click', () => {
    menu.classList.toggle('open');
    const icon = toggler.querySelector('i');
    if (icon) icon.className = menu.classList.contains('open') ? 'fas fa-times' : 'fas fa-bars';
  });
  // Close on outside click
  document.addEventListener('click', e => {
    if (!nav && menu.classList.contains('open') && !toggler.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('open');
    }
  });
})();

/* ──────────────────────────────────────────────────────────────
   3. ACTIVE NAV LINK
────────────────────────────────────────────────────────────── */
(function setActiveNav() {
  const current = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-menu a, .dash-nav-item').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (href === current || (current === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
})();

/* ──────────────────────────────────────────────────────────────
   4. SCROLL REVEAL
────────────────────────────────────────────────────────────── */
(function initScrollReveal() {
  if (!window.IntersectionObserver) return;
  const els = document.querySelectorAll('[data-reveal]');
  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = parseInt(entry.target.dataset.revealDelay || 0);
        setTimeout(() => entry.target.classList.add('visible'), delay);
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
  els.forEach(el => obs.observe(el));
})();

/* ──────────────────────────────────────────────────────────────
   5. FORM VALIDATION HELPERS
────────────────────────────────────────────────────────────── */
const Validator = {
  required(val) { return val.trim().length > 0; },
  email(val)    { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val); },
  phone(val)    { return /^[\d\s\+\-\(\)]{7,15}$/.test(val.trim()); },
  cedula(val)   { return /^\d{6,12}$/.test(val.trim()); },
  minLen(val,n) { return val.trim().length >= n; },

  showError(input, msg) {
    input.classList.remove('is-valid');
    input.classList.add('is-invalid');
    let err = input.closest('.form-group-med')?.querySelector('.form-error-med');
    if (!err) {
      err = document.createElement('div');
      err.className = 'form-error-med';
      err.innerHTML = `<i class="fas fa-exclamation-circle"></i> <span></span>`;
      input.closest('.form-group-med, .input-icon-wrap')?.after(err) ||
      input.parentElement?.after(err);
    }
    const span = err.querySelector('span');
    if (span) span.textContent = msg;
    err.style.display = 'flex';
  },

  showSuccess(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    const err = input.closest('.form-group-med')?.querySelector('.form-error-med');
    if (err) err.style.display = 'none';
  },

  clearAll(form) {
    form.querySelectorAll('.form-control-med').forEach(i => {
      i.classList.remove('is-valid','is-invalid');
    });
    form.querySelectorAll('.form-error-med').forEach(e => e.style.display='none');
  }
};

/* ──────────────────────────────────────────────────────────────
   6. FORM: REGISTRO PACIENTE
────────────────────────────────────────────────────────────── */
(function initRegistroForm() {
  const form = document.getElementById('formRegistroPaciente');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    let valid = true;
    Validator.clearAll(form);

    const fields = [
      { id:'cedula',    fn: v => Validator.cedula(v),      msg: 'Ingresa un número de identificación válido (6-12 dígitos).' },
      { id:'nombre',    fn: v => Validator.minLen(v,2),    msg: 'El nombre debe tener al menos 2 caracteres.' },
      { id:'apellido',  fn: v => Validator.minLen(v,2),    msg: 'El apellido debe tener al menos 2 caracteres.' },
      { id:'telefono',  fn: v => Validator.phone(v),       msg: 'Ingresa un número de teléfono válido.' },
      { id:'correo',    fn: v => Validator.email(v),       msg: 'Ingresa un correo electrónico válido.' },
      { id:'eps',       fn: v => Validator.required(v),    msg: 'Selecciona una EPS.' },
    ];

    fields.forEach(f => {
      const el = document.getElementById(f.id);
      if (!el) return;
      if (!f.fn(el.value)) {
        Validator.showError(el, f.msg);
        valid = false;
      } else {
        Validator.showSuccess(el);
      }
    });

    if (valid) {
      showToast('Paciente registrado exitosamente.', 'success');
      setTimeout(() => form.reset(), 400);
      Validator.clearAll(form);
    } else {
      showToast('Por favor corrige los errores antes de continuar.', 'error');
    }
  });

  // Real-time validation
  form.querySelectorAll('.form-control-med').forEach(input => {
    input.addEventListener('blur', () => {
      if (input.value.trim()) Validator.showSuccess(input);
    });
  });
})();

/* ──────────────────────────────────────────────────────────────
   7. FORM: RESERVAR CITA
────────────────────────────────────────────────────────────── */
(function initReservarForm() {
  const form = document.getElementById('formReservarCita');
  if (!form) return;

  // Set min date to today
  const fechaInput = document.getElementById('fechaCita');
  if (fechaInput) {
    const today = new Date().toISOString().split('T')[0];
    fechaInput.min = today;
  }

  // Dynamic address based on EPS
  const epsMap = {
    'sura':      'Cra. 43A #5A-113, Medellín · Tel: (604) 369-9000',
    'sanitas':   'Av. 19 #103-73, Bogotá · Tel: (601) 648-1800',
    'nueva-eps': 'Cll. 26 #51-53, Bogotá · Tel: 018000-9100-33',
    'compensar': 'Av. Ciudad de Cali #51-66, Bogotá · Tel: (601) 395-9000',
    'coosalud':  'Cll. 30 #17-36, Cartagena · Tel: (605) 660-4444',
    'coomeva':   'Cra. 100 #11A-35, Cali · Tel: (602) 661-5961',
  };
  const epsSelect = document.getElementById('epsReserva');
  const dirInput  = document.getElementById('direccionEps');
  if (epsSelect && dirInput) {
    epsSelect.addEventListener('change', () => {
      dirInput.value = epsMap[epsSelect.value] || '';
      if (dirInput.value) Validator.showSuccess(dirInput);
    });
  }

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    let valid = true;
    Validator.clearAll(form);

    const fields = [
      { id:'docPaciente', fn: v => Validator.cedula(v),   msg: 'Ingresa un documento válido.' },
      { id:'medico',      fn: v => Validator.required(v), msg: 'Selecciona un médico.' },
      { id:'tipoCita',    fn: v => Validator.required(v), msg: 'Selecciona el tipo de cita.' },
      { id:'fechaCita',   fn: v => Validator.required(v), msg: 'Selecciona la fecha de la cita.' },
      { id:'horaCita',    fn: v => Validator.required(v), msg: 'Selecciona la hora de la cita.' },
      { id:'epsReserva',  fn: v => Validator.required(v), msg: 'Selecciona la EPS.' },
    ];

    fields.forEach(f => {
      const el = document.getElementById(f.id);
      if (!el) return;
      if (!f.fn(el.value)) {
        Validator.showError(el, f.msg);
        valid = false;
      } else {
        Validator.showSuccess(el);
      }
    });

    if (valid) {
      showToast('¡Cita reservada exitosamente!', 'success');
      setTimeout(() => { form.reset(); if(dirInput) dirInput.value = ''; }, 400);
      Validator.clearAll(form);
    } else {
      showToast('Revisa los campos requeridos.', 'error');
    }
  });
})();

/* ──────────────────────────────────────────────────────────────
   8. FORM: CONSULTAR CITA
────────────────────────────────────────────────────────────── */
(function initConsultarForm() {
  const form    = document.getElementById('formConsultarCita');
  const results = document.getElementById('resultadoCita');
  if (!form) return;

  // Mock data
  const mockData = {
    '1234567890': {
      nombre: 'Carlos Andrés Pérez', id: '1234567890',
      medico: 'Dr. Juan Rodríguez', especialidad: 'Medicina General',
      tipo: 'General', fecha: '2025-08-15', hora: '10:30 AM',
      eps: 'EPS Sura', direccion: 'Cra. 43A #5A-113, Medellín',
      estado: 'Confirmada'
    },
    '9876543210': {
      nombre: 'María Fernanda López', id: '9876543210',
      medico: 'Dra. Ana Gómez', especialidad: 'Odontología',
      tipo: 'Odontología', fecha: '2025-08-20', hora: '02:15 PM',
      eps: 'Compensar', direccion: 'Av. Ciudad de Cali #51-66, Bogotá',
      estado: 'Pendiente'
    },
    '5551112233': {
      nombre: 'Luis Fernando Torres', id: '5551112233',
      medico: 'Dr. Mario Castro', especialidad: 'Cardiología',
      tipo: 'Especialista', fecha: '2025-09-05', hora: '09:00 AM',
      eps: 'Sanitas', direccion: 'Av. 19 #103-73, Bogotá',
      estado: 'Confirmada'
    },
  };

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const docInput = document.getElementById('docConsulta');
    if (!docInput) return;

    if (!Validator.cedula(docInput.value)) {
      Validator.showError(docInput, 'Ingresa un número de identificación válido.');
      if (results) results.style.display = 'none';
      return;
    }
    Validator.showSuccess(docInput);

    const cita = mockData[docInput.value.trim()];
    if (!cita) {
      if (results) results.style.display = 'none';
      showToast('No se encontró ninguna cita para ese documento.', 'error');
      return;
    }

    // Populate result card
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('res-nombre', cita.nombre);
    set('res-id',     'CC: ' + cita.id);
    set('res-medico', cita.medico);
    set('res-esp',    cita.especialidad);
    set('res-tipo',   cita.tipo);
    set('res-fecha',  formatDate(cita.fecha));
    set('res-hora',   cita.hora);
    set('res-eps',    cita.eps);
    set('res-dir',    cita.direccion);

    // Badge estado
    const estadoBadge = document.getElementById('res-estado');
    if (estadoBadge) {
      estadoBadge.textContent = cita.estado;
      estadoBadge.className   = 'badge-med ' + (cita.estado === 'Confirmada' ? 'badge-success' : 'badge-amber');
    }

    if (results) {
      results.style.display = 'block';
      results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
})();

/* ──────────────────────────────────────────────────────────────
   9. FORM: ACTUALIZAR CITA
────────────────────────────────────────────────────────────── */
(function initActualizarForm() {
  const form = document.getElementById('formActualizarCita');
  if (!form) return;

  // Min date = today
  const fechaInput = document.getElementById('nuevaFecha');
  if (fechaInput) {
    fechaInput.min = new Date().toISOString().split('T')[0];
  }

  // Search patient first
  const searchBtn = document.getElementById('btnBuscarPaciente');
  const docInput  = document.getElementById('docActualizar');
  const fieldsWrap= document.getElementById('updateFields');

  if (searchBtn && docInput && fieldsWrap) {
    const mock = {
      '1234567890': { medico:'Dr. Juan Rodríguez', tipo:'General',  fecha:'2025-08-15', hora:'10:30' },
      '9876543210': { medico:'Dra. Ana Gómez',     tipo:'Odontología', fecha:'2025-08-20', hora:'14:15' },
      '5551112233': { medico:'Dr. Mario Castro',   tipo:'Especialista',fecha:'2025-09-05', hora:'09:00' },
    };
    searchBtn.addEventListener('click', () => {
      if (!Validator.cedula(docInput.value)) {
        Validator.showError(docInput, 'Ingresa un documento válido.');
        fieldsWrap.style.display = 'none';
        return;
      }
      Validator.showSuccess(docInput);
      const data = mock[docInput.value.trim()];
      if (!data) {
        showToast('No se encontró ninguna cita para ese documento.', 'error');
        fieldsWrap.style.display = 'none';
        return;
      }
      // Pre-fill
      const setVal = (id, val) => { const el=document.getElementById(id); if(el) el.value=val; };
      setVal('nuevoMedico', data.medico);
      setVal('nuevoTipo',   data.tipo);
      setVal('nuevaFecha',  data.fecha);
      setVal('nuevaHora',   data.hora);
      fieldsWrap.style.display = 'block';
      fieldsWrap.scrollIntoView({ behavior:'smooth', block:'nearest' });
      showToast('Datos de la cita encontrados.', 'success');
    });
  }

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    let valid = true;
    Validator.clearAll(form);

    const fields = [
      { id:'nuevoMedico', fn: v => Validator.required(v), msg: 'Selecciona el médico.' },
      { id:'nuevoTipo',   fn: v => Validator.required(v), msg: 'Selecciona el tipo de cita.' },
      { id:'nuevaFecha',  fn: v => Validator.required(v), msg: 'Selecciona la nueva fecha.' },
      { id:'nuevaHora',   fn: v => Validator.required(v), msg: 'Selecciona la nueva hora.' },
    ];

    fields.forEach(f => {
      const el = document.getElementById(f.id);
      if (!el || el.closest('[style*="display: none"]')) return;
      if (!f.fn(el.value)) { Validator.showError(el, f.msg); valid = false; }
      else Validator.showSuccess(el);
    });

    if (valid) {
      showToast('¡Cita actualizada exitosamente!', 'success');
      setTimeout(() => {
        form.reset();
        Validator.clearAll(form);
        if (fieldsWrap) fieldsWrap.style.display = 'none';
      }, 400);
    } else {
      showToast('Revisa los campos requeridos.', 'error');
    }
  });
})();

/* ──────────────────────────────────────────────────────────────
   10. TOAST NOTIFICATIONS
────────────────────────────────────────────────────────────── */
function showToast(message, type = 'success') {
  const icons = { success:'fas fa-check-circle', error:'fas fa-times-circle', info:'fas fa-info-circle', warning:'fas fa-exclamation-triangle' };

  let container = document.querySelector('.toast-container-med');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container-med';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-med toast-${type}`;
  toast.innerHTML = `<i class="${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('out');
    setTimeout(() => toast.remove(), 320);
  }, 3800);
}

/* ──────────────────────────────────────────────────────────────
   11. DATE FORMATTER
────────────────────────────────────────────────────────────── */
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('es-CO', { weekday:'long', year:'numeric', month:'long', day:'numeric' });
}

/* ──────────────────────────────────────────────────────────────
   12. CURRENT DATE IN DASHBOARD
────────────────────────────────────────────────────────────── */
(function setCurrentDate() {
  const el = document.getElementById('currentDate');
  if (!el) return;
  el.textContent = new Date().toLocaleDateString('es-CO', {
    weekday:'long', year:'numeric', month:'long', day:'numeric'
  });
})();

/* ──────────────────────────────────────────────────────────────
   13. ANIMATED COUNTERS (dashboard)
────────────────────────────────────────────────────────────── */
(function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el     = entry.target;
      const target = parseInt(el.dataset.count);
      let   current = 0;
      const step    = Math.max(1, Math.floor(target / 60));
      const timer   = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString('es-CO');
        if (current >= target) clearInterval(timer);
      }, 20);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach(c => observer.observe(c));
})();

/* ──────────────────────────────────────────────────────────────
   14. FORM CHARACTER COUNTER
────────────────────────────────────────────────────────────── */
document.querySelectorAll('[data-maxlen]').forEach(input => {
  const max     = parseInt(input.dataset.maxlen);
  const counter = document.getElementById(input.id + '-count');
  if (!counter) return;
  counter.textContent = max;
  input.addEventListener('input', () => {
    const rem = max - input.value.length;
    counter.textContent = rem;
    counter.style.color = rem < 10 ? 'var(--danger)' : 'var(--gray-400)';
  });
});

/* ──────────────────────────────────────────────────────────────
   15. PRINT CITA
────────────────────────────────────────────────────────────── */
function printCita() {
  const result = document.getElementById('resultadoCita');
  if (!result) return;
  const w = window.open('', '_blank');
  w.document.write(`
    <html><head><title>Cita Médica</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
    <style>
      body{font-family:sans-serif;padding:2rem;color:#1f2937;}
      h2{color:#1a4b8c;font-size:1.4rem;}
      .field{margin:.5rem 0;}
      .lbl{font-size:.75rem;text-transform:uppercase;color:#6b7280;font-weight:700;}
      .val{font-size:.95rem;font-weight:600;}
    </style>
    </head><body>
    <h2>MediCitas — Comprobante de Cita</h2>
    <hr/>
    ${result.innerHTML}
    <hr/>
    <p style="font-size:.75rem;color:#9ca3af;">Impreso el ${new Date().toLocaleString('es-CO')}</p>
    </body></html>
  `);
  w.document.close();
  w.print();
}

/* ──────────────────────────────────────────────────────────────
   16. CONFIRM DIALOGS
────────────────────────────────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('[data-confirm]');
  if (!btn) return;
  if (!confirm(btn.dataset.confirm || '¿Confirmas esta acción?')) {
    e.preventDefault();
    e.stopPropagation();
  }
});
