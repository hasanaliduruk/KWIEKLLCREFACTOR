/* =========================================================================
   Operations Toolkit — frontend logic
   ========================================================================= */

// =======================================================================
// TEMA & FONT BOYUTU YÖNETİMİ
// =======================================================================
const FONT_SIZES = [12, 13, 14, 15, 16, 17, 18];
const DEFAULT_FONT = 14;
const DEFAULT_THEME = "daylight";
const THEMES = [
  { id: "daylight", name: "Light" },
  { id: "daylight-soft", name: "Light Soft" },
  { id: "graphite", name: "Graphite" },
  { id: "ocean", name: "Ocean" },
  { id: "special", name: "Special" },
  { id: "warm", name: "Warm" },

  { id: "midnight", name: "Midnight Purple" },
  { id: "carbon", name: "Carbon" },
  { id: "forest", name: "Forest" },
  { id: "arctic", name: "Arctic" },
  { id: "burgundy", name: "Burgundy" },
  { id: "espresso", name: "Espresso" },
  { id: "cobalt", name: "Cobalt" },
  { id: "rose", name: "Rose Dark" },
  { id: "violet", name: "Violet Neon" },
  { id: "slate", name: "Slate" }
];

const htmlEl = document.documentElement;
function parseMarkdown(text) {
  if (!text) return "";
  let html = text
    // Güvenlik için HTML karakterlerini escape et
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Başlıklar (# , ## , ### )
    .replace(/^### (.*$)/gim, '<h3 style="margin: 12px 0 6px; font-size: 15px; color: var(--text);">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 style="margin: 14px 0 6px; font-size: 17px; color: var(--text);">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 style="margin: 16px 0 8px; font-size: 19px; color: var(--text);">$1</h1>')
    // Kalın Metin (**text**)
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text);">$1</strong>')
    // İtalik Metin (*text*)
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Listeler (- veya *)
    .replace(/^\s*[-*]\s+(.*)$/gim, '<li style="margin-bottom: 4px;">$1</li>')
    // Satır Sonları
    .replace(/\n/g, '<br>');

  // Alt alta gelen <li> etiketlerini <ul> içine alarak düzgün liste görünümü sağla
  html = html.replace(/(<li[\s\S]*?<\/li>)+/g, '<ul style="margin: 6px 0 12px 20px; padding: 0;">$&</ul>');
  return html;
}
// =======================================================================
// EVRENSEL JSON AYAR EDİTÖRÜ (Universal Config Editor)
// =======================================================================
class JSONConfigEditor {
  constructor(containerId, fileName, configSchema) {
    this.containerId = containerId;
    this.fileName = fileName;
    this.configSchema = configSchema; 
    // configSchema Formatı: [{ key: "columns", title: "Sütunlar", type: "tags" }, { key: "deposits", title: "Maliyetler", type: "key-value" }]
    this.data = {};
  }

  async load() {
    try {
      const raw = await api().get_settings(this.fileName);
      this.data = typeof raw === "string" ? JSON.parse(raw) : raw;
    } catch (e) {
      this.data = {};
    }
    
    // JSON'da eksik anahtar varsa otomatik oluştur
    this.configSchema.forEach(sec => {
      if (!this.data[sec.key]) this.data[sec.key] = {};
    });
    this.render();
  }

  render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    let html = ``;

    this.configSchema.forEach(sec => {
      html += `<div class="card-title" style="margin-bottom:14px;">${sec.title}</div>`;
      
      if (sec.type === "tags") {
        html += `<div class="row-2">`;
        for (const [colName, valArray] of Object.entries(this.data[sec.key])) {
          let chips = (valArray || []).map(v => `<span class="file-chip" style="margin:2px; padding:3px 6px; border-color:var(--accent);"><span class="file-chip-name">${v}</span><span class="file-chip-remove" data-sec="${sec.key}" data-col="${colName}" data-val="${v}" style="margin-left:4px;">&times;</span></span>`).join('');
          html += `
            <div class="field">
              <label class="field-label">${colName.toUpperCase()}</label>
              <div class="tags-wrapper" style="display:flex; flex-wrap:wrap; gap:4px; padding:4px; background:var(--panel-raised); border:1px solid var(--line); border-radius:var(--radius-sm); min-height:36px; align-items:center;">
                ${chips}
                <input type="text" class="tag-input" data-sec="${sec.key}" data-col="${colName}" style="border:none; background:transparent; outline:none; color:var(--text); flex:1; min-width:80px; font-size:12px;" placeholder="Add and press Enter..." />
              </div>
            </div>`;
        }
        html += `</div>`;
      } else if (sec.type === "key-value") {
        html += `<div class="row-2" style="margin-bottom:14px;">`;
        for (const [k, v] of Object.entries(this.data[sec.key])) {
          html += `
            <div class="field anim-pop" style="background: var(--panel-raised); padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--line); margin-bottom: auto;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <label class="field-label" style="margin-bottom: 0; font-weight: 600;">${k}</label>
                <button class="btn-delete-kv" data-sec="${sec.key}" data-key="${k}" style="background: transparent; border:none; color:var(--err); cursor:pointer; font-size:16px; line-height:1; padding: 2px 4px;" title="Sil">&times;</button>
              </div>
              <input type="number" step="0.01" class="kv-input text-input" data-sec="${sec.key}" data-key="${k}" value="${v}" />
            </div>`;
        }
        html += `</div>
        <div style="display:flex; gap:8px; margin-bottom:14px;">
          <input type="text" class="text-input new-kv-key" data-sec="${sec.key}" placeholder="New Warehouse" style="width:160px; font-size:12.8px; padding:6px 11px;" />
          <button class="btn btn-primary btn-add-kv" data-sec="${sec.key}" style="padding:6px 14px;">Add</button>
        </div><div class="divider"></div>`;
      }
    });
    html += `
    <div style="display:flex; justify-content:flex-end; align-items:center;">
      <div style="display:flex;">
        <button class="btn btn-sm btn-revert" style="padding:6px 14px; margin-right:8px;" title="Unsaved changes will be lost">Revert</button>
        <button class="btn btn-sm btn-save" style="padding:6px 14px; border-color:var(--accent); color:var(--accent);">Save Settings</button>
      </div>
    </div>`;
    

    container.innerHTML = html;
    this.attachEvents(container);
  }

  attachEvents(container) {
    container.querySelectorAll(".tag-input").forEach(input => {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          const val = e.target.value.trim();
          const sec = e.target.dataset.sec;
          const col = e.target.dataset.col;
          if (val && !this.data[sec][col].includes(val)) {
            this.data[sec][col].push(val);
            this.render();
          }
        }
      });
    });

    container.querySelectorAll(".file-chip-remove").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const sec = e.currentTarget.dataset.sec;
        const col = e.currentTarget.dataset.col;
        const val = e.currentTarget.dataset.val;
        this.data[sec][col] = this.data[sec][col].filter(v => v !== val);
        this.render();
      });
    });

    container.querySelectorAll(".kv-input").forEach(input => {
      input.addEventListener("change", (e) => {
        const sec = e.target.dataset.sec;
        const key = e.target.dataset.key;
        this.data[sec][key] = parseFloat(e.target.value) || 0;
      });
    });

    container.querySelectorAll(".btn-delete-kv").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const sec = e.currentTarget.dataset.sec;
        const key = e.currentTarget.dataset.key;
        if (e.currentTarget.dataset.confirm === "1") {
          delete this.data[sec][key];
          this.render();
        } else {
          e.currentTarget.dataset.confirm = "1";
          e.currentTarget.innerHTML = "Delete?";
          e.currentTarget.style.fontSize = "11px";
          e.currentTarget.style.backgroundColor = "var(--err)";
          e.currentTarget.style.color = "#fff";
          e.currentTarget.style.padding = "6px 8px";
          e.currentTarget.style.borderRadius = "4px";
          e.currentTarget.style.top = "6px";
          e.currentTarget.style.right = "6px";
          setTimeout(() => {
            if (document.body.contains(e.currentTarget)) {
              e.currentTarget.dataset.confirm = "0";
              e.currentTarget.innerHTML = "&times;";
              e.currentTarget.style = "background:transparent; border:none; color:var(--err); cursor:pointer; float:right; font-size:16px; line-height:1;";
            }
          }, 3000);
        }
      });
    });

    container.querySelectorAll(".btn-add-kv").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const sec = e.currentTarget.dataset.sec;
        const input = container.querySelector(`.new-kv-key[data-sec="${sec}"]`);
        const newKey = input.value.trim();
        if (newKey && this.data[sec][newKey] === undefined) {
          this.data[sec][newKey] = 0;
          this.render();
        } else if (newKey) {
          toast("Bu anahtar zaten mevcut.");
        }
      });
    });
    container.querySelector(".btn-save").addEventListener("click", async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      await api().save_settings(this.fileName, JSON.stringify(this.data));
      toast("Ayarlar diske kaydedildi.");
      btn.disabled = false;
    });

    container.querySelector(".btn-revert").addEventListener("click", () => {
      this.load();
      toast("Değişiklikler geri alındı.");
    });
  }
}

// ── Kayıt / Yükleme ──
function savePrefs(theme, fontSize) {
  if (api()) {
    api().set_memory_value("opkit_theme", theme).then(() => {
      api().set_memory_value("opkit_font", String(fontSize));
    });
  }
}

