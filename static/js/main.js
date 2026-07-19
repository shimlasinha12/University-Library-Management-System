// ── Sidebar toggle (mobile) ──────────────────────────────
const hamburger = document.getElementById('hamburgerBtn');
const sidebar   = document.getElementById('sidebar');
const overlay   = document.getElementById('sidebarOverlay');

function openSidebar() {
  sidebar?.classList.add('open');
  overlay?.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  sidebar?.classList.remove('open');
  overlay?.classList.remove('open');
  document.body.style.overflow = '';
}

hamburger?.addEventListener('click', openSidebar);
overlay?.addEventListener('click', closeSidebar);

// ── Auto-dismiss alerts ──────────────────────────────────
document.querySelectorAll('.alert-close').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.alert')?.remove();
  });
});

setTimeout(() => {
  document.querySelectorAll('.alert').forEach(el => {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  });
}, 5000);

// ── Delete confirmation modal ────────────────────────────
const deleteModal   = document.getElementById('deleteModal');
let   pendingForm   = null;

document.querySelectorAll('[data-delete-form]').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    pendingForm = document.getElementById(btn.dataset.deleteForm);
    const label = btn.dataset.deleteLabel || 'this record';
    const msgEl = document.getElementById('deleteModalMsg');
    if (msgEl) msgEl.textContent = `Are you sure you want to delete ${label}? This action cannot be undone.`;
    deleteModal?.classList.add('open');
  });
});

document.getElementById('deleteConfirmBtn')?.addEventListener('click', () => {
  pendingForm?.submit();
});

document.getElementById('deleteCancelBtn')?.addEventListener('click', () => {
  deleteModal?.classList.remove('open');
  pendingForm = null;
});

deleteModal?.addEventListener('click', e => {
  if (e.target === deleteModal) {
    deleteModal.classList.remove('open');
    pendingForm = null;
  }
});

// ── Active sidebar link ──────────────────────────────────
const currentPath = window.location.pathname;
document.querySelectorAll('.sidebar-link').forEach(link => {
  const href = link.getAttribute('href');
  if (href && href !== '/' && currentPath.startsWith(href)) {
    link.classList.add('active');
  }
});

// ── Password strength toggle ─────────────────────────────
document.querySelectorAll('[data-toggle-password]').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = document.getElementById(btn.dataset.togglePassword);
    if (!target) return;
    if (target.type === 'password') {
      target.type = 'text';
      btn.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
      target.type = 'password';
      btn.innerHTML = '<i class="fas fa-eye"></i>';
    }
  });
});
