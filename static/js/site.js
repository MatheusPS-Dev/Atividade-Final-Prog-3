// Menu responsivo
const botaoMenu = document.querySelector('.botao--menu');
const menu = document.getElementById('menu-lateral');

if (botaoMenu && menu) {
  botaoMenu.addEventListener('click', () => {
    const aberto = menu.classList.toggle('aberta');
    botaoMenu.setAttribute('aria-expanded', String(aberto));
  });
  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape' && menu.classList.contains('aberta')) {
      menu.classList.remove('aberta');
      botaoMenu.setAttribute('aria-expanded', 'false');
      botaoMenu.focus();
    }
  });
}

// Submissão automática em campos de filtro/ordenação
document.querySelectorAll('[data-autoenvio]').forEach((campo) => {
  campo.addEventListener('change', () => campo.form.submit());
});