function loadPrefs() {
  try {
    return {
      theme: localStorage.getItem("opkit_theme") || DEFAULT_THEME,
      fontSize: parseInt(localStorage.getItem("opkit_font") || DEFAULT_FONT, 10)
    };
  } catch (_) {
    return { theme: DEFAULT_THEME, fontSize: DEFAULT_FONT };
  }
}

// ── Tema Uygulama ──
function applyTheme(theme) {
  htmlEl.setAttribute("data-theme", theme);
  document.querySelectorAll(".theme-swatch").forEach(s => {
    s.classList.toggle("active", s.dataset.theme === theme);
  });
}
function createThemeSwatches() {
  const container = document.getElementById("theme-swatches");
  if (!container) return;

  container.innerHTML = "";

  THEMES.forEach(theme => {
    const swatch = document.createElement("div");
    swatch.className = "theme-swatch";
    swatch.dataset.theme = theme.id;
    swatch.title = theme.name;

    swatch.innerHTML = `
        <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
          <rect width="100" height="100" fill="var(--bg)" />
          <rect width="28" height="100" fill="var(--sidebar-bg)" />
          <!-- Sidebar Aktif Eleman -->
          <rect x="4" y="24" width="20" height="10" rx="3" fill="var(--sidebar-active-bg)" />
          <rect x="7" y="28" width="8" height="2" rx="1" fill="var(--sidebar-active-text)" />
          <rect x="34" y="10" width="60" height="22" rx="3" fill="var(--panel)" />
          <line x1="38" y1="21" x2="88" y2="21" stroke="var(--line-soft)" stroke-width="0.5" />
          <!-- Toggle 1 -->
          <rect x="76" y="13" width="14" height="6" rx="3" fill="var(--accent)" />
          <circle cx="86" cy="16" r="2.5" fill="var(--panel)" />
          <!-- Toggle 2 -->
          <rect x="76" y="23" width="14" height="6" rx="3" fill="var(--accent)" />
          <circle cx="86" cy="26" r="2.5" fill="var(--panel)" />
          <rect x="34" y="38" width="60" height="26" rx="3" fill="var(--panel)" />
          <line x1="37" y1="44" x2="60" y2="44" stroke="var(--line)" stroke-width="1" />
          <rect x="37" y="47" width="54" height="14" rx="2" fill="var(--panel-raised)" />

          <rect x="34" y="70" width="60" height="26" rx="3" fill="var(--panel)" />
          <line x1="37" y1="76" x2="60" y2="76" stroke="var(--line)" stroke-width="1" />
          <rect x="37" y="79" width="54" height="14" rx="2" fill="var(--panel-raised)" />
        </svg>

        <span class="theme-swatch-tip">${theme.name}</span>
    `;

    swatch.addEventListener("click", () => {
        applyTheme(theme.id);
        savePrefs(theme.id, currentFontSize);
    });

    container.appendChild(swatch);
  });
}

// Reusable Tag Pill Component Builder
function createTagInput(tagsArray, onChange, placeholder = "+ Add alias...") {
  const container = document.createElement("div");
  container.className = "tag-input-container";

  function render() {
    container.innerHTML = "";
    tagsArray.forEach((tag, idx) => {
      const pill = document.createElement("span");
      pill.className = "tag-pill";
      pill.innerHTML = `<span>${escapeHtml(tag)}</span><span class="tag-pill-remove" title="Remove alias">&times;</span>`;
      pill.querySelector(".tag-pill-remove").addEventListener("click", (e) => {
        e.stopPropagation();
        tagsArray.splice(idx, 1);
        render();
        onChange(tagsArray);
      });
      container.appendChild(pill);
    });

    const input = document.createElement("input");
    input.type = "text";
    input.className = "tag-input-field";
    input.placeholder = placeholder;
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === ",") {
        e.preventDefault();
        const val = input.value.trim().replace(/,/g, "");
        if (val && !tagsArray.includes(val)) {
          tagsArray.push(val);
          render();
          onChange(tagsArray);
          setTimeout(() => {
            const lastInput = container.querySelector(".tag-input-field");
            if (lastInput) lastInput.focus();
          }, 10);
        }
      }
    });
    container.appendChild(input);
  }

  render();
  return container;
}

// ── Font Boyutu Uygulama ──
let currentFontSize = DEFAULT_FONT;
function applyFontSize(size) {
  currentFontSize = Math.max(FONT_SIZES[0], Math.min(size, FONT_SIZES[FONT_SIZES.length - 1]));
  htmlEl.style.setProperty("--base-font-size", currentFontSize + "px");
  const display = document.getElementById("font-size-display");
  if (display) display.textContent = currentFontSize + "px";
  // Disable buttons at limits
  const decBtn = document.getElementById("font-decrease-btn");
  const incBtn = document.getElementById("font-increase-btn");
  if (decBtn) decBtn.disabled = currentFontSize <= FONT_SIZES[0];
  if (incBtn) incBtn.disabled = currentFontSize >= FONT_SIZES[FONT_SIZES.length - 1];
}

// ── İlk Yükleme ──
createThemeSwatches();
// ── Font Butonları ──
// Settings Tabs (Sekme) Mantığı
document.querySelectorAll(".settings-tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".settings-tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".fba-tables").forEach(p => p.classList.remove("active"));
    
    btn.classList.add("active");
    document.getElementById(btn.dataset.target).classList.add("active");
  });
});

// View (Sayfa) geçişlerinde verilerin senkronize edilmesi
document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", async () => {
    document.querySelectorAll(".nav-item[data-view]").forEach((i) => i.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    item.classList.add("active");
    document.getElementById("view-" + item.dataset.view).classList.add("active");
    
    // Geçiş yapılan sayfadaki ayar dosyalarını bellekten tazeleyerek senkron tut
    if (item.dataset.view === "settings") {
      loadCostUpdaterSettings();
      if(typeof mainRestockEditor !== "undefined") mainRestockEditor.load();
      if(typeof mainOrderEditor !== "undefined") mainOrderEditor.load();
      if(typeof mainInvoiceEditor !== "undefined") mainInvoiceEditor.load();
      if(typeof mainShipmentEditor !== "undefined") mainShipmentEditor.load();
    } else if (item.dataset.view === "restock" && typeof restockEditor !== "undefined") {
      restockEditor.load();
    } else if (item.dataset.view === "ordercreate" && typeof orderEditor !== "undefined") {
      orderEditor.load();
    } else if (item.dataset.view === "invoice" && typeof invoiceEditor !== "undefined") {
      invoiceEditor.load();
    } else if (item.dataset.view === "shipment" && typeof shipmentEditor !== "undefined") {
      shipmentEditor.load();
    }
    
    closeSidebar();
  });
});

const openBtn = document.getElementById("settings-open-folder-btn");
if (openBtn) openBtn.addEventListener("click", async () => { openBtn.disabled = true; try { await api().open_settings_folder(); } finally { openBtn.disabled = false; } });

document.getElementById("font-increase-btn")?.addEventListener("click", () => {
  const next = FONT_SIZES.find(s => s > currentFontSize) || currentFontSize;
  applyFontSize(next);
  savePrefs(htmlEl.getAttribute("data-theme") || DEFAULT_THEME, currentFontSize);
});

document.getElementById("font-decrease-btn")?.addEventListener("click", () => {
  const prev = [...FONT_SIZES].reverse().find(s => s < currentFontSize) || currentFontSize;
  applyFontSize(prev);
  savePrefs(htmlEl.getAttribute("data-theme") || DEFAULT_THEME, currentFontSize);
});

document.getElementById("font-reset-btn")?.addEventListener("click", () => {
  applyFontSize(DEFAULT_FONT);
  savePrefs(htmlEl.getAttribute("data-theme") || DEFAULT_THEME, DEFAULT_FONT);
});

function whenApiReady(cb) {
  if (window.pywebview && window.pywebview.api) {
    cb();
  } else {
    window.addEventListener("pywebviewready", cb, { once: true });
  }
}

function api() {
  return window.pywebview ? window.pywebview.api : null;
}

function initConsoleCopyButtons() {
  document.querySelectorAll(".console").forEach((consoleEl) => {
    const head = consoleEl.querySelector(".console-head");
    const body = consoleEl.querySelector(".console-body");
    if (!head || !body || head.querySelector(".console-copy-btn")) return;

    const btn = document.createElement("button");
    btn.className = "console-copy-btn";
    btn.textContent = "Copy";
    btn.addEventListener("click", async () => {
      const text = body.innerText.trim();
      if (!text) return toast("Nothing to copy yet.");
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
        } else {
          const ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
        }
        btn.textContent = "Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "Copy";
          btn.classList.remove("copied");
        }, 1500);
      } catch (e) {
        toast("Copy failed.");
      }
    });
    head.appendChild(btn);
  });
}

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("visible");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("visible"), 2600);
}

// ---------------------------------------------------------------------
// Sidebar navigation
// ---------------------------------------------------------------------
const sidebarEl = document.querySelector(".sidebar");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const hamburgerBtn = document.getElementById("hamburger-btn");

function closeSidebar() {
  if (sidebarEl) sidebarEl.classList.remove("open");
  if (sidebarOverlay) sidebarOverlay.classList.remove("open");
  if (hamburgerBtn) hamburgerBtn.classList.remove("open");
}

if (hamburgerBtn) {
  hamburgerBtn.addEventListener("click", () => {
    if (sidebarEl) sidebarEl.classList.toggle("open");
    if (sidebarOverlay) sidebarOverlay.classList.toggle("open");
    hamburgerBtn.classList.toggle("open");
  });
}

