window.Pages = window.Pages || {};

Pages.configuracion = {
  render(el) {
    const config = JSON.parse(localStorage.getItem('configuracion')) || {};
    const uf = config.uf_valor || '';
    const pct = config.porcentaje || 0;
    const ufFecha = config.uf_fecha || '';
    el.innerHTML = `
      <div class="page-title"><h1>⚙️ Configuración</h1><p>Ajusta los parámetros de la fórmula de crédito.</p></div>
      <div class="card">
        <h3>📐 Fórmula de Cálculo — Límite Máx. Crédito</h3>
        <div style="background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.15);border-radius:10px;padding:16px;margin:16px 0;font-size:14px;color:#d1d5db;font-family:monospace;">
          Límite = (Sueldo × 60) ÷ UF + Porcentaje adicional
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Valor actual de la UF ($)</label>
            <div style="display:flex;gap:8px;">
              <input type="number" id="cfg-uf" min="1" step="1" value="${uf}" style="flex:1;">
              <button class="btn btn-sm" id="cfg-btn-fetch" onclick="Pages.configuracion.fetchUF()" title="Obtener UF actual desde mindicador.cl">🔄</button>
            </div>
            <div id="cfg-uf-status" style="font-size:11px;color:#6b7280;margin-top:4px;">${ufFecha ? `📅 Última actualización: ${ufFecha}` : '💡 Usa el botón 🔄 para obtener el valor actual desde mindicador.cl'}</div>
          </div>
          <div class="form-group">
            <label>Porcentaje adicional (0 – 100)</label>
            <input type="number" id="cfg-porcentaje" min="0" max="100" step="0.01" value="${pct}">
          </div>
        </div>
        <div id="cfg-preview" style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.02);border-radius:8px;font-size:13px;color:#9ca3af;"></div>
        <div style="margin-top:16px;">
          <button class="btn btn-primary" onclick="Pages.configuracion.guardar()">💾 Guardar configuración</button>
        </div>
        <div id="cfg-resultado"></div>
      </div>
    `;
    this.actualizarPreview();
    document.getElementById('cfg-uf').addEventListener('input', () => this.actualizarPreview());
    document.getElementById('cfg-porcentaje').addEventListener('input', () => this.actualizarPreview());
    if (!uf) this.fetchUF();
  },

  async fetchUF() {
    const btn = document.getElementById('cfg-btn-fetch');
    const status = document.getElementById('cfg-uf-status');
    if (btn) btn.textContent = '⏳';
    if (status) status.textContent = 'Consultando mindicador.cl...';
    try {
      const res = await fetch('https://mindicador.cl/api/uf');
      if (!res.ok) throw new Error('Error al consultar la API');
      const data = await res.json();
      const valor = data.serie?.[0]?.valor;
      const fecha = data.serie?.[0]?.fecha;
      if (!valor) throw new Error('No se encontró el valor UF');
      const input = document.getElementById('cfg-uf');
      if (input) input.value = Math.round(valor);
      if (status) status.textContent = `📅 Actualizado desde mindicador.cl — ${fecha || 'hoy'}`;
      this.actualizarPreview();
    } catch (e) {
      if (status) status.textContent = `❌ Error: ${e.message}. Ingresa el valor manualmente.`;
    } finally {
      if (btn) btn.textContent = '🔄';
    }
  },

  actualizarPreview() {
    const uf = +document.getElementById('cfg-uf')?.value || 0;
    const pct = +document.getElementById('cfg-porcentaje')?.value || 0;
    const preview = document.getElementById('cfg-preview');
    if (preview) {
      if (uf > 0) {
        preview.innerHTML = `🔮 Vista previa: <strong>(Sueldo × 60) ÷ ${uf.toLocaleString()} + ${pct}</strong> = resultado en UF`;
      } else {
        preview.innerHTML = `💡 Ingresa o consulta el valor UF para ver la vista previa.`;
      }
    }
  },

  guardar() {
    const uf = +document.getElementById('cfg-uf').value;
    const pct = +document.getElementById('cfg-porcentaje').value;
    if (pct < 0 || pct > 100) {
      document.getElementById('cfg-resultado').innerHTML = '<div class="alert alert-error">El porcentaje debe estar entre 0 y 100.</div>';
      return;
    }
    if (!uf || uf <= 0) {
      document.getElementById('cfg-resultado').innerHTML = '<div class="alert alert-error">Ingresa un valor UF válido.</div>';
      return;
    }
    const status = document.getElementById('cfg-uf-status');
    const ufFecha = status?.textContent?.includes('Actualizado') ? new Date().toLocaleDateString('es-CL') : '';
    localStorage.setItem('configuracion', JSON.stringify({ uf_valor: uf, porcentaje: pct, uf_fecha: ufFecha }));
    document.getElementById('cfg-resultado').innerHTML = '<div class="alert alert-success">✅ Configuración guardada correctamente.</div>';
  },
};
