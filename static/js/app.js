/* ==========================================================================
   InstaFlow — Frontend SPA (iOS 26 Theme, Pure SVG Icons, Zero Emojis)
   ========================================================================== */
"use strict";

/* ---------------- SVG Icon Library (Zero Emojis) ---------------- */
const ICONS = {
  logo: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
  dashboard: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>`,
  accounts: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
  media: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="4"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>`,
  calendar: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
  publish: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
  settings: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
  sun: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`,
  moon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`,
  user: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
  plus: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
  refresh: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
  trash: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
  play: `<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`,
  pause: `<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`,
  shield: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
  smartphone: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,
  zap: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
  check: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  alert: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`,
  upload: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`,
  eye: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
  logout: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>`,
  clock: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
  flame: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>`,
  video: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>`,
  key: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-1.5 1.5L14 9l-3 3-2-2-4 4 3 3-4 4 3 3 4-4 3 3 4-4-2-2 3.5-3.5L22 5z"></path></svg>`,
  mail: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>`,
  copy: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
  inbox: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>`,
};

/* ---------------- Helpers ---------------- */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const store = {
  get(k) {
    try { return localStorage.getItem(k) || sessionStorage.getItem(k) || this._m?.[k] || null; }
    catch { return this._m?.[k] ?? null; }
  },
  set(k, v) {
    this._m = this._m || {};
    this._m[k] = v;
    try { localStorage.setItem(k, v); } catch {}
    try { sessionStorage.setItem(k, v); } catch {}
  },
  del(k) {
    if (this._m) delete this._m[k];
    try { localStorage.removeItem(k); } catch {}
    try { sessionStorage.removeItem(k); } catch {}
  },
};

const state = {
  token: store.get("instaflow_token"),
  email: store.get("instaflow_email"),
  name: store.get("instaflow_name"),
  pendingEmailForVerification: null,
  theme: store.get("instaflow_theme") || "auto",
  view: "dashboard",
  selectedMediaAccountId: null,
  pollTimer: null,
};

/* ---------------- Sistema de Tema (Claro / Escuro / Automático) ---------------- */
function getEffectiveTheme(pref) {
  if (pref === "claro" || pref === "light") return "light";
  if (pref === "escuro" || pref === "dark") return "dark";
  const hr = new Date().getHours();
  return (hr >= 6 && hr < 18) ? "light" : "dark";
}

function applyTheme(pref) {
  state.theme = pref;
  store.set("instaflow_theme", pref);
  const eff = getEffectiveTheme(pref);
  document.documentElement.setAttribute("data-theme", eff);
  const metaColor = $("#meta-theme-color");
  if (metaColor) metaColor.setAttribute("content", eff === "light" ? "#f8fafc" : "#06080d");
  const themeIco = $("#theme-ico");
  if (themeIco) themeIco.innerHTML = eff === "light" ? ICONS.moon : ICONS.sun;
}