if (sidebarOverlay) sidebarOverlay.addEventListener("click", closeSidebar);

document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item[data-view]").forEach((i) => i.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    item.classList.add("active");
    document.getElementById("view-" + item.dataset.view).classList.add("active");
    closeSidebar();
  });
});

document.querySelectorAll("[data-browse-folder]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const inputId = btn.getAttribute("data-browse-folder");
    const folder = await api().pick_folder();
    if (folder) {
      document.getElementById(inputId).value = folder;
      api().set_memory_value(inputId, folder);
    }
  });
});

whenApiReady(async () => {
  initConsoleCopyButtons();
  const mem = await api().get_memory();

  const savedTheme = mem["opkit_theme"] || DEFAULT_THEME;
  const savedFont = parseInt(mem["opkit_font"] || DEFAULT_FONT, 10);
  applyTheme(savedTheme);
  applyFontSize(savedFont);

  fbaManager.init();
  fbaManager.reloadData();

  if (mem["app_zoom"]) {
    updateAppZoom(parseFloat(mem["app_zoom"]), false);
  }

  document.querySelectorAll("input[type=text]").forEach((input) => {
    if (mem[input.id] && !input.value) input.value = mem[input.id];
    input.addEventListener("change", () => api().set_memory_value(input.id, input.value));
  });

  const loadingOverlay = document.getElementById("loading-overlay");
  if (loadingOverlay) {
    setTimeout(() => {
      loadingOverlay.classList.add("loaded");
      setTimeout(() => {
        if (loadingOverlay.parentNode) loadingOverlay.parentNode.removeChild(loadingOverlay);
      }, 400);
    }, 150);
  }
});

// ---------------------------------------------------------------------
// DYNAMIC FILE DROPZONE (with Selection Toolbar)
// ---------------------------------------------------------------------
const dropZoneRegistry = {};
window.addEventListener("files-dropped", (e) => {
  const { zoneId, paths } = e.detail;
  const zone = dropZoneRegistry[zoneId];
  if (zone && paths && paths.length) zone.addFiles(paths);
});

class FileDropZone {
  constructor({ zoneId, listId, fileTypes = null, multiple = true, accept = null, reorderable = false }) {
    this.zone = document.getElementById(zoneId);
    this.list = document.getElementById(listId);
    this.fileTypes = fileTypes; 
    this.multiple = multiple;
    this.accept = accept; 
    this.reorderable = reorderable; 
    this.files = [];
    this.selected = new Set();
    this._dragFromIndex = null;

    dropZoneRegistry[zoneId] = this;

    this.zone.addEventListener("click", () => this.browse());
    this.zone.addEventListener("dragover", (e) => { e.preventDefault(); this.zone.classList.add("drag-over"); });
    this.zone.addEventListener("dragleave", () => this.zone.classList.remove("drag-over"));
    this.zone.addEventListener("drop", (e) => { e.preventDefault(); this.zone.classList.remove("drag-over"); });
  }

  async browse() {
    const picked = await api().pick_files(this.fileTypes, this.multiple);
    if (picked && picked.length) this.addFiles(picked);
  }

  addFiles(paths) {
    for (const p of paths) {
      if (this.accept && !this.accept(p)) continue;
      if (!this.multiple) { this.files = []; this.selected.clear(); }
      if (!this.files.includes(p)) this.files.push(p);
    }
    this.render();
  }

  removeFile(p) {
    this.files = this.files.filter((f) => f !== p);
    this.selected.delete(p);
    this.render();
  }

  deleteSelected() {
    this.files = this.files.filter((f) => !this.selected.has(f));
    this.selected.clear();
    this.render();
  }

  clear() {
    this.files = [];
    this.selected.clear();
    this.render();
  }

  moveFile(fromIndex, toIndex) {
    if (toIndex < 0 || toIndex >= this.files.length) return;
    const [item] = this.files.splice(fromIndex, 1);
    this.files.splice(toIndex, 0, item);
    this.render();
  }

  toggleAll(checked) {
    if (checked) {
      this.files.forEach(f => this.selected.add(f));
    } else {
      this.selected.clear();
    }
    this.render();
  }

  render() {
    this.list.innerHTML = "";
    if (this.files.length === 0) return;

    // Render Toolbar
    const toolbar = document.createElement("div");
    toolbar.className = "file-list-toolbar";
    
    const allSelected = this.files.length > 0 && this.files.length === this.selected.size;
    const someSelected = this.selected.size > 0;

    toolbar.innerHTML = `
      <label><input type="checkbox" class="select-all" ${allSelected ? "checked" : ""}> Select All</label>
      <div class="toolbar-actions">
          <button class="btn-sm danger btn-delete-sel" ${someSelected ? "" : "disabled"}>Delete Selected</button>
          <button class="btn-sm danger btn-clear-all">Clear All</button>
      </div>
    `;

    toolbar.querySelector(".select-all").addEventListener("change", (e) => this.toggleAll(e.target.checked));
    toolbar.querySelector(".btn-delete-sel").addEventListener("click", () => this.deleteSelected());
    toolbar.querySelector(".btn-clear-all").addEventListener("click", () => this.clear());

    this.list.appendChild(toolbar);

    // Render File Chips
    const container = document.createElement("div");
    container.className = "file-chips-container";
    
    this.files.forEach((p, index) => {
      const chip = this.reorderable ? this._renderReorderableChip(p, index) : this._renderChip(p);
      container.appendChild(chip);
    });

    this.list.appendChild(container);
  }

  _getCheckboxHTML(p) {
    const isChecked = this.selected.has(p) ? "checked" : "";
    return `<input type="checkbox" class="file-chip-checkbox" data-path="${encodeURIComponent(p)}" ${isChecked}>`;
  }

  _bindCheckboxEvent(chip) {
    chip.querySelector(".file-chip-checkbox").addEventListener("change", (e) => {
      const path = decodeURIComponent(e.target.dataset.path);
      if (e.target.checked) this.selected.add(path);
      else this.selected.delete(path);
      this.render(); // Re-render to update toolbar state
    });
  }

  _renderChip(p) {
    const name = p.split(/[\\/]/).pop();
    const chip = document.createElement("div");
    chip.className = "file-chip";
    chip.innerHTML = `
      ${this._getCheckboxHTML(p)}
      <svg class="file-chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5Z"/><path d="M14 3v5h5"/></svg>
      <span class="file-chip-name" title="${p}">${name}</span>
      <span class="file-chip-remove" data-path="${encodeURIComponent(p)}">&times;</span>`;
    
    this._bindCheckboxEvent(chip);
    chip.querySelector(".file-chip-remove").addEventListener("click", (ev) => {
      this.removeFile(decodeURIComponent(ev.target.dataset.path));
    });
    return chip;
  }

  _renderReorderableChip(p, index) {
    const name = p.split(/[\\/]/).pop();
    const chip = document.createElement("div");
    chip.className = "file-chip reorderable";
    chip.draggable = true;

    const isFirst = index === 0;
    const isLast = index === this.files.length - 1;

    chip.innerHTML = `
      <span class="file-chip-handle" title="Drag to reorder">
        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="8" cy="6" r="1.5"/><circle cx="8" cy="12" r="1.5"/><circle cx="8" cy="18" r="1.5"/><circle cx="16" cy="6" r="1.5"/><circle cx="16" cy="12" r="1.5"/><circle cx="16" cy="18" r="1.5"/></svg>
      </span>
      ${this._getCheckboxHTML(p)}
      <span class="file-chip-rank">${index + 1}</span>
      <span class="file-chip-name" title="${p}">${name}</span>
      <span class="file-chip-arrows">
        <span class="file-chip-arrow ${isFirst ? "disabled" : ""}" data-dir="up"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 15l7-7 7 7"/></svg></span>
        <span class="file-chip-arrow ${isLast ? "disabled" : ""}" data-dir="down"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 9l7 7 7-7"/></svg></span>
      </span>
      <span class="file-chip-remove" data-path="${encodeURIComponent(p)}">&times;</span>`;

    this._bindCheckboxEvent(chip);
    chip.querySelector(".file-chip-remove").addEventListener("click", (ev) => this.removeFile(decodeURIComponent(ev.target.dataset.path)));
    chip.querySelectorAll(".file-chip-arrow").forEach((el) => {
      el.addEventListener("click", (ev) => {
        ev.stopPropagation();
        this.moveFile(index, ev.currentTarget.dataset.dir === "up" ? index - 1 : index + 1);
      });
    });

    chip.addEventListener("dragstart", (ev) => { this._dragFromIndex = index; chip.classList.add("dragging"); ev.dataTransfer.effectAllowed = "move"; ev.dataTransfer.setData("text/plain", String(index)); });
    chip.addEventListener("dragend", () => { chip.classList.remove("dragging"); this.list.querySelectorAll(".file-chip").forEach(c => c.classList.remove("drag-over-top", "drag-over-bottom")); });
    chip.addEventListener("dragover", (ev) => {
      ev.preventDefault();
      if (this._dragFromIndex === null || this._dragFromIndex === index) return;
      const rect = chip.getBoundingClientRect();
      chip.classList.toggle("drag-over-top", ev.clientY - rect.top < rect.height / 2);
      chip.classList.toggle("drag-over-bottom", !(ev.clientY - rect.top < rect.height / 2));
    });
    chip.addEventListener("dragleave", () => chip.classList.remove("drag-over-top", "drag-over-bottom"));
    chip.addEventListener("drop", (ev) => {
      ev.preventDefault(); ev.stopPropagation();
      if (this._dragFromIndex === null || this._dragFromIndex === index) return;
      const rect = chip.getBoundingClientRect();
      let targetIndex = (ev.clientY - rect.top < rect.height / 2) ? index : index + 1;
      if (this._dragFromIndex < targetIndex) targetIndex -= 1;
      this.moveFile(this._dragFromIndex, targetIndex);
      this._dragFromIndex = null;
    });

    return chip;
  }
}

