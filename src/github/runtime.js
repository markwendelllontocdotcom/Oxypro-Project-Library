/* Oxypro Project Library, GitHub edition: a local stand-in for Claude's runtime (window.claude), so the same page runs as a
   static website. Projects come from the snapshot below (read-only); MSRA Logs are saved in this browser (localStorage);
   files download through a normal link; there is no photo upload. */
window.__OPL_EDITION = 'github';
window.__OPL_SNAPSHOT = '__SNAPSHOT_DATE__';
(() => {
  'use strict';
  const PROJECTS = __PROJECTS__;
  const READONLY = new Set(['projects', 'settings']);
  const KEY = 'opl-gh:';
  const lsRead = k => { try { const v = localStorage.getItem(KEY + k); return v == null ? null : JSON.parse(v); } catch (e) { return null; } };
  const lsWrite = (k, v) => {
    try { if (v == null) localStorage.removeItem(KEY + k); else localStorage.setItem(KEY + k, JSON.stringify(v)); }
    catch (e) { throw Object.assign(new Error('This browser has no room left to save it. Use Save as to keep the log as a file.'), { code: 'quota_exceeded' }); }
  };
  const clone = x => x == null ? x : JSON.parse(JSON.stringify(x));
  const fail = msg => Object.assign(new Error(msg), { code: 'invalid_argument' });
  const read = (col, id) => col === 'projects' ? (PROJECTS[id] || null) : col === 'settings' ? null : lsRead(col + '/' + id);
  const ids = col => col === 'projects' ? Object.keys(PROJECTS).sort() : col === 'settings' ? [] : (lsRead('index/' + col) || []).filter(id => lsRead(col + '/' + id));
  const listeners = new Map();   // 'col' or 'col/id' -> Set of callbacks
  const on = (k, fn) => { if (!listeners.has(k)) listeners.set(k, new Set()); listeners.get(k).add(fn); return () => listeners.get(k).delete(fn); };
  const docSnap = (col, id) => { const d = read(col, id); return { id, exists: d != null, data: () => clone(d), metadata: { hasPendingWrites: false } }; };
  const colSnap = col => { const docs = ids(col).map(id => docSnap(col, id)); return { docs, size: docs.length, empty: !docs.length }; };
  const changed = (col, id) => {
    (listeners.get(col + '/' + id) || []).forEach(fn => setTimeout(() => fn(docSnap(col, id)), 0));
    (listeners.get(col) || []).forEach(fn => setTimeout(() => fn(colSnap(col)), 0));
  };
  // another tab of the same browser saving a log
  window.addEventListener('storage', e => {
    if (!e.key || !e.key.startsWith(KEY) || e.key.startsWith(KEY + 'index/')) return;
    const [col, id] = e.key.slice(KEY.length).split('/'); if (col && id) changed(col, id);
  });
  const write = (col, id, data) => {
    if (READONLY.has(col)) throw fail('Projects cannot be changed in the GitHub edition.');
    lsWrite(col + '/' + id, data);
    const list = lsRead('index/' + col) || [];
    if (data == null) lsWrite('index/' + col, list.filter(x => x !== id));
    else if (!list.includes(id)) lsWrite('index/' + col, list.concat(id));
    changed(col, id);
  };
  const docRef = (col, id) => ({
    id, path: col + '/' + id,
    get: async () => docSnap(col, id),
    set: async data => write(col, id, clone(data)),
    update: async data => { const o = read(col, id); if (o == null) throw fail('No such document.'); write(col, id, { ...o, ...clone(data) }); },
    delete: async () => { if (!READONLY.has(col)) write(col, id, null); },
    acquire: async () => ({ acquired: true }),
    onSnapshot: (next) => { setTimeout(() => next(docSnap(col, id)), 0); return on(col + '/' + id, next); }
  });
  const db = {
    collection: col => ({ doc: id => docRef(col, id), onSnapshot: (next) => { setTimeout(() => next(colSnap(col)), 0); return on(col, next); } }),
    doc: path => { const [col, id] = String(path).split('/'); return docRef(col, id); }
  };
  const downloads = {
    save: async ({ filename, data }) => {
      const blob = data instanceof Blob ? data : new Blob([data]);
      const url = URL.createObjectURL(blob), a = document.createElement('a');
      a.href = url; a.download = filename; a.style.display = 'none';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      return { status: 'saved' };
    }
  };
  const caps = { db, downloads, user: { can: async () => false }, assets: null };
  window.claude = { use: k => Promise.resolve(caps[k] || null) };
})();