function cycleTheme() {
  const next = state.theme === "auto" ? "claro" : state.theme === "claro" ? "escuro" : "auto";
  applyTheme(next);
  if (state.token) {
    api("/api/auth/theme", { method: "POST", body: { theme: next } }).catch(() => {});
  }
  toast(`Tema: ${next.toUpperCase()}`, "ok");
  if (state.view === "configuracoes") render();
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function parseDate(s) {
  if (!s) return null;
  const d = new Date(/Z$|[+-]\d{2}:\d{2}$/.test(s) ? s : s + "Z");
  return isNaN(d) ? null : d;
}

function fmtDate(s) {
  const d = parseDate(s);
  return d ? d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "—";
}

function shortHash(h) {
  return h ? h.slice(0, 10) + "…" : "—";
}

function fmtSize(b) {
  if (b > 1e9) return (b / 1e9).toFixed(2) + " GB";
  if (b > 1e6) return (b / 1e6).toFixed(1) + " MB";
  return (b / 1e3).toFixed(0) + " KB";
}

/* ---------------- API Wrapper ---------------- */
async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  if (state.token) {
    headers["Authorization"] = "Bearer " + state.token;
    headers["X-Auth-Token"] = state.token;
  }
  let payload;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(path, { method, headers, body: payload });
  let data = null;
  try { data = await res.json(); } catch {}
  if (!res.ok) {
    if (res.status === 401 && !path.startsWith("/api/auth")) {
      logout(false);
    }
    const msg = typeof data?.detail === "string" ? data.detail
      : Array.isArray(data?.detail) ? data.detail.map((x) => x.msg || "").join("; ")
      : data?.detail && typeof data.detail === "object" ? JSON.stringify(data.detail)
      : `Erro HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

/* ---------------- Toast & Modal ---------------- */
function toast(msg, type = "") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  const ico = type === "ok" ? ICONS.check : type === "err" ? ICONS.alert : ICONS.zap;
  el.innerHTML = `<span class="ico">${ico}</span><span>${esc(msg)}</span>`;
  $("#toasts").appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transform = "translateX(20px)";
    setTimeout(() => el.remove(), 250);
  }, 3500);
}

function openModal(html, actions = []) {
  const backdrop = $("#modal-backdrop");
  const modal = $("#modal");
  modal.innerHTML = html + `<div class="mactions"></div>`;
  const box = $(".mactions", modal);
  actions.forEach(({ label, cls = "", onClick }) => {
    const b = document.createElement("button");
    b.className = `btn ${cls}`;
    b.innerHTML = label;
    b.onclick = () => { const r = onClick(); if (r !== false) closeModal(); };
    box.appendChild(b);
  });
  backdrop.classList.add("on");
}

function closeModal() {
  $("#modal-backdrop").classList.remove("on");
}
$("#modal-backdrop").addEventListener("click", (e) => {
  if (e.target.id === "modal-backdrop") closeModal();
});

function confirmDialog(message, okLabel = "Confirmar", cls = "danger") {
  return new Promise((resolve) => {
    openModal(
      `<h3>${ICONS.alert} Confirmação</h3><div class="mbody">${esc(message)}</div>`,
      [
        { label: "Cancelar", onClick: () => resolve(false) },
        { label: okLabel, cls, onClick: () => resolve(true) },
      ]
    );
  });
}

/* ---------------- Autenticação & Verificação de E-mail ---------------- */
function showLogin() {
  clearPoll();
  const lv = $("#login-view");
  const av = $("#app-view");
  if (lv) { lv.classList.remove("hidden"); lv.style.display = "flex"; }
  if (av) { av.classList.remove("on"); av.classList.add("hidden"); av.style.display = "none"; }
}

function showApp() {
  const lv = $("#login-view");
  const av = $("#app-view");
  if (lv) { lv.classList.add("hidden"); lv.style.display = "none"; }
  if (av) { av.classList.remove("hidden"); av.classList.add("on"); av.style.display = "flex"; }
  const emailEl = $("#user-email");
  const displayName = state.name ? `${state.name} (${state.email})` : (state.email || "usuário");
  if (emailEl) emailEl.textContent = displayName;
  const avatarEl = $("#avatar");
  const avatarChar = (state.name || state.email || "U")[0].toUpperCase();
  if (avatarEl) avatarEl.textContent = avatarChar;
  render();
}

function logout(manual = true) {
  state.token = null;
  state.email = null;
  state.name = null;
  store.del("instaflow_token");
  store.del("instaflow_email");
  store.del("instaflow_name");
  clearPoll();
  if (manual) toast("Sessão encerrada.", "ok");
  showLogin();
}

async function doLogin(e) {
  if (e && e.preventDefault) e.preventDefault();
  const email = ($("#login-email")?.value || "").trim();
  const password = $("#login-password")?.value || "";
  if (!email || !email.includes("@")) {
    toast("Informe um e-mail válido.", "err");
    $("#login-email")?.focus();
    return false;
  }
  if (!password || password.length < 4) {
    toast("Senha deve conter no mínimo 4 caracteres.", "err");
    $("#login-password")?.focus();
    return false;
  }
  const btn = $("#btn-login");
  if (btn) btn.disabled = true;
  try {
    const r = await api("/api/auth/login", { method: "POST", body: { email, password } });
    state.token = r.token;
    state.email = r.email;
    state.name = r.name || null;
    store.set("instaflow_token", r.token);
    store.set("instaflow_email", r.email);
    if (r.name) store.set("instaflow_name", r.name);
    toast(`Bem-vindo, ${r.name || r.email}!`, "ok");
    showApp();
  } catch (err) {
    toast(err.message, "err");
  } finally {
    if (btn) btn.disabled = false;
  }
  return false;
}

async function doRegister(e) {
  if (e && e.preventDefault) e.preventDefault();
  const name = ($("#reg-name")?.value || "").trim();
  const email = ($("#reg-email")?.value || "").trim();
  const password = $("#reg-password")?.value || "";
  const passwordConfirm = $("#reg-password-confirm")?.value || "";

  if (!name || name.length < 2) {
    toast("Informe seu nome.", "err");
    $("#reg-name")?.focus();
    return false;
  }
  if (!email || !email.includes("@")) {
    toast("Informe um e-mail válido.", "err");
    $("#reg-email")?.focus();
    return false;
  }
  if (!password || password.length < 4) {
    toast("A senha deve ter no mínimo 4 caracteres.", "err");
    $("#reg-password")?.focus();
    return false;
  }
  if (passwordConfirm && password !== passwordConfirm) {
    toast("As senhas digitadas não coincidem.", "err");
    $("#reg-password-confirm")?.focus();
    return false;
  }

  const btn = $("#btn-register");
  if (btn) btn.disabled = true;
  try {
    const r = await api("/api/auth/register", { method: "POST", body: { name, email, password } });
    if (r.verification_required) {
      state.pendingEmailForVerification = email;
      state.name = name;
      $("#register-form").classList.add("hidden");
      $("#verify-email-form").classList.remove("hidden");
      $("#verify-sub-text").textContent = `Enviamos um código de 6 dígitos para o e-mail ${email}. Digite abaixo:`;
      $("#reg-verif-code-input").value = r.code || "";
      $("#reg-verif-code-input").focus();
      if (!r.smtp_configured) {
        toast(`Código de ativação: ${r.code}`, "ok");
      } else {
        toast("Código enviado para seu e-mail!", "ok");
      }
    } else {
      state.token = r.token;
      state.email = r.email;
      state.name = r.name || name;
      store.set("instaflow_token", r.token);
      store.set("instaflow_email", r.email);
      if (state.name) store.set("instaflow_name", state.name);
      toast("Conta criada com sucesso!", "ok");
      showApp();
    }
  } catch (err) {
    toast(err.message, "err");
  } finally {
    if (btn) btn.disabled = false;
  }
  return false;
}

async function doConfirmSignupEmailCode() {
  const email = state.pendingEmailForVerification || ($("#reg-email")?.value || "").trim();
  const code = ($("#reg-verif-code-input")?.value || "").trim();
  if (!code || code.length < 4) {
    toast("Digite o código de 6 dígitos.", "err");
    $("#reg-verif-code-input")?.focus();
    return;
  }
  const btn = $("#btn-confirm-email-code");
  btn.disabled = true;
  btn.innerHTML = `${ICONS.refresh} Validando...`;
  try {
    const r = await api("/api/auth/verify-email", { method: "POST", body: { email, code } });
    state.token = r.token;
    state.email = r.email;
    state.name = r.name || state.name || null;
    store.set("instaflow_token", r.token);
    store.set("instaflow_email", r.email);
    if (state.name) store.set("instaflow_name", state.name);
    toast("E-mail confirmado com sucesso! Bem-vindo!", "ok");
    showApp();
  } catch (err) {
    toast(err.message, "err");
    btn.disabled = false;
    btn.innerHTML = "Validar Código e Entrar";
  }
}

/* ---------------- Polling Control ---------------- */
function clearPoll() {
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}
function startPoll(fn, ms) {
  clearPoll();
  state.pollTimer = setInterval(fn, ms);
}

/* ---------------- Navegação de Abas & Drawer Control ---------------- */
let drawerCloseTimeout = null;

function isDesktopDevice() {
  return window.innerWidth > 768 && !('ontouchstart' in window && navigator.maxTouchPoints > 1);
}

function openDrawer(withBackdrop = false) {
  if (drawerCloseTimeout) {
    clearTimeout(drawerCloseTimeout);
    drawerCloseTimeout = null;
  }
  const drawer = $("#sidebar-drawer");
  const drawerBackdrop = $("#drawer-backdrop");
  if (drawer) drawer.classList.add("open");
  if (withBackdrop && drawerBackdrop) drawerBackdrop.classList.add("open");
}

function scheduleCloseDrawer(delay = 200) {
  if (drawerCloseTimeout) clearTimeout(drawerCloseTimeout);
  drawerCloseTimeout = setTimeout(() => {
    forceCloseDrawer();
  }, delay);
}

function forceCloseDrawer() {
  if (drawerCloseTimeout) {
    clearTimeout(drawerCloseTimeout);
    drawerCloseTimeout = null;
  }
  const drawer = $("#sidebar-drawer");
  const drawerBackdrop = $("#drawer-backdrop");
  if (drawer) drawer.classList.remove("open");
  if (drawerBackdrop) drawerBackdrop.classList.remove("open");
}

function closeDrawer() {
  forceCloseDrawer();
}

const VIEWS = {
  dashboard: { title: "Dashboard", sub: "Métricas e estatísticas em tempo real", poll: 5000 },
  contas: { title: "Contas Conectadas", sub: "Gerenciamento de perfis e emulação móvel", poll: 4000 },
  midias: { title: "Biblioteca de Mídias", sub: "Arquivos com metadados limpos e organização por conta", poll: 6000 },
  agendamentos: { title: "Agendamentos & Disparos", sub: "Publicações automáticas com rotação inteligente", poll: 4000 },
  aquecimento: { title: "Aquecer Conta", sub: "Maturação automática anti-queda com IA e retenção humana", poll: 2500 },
  gerador_email: { title: "Gerador de E-mail para Instagram", sub: "Caixa temporária compatível com Instagram para receber códigos de confirmação", poll: 3000 },
  publicacoes: { title: "Histórico de Posts", sub: "Log detalhado de execuções com hashes únicos", poll: 3500 },
  configuracoes: { title: "Configurações", sub: "Segurança, troca de senha por e-mail e preferências", poll: 10000 },
};

function render() {
  closeDrawer();
  const v = VIEWS[state.view];
  if (!v) return;
  $("#page-title").textContent = v.title;
  $("#page-sub").textContent = v.sub;
  $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.view === state.view));
  $$(".mobile-nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === state.view));

  const topActions = $("#topbar-actions");
  if (topActions) {
    topActions.innerHTML = `
      <button class="btn primary sm" id="btn-post-now-global">${ICONS.publish} Publicar Agora</button>
    `;
    $("#btn-post-now-global").onclick = () => openDirectPostModal();
  }

  clearPoll();
  const initFn = {
    dashboard: initDashboard,
    contas: initContas,
    midias: initMidias,
    agendamentos: initAgendamentos,
    aquecimento: initAquecimento,
    gerador_email: initGeradorEmail,
    publicacoes: initPublicacoes,
    configuracoes: initConfiguracoes,
  }[state.view];

  if (initFn) initFn();
}

/* ==========================================================================
   MODAL GLOBAL: PUBLICAR AGORA (CONTA ÚNICA OU MULTI-CONTAS COM VARIANTES)
   ========================================================================== */
async function openDirectPostModal() {
  let [accounts, medias] = [[], []];
  try {
    [accounts, medias] = await Promise.all([api("/api/accounts"), api("/api/media")]);
  } catch {}

  if (!accounts.length) {
    toast("Adicione uma conta antes de publicar.", "err");
    return;
  }

  openModal(`
    <h3>${ICONS.publish} Publicar Agora no Instagram</h3>
    <div class="mbody">
      <!-- Abas de Modo: Conta Única vs Multi-Contas -->
      <div class="auth-tabs" style="margin-bottom:14px">
        <button type="button" class="auth-tab active" id="modal-tab-single">Conta Única</button>
        <button type="button" class="auth-tab" id="modal-tab-multi">Distribuir em Multi-Contas</button>
      </div>

      <form id="direct-post-form">
        <!-- Modo 1: Conta Única -->
        <div id="box-mode-single">
          <label class="field">
            <span>Selecionar Conta de Destino</span>
            <select class="input" id="dp-account" required>
              ${accounts.map((a) => `<option value="${a.id}">@${esc(a.ig_username)} (${esc(a.name)})</option>`).join("")}
            </select>
          </label>
        </div>

        <!-- Modo 2: Multi-Contas -->
        <div id="box-mode-multi" class="hidden">
          <label class="field">
            <span style="display:flex;justify-content:space-between;align-items:center">
              <span>Selecionar Perfis de Destino</span>
              <button type="button" class="btn ghost sm" id="btn-select-all-dp-acc" style="font-size:11px;padding:2px 6px;min-height:22px">Selecionar Todas</button>
            </span>
            <div style="display:flex;flex-direction:column;gap:6px;max-height:130px;overflow-y:auto;padding:8px 10px;background:var(--bg-card-sub);border:1px solid var(--border);border-radius:var(--radius-sm)">
              ${accounts.map((a) => `
                <label style="display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--text-primary);cursor:pointer">
                  <input type="checkbox" class="dp-multi-checkbox" value="${a.id}" checked>
                  <span>@${esc(a.ig_username)} <span style="color:var(--text-muted)">(${esc(a.name)})</span></span>
                </label>
              `).join("")}
            </div>
            <div style="font-size:11px;color:var(--green);margin-top:5px">
              ${ICONS.shield} O InstaFlow gerará uma variante visual e hash SHA-256 exclusivo para cada conta, evitando duplicações.
            </div>
          </label>
        </div>

        <div class="row">
          <label class="field">
            <span>Tipo de Destino</span>
            <select class="input" id="dp-target-type">
              <option value="reel" selected>Reels (Vídeo — Qualidade Máxima 1080p/4K)</option>
              <option value="trial_reel">Reels de Teste (Trial Reel — Testar com Não-Seguidores)</option>
              <option value="feed">Feed (Foto — Qualidade Original)</option>
              <option value="story">Story (9:16 Full Screen)</option>
            </select>
          </label>
          <label class="field">
            <span>Selecionar Mídia</span>
            <select class="input" id="dp-media">
              <option value="">Automático (Rotacionar mídias)</option>
              ${medias.map((m) => `<option value="${m.id}">${esc(m.original_name)} (${m.kind === "video" ? "Vídeo" : "Foto"})</option>`).join("")}
            </select>
          </label>
        </div>

        <div style="font-size:11px;color:var(--text-muted);margin:-6px 0 10px;display:flex;align-items:center;gap:6px">
          ${ICONS.bolt || ""} <span><strong>Qualidade Máxima Ativa:</strong> Bitrate original, resolução e cores são preservados 100% sem perdas no padrão iPhone Pro Max.</span>
        </div>

        <label class="field">
          <span>Legenda da Publicação</span>
          <textarea class="input" id="dp-caption" placeholder="Escreva a legenda e hashtags aqui..."></textarea>
        </label>

        <label class="field">
          <span>Marcar Perfis (@usertags) — Opcional</span>
          <input class="input" id="dp-usertags" placeholder="Ex: @perfil1, @perfil2">
        </label>
      </form>
    </div>`,
    [
      { label: "Cancelar", onClick: () => {} },
      {
        label: `${ICONS.publish} Publicar Imediatamente`,
        cls: "primary",
        onClick: async () => {
          const isMulti = $("#box-mode-multi") && !$("#box-mode-multi").classList.contains("hidden");
          const media_id = $("#dp-media").value ? +$("#dp-media").value : null;
          const target_type = $("#dp-target-type").value;
          const caption = $("#dp-caption").value;
          const usertags = $("#dp-usertags").value.trim() || null;

          if (isMulti) {
            const checkedBoxes = [...$$(".dp-multi-checkbox:checked")];
            const account_ids = checkedBoxes.map((b) => +b.value);
            if (!account_ids.length) {
              toast("Selecione ao menos 1 conta para distribuir.", "err");
              return false;
            }
            try {
              const res = await api("/api/posting/multi", {
                method: "POST",
                body: { account_ids, media_id, target_type, caption, usertags, delay_sec: 12 },
              });
              toast(res.message || "Distribuição multi-contas iniciada!", "ok");
              state.view = "publicacoes";
              render();
            } catch (err) {
              toast(err.message, "err");
              return false;
            }
          } else {
            const account_id = +$("#dp-account").value;
            try {
              await api("/api/posting/now", {
                method: "POST",
                body: { account_id, media_id, target_type, caption, usertags },
              });
              toast("Publicação enviada! Acompanhe em Publicações.", "ok");
              state.view = "publicacoes";
              render();
            } catch (err) {
              toast(err.message, "err");
              return false;
            }
          }
        },
      },
    ]
  );

  // Bind Abas do Modal
  const tabSingle = $("#modal-tab-single");
  const tabMulti = $("#modal-tab-multi");
  const boxSingle = $("#box-mode-single");
  const boxMulti = $("#box-mode-multi");
  const btnSelectAll = $("#btn-select-all-dp-acc");

  if (tabSingle && tabMulti && boxSingle && boxMulti) {
    tabSingle.onclick = () => {
      tabSingle.classList.add("active");
      tabMulti.classList.remove("active");
      boxSingle.classList.remove("hidden");
      boxMulti.classList.add("hidden");
    };
    tabMulti.onclick = () => {
      tabMulti.classList.add("active");
      tabSingle.classList.remove("active");
      boxMulti.classList.remove("hidden");
      boxSingle.classList.add("hidden");
    };
  }

  if (btnSelectAll) {
    let allSelected = true;
    btnSelectAll.onclick = () => {
      allSelected = !allSelected;
      $$(".dp-multi-checkbox").forEach((cb) => (cb.checked = allSelected));
      btnSelectAll.textContent = allSelected ? "Desmarcar Todas" : "Selecionar Todas";
    };
  }
}

/* ==========================================================================
   VIEW 1: DASHBOARD REALISTA COM MÉTRICAS DINÂMICAS
   ========================================================================== */
async function initDashboard() {
  const c = $("#content");
  c.innerHTML = `<div id="dashboard-content"></div>`;
  await refreshDashboardData();
  startPoll(refreshDashboardData, VIEWS.dashboard.poll);
}

async function refreshDashboardData() {
  const container = $("#dashboard-content");
  if (!container) return;
  let stats;
  try {
    stats = await api("/api/stats");
  } catch {
    container.innerHTML = `<div class="empty">${ICONS.alert} Falha ao carregar métricas.</div>`;
    return;
  }

  const successRate = stats.total_posts > 0 ? 100 : 0;
  const recentLogs = stats.recent_logs || [];
  const daily = stats.daily_activity || [];
  const maxVal = Math.max(...daily.map((d) => d.count), 5);

  container.innerHTML = `
    <!-- Tiles de Estatísticas Compactas -->
    <div class="grid-stats">
      <div class="stat-card">
        <div class="stat-header"><span>Contas Ativas</span><span class="ico">${ICONS.accounts}</span></div>
        <div class="stat-value">${stats.active_accounts} <span style="font-size:13px;color:var(--text-muted);font-weight:400">/ ${stats.total_accounts}</span></div>
        <div class="stat-sub">${stats.active_accounts > 0 ? "Prontas para disparos" : "Nenhuma conta ativa"}</div>
      </div>
      <div class="stat-card">
        <div class="stat-header"><span>Mídias Salvas</span><span class="ico">${ICONS.media}</span></div>
        <div class="stat-value">${stats.total_medias}</div>
        <div class="stat-sub">Com metadados limpos</div>
      </div>
      <div class="stat-card">
        <div class="stat-header"><span>Posts Hoje</span><span class="ico">${ICONS.publish}</span></div>
        <div class="stat-value">${stats.posts_today}</div>
        <div class="stat-sub">Publicações efetuadas</div>
      </div>
      <div class="stat-card">
        <div class="stat-header"><span>Agendamentos</span><span class="ico">${ICONS.calendar}</span></div>
        <div class="stat-value">${stats.schedules_enabled}</div>
        <div class="stat-sub">Disparos ativos</div>
      </div>
    </div>

    <!-- Gráficos Interativos SVG 100% Reais -->
    <div class="row" style="margin-bottom:16px;align-items:stretch">
      <div class="card" style="flex:1.4">
        <div class="section-title" style="margin:0 0 8px;display:flex;justify-content:space-between">
          <span>Atividade Real de Publicações (Últimos 7 Dias)</span>
          <span class="badge ${stats.total_posts > 0 ? "green" : "gray"}"><span class="dot"></span>${stats.total_posts > 0 ? "Dados Reais Ativos" : "Sem Disparos"}</span>
        </div>
        <div class="chart-container">
          <svg class="svg-bar-chart" viewBox="0 0 350 110" preserveAspectRatio="none">
            <defs>
              <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#6366f1"/>
                <stop offset="100%" stop-color="#a855f7" stop-opacity="0.4"/>
              </linearGradient>
            </defs>
            ${daily.map((item, idx) => {
              const val = item.count;
              const barHeight = val > 0 ? Math.max(12, Math.round((val / maxVal) * 80)) : 0;
              const x = 15 + idx * 48;
              const y = 95 - barHeight;
              return `
                ${barHeight > 0 ? `<rect class="chart-bar" x="${x}" y="${y}" width="26" height="${barHeight}" rx="5" fill="url(#barGrad)" data-val="${val}" data-day="${item.day}"/>` : `<rect x="${x}" y="93" width="26" height="2" rx="1" fill="var(--border)"/>`}
                <text x="${x + 13}" y="108" font-size="10" fill="var(--text-muted)" text-anchor="middle" font-family="inherit">${item.day}</text>
                <text x="${x + 13}" y="${barHeight > 0 ? y - 4 : 88}" font-size="10" font-weight="700" fill="${val > 0 ? 'var(--text-primary)' : 'var(--text-muted)'}" text-anchor="middle" font-family="inherit">${val}</text>
              `;
            }).join("")}
          </svg>
        </div>
      </div>

      <div class="card" style="flex:1">
        <div class="section-title" style="margin:0 0 8px">Taxa de Entrega de Disparos</div>
        <div class="chart-donut-wrap">
          <svg class="chart-donut-circle" viewBox="0 0 36 36">
            <path stroke="var(--border)" stroke-width="3.8" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path stroke="var(--accent)" stroke-dasharray="${successRate}, 100" stroke-width="3.8" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
          </svg>
          <div>
            <div style="font-size:22px;font-weight:800;color:var(--text-primary)">${stats.total_posts > 0 ? `${successRate}%` : "0%"}</div>
            <div style="font-size:11.5px;color:var(--text-secondary)">${stats.total_posts > 0 ? "Conclusão com Sucesso" : "Nenhum Post Ainda"}</div>
            <div style="font-size:11px;color:${stats.active_accounts > 0 ? "var(--green)" : "var(--text-muted)"};margin-top:2px">${ICONS.shield} ${stats.active_accounts > 0 ? "Motor Anti-Queda Ativo" : "Aguardando Conexão"}</div>
          </div>
        </div>
        <div style="margin-top:10px;font-size:11.5px;color:var(--text-muted);border-top:1px solid var(--border);padding-top:8px">
          Total Publicado: <strong>${stats.total_posts}</strong> posts no histórico
        </div>
      </div>
    </div>

    <!-- Tabela de Próximos Disparos & Últimos Posts -->
    <div class="row" style="align-items:flex-start">
      <div class="card" style="flex:1">
        <div class="section-title" style="margin-top:0">Próximos Disparos</div>
        ${stats.upcoming.length ? `
          <div class="table-wrap"><table>
            <tr><th>Agendamento</th><th>Conta</th><th>Horário</th></tr>
            ${stats.upcoming.map((u) => `<tr>
              <td><strong>${esc(u.name)}</strong></td>
              <td><span class="badge blue"><span class="dot"></span>@${esc(u.account)}</span></td>
              <td>${fmtDate(u.next_run)}</td>
            </tr>`).join("")}
          </table></div>` : `<div class="empty"><div class="empty-ico">${ICONS.calendar}</div>Nenhum agendamento programado.</div>`}
      </div>

      <div class="card" style="flex:1">
        <div class="section-title" style="margin-top:0">Últimas Publicações</div>
        ${recentLogs.length ? logTable(recentLogs) : `<div class="empty"><div class="empty-ico">${ICONS.publish}</div>Nenhum post registrado ainda.</div>`}
      </div>
    </div>`;
}

function formatActionName(act) {
  const map = {
    post_reel: "Reels (Vídeo)",
    post_feed: "Feed (Foto)",
    post_story: "Story",
    post_reel_simulado: "Reels (Simulado)",
    post_feed_simulado: "Feed (Simulado)",
    post_story_simulado: "Story (Simulado)",
    fila_reel_concluida: "Fila Concluída",
    fila_feed_concluida: "Fila Concluída",
    fila_story_concluida: "Fila Concluída",
  };
  return map[act] || (act ? act.replace(/_/g, " ") : "Publicação");
}

function logTable(logs) {
  return `<div class="table-wrap"><table>
    <tr><th>Data</th><th>Conta</th><th>Tipo</th><th>Status</th></tr>
    ${logs.slice(0, 5).map((l) => `<tr>
      <td>${fmtDate(l.created_at)}</td>
      <td><strong>@${esc(l.account_name)}</strong></td>
      <td><span class="badge gray">${formatActionName(l.action)}</span></td>
      <td>${statusBadge(l.status)}</td>
    </tr>`).join("")}
  </table></div>`;
}

function statusBadge(status) {
  return status === "success"
    ? `<span class="badge green"><span class="dot"></span>Sucesso</span>`
    : `<span class="badge red"><span class="dot"></span>Falha</span>`;
}

/* ==========================================================================
   VIEW 2: CONTAS INSTAGRAM
   ========================================================================== */
const ACCT_STATUS_META = {
  ativo: ["green", "Conectado / Ativo", false],
  conectando: ["blue", "Autenticando…", true],
  aguardando_codigo: ["amber", "Aguardando 2FA", true],
  checkpoint: ["red", "Verificação Requerida", false],
  erro: ["red", "Erro de Conexão", false],
  pendente: ["gray", "Pendente", false],
};

function initContas() {
  const c = $("#content");
  c.innerHTML = `
    ${accountForm()}
    <div id="accounts-list-wrap"></div>
  `;
  bindAccountForm();
  refreshAccountsList();
  startPoll(refreshAccountsList, VIEWS.contas.poll);
}

function accountForm() {
  return `
  <div class="card panel-form" style="margin-bottom:18px">
    <div class="section-title" style="margin-top:0">Conectar Conta do Instagram</div>
    <form id="acct-form">
      <div class="row">
        <label class="field"><span>Nome Interno (identificação)</span><input class="input" name="name" placeholder="Ex: Meu Perfil Principal" required></label>
        <label class="field"><span>Usuário do Instagram (@)</span><input class="input" name="ig_username" placeholder="usuario_instagram" required></label>
      </div>
      <div class="row">
        <label class="field">
          <span>Senha da Conta</span>
          <input class="input" type="password" id="acct-pwd-input" name="ig_password" placeholder="Digite a senha do Instagram" required>
        </label>
        <label class="field">
          <span>Proxy Residencial / Móvel (Opcional)</span>
          <input class="input" id="acct-proxy-input" name="proxy_url" placeholder="http://usuario:senha@ip:porta ou IP:PORT:USER:PASS">
          <div style="display:flex;align-items:center;gap:8px;margin-top:6px;flex-wrap:wrap">
            <button type="button" class="btn sm ghost" id="btn-test-proxy" style="font-size:11px">${ICONS.shield} Testar Proxy</button>
            <span id="proxy-test-result" style="font-size:11px;color:var(--text-muted)">Opcional — deixe em branco para usar a conexão direta do servidor.</span>
          </div>
        </label>
      </div>

      <div style="margin-bottom:10px">
        <button type="button" class="btn sm ghost" id="btn-toggle-sessionid" style="font-size:11px">
          ${ICONS.key} Opção de Recuperação / Importar via Cookie SessionID
        </button>
        <div id="box-sessionid-import" class="hidden" style="margin-top:6px;padding:8px 10px;background:var(--bg-card-sub);border:1px solid var(--border);border-radius:var(--radius-sm)">
          <input class="input" id="input-sessionid-raw" placeholder="Cole o cookie sessionid aqui..." style="font-size:11.5px;font-family:ui-monospace, monospace">
        </div>
      </div>

      <div class="row">
        <div class="field">
          <span>Emulação de Hardware Móvel</span>
          <div class="fp-box">
            <div class="fp-row"><span>Perfil:</span><span class="badge blue"><span class="dot"></span>Dispositivo Android Real</span></div>
          </div>
        </div>
        <div class="field">
          <span>Pausas Humanizadas (segundos)</span>
          <div class="row">
            <label class="field"><span>Mínimo</span><input class="input" type="number" name="delay_min" value="3" min="1"></label>
            <label class="field"><span>Máximo</span><input class="input" type="number" name="delay_max" value="12" min="2"></label>
          </div>
        </div>
      </div>

      <div class="toggle-row">
        <div>
          <div class="tlabel">Modo Simulação (Ambiente de Teste)</div>
          <div class="tdesc">Testa o fluxo completo sem disparar no Instagram</div>
        </div>
        <label class="switch"><input type="checkbox" name="simulate"><span class="slider"></span></label>
      </div>

      <button class="btn primary" type="submit" style="margin-top:12px">${ICONS.plus} Salvar e Conectar Conta</button>
    </form>
  </div>`;
}

function bindAccountForm() {
  const f = $("#acct-form");
  const btnTog = $("#btn-toggle-sessionid");
  const boxSess = $("#box-sessionid-import");
  const inpSess = $("#input-sessionid-raw");
  const pwdInp = $("#acct-pwd-input");

  if (btnTog && boxSess) btnTog.onclick = () => boxSess.classList.toggle("hidden");
  if (inpSess && pwdInp) inpSess.oninput = () => { if (inpSess.value.trim()) pwdInp.value = inpSess.value.trim(); };

  const btnTestProxy = $("#btn-test-proxy");
  const proxyInp = $("#acct-proxy-input");
  const proxyRes = $("#proxy-test-result");
  if (btnTestProxy && proxyInp && proxyRes) {
    btnTestProxy.onclick = async () => {
      const val = proxyInp.value.trim();
      if (!val) {
        proxyRes.textContent = "Nenhum proxy informado — será usada a conexão direta do servidor.";
        proxyRes.style.color = "var(--text-muted)";
        return;
      }
      const original = btnTestProxy.innerHTML;
      btnTestProxy.disabled = true;
      btnTestProxy.innerHTML = "Testando...";
      proxyRes.textContent = "Verificando conexão e IP de saída...";
      proxyRes.style.color = "var(--text-muted)";
      try {
        const r = await api("/api/accounts/validate-proxy", { method: "POST", body: { proxy_url: val } });
        if (r.ok) {
          proxyRes.textContent = `IP de saída: ${r.ip} · Latência: ${r.latency_ms}ms`;
          proxyRes.style.color = "var(--green)";
          toast("Proxy funcionando!", "ok");
        } else {
          proxyRes.textContent = r.message || "Falha ao validar o proxy.";
          proxyRes.style.color = "var(--red)";
          toast(r.message || "Proxy inválido.", "err");
        }
      } catch (err) {
        proxyRes.textContent = err.message || "Falha ao validar o proxy.";
        proxyRes.style.color = "var(--red)";
        toast(err.message || "Falha ao testar proxy.", "err");
      } finally {
        btnTestProxy.disabled = false;
        btnTestProxy.innerHTML = original;
      }
    };
  }

  if (!f) return;
  f.onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(f);
    const body = {
      name: fd.get("name"),
      ig_username: fd.get("ig_username"),
      ig_password: fd.get("ig_password"),
      proxy_url: fd.get("proxy_url") || null,
      delay_min: +fd.get("delay_min") || 3,
      delay_max: +fd.get("delay_max") || 12,
      simulate: fd.get("simulate") === "on",
      humanize: true,
      warmup: true,
    };
    try {
      await api("/api/accounts", { method: "POST", body });
      f.reset();
      if (boxSess) boxSess.classList.add("hidden");
      toast("Conta adicionada! Emulando smartphone...", "ok");
      refreshAccountsList();
    } catch (err) {
      toast(err.message, "err");
    }
  };
}

async function refreshAccountsList() {
  const wrap = $("#accounts-list-wrap");
  if (!wrap) return;

  const activeEl = document.activeElement;
  if (activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA")) {
    if (activeEl.id && activeEl.id.startsWith("code-")) return;
  }

  $$("input[id^='code-']", wrap).forEach((inp) => {
    if (inp.value) {
      window._draft2fa = window._draft2fa || {};
      window._draft2fa[inp.id] = inp.value;
    }
  });

  let accounts = [];
  try { accounts = await api("/api/accounts"); } catch { return; }

  if (!accounts.length) {
    wrap.innerHTML = `<div class="empty"><div class="empty-ico">${ICONS.accounts}</div>Nenhuma conta cadastrada. Adicione uma conta acima.</div>`;
    return;
  }

  wrap.innerHTML = `<div class="grid-cards">${accounts.map(acctCard).join("")}</div>`;

  if (window._draft2fa) {
    Object.keys(window._draft2fa).forEach((k) => {
      const el = $(`#${k}`, wrap);
      if (el) el.value = window._draft2fa[k];
    });
  }

  bindAccountActions(accounts);
}