// ---------------------------------------------------------------------
// Console & Tool Status Builders
// ---------------------------------------------------------------------
function logLine(bodyId, message, cls = "") {
  const body = document.getElementById(bodyId);
  if(!body) return;
  const line = document.createElement("div");
  line.className = "console-line " + cls;
  line.textContent = message;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
}

function setStatus(dotId, textId, state, label) {
  const dot = document.getElementById(dotId);
  const text = document.getElementById(textId);
  if(dot) dot.className = "console-dot " + state;
  if(text) text.textContent = label;
}

function showResult(bannerId, ok, message, outputPath) {
  const el = document.getElementById(bannerId);
  if(!el) return;
  el.className = "result-banner visible " + (ok ? "ok" : "error");
  el.innerHTML = `<span>${message}</span>`;
  if (ok && outputPath) {
    const btn = document.createElement("button");
    btn.className = "btn";
    btn.textContent = "Open folder";
    btn.addEventListener("click", () => api().open_folder(outputPath));
    el.appendChild(btn);
  }
}

// ---------------------------------------------------------------------
// Job Execution Wrapper (DRY Logic for all Tools)
// ---------------------------------------------------------------------
const TOOLS = [
  { btn: "conv-run-btn", cancelBtn: "conv-cancel-btn", log: "conv-log", dot: "conv-dot", status: "conv-status-text", result: "conv-result", fill: "conv-progress-fill", console: "conv-console" },
  { btn: "tsv-run-btn", cancelBtn: "tsv-cancel-btn", log: "tsv-log", dot: "tsv-dot", status: "tsv-status-text", result: "tsv-result", fill: null, console: "tsv-console" },
  { btn: "cu-run-btn", cancelBtn: "cu-cancel-btn", log: "cu-log", dot: "cu-dot", status: "cu-status-text", result: "cu-result", fill: null, console: "cu-console" },
  { btn: "rs-run-btn", cancelBtn: "rs-cancel-btn", log: "rs-log", dot: "rs-dot", status: "rs-status-text", result: "rs-result", fill: "rs-progress-fill", console: "rs-console" },
  { btn: "fp-run-btn", cancelBtn: "fp-cancel-btn", log: "fp-log", dot: "fp-dot", status: "fp-status-text", result: "fp-result", fill: null, console: "fp-console" },
  { btn: "oc-run-btn", cancelBtn: "oc-cancel-btn", log: "oc-log", dot: "oc-dot", status: "oc-status-text", result: "oc-result", fill: null, console: "oc-console" },
  { btn: "inv-run-btn", cancelBtn: "inv-cancel-btn", log: "inv-log", dot: "inv-dot", status: "inv-status-text", result: "inv-result", fill: null, console: "inv-console" },
  { btn: "sc-run-btn", cancelBtn: "sc-cancel-btn", log: "sc-log", dot: "sc-dot", status: "sc-status-text", result: "sc-result", fill: null, console: "sc-console" },
  { btn: "if-run-btn", cancelBtn: "if-cancel-btn", log: "if-log", dot: "if-dot", status: "if-status-text", result: "if-result", fill: null, console: "if-console" },
  { btn: "exp-run-btn", cancelBtn: "exp-cancel-btn", log: "exp-log", dot: "exp-dot", status: "exp-status-text", result: "exp-result", fill: null, console: "exp-console" },
  { btn: "pe-run-btn", cancelBtn: "pe-cancel-btn", log: "pe-log", dot: "pe-dot", status: "pe-status-text", result: "pe-result", fill: null, console: "pe-console" },
];

function activeTool() { return TOOLS.find((t) => document.getElementById(t.btn)?.disabled) || null; }

function prepareJobUI(prefix) {
  document.getElementById(`${prefix}-console`).classList.add("visible");
  document.getElementById(`${prefix}-result`).classList.remove("visible");
  document.getElementById(`${prefix}-log`).innerHTML = "";
  if(document.getElementById(`${prefix}-progress-fill`)) document.getElementById(`${prefix}-progress-fill`).style.width = "0%";
  setStatus(`${prefix}-dot`, `${prefix}-status-text`, "running", "Running…");
  
  document.getElementById(`${prefix}-run-btn`).disabled = true;
  const cBtn = document.getElementById(`${prefix}-cancel-btn`);
  if(cBtn) cBtn.style.display = "inline-flex";
}

// Global Cancel Attachments
TOOLS.forEach(t => {
  const cBtn = document.getElementById(t.cancelBtn);
  if(cBtn) {
    cBtn.addEventListener("click", async () => {
      await api().cancel_job();
      cBtn.disabled = true; // Prevent spamming cancel
    });
  }
});

// Event Listeners for Job Progress
window.addEventListener("job-log", (e) => {
  const t = activeTool();
  if (!t) return;
  const { message, color, percent } = e.detail;
  let cls = "";
  if (color === "red") cls = "error";
  else if (color === "#90EE90") cls = "ok";
  else if (color === "yellow") cls = "warn";
  logLine(t.log, message, cls);
  if (t.fill && typeof percent === "number") document.getElementById(t.fill).style.width = percent + "%";
});

window.addEventListener("job-done", (e) => {
  const t = activeTool();
  if (!t) return;
  const cBtn = document.getElementById(t.cancelBtn);
  if (cBtn) { cBtn.style.display = "none"; cBtn.disabled = false; }
  
  const { ok, message, output_path } = e.detail;
  logLine(t.log, message, ok ? "ok" : "error");
  setStatus(t.dot, t.status, ok ? "success" : "error", ok ? "Done" : "Failed");
  if (t.fill) document.getElementById(t.fill).style.width = "100%";
  showResult(t.result, ok, message, output_path);
  document.getElementById(t.btn).disabled = false;
});

// =======================================================================
// MODULE LOGIC
// =======================================================================

// Converter
const convZone = new FileDropZone({ zoneId: "conv-dropzone", listId: "conv-file-list", fileTypes: ["Convertible Files (*.csv;*.xlsx;*.xls;*.txt)", "All files (*.*)"] });
document.getElementById("conv-input-type").addEventListener("change", (e) => {
  document.getElementById("conv-type-hint").textContent = { csv: ".csv", xlsx: ".xlsx", txt: ".txt" }[e.target.value] + " files";
  convZone.clear();
});
document.getElementById("conv-run-btn").addEventListener("click", async () => {
  const inputType = document.getElementById("conv-input-type").value;
  const outputType = document.getElementById("conv-output-type").value;
  const outputFolder = document.getElementById("conv-output-folder").value.trim();

  // MANTIKSAL HATA DÜZELTİLDİ: Giriş ve çıkış formatı aynı olamaz
  if (inputType === outputType) return toast("Girdi ve Çıktı formatları aynı olamaz.");
  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!convZone.files.length) return toast("Drop at least one file to convert.");

  prepareJobUI("conv");
  await api().run_converter(convZone.files, outputFolder, inputType, outputType);
});

// TSV
const tsvZone = new FileDropZone({ zoneId: "tsv-dropzone", listId: "tsv-file-list", fileTypes: ["TSV/Text Files (*.tsv;*.txt)", "All files (*.*)"] });
document.getElementById("tsv-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("tsv-output-folder").value.trim();
  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!tsvZone.files.length) return toast("Drop at least one file to convert.");
  prepareJobUI("tsv");
  await api().run_tsv(tsvZone.files, outputFolder, document.getElementById("tsv-save-name").value.trim() || "Converted_File");
});

