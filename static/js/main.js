// Kamau Nails — front-end interactions
document.addEventListener('DOMContentLoaded', function () {

  // Mobile nav toggle
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('mainNav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });
  }

  // Dark / light mode toggle (persists for the session only — no localStorage per policy,
  // but you can wire this to localStorage yourself once you deploy: see README)
  var themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var root = document.documentElement;
      var current = root.getAttribute('data-theme');
      root.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
    });
  }

  // FAQ accordion
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(function (el) { el.classList.remove('open'); });
      if (!wasOpen) item.classList.add('open');
    });
  });

  // Gallery lightbox
  var lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = '<img alt="Enlarged gallery photo">';
  lightbox.style.cssText = 'position:fixed;inset:0;background:rgba(20,15,20,.92);display:none;align-items:center;justify-content:center;z-index:999;cursor:zoom-out;padding:30px;';
  lightbox.querySelector('img').style.cssText = 'max-width:90vw;max-height:85vh;border-radius:12px;';
  document.body.appendChild(lightbox);

  document.querySelectorAll('[data-lightbox]').forEach(function (fig) {
    fig.addEventListener('click', function () {
      lightbox.querySelector('img').src = fig.getAttribute('data-lightbox');
      lightbox.style.display = 'flex';
    });
  });
  lightbox.addEventListener('click', function () { lightbox.style.display = 'none'; });

  // Simple client-side validation feedback (real validation also happens server-side in Django forms)
  document.querySelectorAll('form[novalidate]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var invalid = form.querySelector(':invalid');
      if (invalid) {
        e.preventDefault();
        invalid.focus();
      }
    });
  });
});