function acctCard(a) {
  const meta = ACCT_STATUS_META[a.status] || ["gray", a.status, false];
  const s = a.fingerprint_summary || {};
  const chips = [
    a.simulate ? `<span class="badge blue"><span class="dot"></span>Simulação</span>` : `<span class="badge green"><span class="dot"></span>Modo Real</span>`,
    a.proxy_url ? `<span class="badge amber">${ICONS.shield} Proxy</span>` : "",
  ].filter(Boolean).join(" ");

  return `
  <div class="card acct-card" id="card-acct-${a.id}">
    <div class="head">
      <div>
        <h3>${esc(a.name)}</h3>
        <div class="ig">@${esc(a.ig_username)}</div>
      </div>
      <span class="badge ${meta[0]}"><span class="dot ${meta[2] ? "pulse-dot" : ""}"></span>${meta[1]}</span>
    </div>
    <div style="margin:4px 0 8px">${chips}</div>

    <div class="fp-box">
      <div class="fp-row"><span>Aparelho:</span><span>${esc(s.device || "—")}</span></div>
      <div class="fp-row"><span>Android:</span><span>${esc(s.android || "—")}</span></div>
      <div class="fp-row"><span>Resolução:</span><span>${esc(s.screen || "—")}</span></div>
    </div>

    ${a.status_detail ? `<div class="status-line">${esc(a.status_detail)}</div>` : ""}

    ${a.status === "aguardando_codigo" ? `
      <div style="margin-top:10px;padding:10px;background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.3);border-radius:var(--radius-sm)">
        <div style="font-size:11.5px;color:var(--amber);font-weight:600;margin-bottom:6px">Código 2FA Requerido:</div>
        <div class="row">
          <input class="input" id="code-${a.id}" placeholder="Digite o código SMS/App">
          <button class="btn sm primary" data-act="verify" data-id="${a.id}">${ICONS.check} Confirmar</button>
        </div>
      </div>` : ""}

    ${a.status === "checkpoint" ? `
      <div style="margin-top:10px;padding:10px;background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.3);border-radius:var(--radius-sm)">
        <div style="font-size:11.5px;color:var(--red);font-weight:600;margin-bottom:4px">Confirmação de Segurança:</div>
        <div style="font-size:11px;color:var(--text-secondary);line-height:1.4;margin-bottom:8px">
          Abra o app do Instagram e autorize o acesso ("Fui Eu"). Em seguida, clique em Testar.
        </div>
        <button class="btn sm primary" data-act="check-conn" data-id="${a.id}" style="width:100%">${ICONS.check} Já Confirmei / Testar</button>
      </div>` : ""}

    <div class="acct-actions">
      <button class="btn sm" data-act="check-conn" data-id="${a.id}">${ICONS.zap} Testar</button>
      <button class="btn sm" data-act="view-fp" data-id="${a.id}">${ICONS.smartphone} Aparelho</button>
      <button class="btn sm" data-act="retry" data-id="${a.id}">${ICONS.refresh} Reconectar</button>
      <button class="btn sm danger" data-act="del" data-id="${a.id}">${ICONS.trash}</button>
    </div>
  </div>`;
}

