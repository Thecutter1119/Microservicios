// ms-reportes [REP] — Frontend JavaScript — ReportEngine
const API_BASE = 'http://localhost:8000';
const SESSION_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo';
let currentReporteId = null;
let plantillasCache = [];

async function apiCall(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + SESSION_TOKEN } };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_BASE + path, opts);
    const data = await res.json();
    if (data.request_id) { const el = document.getElementById('last-req-id'); if (el) el.textContent = data.request_id; const bar = document.getElementById('req-id-dashboard'); if (bar) bar.style.display = 'flex'; }
    if (!res.ok) throw { status: res.status, detail: data.detail || data.message || 'Error desconocido', data };
    return data;
  } catch(err) {
    if (err.detail) throw err;
    throw { status: 0, detail: 'Sin conexion con ' + API_BASE, data: null };
  }
}

const VIEW_TITLES = { dashboard:'Dashboard', plantillas:'Plantillas de Reporte', reportes:'Reportes Generados', programaciones:'Programaciones', integraciones:'Mapa de Integraciones', firma:'Firma del Microservicio' };
const VIEW_ACTIONS = {
  dashboard: '<button class="btn btn-primary" onclick="openModal(\'modal-solicitar\')">+ Nuevo Reporte</button>',
  plantillas: '<button class="btn btn-primary" onclick="openModal(\'modal-plantilla\')">+ Nueva Plantilla</button>',
  reportes: '<button class="btn btn-primary" onclick="openModal(\'modal-solicitar\')">+ Solicitar Reporte</button>',
  programaciones: '<button class="btn btn-primary" onclick="openModal(\'modal-programacion\')">+ Nueva Programacion</button>',
  integraciones: '', firma: ''
};

function setView(name, el) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const view = document.getElementById('view-' + name);
  if (view) view.classList.add('active');
  if (el) el.classList.add('active');
  const titleEl = document.getElementById('page-title');
  if (titleEl) titleEl.textContent = VIEW_TITLES[name] || name;
  const actEl = document.getElementById('topbar-actions');
  if (actEl) actEl.innerHTML = VIEW_ACTIONS[name] || '';
  if (name === 'dashboard') cargarDashboard();
  if (name === 'plantillas') cargarPlantillas();
  if (name === 'reportes') cargarReportes();
  if (name === 'programaciones') cargarProgramaciones();
  if (name === 'firma') cargarFirma();
}

function toast(msg, type = 'info', duration = 4000) {
  const icons = { success: 'OK', error: 'ERR', info: 'i', warning: '!' };
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = '<span>' + (icons[type]||'i') + '</span><span>' + msg + '</span>';
  const c = document.getElementById('toast-container');
  if (c) c.appendChild(el);
  setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, duration);
}

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
  if (id === 'modal-solicitar') populatePlantillaSelect('rep-plantilla-id');
  if (id === 'modal-programacion') populatePlantillaSelect('prog-plantilla-id');
}
function closeModal(id) { const el = document.getElementById(id); if (el) el.classList.remove('open'); }

function estadoBadge(estado) {
  const map = { activa:'badge-green', inactiva:'badge-muted', pausada:'badge-orange', pendiente:'badge-blue', generando:'badge-orange', completado:'badge-green', error:'badge-red' };
  return '<span class="badge ' + (map[estado]||'badge-muted') + '">' + estado + '</span>';
}
function fmtDate(iso) { if (!iso) return '-'; try { return new Date(iso).toLocaleString('es-CO', {dateStyle:'short', timeStyle:'short'}); } catch(e) { return iso; } }
function fmtBytes(b) { if (!b) return '-'; if (b < 1024) return b + ' B'; if (b < 1048576) return (b/1024).toFixed(1) + ' KB'; return (b/1048576).toFixed(2) + ' MB'; }
function fieldBox(label, value) { return '<div style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:12px"><div style="font-size:10px;font-family:\'DM Mono\',monospace;color:var(--muted);text-transform:uppercase;margin-bottom:4px">' + label + '</div><div style="font-size:13px;color:var(--text)">' + value + '</div></div>'; }

