function estaAutenticado() {
  return !!localStorage.getItem('token');
}

async function verificarSesion() {
  const token = localStorage.getItem('token');
  if (!token) return false;
  try {
    await API.me();
    return true;
  } catch {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return false;
  }
}

function mostrarTopbar() {
  const topbar = document.getElementById('topbar');
  topbar.style.display = 'flex';
  const userData = localStorage.getItem('user');
  if (userData) {
    try {
      const u = JSON.parse(userData);
      document.getElementById('username-display').textContent = `👤 ${u.username}`;
    } catch {}
  }
}

(async function init() {
  const main = document.getElementById('main-content');

  Router.register('/login', async (el) => {
    Auth.renderLogin(el);
  });

  Router.register('/register', async (el) => {
    Auth.renderRegister(el);
  });

  Router.register('/', async (el) => {
    if (!estaAutenticado()) {
      window.location.hash = '#/login';
      return;
    }
    if (!(await verificarSesion())) {
      window.location.hash = '#/login';
      return;
    }
    mostrarTopbar();
    Pages.clientes.render(el);
  });

  Router.init();
})();