function bindAccountActions(accounts) {
  $$("[data-act]", $("#accounts-list-wrap")).forEach((b) => {
    b.onclick = async () => {
      const id = +b.dataset.id;
      const act = b.dataset.act;
      const acct = accounts.find((a) => a.id === id);

      try {
        if (act === "del") {
          const ok = await confirmDialog(`Deseja excluir a conta "${acct?.name}"?`);
          if (!ok) return;
          await api(`/api/accounts/${id}`, { method: "DELETE" });
          toast("Conta excluída.", "ok");
          refreshAccountsList();
        } else if (act === "check-conn") {
          toast("Validando conexão...", "");
          const r = await api(`/api/accounts/${id}/check-connection`, { method: "POST" });
          if (r.status.startsWith("connected")) {
            toast(`Conta @${r.username} conectada e ativa!`, "ok");
            refreshAccountsList();
          } else {
            toast(`Status: ${r.message}`, "err");
            refreshAccountsList();
          }
        } else if (act === "view-fp") {
          const fp = acct.fingerprint || {};
          const dev = fp.device || {};
          openModal(`
            <h3>${ICONS.smartphone} Hardware Emulado: ${esc(dev.manufacturer)} ${esc(dev.model)}</h3>
            <div class="mbody">
              <div class="fp-box">
                <div class="fp-row"><span>Dispositivo:</span><span>${esc(dev.device)}</span></div>
                <div class="fp-row"><span>Android:</span><span>Android ${esc(dev.android_release)}</span></div>
                <div class="fp-row"><span>Resolução:</span><span>${esc(dev.resolution)} (${esc(dev.dpi)})</span></div>
                <div class="fp-row"><span>Chipset / CPU:</span><span>${esc(dev.cpu)}</span></div>
              </div>
            </div>`,
            [{ label: "Fechar", cls: "primary", onClick: () => {} }]
          );
        } else if (act === "retry") {
          openModal(`
            <h3>${ICONS.refresh} Reconectar @${esc(acct?.ig_username)}</h3>
            <div class="mbody">
              <label class="field">
                <span>Senha da Conta ou Cookie SessionID</span>
                <input class="input" type="password" id="modal-new-pass" placeholder="Digite a senha ou cole o sessionid" required>
              </label>
              <label class="field">
                <span>Proxy Residencial (Opcional)</span>
                <input class="input" id="modal-new-proxy" value="${esc(acct?.proxy_url || "")}" placeholder="http://user:pass@host:port">
              </label>
            </div>`,
            [
              { label: "Cancelar", onClick: () => {} },
              {
                label: `${ICONS.refresh} Conectar`,
                cls: "primary",
                onClick: async () => {
                  const pass = $("#modal-new-pass")?.value?.trim();
                  if (!pass) { toast("Informe a senha ou sessionid.", "err"); return false; }
                  const proxy_url = $("#modal-new-proxy")?.value?.trim() || null;
                  try {
                    await api(`/api/accounts/${id}/update-credentials`, { method: "POST", body: { ig_password: pass, proxy_url } });
                    toast("Reconectando...", "ok");
                    refreshAccountsList();
                  } catch (err) {
                    toast(err.message, "err");
                    return false;
                  }
                },
              },
            ]
          );
        } else if (act === "verify") {
          const inp = $("#code-" + id);
          const code = inp?.value?.trim();
          if (!code) { toast("Digite o código 2FA.", "err"); inp?.focus(); return; }
          b.disabled = true;
          b.innerHTML = `${ICONS.refresh} Validando...`;
          try {
            await api(`/api/accounts/${id}/verify`, { method: "POST", body: { code } });
            if (window._draft2fa) delete window._draft2fa[`code-${id}`];
            toast("2FA autenticado com sucesso!", "ok");
            refreshAccountsList();
          } catch (err) {
            toast(err.message, "err");
            b.disabled = false;
            b.innerHTML = `${ICONS.check} Confirmar`;
          }
        }
      } catch (err) {
        toast(err.message, "err");
      }
    };
  });
}

/* ==========================================================================
   VIEW 3: MÍDIAS (COM VINCULAÇÃO POR CONTA & QUALIDADE TOTAL)
   ========================================================================== */
async function initMidias() {
  const c = $("#content");
  let accounts = [];
  try { accounts = await api("/api/accounts"); } catch {}

  c.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;gap:10px;flex-wrap:wrap">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:12.5px;color:var(--text-muted);font-weight:600">Filtrar por Conta:</span>
        <select class="input" id="media-account-filter" style="max-width:220px;min-height:34px;padding:6px 10px;font-size:12px">
          <option value="">Todas as Mídias</option>
          ${accounts.map((a) => `<option value="${a.id}" ${state.selectedMediaAccountId === a.id ? "selected" : ""}>@${esc(a.ig_username)} (${esc(a.name)})</option>`).join("")}
        </select>
      </div>

      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:12.5px;color:var(--text-muted);font-weight:600">Vincular Upload a:</span>
        <select class="input" id="media-upload-target-account" style="max-width:220px;min-height:34px;padding:6px 10px;font-size:12px">
          <option value="">Todas as Contas (Global)</option>
          ${accounts.map((a) => `<option value="${a.id}">@${esc(a.ig_username)} (${esc(a.name)})</option>`).join("")}
        </select>
      </div>
    </div>

    <div class="dropzone" id="dropzone">
      <div class="dz-ico">${ICONS.upload}</div>
      <div style="font-size:14px;font-weight:700;color:var(--text-primary)">Arraste vídeos/fotos ou clique para enviar em massa</div>
      <div style="font-size:11.5px;color:var(--text-muted);margin-top:4px">Preserva 100% da qualidade original (bitrate e resolução). Metadados e EXIF são limpos automaticamente.</div>
    </div>
    <input type="file" id="file-input" multiple accept=".jpg,.jpeg,.png,.webp,.mp4,.mov" style="display:none">
    <div id="upload-progress-container"></div>
    <div id="media-list-wrap"></div>
  `;

  $("#media-account-filter").onchange = (e) => {
    state.selectedMediaAccountId = e.target.value ? +e.target.value : null;
    refreshMediaList();
  };

  bindMediaUploader();
  refreshMediaList();
  startPoll(refreshMediaList, VIEWS.midias.poll);
}

function bindMediaUploader() {
  const dz = $("#dropzone");
  const input = $("#file-input");
  if (!dz || !input) return;

  dz.onclick = () => input.click();
  input.onchange = () => uploadFiles(input.files);

  ["dragover", "dragenter"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("over"); }));
  dz.addEventListener("drop", (e) => uploadFiles(e.dataTransfer.files));
}

async function refreshMediaList() {
  const wrap = $("#media-list-wrap");
  if (!wrap) return;
  let medias = [];
  try {
    const url = state.selectedMediaAccountId ? `/api/media?account_id=${state.selectedMediaAccountId}` : "/api/media";
    medias = await api(url);
  } catch { return; }

  if (!medias.length) {
    wrap.innerHTML = `<div class="empty"><div class="empty-ico">${ICONS.media}</div>Nenhuma mídia encontrada na biblioteca. Faça o upload acima.</div>`;
    return;
  }

  const pendingCount = medias.filter(m => (m.times_used || 0) === 0).length;
  const sentCount = medias.filter(m => (m.times_used || 0) > 0).length;

  wrap.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:10px;padding:10px 14px;background:var(--bg-card-sub);border:1px solid var(--border);border-radius:var(--radius-sm)">
      <div style="font-size:12.5px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;flex-wrap:wrap">
        <span>Total: <strong>${medias.length}</strong> mídias</span>
        <span class="badge blue"><span class="dot"></span>${pendingCount} Pendentes</span>
        <span class="badge green"><span class="dot"></span>${sentCount} Já Enviadas</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
        ${sentCount > 0 ? `
          <button class="btn sm ghost" id="btn-reset-all-media-status" title="Zera o contador para poder postar a lista novamente">
            ${ICONS.refresh} Reiniciar Fila (Resetar Envios)
          </button>
        ` : ""}
        <button class="btn sm danger" id="btn-delete-all-media" title="Exclui todas as mídias da biblioteca permanentemente">
          ${ICONS.trash} Excluir Todas as Mídias
        </button>
      </div>
    </div>
    <div class="grid-cards">${medias.map(mediaCard).join("")}</div>
  `;

  const btnReset = $("#btn-reset-all-media-status");
  if (btnReset) {
    btnReset.onclick = async () => {
      const ok = await confirmDialog("Deseja marcar todas as mídias como pendentes (não enviadas) para permitir uma nova rodada de disparos?", "Reiniciar Fila", "primary");
      if (!ok) return;
      try {
        const url = state.selectedMediaAccountId ? `/api/media/reset-status?account_id=${state.selectedMediaAccountId}` : "/api/media/reset-status";
        const res = await api(url, { method: "POST" });
        toast(res.message || "Fila reiniciada com sucesso!", "ok");
        refreshMediaList();
      } catch (err) {
        toast(err.message, "err");
      }
    };
  }

  const btnDeleteAll = $("#btn-delete-all-media");
  if (btnDeleteAll) {
    btnDeleteAll.onclick = async () => {
      const ok = await confirmDialog(`Tem certeza que deseja EXCLUIR TODAS as ${medias.length} mídias da sua biblioteca? Esta ação não pode ser desfeita.`, "Excluir Tudo Permanentemente", "danger");
      if (!ok) return;
      btnDeleteAll.disabled = true;
      btnDeleteAll.innerHTML = `${ICONS.refresh} Excluindo...`;
      try {
        const url = state.selectedMediaAccountId ? `/api/media/all/clear?account_id=${state.selectedMediaAccountId}` : "/api/media/all/clear";
        const res = await api(url, { method: "DELETE" });
        toast(res.message || "Todas as mídias foram excluídas.", "ok");
        refreshMediaList();
      } catch (err) {
        toast(err.message, "err");
        btnDeleteAll.disabled = false;
        btnDeleteAll.innerHTML = `${ICONS.trash} Excluir Todas as Mídias`;
      }
    };
  }

  bindMediaActions(medias);
}