// =======================================================================
// FBA INVENTORY PRO MODULE
// =======================================================================
const fbaManager = {
  data: { sirali: [], analiz: [], stock: {} },

  init() {
    document.querySelector("#view-fba").addEventListener("click", (e) => {
      const td = e.target.closest("td.clickable-cell");
      if (!td) return;
      const textToCopy = td.textContent.trim();
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy);
        toast(`📋 Kopyalandı: ${textToCopy}`);
      }
    });
    document.getElementById("fba-btn-master")?.addEventListener("click", () => this.importFile("master"));
    document.getElementById("fba-btn-picklist")?.addEventListener("click", () => this.importFile("picklist"));
    document.getElementById("fba-btn-stock")?.addEventListener("click", () => this.importFile("stock"));
    document.getElementById("fba-btn-detect")?.addEventListener("click", () => this.detectIDs());
    document.getElementById("fba-btn-reset")?.addEventListener("click", () => this.resetData());
    document.getElementById("fba-btn-export")?.addEventListener("click", () => this.exportExcel());

    // Debounce Zamanlayıcısı
    let debounceTimer;
    
    const filterInputs = ["fba-skt-min", "fba-skt-max", "fba-amz-min", "fba-amz-max", "fba-search"];
    filterInputs.forEach(id => {
      document.getElementById(id)?.addEventListener("input", () => {
        // Kullanıcı yazmaya devam ediyorsa önceki emri iptal et
        clearTimeout(debounceTimer);
        // Yazma işlemi bittikten 250 milisaniye sonra filtreyi çalıştır
        debounceTimer = setTimeout(() => this.applyFilters(), 250);
      });
    });

    document.getElementById("fba-btn-clear-filters")?.addEventListener("click", () => {
      filterInputs.forEach(id => document.getElementById(id).value = "");
      this.applyFilters();
    });
  },

  async reloadData() {
    const res = await api().inv_get_all_data();
    if (res.ok) {
      this.data = res;
      this.renderTables();
    } else toast("Veri okuma hatası: " + res.message);
  },

  async importFile(type) {
    const files = await api().pick_files(["Spreadsheet Files (*.xlsx;*.xls;*.csv)", "All files (*.*)"], type === "picklist");
    if (!files || files.length === 0) return;
    
    let res;
    if (type === "master") res = await api().inv_import_master_excel(files[0]);
    else if (type === "picklist") res = await api().inv_import_picklist(files);
    else if (type === "stock") res = await api().inv_import_stock(files[0]);

    if (res.ok) { toast(res.message); this.reloadData(); }
    else toast("Hata: " + res.message);
  },

  async detectIDs() {
    const files = await api().pick_files(["Spreadsheet Files (*.xlsx;*.xls;*.csv)", "All files (*.*)"], type === "picklist");
    if (!files || !files.length) return;
    const res = await api().inv_detect_missing_ids(files[0]);
    if (res.ok) {
      if (res.missing.length === 0) toast("Tüm ID'ler sistemde kayıtlı.");
      else {
        console.log("Eksik ID'ler:\n" + res.missing.join("\n"));
        toast(`${res.missing.length} adet eksik ID bulundu. Console'u kontrol et.`);
      }
    } else toast("Hata: " + res.message);
  },

  async resetData() {
    if (!confirm("Tüm FBA geçmişi ve stok verileri silinecek. Onaylıyor musun?")) return;
    const res = await api().inv_reset_data();
    if (res.ok) { toast(res.message); this.reloadData(); }
  },

  async exportExcel() {
    const folder = await api().pick_folder();
    if (!folder) return;
    const res = await api().inv_export_excel(folder);
    if (res.ok) toast("Rapor oluşturuldu: " + res.path);
    else toast("Hata: " + res.message);
  },

  renderTables() {
    this._renderSirali();
    this._renderAnaliz();
    this._renderStock();
    this.applyFilters();
  },

  _renderSirali() {
    const tbody = document.querySelector("#fba-table-sirali tbody");
    if (!tbody) return;
    
    tbody.innerHTML = this.data.sirali.map(r => {
      const searchStr = `${r.shipment_name || ''} ${r.shipment_id || ''} ${r.sku || ''}`.replace(/"/g, '').toLowerCase();
      
      return `
      <tr data-search="${searchStr}" data-skt="${r.days_remaining || 0}" data-amz="${r.amz_stock_days || 0}">
        <td class="clickable-cell">${r.shipment_name}</td>
        <td class="clickable-cell">${r.shipment_id}</td>
        <td class="clickable-cell">${r.created_date}</td>
        <td class="clickable-cell">${r.sku}</td>
        <td class="clickable-cell" style="text-align:center;">${r.qty_shipped}</td>
        <td class="clickable-cell">${r.exp_date_usa}</td>
        <td class="clickable-cell">${r.exp_date_tur}</td>
        <td class="clickable-cell" style="text-align:center;">${r.days_remaining}</td>
        <td class="clickable-cell" style="text-align:center;">${r.amz_stock_days}</td>
      </tr>
    `}).join("");
  },

  _renderAnaliz() {
    const tbody = document.querySelector("#fba-table-analiz tbody");
    if (!tbody) return;
    
    const skuCounts = this.data.analiz.reduce((acc, r) => { acc[r.sku] = (acc[r.sku] || 0) + 1; return acc; }, {});

    tbody.innerHTML = this.data.analiz.map(r => {
      const isMultiple = skuCounts[r.sku] > 1;
      const isCritical = r.days_remaining <= 180;
      const hasStock = r.amz_stock_allocated > 0;
      
      const skuStyle = isMultiple ? 'background-color:#C6EFCE; color:#006100; font-weight:bold;' : '';
      const stockStyle = hasStock ? 'background-color:#C6EFCE; color:#006100; font-weight:bold; text-align:center;' : 'text-align:center;';
      const sktStyle = isCritical ? 'background-color:#FFCDD2; color:#B71C1C; font-weight:bold; text-align:center;' : 'text-align:center;';
      
      const searchStr = `${r.shipment_name || ''} ${r.shipment_id || ''} ${r.sku || ''}`.replace(/"/g, '').toLowerCase();

      return `
        <tr data-search="${searchStr}" data-skt="${r.days_remaining || 0}" data-amz="${r.amz_stock_days || 0}">
          <td class="clickable-cell">${r.shipment_name}</td>
          <td class="clickable-cell">${r.shipment_id}</td>
          <td class="clickable-cell" style="${skuStyle}">${r.sku}</td>
          <td class="clickable-cell" style="text-align:center;">${r.qty_shipped}</td>
          <td class="clickable-cell" style="${stockStyle}">${r.amz_stock_allocated}</td>
          <td class="clickable-cell" style="text-align:center;">${r.amz_stock_days}</td>
          <td class="clickable-cell" style="${sktStyle}">${r.days_remaining}</td>
          <td style="padding:0; min-width: 150px;">
            <input type="text" class="fba-note-input" value="${(r.note || '').replace(/"/g, '&quot;')}" 
                   data-id="${r.shipment_id}" data-sku="${r.sku}" data-exp="${r.exp_date_usa}"
                   style="width:100%; height:100%; border:none; background:transparent; padding:8px; color:var(--text); outline:none;">
          </td>
        </tr>
      `;
    }).join("");

    document.querySelectorAll(".fba-note-input").forEach(inp => {
      inp.addEventListener("change", async (e) => {
        const { id, sku, exp } = e.target.dataset;
        await api().inv_update_note(id, sku, exp, e.target.value);
        toast("Not güncellendi.");
      });
    });
  },

  _renderStock() {
    const tbody = document.querySelector("#fba-table-amz tbody");
    if (!tbody) return;
    tbody.innerHTML = Object.entries(this.data.stock).map(([sku, qty]) => `
      <tr data-search="${sku}">
        <td class="clickable-cell">${sku}</td><td class="clickable-cell" style="text-align:center;">${qty}</td>
      </tr>
    `).join("");
  },

  applyFilters() {
    const searchInput = document.getElementById("fba-search").value.trim();
    const search = searchInput.toLowerCase();
    
    // Düzenli İfade (Regex) inşası - Güvenlik yalıtımı yapıldı
    const regex = search ? new RegExp(`(${search.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')})`, 'gi') : null;
    
    const sktMinInput = document.getElementById("fba-skt-min").value;
    const sktMin = sktMinInput === "" ? -999999 : parseInt(sktMinInput, 10);
    const sktMaxInput = document.getElementById("fba-skt-max").value;
    const sktMax = sktMaxInput === "" ? 999999 : parseInt(sktMaxInput, 10);
    
    const amzMinInput = document.getElementById("fba-amz-min").value;
    const amzMin = amzMinInput === "" ? -999999 : parseInt(amzMinInput, 10);
    const amzMaxInput = document.getElementById("fba-amz-max").value;
    const amzMax = amzMaxInput === "" ? 999999 : parseInt(amzMaxInput, 10);

    const highlightCell = (td) => {
      if (td.querySelector('input')) return; // Input olan hücreyi (Not sütunu) asla bozma
      
      const originalText = td.dataset.orig || td.textContent;
      if (!td.dataset.orig) td.dataset.orig = originalText;

      if (!search) {
          td.innerHTML = originalText;
          return;
      }
      td.innerHTML = originalText.replace(regex, '<mark class="highlight">$1</mark>');
    };

    document.querySelectorAll("#fba-table-sirali tbody tr, #fba-table-analiz tbody tr").forEach(tr => {
      const textMatch = !search || (tr.dataset.search && tr.dataset.search.includes(search));
      const skt = parseInt(tr.dataset.skt, 10) || 0;
      const amz = parseInt(tr.dataset.amz, 10) || 0;
      
      const isVisible = textMatch && (skt >= sktMin && skt <= sktMax) && (amz >= amzMin && amz <= amzMax);
      tr.style.display = isVisible ? "" : "none";

      if (isVisible) Array.from(tr.children).forEach(highlightCell);
    });

    document.querySelectorAll("#fba-table-amz tbody tr").forEach(tr => {
      const textMatch = !search || (tr.dataset.search && tr.dataset.search.includes(search));
      tr.style.display = textMatch ? "" : "none";
      if (textMatch) Array.from(tr.children).forEach(highlightCell);
    });
  }
};

// Cost Updater
const cuZone = new FileDropZone({ zoneId: "cu-dropzone", listId: "cu-file-list", multiple: false, fileTypes: ["CSV Files (*.csv)", "All files (*.*)"], accept: (p) => p.toLowerCase().endsWith(".csv") });

let currentCuSettings = {};

async function loadCostUpdaterSettings() {
  const isV2 = document.getElementById("cu-version-toggle").checked;
  const fileName = isV2 ? "costupdater2_settings.json" : "costupdater_settings.json";
  
  const rawData = await api().get_settings(fileName);
  try {
    currentCuSettings = typeof rawData === "string" ? JSON.parse(rawData) : rawData;
  } catch (e) {
    currentCuSettings = { columns: {}, warehouses: {} };
  }
  
  renderCostUpdaterUI(currentCuSettings, isV2);
}

function renderCostUpdaterUI(data, isV2) {
  ['cu-settings-container', 'cu-settings-main-container'].forEach(containerId => {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `<div class="card-title" style="margin-top:4px;">Sütun Eşleştirmeleri</div>`;
    html += `<p class="muted" style="margin-top:-8px; margin-bottom:14px;">Alternatif isimleri yazıp Enter tuşuna basarak etiket (chip) olarak ekleyin. Eşleşen ilk sütun kullanılacaktır.</p><div class="row-2">`;
    
    for (const [key, val] of Object.entries(data.columns || {})) {
      let chips = (val || []).map(v => `<span class="file-chip" style="margin:2px; padding:3px 6px; border-color:var(--accent);"><span class="file-chip-name">${v}</span><span class="file-chip-remove" data-col="${key}" data-val="${v}" style="margin-left:4px;">&times;</span></span>`).join('');
      html += `
        <div class="field">
          <label class="field-label">${key.toUpperCase()}</label>
          <div class="tags-wrapper" style="display:flex; flex-wrap:wrap; gap:4px; padding:4px; background:var(--panel-raised); border:1px solid var(--line); border-radius:var(--radius-sm); min-height:36px; align-items:center;">
            ${chips}
            <input type="text" class="tag-input" data-col="${key}" style="border:none; background:transparent; outline:none; color:var(--text); flex:1; min-width:80px; font-size:12px;" placeholder="Add and press Enter..." />
          </div>
        </div>`;
    }
    
    html += `</div><div class="divider"></div>
    <div class="card-title" style="margin-bottom:14px;">Depo Maliyetleri</div>
    <div class="row-2" style="margin-bottom: 14px;">`;
    
    for (const [wh, costData] of Object.entries(data.warehouses || {})) {
      if (isV2) {
        html += `
          <div class="field" style="grid-column: span 2; background: var(--panel-raised); padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--line); position:relative;">
            <button class="btn-delete-wh" data-wh="${wh}" style="position:absolute; top:8px; right:8px; background:transparent; border:none; color:var(--err); cursor:pointer; font-weight:bold; font-size:16px; line-height:1;" title="Delete Warehouse">&times;</button>
            <label class="field-label" style="color: var(--text); font-weight: 600;">${wh} WAREHOUSE</label>
            <div class="input-row" style="margin-top: 8px; align-items: flex-end;">
              <div style="flex: 1;"><label class="field-label" style="font-size: 10px;">Add. Cost</label><input type="number" step="0.01" class="cu-wh-input text-input" data-wh="${wh}" data-prop="v2_additional_cost" value="${costData.v2_additional_cost}" /></div>
              <div style="flex: 1;"><label class="field-label" style="font-size: 10px;">Equation</label>
                <select class="select cu-wh-input" data-wh="${wh}" data-prop="v2_equation" style="width: 100%; padding: 9px 11px;">
                  <option value="1" ${costData.v2_equation === 1 ? 'selected' : ''}>1</option>
                  <option value="2" ${costData.v2_equation === 2 ? 'selected' : ''}>2</option>
                </select>
              </div>
              <div style="flex: 1;"><label class="field-label" style="font-size: 10px;">WH Fee</label><input type="number" step="0.01" class="cu-wh-input text-input" data-wh="${wh}" data-prop="v2_warehouse_fee" value="${costData.v2_warehouse_fee}" /></div>
            </div>
          </div>`;
      } else {
        html += `
          <div class="field" style="position:relative; background: var(--panel-raised); padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--line); margin-bottom: auto;">
            <label class="field-label">${wh} <button class="btn-delete-wh" data-wh="${wh}" style="background:transparent; border:none; color:var(--err); cursor:pointer; float:right; font-size:16px; line-height:1;" title="Delete Warehouse">&times;</button></label>
            <input type="number" step="0.01" class="cu-wh-input text-input" data-wh="${wh}" value="${costData}" style="margin-top:4px;" />
          </div>`;
      }
    }
    
    html += `</div>
    <div class="divider"></div>
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div style="display:flex; gap:8px;">
        <input type="text" class="text-input new-wh-input" placeholder="New Warehouse (e.g., TX)" style="width:160px; font-size:12.8px; padding:6px 11px;" />
        <button class="btn btn-primary btn-add-warehouse" style="padding:6px 14px;">Add</button>
      </div>
      <div style="display:flex;">
        <button class="btn btn-revert-cu-settings" style="padding:6px 14px; margin-right:8px;" title="Delete unsaved changes">Revert</button>
        <button class="btn btn-save-cu-settings" style="padding:6px 14px; border-color:var(--accent); color:var(--accent);">Save Settings</button>
      </div>
    </div>`;
    
    container.innerHTML = html;

    // -- Event Listeners (Bi-directional Data Binding) --
    
    // Senkronizasyon
    document.querySelectorAll(".cu-wh-input").forEach(input => {
      input.addEventListener("change", (e) => {
        const wh = e.target.dataset.wh;
        const prop = e.target.dataset.prop;
        if (isV2) {
          currentCuSettings.warehouses[wh][prop] = parseFloat(e.target.value) || 0;
        } else {
          currentCuSettings.warehouses[wh] = parseFloat(e.target.value) || 0;
        }
      });
    });

    // Etiket Ekleme
    document.querySelectorAll(".tag-input").forEach(input => {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          const val = e.target.value.trim();
          const col = e.target.dataset.col;
          if (val && !currentCuSettings.columns[col].includes(val)) {
            currentCuSettings.columns[col].push(val);
            renderCostUpdaterUI(currentCuSettings, isV2);
          }
        }
      });
    });

    // Etiket Silme
    document.querySelectorAll(".file-chip-remove").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const col = e.currentTarget.dataset.col;
        const val = e.currentTarget.dataset.val;
        currentCuSettings.columns[col] = currentCuSettings.columns[col].filter(v => v !== val);
        renderCostUpdaterUI(currentCuSettings, isV2);
      });
    });

    // Çökmeyi Engelleyen Modern Depo Silme (Satır İçi Onay)
    document.querySelectorAll(".btn-delete-wh").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const wh = e.currentTarget.dataset.wh;
        if (e.currentTarget.dataset.confirm === "1") {
          delete currentCuSettings.warehouses[wh];
          renderCostUpdaterUI(currentCuSettings, isV2);
        } else {
          // İki aşamalı doğrulama: Buton 3 saniyeliğine "Sil?" uyarısına dönüşür
          e.currentTarget.dataset.confirm = "1";
          e.currentTarget.innerHTML = "Delete?";
          e.currentTarget.style.fontSize = "11px";
          e.currentTarget.style.backgroundColor = "var(--err)";
          e.currentTarget.style.color = "#fff";
          e.currentTarget.style.padding = "6px 8px";
          e.currentTarget.style.borderRadius = "4px";
          e.currentTarget.style.top = "6px";
          e.currentTarget.style.right = "6px";
          
          setTimeout(() => {
            if (document.body.contains(e.currentTarget)) { // DOM'dan silinmediyse sıfırla
              e.currentTarget.dataset.confirm = "0";
              e.currentTarget.innerHTML = "&times;";
              e.currentTarget.style = "position:absolute; top:8px; right:8px; background:transparent; border:none; color:var(--err); cursor:pointer; font-weight:bold; font-size:16px; line-height:1;";
            }
          }, 3000);
        }
      });
    });
  

    // Blokajsız Yeni Depo Ekleme
    const addWhBtn = container.querySelector(".btn-add-warehouse");
    const addWhInput = container.querySelector(".new-wh-input");
    
    if (addWhBtn && addWhInput) {
      addWhBtn.addEventListener("click", () => {
        const newWh = addWhInput.value.trim().toUpperCase();
        if (newWh) {
          if (!currentCuSettings.warehouses[newWh]) {
            if (isV2) {
              currentCuSettings.warehouses[newWh] = { v2_additional_cost: 0, v2_equation: 1, v2_warehouse_fee: 0 };
            } else {
              currentCuSettings.warehouses[newWh] = 0;
            }
            renderCostUpdaterUI(currentCuSettings, isV2);
          } else {
            toast("This warehouse code is already in the system.");
          }
        }
      });
      
      // Enter'a basılınca butonu tetikler
      addWhInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter") addWhBtn.click();
      });
    }

    // Bağımsız Diske Yazma İşlemi (Save)
    const saveSettingsBtn = container.querySelector(".btn-save-cu-settings");
    if (saveSettingsBtn) {
      saveSettingsBtn.addEventListener("click", async () => {
        saveSettingsBtn.disabled = true;
        const fileName = isV2 ? "costupdater2_settings.json" : "costupdater_settings.json";
        await api().save_settings(fileName, JSON.stringify(currentCuSettings));
        toast("Settings saved to disk successfully.");
        saveSettingsBtn.disabled = false;
      });
    }
    const revertSettingsBtn = document.getElementById("btn-revert-cu-settings");
    if (revertSettingsBtn) {
      revertSettingsBtn.addEventListener("click", () => {
        loadCostUpdaterSettings();
        toast("Changes reverted.");
      });
    }
  });
}