async function populatePlantillaSelect(selectId) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = '<option value="">Cargando...</option>';
  try {
    const res = await apiCall('GET', '/api/v1/plantillas?por_pagina=100');
    plantillasCache = res.data || [];
    const activas = plantillasCache.filter(p => p.estado === 'activa');
    sel.innerHTML = activas.length ? activas.map(p => '<option value="' + p.id + '">' + p.nombre + '</option>').join('') : '<option value="">No hay plantillas activas</option>';
  } catch(e) { sel.innerHTML = '<option value="">Error al cargar</option>'; }
}

async function cargarDashboard() {
  const [r1,r2,r3,r4] = await Promise.allSettled([
    apiCall('GET','/api/v1/plantillas?estado=activa&por_pagina=1'),
    apiCall('GET','/api/v1/reportes?estado=completado&por_pagina=1'),
    apiCall('GET','/api/v1/reportes?estado=generando&por_pagina=1'),
    apiCall('GET','/api/v1/programaciones?estado=activa&por_pagina=1')
  ]);
  const set = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
  if (r1.status==='fulfilled') set('stat-plantillas', r1.value.paginacion.total);
  if (r2.status==='fulfilled') set('stat-completados', r2.value.paginacion.total);
  if (r3.status==='fulfilled') set('stat-generando', r3.value.paginacion.total);
  if (r4.status==='fulfilled') set('stat-progs', r4.value.paginacion.total);
  try {
    const rec = await apiCall('GET','/api/v1/reportes?por_pagina=8');
    renderTablaRecientes(rec.data || []);
  } catch(e) {
    const el = document.getElementById('tabla-recientes');
    if (el) el.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">Error: ' + e.detail + '</div></div>';
  }
}