function mediaCard(m) {
  const isVideo = m.kind === "video";
  const isSent = (m.times_used || 0) > 0;
  const fileUrl = `/api/media/${m.id}/file?token=${state.token}`;

  return `
  <div class="card media-card" style="${isSent ? 'border-color: rgba(16, 185, 129, 0.35);' : ''}">
    <div class="thumb">
      ${isVideo ? `<video src="${fileUrl}" muted preload="metadata"></video><div style="position:absolute;color:#fff;background:rgba(0,0,0,0.6);padding:6px;border-radius:50%">${ICONS.video}</div>`
                : `<img src="${fileUrl}" alt="${esc(m.original_name)}" loading="lazy">`}
      <div style="position:absolute;top:6px;left:6px">
        ${isSent ? `<span class="badge green" style="background:rgba(6,15,25,0.85);backdrop-filter:blur(8px)"><span class="dot"></span>Já Enviado</span>`
                 : `<span class="badge blue" style="background:rgba(6,15,25,0.85);backdrop-filter:blur(8px)"><span class="dot"></span>Pendente</span>`}
      </div>
    </div>
    <h4 title="${esc(m.original_name)}">${esc(m.original_name)}</h4>
    <div class="meta">
      <span class="badge ${isVideo ? "amber" : "blue"}"><span class="dot"></span>${isVideo ? "Vídeo MP4" : "Imagem"}</span>
      ${m.account_name ? `<span class="badge gray">@${esc(m.account_name)}</span>` : `<span class="badge gray">Global</span>`}
      <div style="margin-top:3px">${fmtSize(m.size_bytes)} · Status: <strong>${isSent ? `Enviado ${m.times_used}x` : "Pendente de envio"}</strong></div>
      <div class="mono" style="margin-top:1px">SHA: ${shortHash(m.active_sha256)}</div>
    </div>
    <div class="actions">
      ${isSent ? `<button class="btn sm ghost" data-mact="reset_one" data-id="${m.id}" title="Marcar como pendente">${ICONS.refresh} Reutilizar</button>` : ""}
      <button class="btn sm" data-mact="remix" data-id="${m.id}" title="Gera um novo hash exclusivo">${ICONS.refresh} Re-hash</button>
      <button class="btn sm" data-mact="preview" data-id="${m.id}">${ICONS.eye} Ver</button>
      <button class="btn sm danger" data-mact="del" data-id="${m.id}">${ICONS.trash}</button>
    </div>
  </div>`;
}

function bindMediaActions(medias) {
  $$("[data-mact]", $("#media-list-wrap")).forEach((b) => {
    b.onclick = async () => {
      const id = +b.dataset.id;
      const act = b.dataset.mact;
      const m = medias.find((item) => item.id === id);

      try {
        if (act === "del") {
          const ok = await confirmDialog(`Deseja excluir "${m?.original_name}"?`);
          if (!ok) return;
          await api(`/api/media/${id}`, { method: "DELETE" });
          toast("Mídia excluída.", "ok");
          refreshMediaList();
        } else if (act === "reset_one") {
          await api(`/api/media/${id}/reset-status`, { method: "POST" });
          toast(`"${m?.original_name}" marcada como pendente.`, "ok");
          refreshMediaList();
        } else if (act === "remix") {
          const res = await api(`/api/media/${id}/remix`, { method: "POST" });
          toast(`Novo hash gerado: ${shortHash(res.active_sha256)}`, "ok");
          refreshMediaList();
        } else if (act === "preview") {
          const fileUrl = `/api/media/${id}/file?token=${state.token}`;
          const content = m.kind === "video"
            ? `<video src="${fileUrl}" controls style="max-width:100%;max-height:60vh;border-radius:var(--radius)"></video>`
            : `<img src="${fileUrl}" style="max-width:100%;max-height:60vh;border-radius:var(--radius);object-fit:contain">`;
          openModal(`
            <h3>${ICONS.eye} ${esc(m.original_name)}</h3>
            <div class="mbody" style="text-align:center">${content}</div>`,
            [{ label: "Fechar", cls: "primary", onClick: () => {} }]
          );
        }
      } catch (err) {
        toast(err.message, "err");
      }
    };
  });
}

async function uploadFiles(files) {
  if (!files || !files.length) return;
  const fileList = Array.from(files);
  const totalFiles = fileList.length;
  const targetAccId = $("#media-upload-target-account")?.value || null;

  let uploadedCount = 0;
  const totalBytes = fileList.reduce((acc, f) => acc + f.size, 0);

  const BATCH_SIZE = 4;
  toast(`Enviando ${totalFiles} arquivo(s) com limpeza de metadados...`, "");

  for (let i = 0; i < totalFiles; i += BATCH_SIZE) {
    const batch = fileList.slice(i, i + BATCH_SIZE);
    const fd = new FormData();
    batch.forEach((f) => fd.append("files", f));
    if (targetAccId) fd.append("account_id", targetAccId);

    try {
      await api("/api/media/upload", { method: "POST", form: fd });
      uploadedCount += batch.length;
      refreshMediaList();
    } catch (err) {
      toast(`Erro: ${err.message}`, "err");
    }
  }

  toast(`${uploadedCount} mídias adicionadas com sucesso!`, "ok");
  refreshMediaList();
}

/* ==========================================================================
   VIEW 4: AGENDAMENTOS (ROTAÇÃO INTELIGENTE)
   ========================================================================== */
async function initAgendamentos() {
  const c = $("#content");
  let [accounts, medias] = [[], []];
  try {
    [accounts, medias] = await Promise.all([api("/api/accounts"), api("/api/media")]);
  } catch {}

  c.innerHTML = `
    <div class="card panel-form" style="margin-bottom:18px">
      <div class="section-title" style="margin-top:0">Criar Novo Agendamento Automático</div>
      <form id="sched-form" onsubmit="return false;">
        <div class="row">
          <label class="field"><span>Nome do Agendamento</span><input class="input" id="sched-name" name="name" placeholder="Ex: Postagens Diárias" value="Postagens Diárias" required></label>
          <label class="field"><span>Conta do Instagram</span>
            <select class="input" id="sched-account-id" name="account_id" required>
              ${accounts.map((a) => `<option value="${a.id}">@${esc(a.ig_username)} (${esc(a.name)})</option>`).join("")}
            </select>
          </label>
        </div>

        <div class="row">
          <label class="field"><span>Modo</span>
            <select class="input" name="mode" id="sched-mode">
              <option value="times">Horários Fixos do Dia (HH:MM)</option>
              <option value="interval">Intervalo Contínuo (a cada X horas)</option>
              <option value="once">Disparo Único (Data e Hora)</option>
            </select>
          </label>

          <label class="field"><span>Tipo de Postagem</span>
            <select class="input" name="target_type" id="sched-target-type">
              <option value="reel" selected>Reels (Vídeo — Qualidade Máxima 1080p/4K)</option>
              <option value="trial_reel">Reels de Teste (Trial Reel — Testar com Não-Seguidores)</option>
              <option value="feed">Feed (Foto — Qualidade Original)</option>
              <option value="story">Story (9:16 Full Screen)</option>
            </select>
          </label>
        </div>

        <div class="row">
          <label class="field" id="f-times">
            <span>Horários do Dia (separados por vírgula)</span>
            <input class="input" id="sched-times-input" name="times" placeholder="09:00, 14:30, 20:00" value="09:00, 18:30">
          </label>
          <label class="field" id="f-interval" style="display:none">
            <span>Intervalo em Horas</span>
            <input class="input" id="sched-interval-input" type="number" name="interval_hours" value="12" min="0.02" step="0.5">
          </label>
          <label class="field" id="f-once" style="display:none">
            <span>Data e Hora</span>
            <input class="input" id="sched-once-input" type="datetime-local" name="scheduled_at">
          </label>
        </div>

        <div class="row">
          <label class="field"><span>Legenda</span><textarea class="input" id="sched-caption" name="caption" placeholder="Legenda e hashtags..."></textarea></label>
          <div style="flex:1">
            <label class="field"><span>Marcar Perfis (@usertags)</span><input class="input" id="sched-usertags" name="usertags" placeholder="@perfil1, @perfil2"></label>
            <label class="field"><span>Mídia</span>
              <select class="input" id="sched-media-id" name="media_id">
                <option value="">Automático (Rotacionar mídias menos usadas)</option>
                ${medias.map((m) => `<option value="${m.id}">${esc(m.original_name)}</option>`).join("")}
              </select>
            </label>
          </div>
        </div>

        <button class="btn primary" id="btn-save-sched" type="button" style="margin-top:12px">${ICONS.plus} Salvar Agendamento</button>
      </form>
    </div>

    <div id="schedules-list-wrap"></div>
  `;

  bindScheduleForm();
  refreshSchedulesList();
  startPoll(refreshSchedulesList, VIEWS.agendamentos.poll);
}

function bindScheduleForm() {
  const f = $("#sched-form");
  const modeSel = $("#sched-mode");
  const btnSave = $("#btn-save-sched");
  if (!f || !modeSel || !btnSave) return;

  modeSel.onchange = () => {
    $("#f-times").style.display = modeSel.value === "times" ? "" : "none";
    $("#f-interval").style.display = modeSel.value === "interval" ? "" : "none";
    $("#f-once").style.display = modeSel.value === "once" ? "" : "none";
  };

  btnSave.onclick = async () => {
    const name = ($("#sched-name")?.value || "").trim();
    const account_id = +$("#sched-account-id")?.value;
    if (!name || !account_id) { toast("Preencha nome e conta.", "err"); return; }
    const mode = modeSel.value;
    const target_type = $("#sched-target-type")?.value || "reel";
    let times = null;
    let interval_hours = null;
    let scheduled_at = null;

    if (mode === "times") {
      times = ($("#sched-times-input")?.value || "").split(",").map((t) => t.trim()).filter(Boolean);
    } else if (mode === "interval") {
      interval_hours = +($("#sched-interval-input")?.value || 12);
    } else if (mode === "once") {
      scheduled_at = $("#sched-once-input")?.value;
    }

    const caption = $("#sched-caption")?.value || "";
    const usertags = $("#sched-usertags")?.value.trim() || null;
    const media_id = $("#sched-media-id")?.value ? +$("#sched-media-id").value : null;

    btnSave.disabled = true;
    try {
      await api("/api/schedules", {
        method: "POST",
        body: { account_id, name, mode, target_type, interval_hours, times, scheduled_at, caption, usertags, jitter_min: 0, media_id, enabled: true },
      });
      toast("Agendamento salvo!", "ok");
      refreshSchedulesList();
    } catch (err) {
      toast(err.message, "err");
    } finally {
      btnSave.disabled = false;
    }
  };
}

async function refreshSchedulesList() {
  const wrap = $("#schedules-list-wrap");
  if (!wrap) return;
  let schedules = [];
  try { schedules = await api("/api/schedules"); } catch { return; }

  if (!schedules.length) {
    wrap.innerHTML = `<div class="empty"><div class="empty-ico">${ICONS.calendar}</div>Nenhum agendamento cadastrado.</div>`;
    return;
  }

  wrap.innerHTML = `
    <div class="card table-wrap"><table>
      <tr>
        <th>Nome</th>
        <th>Conta</th>
        <th>Tipo</th>
        <th>Gatilho</th>
        <th>Próximo Disparo</th>
        <th>Status</th>
        <th style="text-align:right">Ações</th>
      </tr>
      ${schedules.map((s) => `<tr>
        <td><strong>${esc(s.name)}</strong></td>
        <td><span class="badge blue"><span class="dot"></span>@${esc(s.account_name)}</span></td>
        <td><span class="badge gray">${s.target_type === "story" ? "Story" : (s.target_type === "feed" ? "Feed" : "Reels")}</span></td>
        <td>${s.mode === "interval" ? `A cada ${s.interval_hours}h` : (s.times || []).join(", ")}</td>
        <td>${s.next_run_at ? fmtDate(s.next_run_at) : "—"}</td>
        <td>${s.enabled ? `<span class="badge green"><span class="dot"></span>Ativo</span>` : `<span class="badge gray">Pausado</span>`}</td>
        <td style="text-align:right;white-space:nowrap">
          <button class="btn sm primary" data-sact="run" data-id="${s.id}">${ICONS.play} Disparar</button>
          <button class="btn sm danger" data-sact="del" data-id="${s.id}">${ICONS.trash}</button>
        </td>
      </tr>`).join("")}
    </table></div>`;

  $$("[data-sact]", wrap).forEach((b) => {
    b.onclick = async () => {
      const id = +b.dataset.id;
      const act = b.dataset.sact;
      if (act === "del") {
        if (!await confirmDialog("Deseja remover este agendamento?")) return;
        await api(`/api/schedules/${id}`, { method: "DELETE" });
        toast("Agendamento removido.", "ok");
        refreshSchedulesList();
      } else if (act === "run") {
        await api(`/api/schedules/${id}/run-now`, { method: "POST" });
        toast("Post disparado! Acompanhe em Publicações.", "ok");
      }
    };
  });
}

/* ==========================================================================
   VIEW 5: MATURAÇÃO DE CONTAS COM IA (ANTI-QUEDA INTELIGENTE & PAÍSES)
   ========================================================================== */