function FBATablesScrollHandler() {
  const scrollContainers = document.querySelectorAll('.fba-tables');

  scrollContainers.forEach(container => {
    let isDown = false;
    let startX;
    let scrollLeft;

    container.addEventListener('mousedown', (e) => {
      // Eğer tıklanan şey bir input veya buton değilse kaydırmayı başlat
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'A') return;
      
      isDown = true;
      container.classList.add('grab');
      startX = e.pageX - container.offsetLeft;
      scrollLeft = container.scrollLeft;
    });

    container.addEventListener('mouseleave', () => {
      isDown = false;
      container.classList.remove('grab');
    });

    container.addEventListener('mouseup', () => {
      isDown = false;
      container.classList.remove('grab');
    });

    container.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - container.offsetLeft;
      const walk = (x - startX) * 1.5; // Kaydırma hızı çarpanı (istersen artırıp azaltabilirsin)
      container.scrollLeft = scrollLeft - walk;
    });
  });
}

document.getElementById("cu-version-toggle").addEventListener("change", loadCostUpdaterSettings);
whenApiReady(loadCostUpdaterSettings);

document.getElementById("cu-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("cu-output-folder").value.trim();
  const isV2 = document.getElementById("cu-version-toggle").checked;
  
  if (!outputFolder) return toast("No target folder selected.");
  if (!cuZone.files.length) return toast("No CSV file to process.");
  
  // Veriler anlık olarak currentCuSettings objesine senkronize edildiğinden DOM kazımaya gerek yoktur.
  const fileName = isV2 ? "costupdater2_settings.json" : "costupdater_settings.json";
  await api().save_settings(fileName, JSON.stringify(currentCuSettings));
  
  prepareJobUI("cu");
  await api().run_costupdater(cuZone.files[0], outputFolder, currentCuSettings, isV2 ? 2 : 1);
});

