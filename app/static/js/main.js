document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-toggle-password]').forEach(function (button) {
    button.addEventListener('click', function () {
      var input = document.getElementById(button.getAttribute('data-toggle-password'));
      if (!input) return;
      var showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      button.innerHTML = showing
        ? '<i data-lucide="eye" class="w-4 h-4"></i>'
        : '<i data-lucide="eye-off" class="w-4 h-4"></i>';
      if (window.lucide) window.lucide.createIcons();
    });
  });
});