async function initAquecimento() {
  const c = $("#content");
  let accounts = [];
  try { accounts = await api("/api/accounts"); } catch {}

  c.innerHTML = `
    <div class="card panel-form" style="margin-bottom:18px">
      <div class="section-title" style="margin-top:0">${ICONS.shield} Aquecer Conta 24/7 (Maturação por País com IA)</div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:14px;line-height:1.5">
        O robô autônomo opera <strong>24 horas por dia em ciclos humanos</strong> durante 3 dias: abre o app, assiste Reels regionais com 10 a 25s de retenção, aplica curtidas espaçadas, fecha o Instagram, descansa e reabre no próximo ciclo para treinar o algoritmo da Meta a entregar suas futuras postagens para o país escolhido.
      </div>

      <form id="warmup-form" onsubmit="return false;">
        <div class="row">
          <label class="field">
            <span>Conta a ser Aquecida</span>
            <select class="input" id="warmup-account-id" required>
              ${accounts.map((a) => `<option value="${a.id}">@${esc(a.ig_username)} (${esc(a.name)})</option>`).join("")}
            </select>
          </label>

          <label class="field">
            <span>País Alvo de Entrega (Segmentação de Algoritmo)</span>
            <select class="input" id="warmup-country" required>
              <option value="BR" selected>Brasil (BR) — Conteúdos e Criadores Nacionais</option>
              <option value="US">Estados Unidos (US) — Viral & Trending USA</option>
              <option value="PT">Portugal (PT) — Lisboa / Porto / Portugal</option>
              <option value="ES">Espanha (ES) — Madrid / Barcelona</option>
              <option value="UK">Reino Unido (UK) — Londres / Manchester</option>
              <option value="MX">México (MX) — CDMX / México</option>
              <option value="FR">França (FR) — Paris / França</option>
              <option value="DE">Alemanha (DE) — Berlim / Alemanha</option>
              <option value="IT">Itália (IT) — Roma / Milão</option>
              <option value="AR">Argentina (AR) — Buenos Aires</option>
              <option value="GLOBAL">Global (Internacional) — Recomendações Globais</option>
            </select>
          </label>
        </div>

        <div class="row">
          <label class="field">
            <span>Idade / Tempo de Criação da Conta</span>
            <select class="input" id="warmup-account-age">
              <option value="hoje" selected>Conta Criada Hoje (Recém-Criada / 1º Dia) — Ultra-Cauteloso</option>
              <option value="recente">Conta Nova (2 a 7 Dias) — Maturação Progressiva</option>
              <option value="madura">Conta Madura (+7 Dias) — Aquecimento de Algoritmo</option>
            </select>
          </label>

          <label class="field">
            <span>Duração do Ciclo Autônomo</span>
            <select class="input" id="warmup-days">
              <option value="3" selected>3 Dias (Ciclo Completo 24/7 — Recomendado)</option>
              <option value="2">2 Dias (Ciclo Acelerado)</option>
              <option value="1">1 Dia (Aquecimento Rápido)</option>
            </select>
          </label>
        </div>

        <div style="padding:10px 12px;background:var(--accent-surface);border:1px solid rgba(99,102,241,0.25);border-radius:var(--radius-sm);margin:8px 0 14px">
          <div style="font-size:11.5px;color:var(--text-primary);font-weight:600" id="warmup-country-desc">
            Segmentação Ativa: O robô consumirá Reels e hashtags de criadores do Brasil para que suas futuras postagens sejam entregues prioritariamente ao público brasileiro.
          </div>
        </div>

        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button class="btn primary" id="btn-start-warmup" type="button">${ICONS.flame} Iniciar Aquecimento 24/7 (3 Dias)</button>
        </div>
      </form>
    </div>
    <div id="warmup-live-wrap"></div>
  `;

  $("#warmup-country").onchange = (e) => {
    const val = e.target.value;
    const countryNames = {
      BR: "do Brasil", US: "dos Estados Unidos", PT: "de Portugal",
      ES: "da Espanha", UK: "do Reino Unido", MX: "do México",
      FR: "da França", DE: "da Alemanha", IT: "da Itália",
      AR: "da Argentina", GLOBAL: "Globais Internacionais"
    };
    const cName = countryNames[val] || "do país selecionado";
    $("#warmup-country-desc").textContent = `Segmentação Ativa: O robô consumirá Reels e hashtags de criadores ${cName} para que suas futuras postagens sejam entregues prioritariamente a esse público.`;
  };

  $("#warmup-days").onchange = (e) => {
    const d = e.target.value;
    const btn = $("#btn-start-warmup");
    if (btn) btn.innerHTML = `${ICONS.flame} Iniciar Aquecimento 24/7 (${d} ${d === "1" ? "Dia" : "Dias"})`;
  };

  $("#btn-start-warmup").onclick = async () => {
    const account_id = +$("#warmup-account-id")?.value;
    const account_age = $("#warmup-account-age")?.value || "hoje";
    const target_country = $("#warmup-country")?.value || "BR";
    const total_days = +($("#warmup-days")?.value || 3);

    if (!account_id) { toast("Selecione uma conta.", "err"); return; }
    const btn = $("#btn-start-warmup");
    btn.disabled = true;
    btn.innerHTML = `${ICONS.refresh} Iniciando Robô 24/7...`;
    try {
      await api("/api/warmup/start", {
        method: "POST",
        body: { account_id, account_age, target_country, total_days, intensity: "medio" }
      });
      toast("Aquecimento 24/7 iniciado com sucesso!", "ok");
      refreshWarmupView();
    } catch (err) {
      toast(err.message, "err");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `${ICONS.flame} Iniciar Aquecimento 24/7 (${total_days} ${total_days === 1 ? "Dia" : "Dias"})`;
    }
  };

  refreshWarmupView();
  startPoll(refreshWarmupView, VIEWS.aquecimento.poll);
}

async function refreshWarmupView() {
  const liveWrap = $("#warmup-live-wrap");
  if (!liveWrap) return;
  let sessions = [];
  try { sessions = await api("/api/warmup/sessions"); } catch { return; }

  if (!sessions.length) {
    liveWrap.innerHTML = "";
    return;
  }

  // Garante estritamente 1 único card por conta (sem duplicatas)
  const uniqueSessions = [];
  const seenAccs = new Set();
  for (const s of sessions) {
    if (!seenAccs.has(s.account_id)) {
      seenAccs.add(s.account_id);
      uniqueSessions.push(s);
    }
  }

  const countryNames = {
    BR: "Brasil", US: "Estados Unidos", PT: "Portugal", ES: "Espanha",
    UK: "Reino Unido", MX: "México", FR: "França", DE: "Alemanha",
    IT: "Itália", AR: "Argentina", GLOBAL: "Global"
  };

  const consoles = $$(".warmup-console", liveWrap);
  const scrollMap = {};
  consoles.forEach((c) => {
    const id = c.dataset.consoleId;
    if (id) {
      scrollMap[id] = {
        top: c.scrollTop,
        wasAtBottom: (c.scrollHeight - c.scrollTop - c.clientHeight < 50),
      };
    }
  });

  liveWrap.innerHTML = uniqueSessions.map((s) => {
    const isRunning = s.status === "em_andamento";
    const isDone = s.status === "concluido";
    const isPaused = s.status === "interrompido" || !isRunning;
    const cKey = (s.target_country || "BR").toUpperCase();
    const cName = countryNames[cKey] || s.target_country || "Brasil";
    const currentDay = s.current_day || 1;
    const totalDays = s.total_days || 3;
    const progressPct = isDone ? 100 : Math.min(99, Math.round(((currentDay - 1) / totalDays) * 100) + Math.min(30, (s.views_done % 15) * 2));

    return `
      <div class="card warmup-live-card" style="border-left:4px solid ${isDone ? 'var(--green)' : (isRunning ? 'var(--accent)' : 'var(--border)')};margin-bottom:18px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
          <div>
            <strong style="font-size:15px;color:var(--text-primary)">@${esc(s.account_name)}</strong>
            <span style="color:var(--text-secondary);font-size:12px;margin-left:6px">· Segmentação: <strong>${cName}</strong></span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <div>
              ${isDone ? `<span class="badge green"><span class="dot"></span>Pronta para Postar (Blindada)</span>` : (
                isRunning ? `<span class="badge blue"><span class="dot pulse-dot"></span>Robô 24/7 Ativo (Dia ${currentDay} de ${totalDays})</span>` :
                `<span class="badge gray"><span class="dot"></span>Pausado pelo Usuário</span>`
              )}
            </div>
            ${isRunning ? `
              <button class="btn sm danger btn-pause-warmup" data-stop-acc="${s.account_id}">${ICONS.pause} Pausar</button>
            ` : `
              <button class="btn sm primary btn-resume-warmup" data-resume-acc="${s.account_id}" data-country="${s.target_country}" data-days="${s.total_days}" data-age="${s.account_age}">
                ${ICONS.play} Retomar
              </button>
            `}
          </div>
        </div>

        <!-- Barra de Progresso dos 3 Dias -->
        <div style="margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;color:var(--text-muted);margin-bottom:4px">
            <span>Progresso da Maturação: <strong>Dia ${currentDay} de ${totalDays} (24h/dia)</strong></span>
            <span style="font-weight:700;color:var(--text-primary)">${progressPct}%</span>
          </div>
          <div style="background:var(--bg-card-sub);border:1px solid var(--border);border-radius:8px;height:8px;overflow:hidden">
            <div style="background:var(--accent-gradient);height:100%;width:${progressPct}%;transition:width 0.3s ease"></div>
          </div>
        </div>

        <div class="grid-stats" style="margin-bottom:12px">
          <div class="stat-card" style="padding:10px 14px"><div class="stat-header"><span>Reels Assistidos (${cName})</span></div><div class="stat-value" style="font-size:20px">${s.views_done}</div></div>
          <div class="stat-card" style="padding:10px 14px"><div class="stat-header"><span>Curtidas Orgânicas</span></div><div class="stat-value" style="font-size:20px">${s.likes_done}</div></div>
          <div class="stat-card" style="padding:10px 14px"><div class="stat-header"><span>Ciclos Executados</span></div><div class="stat-value" style="font-size:20px">${s.cycles_completed || 0}</div></div>
        </div>

        <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.6px;font-weight:700;margin-bottom:6px">
          Histórico de Ações do Robô em Tempo Real
        </div>
        <div class="warmup-console" data-console-id="${s.id}">${(s.logs || []).map((l) => `<div class="warmup-log-item"><span class="warmup-log-time">[${esc(l.time)}]</span><span class="warmup-log-text">${esc(l.text)}</span></div>`).join("")}</div>
      </div>
    `;
  }).join("");

  $$(".warmup-console", liveWrap).forEach((c) => {
    const id = c.dataset.consoleId;
    if (scrollMap[id]) {
      if (scrollMap[id].wasAtBottom) {
        c.scrollTop = c.scrollHeight;
      } else {
        c.scrollTop = scrollMap[id].top;
      }
    } else {
      c.scrollTop = c.scrollHeight;
    }
  });

  $$("[data-stop-acc]", liveWrap).forEach((btn) => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const accId = +btn.dataset.stopAcc;
      btn.disabled = true;
      btn.innerHTML = `${ICONS.refresh} Pausando...`;
      try {
        await api(`/api/warmup/stop/${accId}`, { method: "POST" });
        toast("Aquecimento pausado com sucesso!", "ok");
        await refreshWarmupView();
      } catch (err) {
        toast(err.message, "err");
        btn.disabled = false;
        btn.innerHTML = `${ICONS.pause} Pausar`;
      }
    };
  });

  $$("[data-resume-acc]", liveWrap).forEach((btn) => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const accId = +btn.dataset.resumeAcc;
      const target_country = btn.dataset.country || "BR";
      const total_days = +(btn.dataset.days || 3);
      const account_age = btn.dataset.age || "hoje";
      btn.disabled = true;
      btn.innerHTML = `${ICONS.refresh} Retomando...`;
      try {
        await api("/api/warmup/start", {
          method: "POST",
          body: { account_id: accId, account_age, target_country, total_days, intensity: "medio" }
        });
        toast("Aquecimento retomado com sucesso!", "ok");
        await refreshWarmupView();
      } catch (err) {
        toast(err.message, "err");
        btn.disabled = false;
        btn.innerHTML = `${ICONS.play} Retomar`;
      }
    };
  });
}

/* ==========================================================================
   VIEW: GERADOR DE E-MAIL TEMPORÁRIO (COMPATÍVEL COM INSTAGRAM)
   ========================================================================== */
const tempMailState = {
  email: store.get("instaflow_temp_email") || "",
  token: store.get("instaflow_temp_token") || "",
  provider: store.get("instaflow_temp_provider") || "mailtm",
  messages: [],
  latestCode: null,
};