// Restock
const EXCEL_TYPES = ["Excel Files (*.xlsx;*.xls)", "All files (*.*)"];
const CSV_TYPE = ["CSV Files (*.csv)", "All files (*.*)"];
const rsHamZone = new FileDropZone({ zoneId: "rs-ham-dropzone", listId: "rs-ham-file-list", fileTypes: EXCEL_TYPES, reorderable: true });
const rsExportZone = new FileDropZone({ zoneId: "rs-export-dropzone", listId: "rs-export-file-list", fileTypes: EXCEL_TYPES });
const rsRestockZone = new FileDropZone({ zoneId: "rs-restock-dropzone", listId: "rs-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });

function updateRestockCardVisibility() {
  const exportOn = document.getElementById("rs-export-toggle").checked;
  const restockOn = document.getElementById("rs-restock-toggle").checked;
  document.getElementById("rs-export-card").style.display = exportOn ? "" : "none";
  document.getElementById("rs-restock-card").style.display = restockOn ? "" : "none";
}
document.getElementById("rs-export-toggle").addEventListener("change", (e) => {
  if (e.target.checked === false && document.getElementById("rs-restock-toggle").checked) document.getElementById("rs-restock-toggle").checked = false;
  updateRestockCardVisibility();
});
document.getElementById("rs-restock-toggle").addEventListener("change", (e) => {
  if (e.target.checked) document.getElementById("rs-export-toggle").checked = true;
  updateRestockCardVisibility();
});
updateRestockCardVisibility();

// Restock Modülü JSON Editor Bağlantısı
const restockEditor = new JSONConfigEditor("rs-settings-container", "restock_settings.json", [
  { key: "columns", title: "Column Mappings", type: "tags" },
  { key: "deposits", title: "Warehouse Costs", type: "key-value" }
]);
const mainRestockEditor = new JSONConfigEditor("rs-settings-main-container", "restock_settings.json", [
  { key: "columns", title: "Column Mappings", type: "tags" },
  { key: "deposits", title: "Warehouse Costs", type: "key-value" }
]);

document.getElementById("rs-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("rs-output-folder").value.trim();
  const doExport = document.getElementById("rs-export-toggle").checked;
  const doRestock = document.getElementById("rs-restock-toggle").checked;

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!rsHamZone.files.length) return toast("Drop at least one raw supplier file.");
  if (doExport && !rsExportZone.files.length) return toast("Export step is on — drop export file(s).");
  if (doRestock && !rsRestockZone.files.length) return toast("Restock step is on — drop the main workbook.");

  // Editor üzerindeki güncel JSON verisini diske kaydet
  await api().save_settings("restock_settings.json", JSON.stringify(restockEditor.data));
  prepareJobUI("rs");
  
  // Metin dosyası (.txt) değil JSON sözlüğü gönderilir
  await api().run_restock(rsHamZone.files, rsExportZone.files, rsRestockZone.files, doExport, doRestock, document.getElementById("rs-save-name").value.trim() || "restock_sonuc", outputFolder, restockEditor.data);
});

// Future Price
const fpRestockZone = new FileDropZone({ zoneId: "fp-restock-dropzone", listId: "fp-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const fpFutureZone = new FileDropZone({ zoneId: "fp-future-dropzone", listId: "fp-future-file-list", multiple: false, fileTypes: EXCEL_TYPES });
document.getElementById("fp-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("fp-output-folder").value.trim();
  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!fpRestockZone.files.length || !fpFutureZone.files.length) return toast("Drop both restock and future price files.");
  prepareJobUI("fp");
  await api().run_future_price(fpRestockZone.files[0], fpFutureZone.files[0], document.getElementById("fp-save-name").value.trim() || "Future_Price_Sonuc", outputFolder);
});

// Order Creator
const ocRestockZone = new FileDropZone({ zoneId: "oc-restock-dropzone", listId: "oc-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const ocOrderformZone = new FileDropZone({ zoneId: "oc-orderform-dropzone", listId: "oc-orderform-file-list", multiple: false, fileTypes: EXCEL_TYPES });
document.getElementById("oc-template-btn").addEventListener("click", () => api().open_template_folder());
const orderEditor = new JSONConfigEditor("oc-settings-container", "ordercreate_settings.json", [
  { key: "restock_columns", title: "Restock File Columns", type: "tags" },
  { key: "orderform_columns", title: "Order Form File Columns", type: "tags" }
]);
const mainOrderEditor = new JSONConfigEditor("oc-settings-main-container", "ordercreate_settings.json", [
  { key: "restock_columns", title: "Restock File Columns", type: "tags" },
  { key: "orderform_columns", title: "Order Form File Columns", type: "tags" }
]);
document.getElementById("oc-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("oc-output-folder").value.trim();
  if (!outputFolder || !ocRestockZone.files.length || !ocOrderformZone.files.length) return toast("Ensure files and destination folder are set.");
  
  await api().save_settings("ordercreate_settings.json", JSON.stringify(orderEditor.data));
  prepareJobUI("oc");
  
  await api().run_order_create(ocRestockZone.files, ocOrderformZone.files, outputFolder, orderEditor.data);
});

// Invoice Processor
const invZone = new FileDropZone({ zoneId: "inv-dropzone", listId: "inv-file-list", fileTypes: ["CSV Files (*.csv)", "All files (*.*)"] });
const invoiceEditor = new JSONConfigEditor("inv-settings-container", "invoice_settings.json", [
  { key: "columns", title: "Column Mappings", type: "tags" }
]);
const mainInvoiceEditor = new JSONConfigEditor("inv-settings-main-container", "invoice_settings.json", [
  { key: "columns", title: "Column Mappings", type: "tags" }
]);
document.getElementById("inv-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("inv-output-folder").value.trim();
  const settingsContent = document.getElementById("inv-settings").value;
  if (!outputFolder || !invZone.files.length) return toast("Drop files and select destination.");
  await api().save_settings("invoice_settings.json", JSON.stringify(invoiceEditor.data));
  prepareJobUI("inv");
  await api().run_invoice(invZone.files, outputFolder, invoiceEditor.data, document.getElementById("inv-delzero-toggle").checked);
});

