/* ─── Hamburger menu ──────────────────────────────────── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const bars = hamburger.querySelectorAll('span');
    if (navLinks.classList.contains('open')) {
      bars[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      bars[1].style.opacity   = '0';
      bars[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
    }
  });

  // Close on link click
  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      hamburger.querySelectorAll('span').forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
    });
  });
}

/* ─── Cursor glow ─────────────────────────────────────── */
const cursor = document.createElement('div');
cursor.classList.add('glow-cursor');
document.body.appendChild(cursor);

let mx = 0, my = 0;
document.addEventListener('mousemove', e => {
  mx = e.clientX; my = e.clientY;
  cursor.style.left = mx + 'px';
  cursor.style.top  = my + 'px';
});

/* ─── Active nav link ─────────────────────────────────── */
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-links a').forEach(a => {
  const href = a.getAttribute('href');
  if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
    a.classList.add('active');
  }
});

/* ─── Contact form validation ─────────────────────────── */
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', function (e) {
    let valid = true;

    // Name
    const nameEl  = document.getElementById('name');
    const nameErr = document.getElementById('name-error');
    if (!nameEl.value.trim() || nameEl.value.trim().length < 2) {
      showError(nameEl, nameErr, 'Имя должно содержать минимум 2 символа.');
      valid = false;
    } else {
      clearError(nameEl, nameErr);
    }

    // Email
    const emailEl  = document.getElementById('email');
    const emailErr = document.getElementById('email-error');
    const emailRe  = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailEl.value.trim() || !emailRe.test(emailEl.value)) {
      showError(emailEl, emailErr, 'Введите корректный email-адрес.');
      valid = false;
    } else {
      clearError(emailEl, emailErr);
    }

    // Message
    const msgEl  = document.getElementById('message');
    const msgErr = document.getElementById('message-error');
    if (!msgEl.value.trim() || msgEl.value.trim().length < 10) {
      showError(msgEl, msgErr, 'Сообщение должно содержать минимум 10 символов.');
      valid = false;
    } else {
      clearError(msgEl, msgErr);
    }

    if (!valid) e.preventDefault();
  });

  // Real-time validation
  ['name', 'email', 'message'].forEach(id => {
    const el  = document.getElementById(id);
    const err = document.getElementById(id + '-error');
    if (el) el.addEventListener('input', () => clearError(el, err));
  });
}

function showError(input, errEl, msg) {
  input.classList.add('is-invalid');
  if (errEl) { errEl.textContent = msg; errEl.style.display = 'block'; }
}

function clearError(input, errEl) {
  input.classList.remove('is-invalid');
  if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }
}

/* ─── Admin project form validation ──────────────────── */
const projectForm = document.getElementById('project-form');
if (projectForm) {
  projectForm.addEventListener('submit', function (e) {
    let valid = true;

    const titleEl  = document.getElementById('title');
    const titleErr = document.getElementById('title-error');
    if (!titleEl.value.trim() || titleEl.value.trim().length < 3) {
      showError(titleEl, titleErr, 'Название должно содержать минимум 3 символа.');
      valid = false;
    } else {
      clearError(titleEl, titleErr);
    }

    const descEl  = document.getElementById('description');
    const descErr = document.getElementById('description-error');
    if (!descEl.value.trim() || descEl.value.trim().length < 10) {
      showError(descEl, descErr, 'Описание должно содержать минимум 10 символов.');
      valid = false;
    } else {
      clearError(descEl, descErr);
    }

    if (!valid) e.preventDefault();
  });
}

/* ─── Auto-hide flash messages ────────────────────────── */
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity 0.5s ease';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4000);

/* ─── Confirm delete ─────────────────────────────────── */
document.querySelectorAll('.delete-form').forEach(f => {
  f.addEventListener('submit', e => {
    if (!confirm('Вы уверены? Это действие нельзя отменить.')) e.preventDefault();
  });
});