async function initGeradorEmail() {
  const c = $("#content");

  c.innerHTML = `
    <div class="card panel-form" style="margin-bottom:18px">
      <div class="section-title" style="margin-top:0">${ICONS.mail} Gerador de E-mail para Instagram</div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:14px;line-height:1.5">
        Crie caixas de entrada temporárias com domínios limpos e ativos aceitos pelo Instagram. O InstaFlow monitora a caixa e <strong>extrai automaticamente o código de 6 dígitos</strong> recebido.
      </div>

      <div class="row" style="margin-bottom:12px">
        <label class="field">
          <span>Provedor de Domínio</span>
          <select class="input" id="temp-mail-provider">
            <option value="mailtm" ${tempMailState.provider === "mailtm" ? "selected" : ""}>Mail.tm (Domínio Limpo — Alta compatibilidade)</option>
            <option value="guerrilla" ${tempMailState.provider === "guerrilla" ? "selected" : ""}>GuerrillaMail (Alternativo / SharkLasers)</option>
          </select>
        </label>
        <label class="field">
          <span>Prefixo Personalizado (Opcional)</span>
          <input class="input" id="temp-mail-prefix" placeholder="Ex: conta.nova, instagram.perfil">
        </label>
      </div>

      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn primary" id="btn-generate-temp-mail" type="button">${ICONS.zap} Gerar Novo E-mail Compatível</button>
      </div>
    </div>

    <!-- Card do E-mail Ativo & Código Detectado -->
    <div id="temp-mail-active-card-wrap"></div>

    <!-- Caixa de Entrada de Mensagens -->
    <div class="section-title" style="margin:20px 0 10px;display:flex;justify-content:space-between;align-items:center">
      <span>${ICONS.inbox} Mensagens Recebidas em Tempo Real</span>
      <button class="btn sm ghost" id="btn-refresh-inbox">${ICONS.refresh} Atualizar Caixa</button>
    </div>
    <div id="temp-mail-inbox-wrap"></div>
  `;

  $("#btn-generate-temp-mail").onclick = async () => {
    const provider = $("#temp-mail-provider")?.value || "mailtm";
    const prefix = ($("#temp-mail-prefix")?.value || "").trim() || null;
    const btn = $("#btn-generate-temp-mail");
    btn.disabled = true;
    btn.innerHTML = `${ICONS.refresh} Gerando e-mail...`;
    try {
      const res = await api("/api/temp-email/generate", { method: "POST", body: { provider, prefix } });
      tempMailState.email = res.email;
      tempMailState.token = res.token;
      tempMailState.provider = res.provider;
      tempMailState.latestCode = null;
      store.set("instaflow_temp_email", res.email);
      store.set("instaflow_temp_token", res.token);
      store.set("instaflow_temp_provider", res.provider);
      toast(`Novo e-mail gerado: ${res.email}`, "ok");
      renderActiveTempMailCard();
      refreshTempMailInbox();
    } catch (err) {
      toast(err.message, "err");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `${ICONS.zap} Gerar Novo E-mail Compatível`;
    }
  };

  $("#btn-refresh-inbox").onclick = () => {
    refreshTempMailInbox(true);
  };

  renderActiveTempMailCard();
  if (tempMailState.email && tempMailState.token) {
    refreshTempMailInbox();
    startPoll(() => refreshTempMailInbox(false), VIEWS.gerador_email.poll);
  } else {
    $("#btn-generate-temp-mail").click();
  }
}

function renderActiveTempMailCard() {
  const wrap = $("#temp-mail-active-card-wrap");
  if (!wrap) return;

  if (!tempMailState.email) {
    wrap.innerHTML = "";
    return;
  }

  wrap.innerHTML = `
    <div class="card" style="border-left:4px solid var(--accent);margin-bottom:18px;background:var(--bg-card)">
      <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.6px;font-weight:700;margin-bottom:6px">
        E-mail Ativo para Cadastro / Verificação no Instagram
      </div>

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
        <input class="input mono" id="active-temp-email-input" value="${esc(tempMailState.email)}" readonly style="font-size:15px;font-weight:700;color:var(--accent);max-width:420px;background:var(--bg-card-sub);cursor:pointer">
        <button class="btn primary" id="btn-copy-temp-email" type="button">${ICONS.copy} Copiar E-mail</button>
      </div>

      ${tempMailState.latestCode ? `
        <div style="margin-top:14px;padding:14px 16px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.4);border-radius:var(--radius);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
          <div>
            <div style="font-size:11.5px;color:var(--green);font-weight:700;display:flex;align-items:center;gap:6px">
              <span class="dot pulse-dot" style="background:var(--green)"></span>
              Código do Instagram Detectado com Sucesso!
            </div>
            <div style="font-size:26px;font-weight:900;letter-spacing:4px;color:var(--text-primary);margin-top:2px;font-family:ui-monospace,monospace">
              ${esc(tempMailState.latestCode)}
            </div>
          </div>
          <button class="btn sm primary" id="btn-copy-detected-code" style="background:var(--green);border-color:transparent">${ICONS.copy} Copiar Código</button>
        </div>
      ` : `
        <div style="margin-top:10px;font-size:11.5px;color:var(--text-muted);display:flex;align-items:center;gap:6px">
          <span class="dot pulse-dot" style="background:var(--blue)"></span>
          Aguardando recebimento do código de confirmação do Instagram... (Atualização automática a cada 3s)
        </div>
      `}
    </div>
  `;

  $("#btn-copy-temp-email").onclick = () => {
    navigator.clipboard.writeText(tempMailState.email).then(() => {
      const b = $("#btn-copy-temp-email");
      b.innerHTML = `${ICONS.check} Copiado!`;
      toast("E-mail copiado para a área de transferência!", "ok");
      setTimeout(() => { if (b) b.innerHTML = `${ICONS.copy} Copiar E-mail`; }, 2000);
    });
  };

  $("#active-temp-email-input").onclick = () => {
    $("#btn-copy-temp-email").click();
  };

  const btnCopyCode = $("#btn-copy-detected-code");
  if (btnCopyCode) {
    btnCopyCode.onclick = () => {
      navigator.clipboard.writeText(tempMailState.latestCode).then(() => {
        btnCopyCode.innerHTML = `${ICONS.check} Código Copiado!`;
        toast(`Código ${tempMailState.latestCode} copiado! Cole no Instagram.`, "ok");
        setTimeout(() => { if (btnCopyCode) btnCopyCode.innerHTML = `${ICONS.copy} Copiar Código`; }, 2000);
      });
    };
  }
}

async function refreshTempMailInbox(manual = false) {
  const wrap = $("#temp-mail-inbox-wrap");
  if (!wrap || !tempMailState.token) return;

  try {
    const res = await api(`/api/temp-email/inbox?provider=${tempMailState.provider}&token=${encodeURIComponent(tempMailState.token)}`);
    const msgs = res.messages || [];
    const prevCode = tempMailState.latestCode;
    tempMailState.messages = msgs;
    tempMailState.latestCode = res.latest_code;

    if (res.latest_code && res.latest_code !== prevCode) {
      toast(`Código do Instagram recebido: ${res.latest_code}!`, "ok");
      renderActiveTempMailCard();
    }

    if (!msgs.length) {
      wrap.innerHTML = `<div class="empty"><div class="empty-ico">${ICONS.mail}</div>Nenhum e-mail recebido ainda. Cole o endereço acima no Instagram e envie o código.</div>`;
      if (manual) toast("Caixa de entrada atualizada. Nenhuma nova mensagem.", "");
      return;
    }

    wrap.innerHTML = `
      <div class="card table-wrap"><table>
        <tr>
          <th>Remetente</th>
          <th>Assunto</th>
          <th>Código</th>
          <th>Horário</th>
          <th style="text-align:right">Ação</th>
        </tr>
        ${msgs.map((m) => `
          <tr style="${m.is_instagram ? 'background:rgba(99,102,241,0.06)' : ''}">
            <td>
              <div style="font-weight:700;color:var(--text-primary)">${esc(m.from)}</div>
              ${m.is_instagram ? `<span class="badge green sm" style="font-size:9.5px;padding:1px 6px">Instagram Oficial</span>` : ""}
            </td>
            <td><strong>${esc(m.subject)}</strong></td>
            <td>
              ${m.code_extracted ? `<span class="badge green" style="font-size:12px;font-weight:800;letter-spacing:1px">${esc(m.code_extracted)}</span>` : `<span class="badge gray">—</span>`}
            </td>
            <td style="color:var(--text-muted);font-size:11px">${fmtDate(m.created_at)}</td>
            <td style="text-align:right">
              <button class="btn sm" data-temp-msg-id="${m.id}">${ICONS.eye} Ler E-mail</button>
            </td>
          </tr>
        `).join("")}
      </table></div>
    `;

    $$("[data-temp-msg-id]", wrap).forEach((b) => {
      b.onclick = async () => {
        const msgId = b.dataset.tempMsgId;
        b.disabled = true;
        try {
          const detail = await api(`/api/temp-email/message/${msgId}?provider=${tempMailState.provider}&token=${encodeURIComponent(tempMailState.token)}`);
          openModal(`
            <h3>${ICONS.mail} ${esc(detail.subject)}</h3>
            <div style="font-size:11.5px;color:var(--text-muted);margin-bottom:12px">
              De: <strong>${esc(detail.from)}</strong> · ${fmtDate(detail.created_at)}
            </div>
            ${detail.code_extracted ? `
              <div style="padding:10px 14px;background:rgba(16,185,129,0.15);border-radius:var(--radius-sm);margin-bottom:12px;display:flex;justify-content:space-between;align-items:center">
                <span>Código Extraído: <strong style="font-size:16px;letter-spacing:2px">${esc(detail.code_extracted)}</strong></span>
                <button class="btn sm primary" onclick="navigator.clipboard.writeText('${detail.code_extracted}');toast('Código copiado!','ok')">${ICONS.copy} Copiar</button>
              </div>
            ` : ""}
            <div class="mbody" style="background:var(--bg-card-sub);padding:14px;border-radius:var(--radius-sm);max-height:50vh;overflow-y:auto;font-size:13px;line-height:1.6;border:1px solid var(--border)">
              ${detail.html ? detail.html : `<pre style="white-space:pre-wrap;font-family:inherit">${esc(detail.text)}</pre>`}
            </div>
          `, [{ label: "Fechar", cls: "primary", onClick: () => {} }]);
        } catch (err) {
          toast(err.message, "err");
        } finally {
          b.disabled = false;
        }
      };
    });

  } catch (err) {
    if (manual) toast(err.message, "err");
  }
}

/* ==========================================================================
   VIEW 6: PUBLICAÇÕES (HISTÓRICO E LOGS)
   ========================================================================== */
function initPublicacoes() {
  const c = $("#content");
  c.innerHTML = `<div id="logs-list-wrap"></div>`;
  refreshLogsList();
  startPoll(refreshLogsList, VIEWS.publicacoes.poll);
}

async function refreshLogsList() {
  const wrap = $("#logs-list-wrap");
  if (!wrap) return;
  let logs = [];
  try { logs = await api("/api/logs?limit=100"); } catch { return; }

  if (!logs.length) {
    wrap.innerHTML = `<div class="empty"><div class="empty-ico">${ICONS.publish}</div>Nenhuma publicação executada ainda.</div>`;
    return;
  }

    wrap.innerHTML = `
      <div class="card table-wrap"><table>
        <tr><th>Data</th><th>Conta</th><th>Mídia</th><th>Tipo</th><th>SHA-256 (Antes → Depois)</th><th>Status</th></tr>
        ${logs.map((l) => `<tr>
          <td>${fmtDate(l.created_at)}</td>
          <td><span class="badge blue"><span class="dot"></span>@${esc(l.account_name)}</span></td>
          <td class="mono">${esc(l.media_name || "—")}</td>
          <td><span class="badge gray">${formatActionName(l.action)}</span></td>
          <td><span class="mono">${shortHash(l.hash_before)} → <strong style="color:var(--accent)">${shortHash(l.hash_after)}</strong></span></td>
          <td>${statusBadge(l.status)}</td>
        </tr>`).join("")}
      </table></div>`;
}

/* ==========================================================================
   VIEW 7: CONFIGURAÇÕES (TROCA DE SENHA COM CÓDIGO NO E-MAIL)
   ========================================================================== */