function renderTablaRecientes(reportes) {
  const el = document.getElementById('tabla-recientes');
  if (!el) return;
  if (!reportes.length) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">o</div><div class="empty-text">No hay reportes</div></div>'; return; }
  el.innerHTML = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Plantilla</th><th>Estado</th><th>Formato</th><th>Solicitado</th><th>Tamano</th></tr></thead><tbody>' +
    reportes.map(r => '<tr onclick="verDetalleReporte('+r.id+')" style="cursor:pointer"><td class="mono">#'+r.id+'</td><td style="color:var(--text);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+r.nombre+'</td><td class="mono">'+r.plantilla_id+'</td><td>'+estadoBadge(r.estado)+'</td><td><span class="badge badge-muted">'+r.formato_salida+'</span></td><td>'+fmtDate(r.fecha_solicitud)+'</td><td>'+fmtBytes(r.tamano_bytes)+'</td></tr>').join('') +
    '</tbody></table>';
}

async function cargarPlantillas() {
  const estadoEl = document.getElementById('filtro-estado-plantilla');
  const estado = estadoEl ? estadoEl.value : '';
  const el = document.getElementById('tabla-plantillas');
  if (!el) return;
  el.innerHTML = '<div class="loading"><div class="spinner"></div> Cargando...</div>';
  try {
    const res = await apiCall('GET', '/api/v1/plantillas?por_pagina=50' + (estado ? '&estado=' + estado : ''));
    const items = res.data || [];
    plantillasCache = items;
    if (!items.length) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">-</div><div class="empty-text">No hay plantillas</div></div>'; return; }
    el.innerHTML = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Descripcion</th><th>Fuentes</th><th>Estado</th><th>Creada</th><th>Acciones</th></tr></thead><tbody>' +
      items.map(p => '<tr><td class="mono">#'+p.id+'</td><td style="color:var(--text);font-weight:500" class="mono">'+p.nombre+'</td><td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+p.descripcion+'</td><td class="mono" style="font-size:11px">'+(p.microservicios_fuente||[]).join(', ')+'</td><td>'+estadoBadge(p.estado)+'</td><td>'+fmtDate(p.created_at)+'</td><td><div style="display:flex;gap:6px"><button class="btn btn-ghost btn-sm" onclick="togglePlantillaEstado('+p.id+',\''+p.estado+'\')">'+(p.estado==='activa'?'Desactivar':'Activar')+'</button><button class="btn btn-danger btn-sm" onclick="eliminarPlantilla('+p.id+',\''+p.nombre.replace(/'/g,"\\'")+'\')" >X</button></div></td></tr>').join('') +
      '</tbody></table>';
  } catch(e) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">' + e.detail + '</div></div>'; }
}

async function crearPlantilla() {
  const nombre = document.getElementById('pla-nombre').value.trim();
  const descripcion = document.getElementById('pla-descripcion').value.trim();
  const fuentesStr = document.getElementById('pla-fuentes').value.trim();
  const paramsStr = document.getElementById('pla-params').value.trim();
  const configStr = document.getElementById('pla-config').value.trim();
  const estado = document.getElementById('pla-estado').value;
  if (!nombre || !descripcion) { toast('Nombre y descripcion son requeridos', 'warning'); return; }
  let pr, cc;
  try { pr = JSON.parse(paramsStr || '[]'); } catch(e) { toast('Parametros: JSON invalido', 'error'); return; }
  try { cc = JSON.parse(configStr || '{}'); } catch(e) { toast('Configuracion: JSON invalido', 'error'); return; }
  const mf = fuentesStr ? fuentesStr.split(',').map(s=>s.trim()).filter(Boolean) : [];
  try {
    await apiCall('POST','/api/v1/plantillas',{nombre,descripcion,microservicios_fuente:mf,parametros_requeridos:pr,configuracion_consultas:cc,estado});
    toast('Plantilla "'+nombre+'" creada', 'success'); closeModal('modal-plantilla'); cargarPlantillas();
  } catch(e) { toast('Error: '+e.detail,'error'); }
}

async function togglePlantillaEstado(id, estadoActual) {
  try { await apiCall('PUT','/api/v1/plantillas/'+id,{estado: estadoActual==='activa'?'inactiva':'activa'}); toast('Estado actualizado','success'); cargarPlantillas(); }
  catch(e) { toast('Error: '+e.detail,'error'); }
}

async function eliminarPlantilla(id, nombre) {
  if (!confirm('Eliminar "'+nombre+'"?')) return;
  try { await apiCall('DELETE','/api/v1/plantillas/'+id); toast('Plantilla eliminada','success'); cargarPlantillas(); }
  catch(e) { toast('Error: '+e.detail,'error'); }
}

async function cargarReportes() {
  const estadoEl = document.getElementById('filtro-estado-reporte');
  const estado = estadoEl ? estadoEl.value : '';
  const el = document.getElementById('tabla-reportes');
  if (!el) return;
  el.innerHTML = '<div class="loading"><div class="spinner"></div> Cargando...</div>';
  try {
    const res = await apiCall('GET','/api/v1/reportes?por_pagina=50'+(estado?'&estado='+estado:''));
    const items = res.data || [];
    if (!items.length) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">o</div><div class="empty-text">No hay reportes</div></div>'; return; }
    el.innerHTML = '<table><thead><tr><th>ID</th><th>Nombre</th><th>Estado</th><th>Formato</th><th>Solicitado</th><th>Generado</th><th>Tamano</th><th>Acciones</th></tr></thead><tbody>' +
      items.map(r => {
        let acc = '<button class="btn btn-ghost btn-sm" onclick="verDetalleReporte('+r.id+')">Ver</button>';
        if (r.estado==='completado') { acc += '<button class="btn btn-primary btn-sm" onclick="descargarReporteDirecto('+r.id+')">Descargar</button><button class="btn btn-ghost btn-sm" onclick="invalidarCache('+r.id+')">Cache</button>'; }
        return '<tr><td class="mono">#'+r.id+'</td><td style="color:var(--text);max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+r.nombre+'</td><td>'+estadoBadge(r.estado)+'</td><td><span class="badge badge-muted">'+r.formato_salida+'</span></td><td>'+fmtDate(r.fecha_solicitud)+'</td><td>'+fmtDate(r.fecha_generacion)+'</td><td>'+fmtBytes(r.tamano_bytes)+'</td><td><div style="display:flex;gap:6px;flex-wrap:wrap">'+acc+'</div></td></tr>';
      }).join('') + '</tbody></table>';
  } catch(e) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">'+e.detail+'</div></div>'; }
}

async function solicitarReporte() {
  const nombre = document.getElementById('rep-nombre').value.trim();
  const plantilla_id = parseInt(document.getElementById('rep-plantilla-id').value);
  const formato_salida = document.getElementById('rep-formato').value;
  const paramsStr = document.getElementById('rep-params').value.trim();
  if (!nombre) { toast('El nombre es requerido','warning'); return; }
  if (!plantilla_id) { toast('Selecciona una plantilla','warning'); return; }
  let parametros;
  try { parametros = JSON.parse(paramsStr||'{}'); } catch(e) { toast('Parametros: JSON invalido','error'); return; }
  const btn = document.getElementById('btn-generar-reporte');
  btn.disabled = true; btn.textContent = 'Procesando...';
  try {
    const res = await apiCall('POST','/api/v1/reportes',{nombre,plantilla_id,parametros,formato_salida});
    const {reporte_id, desde_cache} = res.data;
    toast(desde_cache ? 'Reporte #'+reporte_id+' desde cache' : 'Reporte #'+reporte_id+' en generacion (202)', desde_cache?'success':'info');
    closeModal('modal-solicitar'); cargarReportes();
    setView('reportes', document.querySelector('[data-view="reportes"]'));
  } catch(e) { toast('Error: '+e.detail,'error'); }
  finally { btn.disabled=false; btn.textContent='Generar Reporte'; }
}

async function verDetalleReporte(id) {
  currentReporteId = id;
  openModal('modal-detalle-reporte');
  const body = document.getElementById('detalle-reporte-body');
  if (body) body.innerHTML = '<div class="loading"><div class="spinner"></div> Cargando...</div>';
  const btnDesc = document.getElementById('btn-descargar-reporte');
  if (btnDesc) btnDesc.style.display = 'none';
  try {
    const res = await apiCall('GET','/api/v1/reportes/'+id);
    const r = res.data;
    if (body) body.innerHTML = '<div style="display:flex;flex-direction:column;gap:12px"><div class="req-id-bar"><span>Request ID:</span> <strong>'+res.request_id+'</strong></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'+fieldBox('ID','#'+r.id)+fieldBox('Estado',estadoBadge(r.estado))+fieldBox('Formato','<span class="badge badge-muted">'+r.formato_salida+'</span>')+fieldBox('Plantilla','#'+r.plantilla_id)+fieldBox('Nombre',r.nombre)+fieldBox('Solicitado por','usuario #'+r.solicitado_por)+fieldBox('Solicitud',fmtDate(r.fecha_solicitud))+fieldBox('Generacion',fmtDate(r.fecha_generacion))+fieldBox('Tamano',fmtBytes(r.tamano_bytes))+fieldBox('Creado',fmtDate(r.created_at))+'</div><div><div style="font-size:11px;color:var(--muted);font-family:\'DM Mono\',monospace;margin-bottom:6px">PARAMETROS</div><pre style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:12px;font-size:12px;font-family:\'DM Mono\',monospace;overflow-x:auto;color:var(--text)">'+JSON.stringify(r.parametros,null,2)+'</pre></div></div>';
    if (r.estado==='completado' && btnDesc) btnDesc.style.display='flex';
  } catch(e) { if (body) body.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">'+e.detail+'</div></div>'; }
}

async function descargarReporte() { if (currentReporteId) await descargarReporteDirecto(currentReporteId); }

async function descargarReporteDirecto(id) {
  try {
    const response = await fetch(API_BASE+'/api/v1/reportes/'+id+'/descargar', {headers:{'Authorization':'Bearer '+SESSION_TOKEN}});
    if (!response.ok) { const err = await response.json(); toast('Error: '+(err.detail||err.message),'error'); return; }
    const disposition = response.headers.get('Content-Disposition')||'';
    const match = disposition.match(/filename="([^"]+)"/);
    const filename = match ? match[1] : 'reporte_'+id+'.csv';
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href=url; a.download=filename; a.click();
    URL.revokeObjectURL(url);
    toast('Reporte #'+id+' descargado','success');
  } catch(e) { toast('Error al descargar','error'); }
}

async function invalidarCache(id) {
  if (!confirm('Invalidar cache del reporte #'+id+'?')) return;
  try { await apiCall('POST','/api/v1/reportes/'+id+'/invalidar-cache'); toast('Cache invalidado','success'); cargarReportes(); }
  catch(e) { toast('Error: '+e.detail,'error'); }
}

function toggleDiaField() {
  const p = document.getElementById('prog-periodicidad').value;
  const diaField = document.getElementById('dia-field');
  const semanal = document.getElementById('prog-dia-semanal');
  const mensual = document.getElementById('prog-dia-mensual');
  const label = document.getElementById('dia-label');
  if (p==='diario') { diaField.style.display='none'; }
  else if (p==='semanal') { diaField.style.display=''; semanal.style.display=''; mensual.style.display='none'; label.textContent='Dia de la semana'; }
  else { diaField.style.display=''; semanal.style.display='none'; mensual.style.display=''; label.textContent='Dia del mes (1-31)'; }
}

async function cargarProgramaciones() {
  const estadoEl = document.getElementById('filtro-estado-prog');
  const estado = estadoEl ? estadoEl.value : '';
  const el = document.getElementById('tabla-programaciones');
  if (!el) return;
  el.innerHTML = '<div class="loading"><div class="spinner"></div> Cargando...</div>';
  try {
    const res = await apiCall('GET','/api/v1/programaciones?por_pagina=50'+(estado?'&estado='+estado:''));
    const items = res.data || [];
    if (!items.length) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">o</div><div class="empty-text">No hay programaciones</div></div>'; return; }
    el.innerHTML = '<table><thead><tr><th>ID</th><th>Plantilla</th><th>Periodicidad</th><th>Hora</th><th>Estado</th><th>Proxima</th><th>Ultima</th><th>Acciones</th></tr></thead><tbody>' +
      items.map(p => {
        const acc = (p.estado==='activa' ? '<button class="btn btn-ghost btn-sm" onclick="desactivarProg('+p.id+')">Pausar</button>' : '<button class="btn btn-primary btn-sm" onclick="reactivarProg('+p.id+')">Activar</button>') +
          '<button class="btn btn-ghost btn-sm" onclick="ejecutarProg('+p.id+')">Ejecutar</button>';
        return '<tr><td class="mono">#'+p.id+'</td><td class="mono" style="font-size:11px">#'+p.plantilla_id+'</td><td><span class="badge badge-blue">'+p.periodicidad+'</span></td><td class="mono">'+(p.hora_ejecucion||'-')+(p.dia_ejecucion?' ('+p.dia_ejecucion+')':'')+'</td><td>'+estadoBadge(p.estado)+'</td><td style="font-size:12px">'+fmtDate(p.proxima_ejecucion)+'</td><td style="font-size:12px">'+fmtDate(p.ultima_ejecucion)+'</td><td><div style="display:flex;gap:6px">'+acc+'</div></td></tr>';
      }).join('') + '</tbody></table>';
  } catch(e) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">'+e.detail+'</div></div>'; }
}

async function crearProgramacion() {
  const plantilla_id = parseInt(document.getElementById('prog-plantilla-id').value);
  const periodicidad = document.getElementById('prog-periodicidad').value;
  const hora = document.getElementById('prog-hora').value;
  const rolesStr = document.getElementById('prog-roles').value.trim();
  const usuariosStr = document.getElementById('prog-usuarios').value.trim();
  if (!plantilla_id) { toast('Selecciona una plantilla','warning'); return; }
  if (!hora) { toast('La hora es requerida','warning'); return; }
  let dia_ejecucion = null;
  if (periodicidad==='semanal') dia_ejecucion = document.getElementById('prog-dia-semanal').value;
  if (periodicidad==='mensual') dia_ejecucion = document.getElementById('prog-dia-mensual').value;
  const roles = rolesStr ? rolesStr.split(',').map(s=>parseInt(s.trim())).filter(Boolean) : [];
  const usuarios = usuariosStr ? usuariosStr.split(',').map(s=>parseInt(s.trim())).filter(Boolean) : [];
  try {
    const res = await apiCall('POST','/api/v1/programaciones',{plantilla_id,periodicidad,dia_ejecucion,hora_ejecucion:hora+':00',destinatarios:{roles,usuarios}});
    toast('Programacion creada - proxima: '+fmtDate(res.data&&res.data.proxima_ejecucion),'success');
    closeModal('modal-programacion'); cargarProgramaciones();
  } catch(e) { toast('Error: '+e.detail,'error'); }
}

async function desactivarProg(id) {
  try { await apiCall('POST','/api/v1/programaciones/'+id+'/desactivar'); toast('Programacion #'+id+' pausada','success'); cargarProgramaciones(); }
  catch(e) { toast('Error: '+e.detail,'error'); }
}

async function reactivarProg(id) {
  try {
    const res = await apiCall('POST','/api/v1/programaciones/'+id+'/reactivar');
    toast('Programacion #'+id+' reactivada - proxima: '+fmtDate(res.data&&res.data.proxima_ejecucion),'success');
    cargarProgramaciones();
  } catch(e) { toast('Error: '+e.detail,'error'); }
}

async function ejecutarProg(id) {
  if (!confirm('Ejecutar manualmente la programacion #'+id+'?')) return;
  try {
    const res = await apiCall('POST','/api/v1/programaciones/'+id+'/ejecutar');
    toast('Reporte #'+res.data.reporte_id+' iniciado','success');
    setView('reportes', document.querySelector('[data-view="reportes"]'));
  } catch(e) { toast('Error: '+e.detail,'error'); }
}

async function cargarFirma() {
  const loading = document.getElementById('firma-loading');
  const content = document.getElementById('firma-content');
  if (loading) loading.style.display = 'flex';
  if (content) content.style.display = 'none';
  try {
    const res = await fetch(API_BASE+'/info');
    const data = await res.json();
    renderFirma(data);
  } catch(e) {
    if (loading) loading.innerHTML = '<div class="empty-state"><div class="empty-icon">!</div><div class="empty-text">No se puede conectar a '+API_BASE+'</div></div>';
  }
}

function renderFirma(d) {
  const loading = document.getElementById('firma-loading');
  const el = document.getElementById('firma-content');
  if (loading) loading.style.display = 'none';
  if (!el) return;
  el.style.display = 'block';
  const fRow = (k,v) => '<div class="firma-row"><span class="firma-key">'+k+'</span><span class="firma-val">'+v+'</span></div>';
  const epRow = (str) => {
    const p = str.trim().split(/\s+/);
    const cls = {GET:'method-get',POST:'method-post',PUT:'method-put',DELETE:'method-delete'}[p[0]]||'method-get';
    return '<li><span class="method-badge '+cls+'">'+p[0]+'</span><span style="flex:1;color:var(--text)">'+(p[1]||'')+'</span><span style="color:var(--muted);font-size:10px">'+p.slice(2).join(' ')+'</span></li>';
  };
  const intH = Object.entries(d.integraciones||{}).map(([k,v])=>fRow(k,Array.isArray(v)?v.join(', '):v)).join('');
  const ep = d.endpoints || {};
  el.innerHTML =
    '<div class="firma-grid" style="margin-bottom:16px">' +
      '<div class="firma-block"><h3>Identidad</h3>'+fRow('Servicio',d.microservicio||'')+fRow('Codigo','['+(d.codigo||'')+']')+fRow('Version',d.version||'')+fRow('Modulo',d.modulo||'')+fRow('Stack',d.stack||'')+fRow('DB',d.base_datos||'')+fRow('Requisitos',(d.requisitos&&d.requisitos.total)||24)+'</div>' +
      '<div class="firma-block"><h3>Integraciones</h3>'+intH+'</div>' +
    '</div><div class="firma-grid">' +
      '<div class="firma-block"><h3>Plantillas y Reportes</h3><ul class="endpoint-list">'+[...(ep.plantillas||[]),...(ep.reportes||[])].map(e=>epRow(e.replace(/\s*—\s*/,' '))).join('')+'</ul></div>' +
      '<div class="firma-block"><h3>Programaciones y Sistema</h3><ul class="endpoint-list">'+[...(ep.programaciones||[]),...(ep.sistema||[])].map(e=>epRow(e.replace(/\s*—\s*/,' '))).join('')+'</ul></div>' +
    '</div>';
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.modal-overlay').forEach(o => { o.addEventListener('click', e => { if (e.target===o) closeModal(o.id); }); });
  toggleDiaField();
  cargarDashboard();
});
