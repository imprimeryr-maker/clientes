function getToken() {
  return localStorage.getItem('token');
}

const API = {
  async request(method, path, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    const token = getToken();
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`/api${path}`, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      if (res.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.hash = '#/login';
      }
      throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
  },

  get(path) { return this.request('GET', path); },
  post(path, body) { return this.request('POST', path, body); },
  put(path, body) { return this.request('PUT', path, body); },
  del(path) { return this.request('DELETE', path); },

  // Auth
  login(data) { return this.post('/auth/login', data); },
  register(data) { return this.post('/auth/register', data); },
  me() { return this.get('/auth/me'); },
  logout() { return this.post('/auth/logout'); },

  // Clientes
  listarClientes() { return this.get('/clientes'); },
  crearCliente(data) { return this.post('/clientes', data); },
  actualizarCliente(id, data) { return this.put(`/clientes/${id}`, data); },
  eliminarCliente(id) { return this.del(`/clientes/${id}`); },
};