async function initConfiguracoes() {
  const c = $("#content");
  let settings = null;
  try { settings = await api("/api/auth/settings"); } catch (err) { return; }

  const currentTheme = state.theme || "auto";

  c.innerHTML = `
    <div class="settings-grid">
      <!-- Aparência -->
      <div class="card">
        <div class="section-title" style="margin-top:0">${ICONS.sun} Aparência & Tema</div>
        <div class="theme-options-grid">
          <div class="theme-option-card ${currentTheme === "claro" ? "active" : ""}" data-theme-choice="claro">
            <div class="theme-preview-box theme-preview-light"></div>
            <div class="theme-option-name">Claro</div>
          </div>
          <div class="theme-option-card ${currentTheme === "escuro" ? "active" : ""}" data-theme-choice="escuro">
            <div class="theme-preview-box theme-preview-dark"></div>
            <div class="theme-option-name">Escuro</div>
          </div>
          <div class="theme-option-card ${currentTheme === "auto" ? "active" : ""}" data-theme-choice="auto">
            <div class="theme-preview-box theme-preview-auto"></div>
            <div class="theme-option-name">Auto (Ciclo Solar)</div>
          </div>
        </div>
      </div>

      <!-- Dados da Conta -->
      <div class="card">
        <div class="section-title" style="margin-top:0">${ICONS.user} Dados da Conta</div>
        <div style="font-size:12.5px;color:var(--text-secondary);margin-bottom:10px">
          E-mail de Acesso: <strong>${esc(settings.email)}</strong>
        </div>
        <div style="font-size:11.5px;color:var(--green)">${ICONS.check} Conta Verificada e Protegida</div>
      </div>

      <!-- Trocar Senha com Verificação por E-mail -->
      <div class="card" style="grid-column: 1 / -1">
        <div class="section-title" style="margin-top:0">${ICONS.key} Redefinir Senha de Acesso (Confirmação por E-mail)</div>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">
          Para alterar sua senha, clique no botão abaixo para receber um código de segurança de 6 dígitos no seu e-mail cadastrado (<strong>${esc(settings.email)}</strong>).
        </div>

        <div style="margin-bottom:12px">
          <button class="btn sm" id="btn-request-pwd-code">${ICONS.refresh} Solicitar Código no E-mail</button>
        </div>

        <div class="row">
          <input class="input" id="cfg-pwd-code-input" placeholder="Código de 6 Dígitos" style="font-size:12px">
          <input class="input" type="password" id="cfg-new-pwd-input" placeholder="Nova Senha (Mínimo 4 caracteres)" style="font-size:12px">
          <button class="btn primary sm" id="btn-submit-new-pwd">${ICONS.check} Confirmar Nova Senha</button>
        </div>
      </div>
    </div>
  `;

  // Bind Seletor de Tema
  $$(".theme-option-card", c).forEach((card) => {
    card.onclick = async () => {
      const choice = card.dataset.themeChoice;
      $$(".theme-option-card", c).forEach((x) => x.classList.toggle("active", x === card));
      applyTheme(choice);
      try {
        await api("/api/auth/theme", { method: "POST", body: { theme: choice } });
        toast(`Tema ${choice.toUpperCase()} aplicado!`, "ok");
      } catch {}
    };
  });

  // Solicitar Código de Senha por E-mail
  $("#btn-request-pwd-code").onclick = async () => {
    const btn = $("#btn-request-pwd-code");
    btn.disabled = true;
    btn.innerHTML = `${ICONS.refresh} Enviando...`;
    try {
      const res = await api("/api/auth/request-password-code", { method: "POST" });
      $("#cfg-pwd-code-input").value = res.code || "";
      $("#cfg-pwd-code-input").focus();
      if (!res.smtp_configured) {
        toast(`Código de segurança: ${res.code}`, "ok");
      } else {
        toast("Código enviado para seu e-mail cadastrado!", "ok");
      }
    } catch (err) {
      toast(err.message, "err");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `${ICONS.refresh} Solicitar Código no E-mail`;
    }
  };

  // Confirmar Nova Senha com Código
  $("#btn-submit-new-pwd").onclick = async () => {
    const code = ($("#cfg-pwd-code-input")?.value || "").trim();
    const new_password = ($("#cfg-new-pwd-input")?.value || "").trim();
    if (!code || code.length < 4) {
      toast("Digite o código de 6 dígitos recebido no e-mail.", "err");
      $("#cfg-pwd-code-input")?.focus();
      return;
    }
    if (!new_password || new_password.length < 4) {
      toast("A nova senha deve ter no mínimo 4 caracteres.", "err");
      $("#cfg-new-pwd-input")?.focus();
      return;
    }
    const btn = $("#btn-submit-new-pwd");
    btn.disabled = true;
    btn.innerHTML = `${ICONS.refresh} Atualizando...`;
    try {
      const res = await api("/api/auth/change-password-with-code", {
        method: "POST",
        body: { code, new_password },
      });
      toast(res.message || "Senha atualizada com sucesso!", "ok");
      $("#cfg-pwd-code-input").value = "";
      $("#cfg-new-pwd-input").value = "";
    } catch (err) {
      toast(err.message, "err");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `${ICONS.check} Confirmar Nova Senha`;
    }
  };
}

/* ---------------- Inicialização do Sistema ---------------- */
function init() {
  applyTheme(state.theme);

  // Configuração Inteligente do Menu Lateral (Hover no Desktop / Clique no Mobile)
  const btnHam = $("#btn-hamburger");
  const drawer = $("#sidebar-drawer");
  const drawerBackdrop = $("#drawer-backdrop");
  const btnCloseDrawer = $("#btn-close-drawer");
  const hoverZone = $("#sidebar-hover-zone");

  if (btnHam && drawer) {
    // DESKTOP: Abrir ao passar o mouse sobre o botão hambúrguer
    btnHam.addEventListener("mouseenter", () => {
      if (isDesktopDevice()) {
        openDrawer(false);
      }
    });

    btnHam.addEventListener("mouseleave", () => {
      if (isDesktopDevice()) {
        scheduleCloseDrawer(240);
      }
    });

    // DESKTOP: Abrir ao encostar na borda esquerda
    if (hoverZone) {
      hoverZone.addEventListener("mouseenter", () => {
        if (isDesktopDevice()) {
          openDrawer(false);
        }
      });
    }

    // Manter aberto enquanto o mouse estiver dentro do menu
    drawer.addEventListener("mouseenter", () => {
      if (isDesktopDevice()) {
        if (drawerCloseTimeout) {
          clearTimeout(drawerCloseTimeout);
          drawerCloseTimeout = null;
        }
        openDrawer(false);
      }
    });

    // Fechar suavemente quando o mouse sair do menu no desktop
    drawer.addEventListener("mouseleave", () => {
      if (isDesktopDevice()) {
        scheduleCloseDrawer(200);
      }
    });

    // CLIQUE (Mobile & Desktop):
    // No mobile -> abre gaveta com backdrop escurecido
    // No desktop -> alterna se for clicado
    btnHam.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!isDesktopDevice()) {
        openDrawer(true);
      } else {
        if (drawer.classList.contains("open")) {
          forceCloseDrawer();
        } else {
          openDrawer(false);
        }
      }
    });
  }

  if (btnCloseDrawer) {
    btnCloseDrawer.addEventListener("click", (e) => {
      e.stopPropagation();
      forceCloseDrawer();
    });
  }

  if (drawerBackdrop) {
    drawerBackdrop.addEventListener("click", () => {
      forceCloseDrawer();
    });
  }

  // Injeta ícones SVG puros (zero emojis)
  if ($("#nav-ico-dashboard")) $("#nav-ico-dashboard").innerHTML = ICONS.dashboard;
  if ($("#nav-ico-contas")) $("#nav-ico-contas").innerHTML = ICONS.accounts;
  if ($("#nav-ico-midias")) $("#nav-ico-midias").innerHTML = ICONS.media;
  if ($("#nav-ico-agendamentos")) $("#nav-ico-agendamentos").innerHTML = ICONS.calendar;
  if ($("#nav-ico-aquecimento")) $("#nav-ico-aquecimento").innerHTML = ICONS.flame;
  if ($("#nav-ico-gerador-email")) $("#nav-ico-gerador-email").innerHTML = ICONS.mail;
  if ($("#nav-ico-publicacoes")) $("#nav-ico-publicacoes").innerHTML = ICONS.publish;
  if ($("#nav-ico-configuracoes")) $("#nav-ico-configuracoes").innerHTML = ICONS.settings;
  if ($("#logout-ico")) $("#logout-ico").innerHTML = ICONS.logout;
  if ($("#logout-topbar-ico")) $("#logout-topbar-ico").innerHTML = ICONS.logout;

  if ($("#mob-ico-dashboard")) $("#mob-ico-dashboard").innerHTML = ICONS.dashboard;
  if ($("#mob-ico-contas")) $("#mob-ico-contas").innerHTML = ICONS.accounts;
  if ($("#mob-ico-midias")) $("#mob-ico-midias").innerHTML = ICONS.media;
  if ($("#mob-ico-agendamentos")) $("#mob-ico-agendamentos").innerHTML = ICONS.calendar;
  if ($("#mob-ico-aquecimento")) $("#mob-ico-aquecimento").innerHTML = ICONS.flame;
  if ($("#mob-ico-configuracoes")) $("#mob-ico-configuracoes").innerHTML = ICONS.settings;

  const themeQuickBtn = $("#btn-theme-quick");
  if (themeQuickBtn) themeQuickBtn.onclick = () => cycleTheme();

  $$(".nav-btn").forEach((b) => {
    b.onclick = () => {
      state.view = b.dataset.view;
      render();
    };
  });
  $$(".mobile-nav-item").forEach((b) => {
    b.onclick = () => {
      state.view = b.dataset.view;
      render();
    };
  });

  const tabLogin = $("#tab-btn-login");
  const tabRegister = $("#tab-btn-register");
  const formLogin = $("#login-form");
  const formRegister = $("#register-form");
  const formVerify = $("#verify-email-form");

  if (tabLogin && tabRegister && formLogin && formRegister) {
    tabLogin.onclick = () => {
      tabLogin.classList.add("active");
      tabRegister.classList.remove("active");
      formLogin.classList.remove("hidden");
      formRegister.classList.add("hidden");
      if (formVerify) formVerify.classList.add("hidden");
    };
    tabRegister.onclick = () => {
      tabRegister.classList.add("active");
      tabLogin.classList.remove("active");
      formRegister.classList.remove("hidden");
      formLogin.classList.add("hidden");
      if (formVerify) formVerify.classList.add("hidden");
    };
  }

  if (formLogin) formLogin.onsubmit = (e) => { if (e && e.preventDefault) e.preventDefault(); doLogin(); return false; };
  if (formRegister) formRegister.onsubmit = (e) => { if (e && e.preventDefault) e.preventDefault(); doRegister(); return false; };

  const btnLogin = $("#btn-login");
  if (btnLogin) btnLogin.onclick = (e) => { if (e && e.preventDefault) e.preventDefault(); doLogin(); };

  const btnRegister = $("#btn-register");
  if (btnRegister) btnRegister.onclick = (e) => { if (e && e.preventDefault) e.preventDefault(); doRegister(); };

  const btnConfirmCode = $("#btn-confirm-email-code");
  if (btnConfirmCode) btnConfirmCode.onclick = () => doConfirmSignupEmailCode();

  const btnResendCode = $("#btn-resend-signup-code");
  if (btnResendCode) {
    btnResendCode.onclick = async () => {
      const email = state.pendingEmailForVerification || ($("#reg-email")?.value || "").trim();
      if (!email) return;
      try {
        const res = await api("/api/auth/resend-verification", { method: "POST", body: { email } });
        toast(res.message || "Novo código enviado!", "ok");
        $("#reg-verif-code-input").value = res.code || "";
      } catch (err) {
        toast(err.message, "err");
      }
    };
  }

  const btnBackSignup = $("#btn-back-to-signup");
  if (btnBackSignup) {
    btnBackSignup.onclick = () => {
      $("#verify-email-form").classList.add("hidden");
      $("#register-form").classList.remove("hidden");
    };
  }

  const passIn = $("#login-password");
  if (passIn) passIn.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); doLogin(); } };

  const emailIn = $("#login-email");
  if (emailIn) emailIn.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); doLogin(); } };

  const regCodeIn = $("#reg-verif-code-input");
  if (regCodeIn) regCodeIn.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); doConfirmSignupEmailCode(); } };

  const btnLogout = $("#btn-logout");
  if (btnLogout) btnLogout.onclick = () => logout();

  const btnLogoutTopbar = $("#btn-logout-topbar");
  if (btnLogoutTopbar) btnLogoutTopbar.onclick = () => logout();

  if (state.token) {
    api("/api/auth/me").then((u) => {
      if (u && u.email) {
        state.email = u.email;
        store.set("instaflow_email", u.email);
        if (u.theme_preference) {
          applyTheme(u.theme_preference);
        }
        showApp();
      } else {
        showLogin();
      }
    }).catch(() => {
      showLogin();
    });
  } else {
    showLogin();
  }
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      for (let reg of registrations) {
        reg.update();
      }
    });
    navigator.serviceWorker.register("/static/sw.js?v=502").catch(() => {});
  });
}

init();