// Shipment Creator
const scInvoiceZone = new FileDropZone({ zoneId: "sc-invoice-dropzone", listId: "sc-invoice-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const scOrderformZone = new FileDropZone({ zoneId: "sc-orderform-dropzone", listId: "sc-orderform-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const scRestockZone = new FileDropZone({ zoneId: "sc-restock-dropzone", listId: "sc-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const shipmentEditor = new JSONConfigEditor("sc-settings-container", "shipment_settings.json", [
  { key: "restock_columns", title: "Restock File Columns", type: "tags" },
  { key: "orderform_columns", title: "Order Form File Columns", type: "tags" },
  { key: "invoice_columns", title: "Invoice File Columns", type: "tags" }
]);
const mainShipmentEditor = new JSONConfigEditor("sc-settings-main-container", "shipment_settings.json", [
  { key: "restock_columns", title: "Restock File Columns", type: "tags" },
  { key: "orderform_columns", title: "Order Form File Columns", type: "tags" },
  { key: "invoice_columns", title: "Invoice File Columns", type: "tags" }
]);
document.getElementById("sc-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("sc-output-folder").value.trim();
  const dcCode = document.getElementById("sc-dc-code").value.trim();
  if (!outputFolder || !dcCode || !scInvoiceZone.files.length || !scOrderformZone.files.length || !scRestockZone.files.length) return toast("Fill all fields and drop files.");
  api().set_memory_value("sc-dc-code", dcCode);
  await api().save_settings("shipment_settings.json", JSON.stringify(shipmentEditor.data));
  prepareJobUI("sc");
  await api().run_shipment_creator(scInvoiceZone.files, scOrderformZone.files, scRestockZone.files, dcCode, document.getElementById("sc-save-name").value.trim() || "shipment_sonuc", outputFolder, shipmentEditor.data);
});

// Invoice Finder
const ifAllinvoicesZone = new FileDropZone({ zoneId: "if-allinvoices-dropzone", listId: "if-allinvoices-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const ifSourceZone = new FileDropZone({ zoneId: "if-source-dropzone", listId: "if-source-file-list", multiple: false, fileTypes: EXCEL_TYPES });
document.getElementById("if-mode-toggle").addEventListener("change", (e) => {
  const isDate = e.target.checked;
  document.getElementById("if-date-mode-card").style.display = isDate ? "" : "none";
  document.getElementById("if-upc-mode-card").style.display = isDate ? "none" : "";
  document.getElementById("if-mode-label").textContent = isDate ? "Mode: search by date (using pasted Amazon data)" : "Mode: search by UPC list";
});
document.getElementById("if-instructions-btn").addEventListener("click", async () => {
  document.getElementById("if-instructions-modal").classList.add("visible");
  document.getElementById("if-instructions-body").textContent = await api().get_invoice_finder_instructions() || "No instructions found.";
});
document.getElementById("if-instructions-close").addEventListener("click", () => document.getElementById("if-instructions-modal").classList.remove("visible"));
document.getElementById("if-instructions-modal").addEventListener("click", (e) => { if(e.target.id === "if-instructions-modal") e.target.classList.remove("visible"); });

document.getElementById("if-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("if-output-folder").value.trim();
  const invoiceFolder = document.getElementById("if-invoice-folder").value.trim();
  if (!outputFolder || !invoiceFolder || !ifAllinvoicesZone.files.length) return toast("Provide all required folders and ALL INVOICES file.");
  
  prepareJobUI("if");

  if (document.getElementById("if-mode-toggle").checked) {
    if (!document.getElementById("if-date").value.trim() || !ifSourceZone.files.length) { document.getElementById("if-run-btn").disabled = false; return toast("Provide cutoff date and source file."); }
    await api().run_invoice_finder_date_mode(ifSourceZone.files[0], ifAllinvoicesZone.files[0], invoiceFolder, outputFolder, document.getElementById("if-date").value.trim());
  } else {
    if (!document.getElementById("if-upcs").value.trim() || !document.getElementById("if-months").value.trim()) { document.getElementById("if-run-btn").disabled = false; return toast("Provide UPCs and months."); }
    await api().run_invoice_finder_upc_mode(ifAllinvoicesZone.files[0], invoiceFolder, outputFolder, document.getElementById("if-upcs").value.trim(), document.getElementById("if-months").value.trim());
  }
});

// Expiration
whenApiReady(async () => {
  const creds = await api().get_expiration_credentials();
  if (creds.username) document.getElementById("exp-username").value = creds.username;
  if (creds.password) document.getElementById("exp-password").value = creds.password;
});
document.getElementById("exp-run-btn").addEventListener("click", async () => {
  const [username, password, shipmentIds, outputFolder] = ["exp-username", "exp-password", "exp-shipment-ids", "exp-output-folder"].map(id => document.getElementById(id).value.trim());
  if (!username || !password || !shipmentIds || !outputFolder) return toast("Fill all required fields.");
  prepareJobUI("exp");
  await api().run_expiration(username, password, shipmentIds, outputFolder, document.getElementById("exp-remember-toggle").checked);
});

// PK EXTRACTOR

const peCsvZone = new FileDropZone({ zoneId: "pe-csv-dropzone", listId: "pe-csv-file-list", multiple: false, fileTypes: CSV_TYPE });
document.getElementById("pe-run-btn").addEventListener("click", async () => {
  if (!peCsvZone.files.length) return toast("Fill all fields and drop files.");
  prepareJobUI("pe");
  await api().run_pk_extractor(peCsvZone.files[0]);
});


// Updates View
const updatesView = {
  currentVersion: "",
  latestData: null,
  async init() {
    this.currentVersion = await api().get_current_version();
    const vEl = document.getElementById("updates-current-version"); if (vEl) vEl.textContent = this.currentVersion;
    document.getElementById("updates-check-btn")?.addEventListener("click", () => this.check());
    document.getElementById("updates-install-btn")?.addEventListener("click", () => this.install());
    document.getElementById("updates-notes-btn")?.addEventListener("click", () => {
      const rawNotes = this.latestData?.notes || "No notes.";
      document.getElementById("if-instructions-body").innerHTML = parseMarkdown(rawNotes);
      document.getElementById("if-instructions-modal").classList.add("visible");
    });
  },
  async check() {
    document.getElementById("updates-check-btn").disabled = true;
    document.getElementById("updates-status").textContent = "Checking…";
    await api().run_check_for_updates();
  },
  install() {
    const asset = this.latestData?.assets.find(a => a.name.endsWith(".exe")) || this.latestData?.assets[0];
    if (!asset) return;
    document.getElementById("updates-status").textContent = "Downloading…";
    document.getElementById("updates-progress").style.display = "block";
    api().run_download_update(asset.browser_download_url);
  }
};

window.addEventListener("update-status", e => {
  const s = document.getElementById("updates-status");
  document.getElementById("updates-check-btn").disabled = false;
  
  if(e.detail.state === "update-available") { 
      s.textContent = `New version available: ${e.detail.version}`; 
      document.getElementById("updates-install-btn").style.display = ""; 
      document.getElementById("updates-notes-btn").style.display = ""; 
      updatesView.latestData = e.detail; 
  } else if (e.detail.state === "up-to-date") {
      // Ekrana sadece "up-to-date" yazdırmak yerine durumu netleştir.
      s.textContent = `Uygulama güncel. (Sunucudaki sürüm: ${e.detail.version})`;
  } else {
      s.textContent = e.detail.state;
  }
});

window.addEventListener("update-badge", e => {
  const data = e.detail;
  updatesView.latestData = data;
  
  const updateNavItem = document.querySelector('.nav-item[data-view="updates"]');
  if (updateNavItem) {
      updateNavItem.classList.add("has-update");
  }
  const s = document.getElementById("updates-status");
  const b = document.getElementById("update-badge");
  if (b) { b.classList.add("visible"); b.innerHTML = data.version; }
  if (s) s.textContent = `New version available: ${data.version}`;
  const installBtn = document.getElementById("updates-install-btn");
  if (installBtn) installBtn.style.display = "";
  const notesBtn = document.getElementById("updates-notes-btn");
  if (notesBtn) notesBtn.style.display = "";
  
  toast(`New update is available: ${data.version}`);
});

// Responsive Init
function applyResponsiveSettings() {
  const narrow = document.querySelector(".main")?.clientWidth < 720;
  document.querySelectorAll(".settings-card").forEach(c => { if(narrow) c.classList.add("collapsed"); else if(c.dataset.userToggled!=="1") c.classList.remove("collapsed"); });
}
window.addEventListener("resize", () => requestAnimationFrame(applyResponsiveSettings));
document.addEventListener("click", e => { 
  const head = e.target.closest(".settings-card-head"); 
  if (head) {
    const card = head.closest(".settings-card");
    card.classList.toggle("collapsed");
    card.dataset.userToggled = "1";
  }
});
whenApiReady(() => { 
  updatesView.init(); 
  applyResponsiveSettings(); 
  if (api() && api().run_silent_update_check) {
      api().run_silent_update_check();
  }
});
whenApiReady(async () => {
  FBATablesScrollHandler();
  restockEditor.load();
  orderEditor.load();
  invoiceEditor.load();
  shipmentEditor.load();
});
  // Eski whenApiReady fonksiyonunun geri kalan kodları aynı kalacak...
// =======================================================================
// FLUID LAYOUT ZOOM & SCROLL FIX (Ctrl + Scroll / Ctrl + Keys)
// =======================================================================
let currentZoom = 1.0;

function updateAppZoom(newZoom, save = true) {
  currentZoom = Math.max(0.5, Math.min(newZoom, 2.0));
  
  const appEl = document.querySelector(".app");
  if (appEl) {
    appEl.style.transform = `scale(${currentZoom})`;
    appEl.style.width = `${(100 / currentZoom)}vw`;
    appEl.style.height = `${(100 / currentZoom)}vh`;
  }
  
  // Değer değiştiğinde Python tarafındaki hafızaya (last_paths.json) kaydet
  if (save && api()) {
    api().set_memory_value("app_zoom", currentZoom);
  }
}

// Ctrl + Fare Tekeri ile Yakınlaştırma/Uzaklaştırma
window.addEventListener('wheel', function(e) {
  if (e.ctrlKey) {
    e.preventDefault();
    if (e.deltaY < 0) {
      updateAppZoom(currentZoom + 0.1);
    } else {
      updateAppZoom(currentZoom - 0.1);
    }
  }
}, { passive: false });

// Ctrl + (+), Ctrl + (-) ve Ctrl + (0) kısayolları
window.addEventListener('keydown', function(e) {
  if (e.ctrlKey) {
    if (e.key === '=' || e.key === '+') {
      e.preventDefault();
      updateAppZoom(currentZoom + 0.1);
    } else if (e.key === '-') {
      e.preventDefault();
      updateAppZoom(currentZoom - 0.1);
    } else if (e.key === '0') {
      e.preventDefault();
      updateAppZoom(1.0); // Varsayılana sıfırla (%100)
    }
  }
});