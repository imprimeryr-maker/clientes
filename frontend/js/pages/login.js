const Auth = {
  async renderLogin(el) {
    el.innerHTML = `
      <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;">
        <div style="width:100%;max-width:400px;">
          <div style="text-align:center;margin-bottom:32px;">
            <img src="/assets/LogotipoCapitalizarme%20vertical-14.png" alt="Logo" style="max-width:120px;margin-bottom:16px;">
            <p style="color:#6b7280;font-size:14px;margin-top:4px;">Inicia sesión para continuar</p>
          </div>
          <div class="card" style="padding:32px;">
            <div id="login-error" class="alert alert-error" style="display:none;"></div>
            <div class="form-group">
              <label>Usuario</label>
              <input type="text" id="login-username" placeholder="Ingresa tu usuario" autocomplete="username">
            </div>
            <div class="form-group">
              <label>Contraseña</label>
              <input type="password" id="login-password" placeholder="Ingresa tu contraseña" autocomplete="current-password">
            </div>
            <button class="btn btn-primary" onclick="Auth.iniciarSesion()" style="width:100%;justify-content:center;padding:12px;margin-top:8px;">
              Ingresar
            </button>
            <p style="text-align:center;margin-top:16px;font-size:13px;color:#6b7280;">
              ¿Primera vez? <span onclick="Auth.mostrarRegistro()" style="color:#D4AF37;cursor:pointer;">Crear cuenta</span>
            </p>
          </div>
        </div>
      </div>
    `;
    document.getElementById('topbar').style.display = 'none';
    document.getElementById('login-username')?.focus();
  },

  async renderRegister(el) {
    el.innerHTML = `
      <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;">
        <div style="width:100%;max-width:400px;">
          <div style="text-align:center;margin-bottom:32px;">
            <img src="/assets/LogotipoCapitalizarme%20vertical-14.png" alt="Logo" style="max-width:120px;margin-bottom:16px;">
            <p style="color:#6b7280;font-size:14px;margin-top:4px;">Crear nueva cuenta</p>
          </div>
          <div class="card" style="padding:32px;">
            <div id="register-error" class="alert alert-error" style="display:none;"></div>
            <div id="register-success" class="alert alert-success" style="display:none;"></div>
            <div class="form-group">
              <label>Usuario</label>
              <input type="text" id="reg-username" placeholder="Elige un nombre de usuario">
            </div>
            <div class="form-group">
              <label>Contraseña</label>
              <input type="password" id="reg-password" placeholder="Mínimo 4 caracteres">
            </div>
            <div class="form-group">
              <label>Confirmar contraseña</label>
              <input type="password" id="reg-confirm" placeholder="Repite la contraseña">
            </div>
            <button class="btn btn-primary" onclick="Auth.registrar()" style="width:100%;justify-content:center;padding:12px;margin-top:8px;">
              Crear cuenta
            </button>
            <p style="text-align:center;margin-top:16px;font-size:13px;color:#6b7280;">
              ¿Ya tienes cuenta? <span onclick="Auth.mostrarLogin()" style="color:#D4AF37;cursor:pointer;">Iniciar sesión</span>
            </p>
          </div>
        </div>
      </div>
    `;
    document.getElementById('topbar').style.display = 'none';
  },

  mostrarRegistro() {
    const main = document.getElementById('main-content');
    this.renderRegister(main);
  },

  mostrarLogin() {
    const main = document.getElementById('main-content');
    this.renderLogin(main);
  },

  async iniciarSesion() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');

    if (!username || !password) {
      errorEl.textContent = 'Completa todos los campos';
      errorEl.style.display = 'block';
      return;
    }

    try {
      const res = await API.login({ username, password });
      localStorage.setItem('token', res.token);
      localStorage.setItem('user', JSON.stringify(res.usuario));
      window.location.hash = '#/';
    } catch (e) {
      errorEl.textContent = e.message;
      errorEl.style.display = 'block';
    }
  },

  async registrar() {
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;
    const errorEl = document.getElementById('register-error');
    const successEl = document.getElementById('register-success');
    errorEl.style.display = 'none';
    successEl.style.display = 'none';

    if (!username || !password || !confirm) {
      errorEl.textContent = 'Completa todos los campos';
      errorEl.style.display = 'block';
      return;
    }
    if (password !== confirm) {
      errorEl.textContent = 'Las contraseñas no coinciden';
      errorEl.style.display = 'block';
      return;
    }

    try {
      await API.register({ username, password });
      successEl.textContent = 'Cuenta creada correctamente. Redirigiendo al login...';
      successEl.style.display = 'block';
      setTimeout(() => Auth.mostrarLogin(), 1500);
    } catch (e) {
      errorEl.textContent = e.message;
      errorEl.style.display = 'block';
    }
  },

  async logout() {
    try {
      await API.logout();
    } catch {}
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.hash = '#/login';
    window.location.reload();
  },
};
