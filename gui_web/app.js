/* =========================================================================
   Operations Toolkit — frontend logic
   Talks to Python through window.pywebview.api (see app.py)
   ========================================================================= */

// ---------------------------------------------------------------------
// Wait for pywebview to be ready (it injects window.pywebview asynchronously)
// ---------------------------------------------------------------------
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

// ---------------------------------------------------------------------
// Toast helper
// ---------------------------------------------------------------------
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
document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item[data-view]").forEach((i) => i.classList.remove("active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    item.classList.add("active");
    document.getElementById("view-" + item.dataset.view).classList.add("active");
  });
});

// ---------------------------------------------------------------------
// Browse-folder buttons (generic, works for any input via data-browse-folder)
// ---------------------------------------------------------------------
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

// Restore remembered path values on load
whenApiReady(async () => {
  const mem = await api().get_memory();
  document.querySelectorAll("input[type=text]").forEach((input) => {
    if (mem[input.id] && !input.value) input.value = mem[input.id];
  });
  // Persist on manual edits too
  document.querySelectorAll("input[type=text]").forEach((input) => {
    input.addEventListener("change", () => api().set_memory_value(input.id, input.value));
  });

  // Hide the loading overlay once the page is interactive
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingFill = document.getElementById("loading-bar-fill");
  if (loadingOverlay) {
    if (loadingFill) loadingFill.style.width = "100%";
    setTimeout(() => {
      loadingOverlay.classList.add("loaded");
      setTimeout(() => {
        if (loadingOverlay.parentNode) loadingOverlay.parentNode.removeChild(loadingOverlay);
      }, 400);
    }, 150);
  }
});

// =======================================================================
// LOADING-SCREEN STATUS UPDATES
// =======================================================================
// Python pushes these during staged imports (see app.py _set_loading_status).
// For now the overlay always completes its animation above regardless ---
// this hook is kept for future progress reporting if imports are refactored.
window.addEventListener("loading-status", (e) => {
  const { message, percent } = e.detail;
  const statusEl = document.getElementById("loading-status");
  const fillEl = document.getElementById("loading-bar-fill");
  if (statusEl) statusEl.textContent = message;
  if (fillEl && typeof percent === "number") fillEl.style.width = percent + "%";
});

// ---------------------------------------------------------------------
// Generic dropzone + file list manager
// Each instance tracks an array of absolute file paths.
//
// Real filesystem paths are NOT available through plain browser drag-drop
// events (browsers hide them for security). pywebview restores this on the
// Python side via window.dom — see app.py's bind_dropzones() / _handle_drop().
// Python resolves which .dropzone element received the drop (by id, bound
// at startup) and fires a 'files-dropped' CustomEvent with {zoneId, paths}.
// Each FileDropZone instance registers itself here so the right instance
// picks up the event. Dragover/dragleave styling still works as normal CSS-
// only feedback since that doesn't need real paths.
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
    this.fileTypes = fileTypes; // for native dialog filter, e.g. ['Excel Files (*.xlsx;*.xls)']
    this.multiple = multiple;
    this.accept = accept; // function(filename) => bool, for filtering dropped/picked files
    this.reorderable = reorderable; // enables drag-handle + up/down arrows; order is then meaningful data
    this.files = [];
    this._dragFromIndex = null;

    dropZoneRegistry[zoneId] = this;

    this.zone.addEventListener("click", () => this.browse());

    // Visual feedback only — actual file paths arrive via the
    // 'files-dropped' event dispatched from Python (see above).
    this.zone.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.zone.classList.add("drag-over");
    });
    this.zone.addEventListener("dragleave", () => this.zone.classList.remove("drag-over"));
    this.zone.addEventListener("drop", (e) => {
      e.preventDefault();
      this.zone.classList.remove("drag-over");
    });
  }

  async browse() {
    const picked = await api().pick_files(this.fileTypes, this.multiple);
    if (picked && picked.length) this.addFiles(picked);
  }

  addFiles(paths) {
    for (const p of paths) {
      if (this.accept && !this.accept(p)) continue;
      if (!this.multiple) this.files = [];
      if (!this.files.includes(p)) this.files.push(p);
    }
    this.render();
  }

  removeFile(p) {
    this.files = this.files.filter((f) => f !== p);
    this.render();
  }

  moveFile(fromIndex, toIndex) {
    if (toIndex < 0 || toIndex >= this.files.length) return;
    const [item] = this.files.splice(fromIndex, 1);
    this.files.splice(toIndex, 0, item);
    this.render();
  }

  clear() {
    this.files = [];
    this.render();
  }

  render() {
    this.list.innerHTML = "";
    this.files.forEach((p, index) => {
      const chip = this.reorderable ? this._renderReorderableChip(p, index) : this._renderChip(p);
      this.list.appendChild(chip);
    });
  }

  _renderChip(p) {
    const name = p.split(/[\\/]/).pop();
    const chip = document.createElement("div");
    chip.className = "file-chip";
    chip.innerHTML = `
      <svg class="file-chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5Z"/><path d="M14 3v5h5"/></svg>
      <span class="file-chip-name" title="${p}">${name}</span>
      <span class="file-chip-remove" data-path="${encodeURIComponent(p)}">&times;</span>`;
    chip.querySelector(".file-chip-remove").addEventListener("click", (ev) => {
      ev.stopPropagation();
      this.removeFile(decodeURIComponent(ev.target.dataset.path));
    });
    return chip;
  }

  _renderReorderableChip(p, index) {
    const name = p.split(/[\\/]/).pop();
    const chip = document.createElement("div");
    chip.className = "file-chip reorderable";
    chip.draggable = true;
    chip.dataset.index = String(index);

    const isFirst = index === 0;
    const isLast = index === this.files.length - 1;

    chip.innerHTML = `
      <span class="file-chip-handle" title="Drag to reorder">
        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="8" cy="6" r="1.5"/><circle cx="8" cy="12" r="1.5"/><circle cx="8" cy="18" r="1.5"/><circle cx="16" cy="6" r="1.5"/><circle cx="16" cy="12" r="1.5"/><circle cx="16" cy="18" r="1.5"/></svg>
      </span>
      <span class="file-chip-rank">${index + 1}</span>
      <svg class="file-chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8l-5-5Z"/><path d="M14 3v5h5"/></svg>
      <span class="file-chip-name" title="${p}">${name}</span>
      <span class="file-chip-arrows">
        <span class="file-chip-arrow ${isFirst ? "disabled" : ""}" data-dir="up" title="Move up">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 15l7-7 7 7"/></svg>
        </span>
        <span class="file-chip-arrow ${isLast ? "disabled" : ""}" data-dir="down" title="Move down">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 9l7 7 7-7"/></svg>
        </span>
      </span>
      <span class="file-chip-remove" data-path="${encodeURIComponent(p)}">&times;</span>`;

    chip.querySelector(".file-chip-remove").addEventListener("click", (ev) => {
      ev.stopPropagation();
      this.removeFile(decodeURIComponent(ev.target.dataset.path));
    });
    chip.querySelectorAll(".file-chip-arrow").forEach((arrowEl) => {
      arrowEl.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const dir = ev.currentTarget.dataset.dir;
        this.moveFile(index, dir === "up" ? index - 1 : index + 1);
      });
    });

    chip.addEventListener("dragstart", (ev) => {
      this._dragFromIndex = index;
      chip.classList.add("dragging");
      ev.dataTransfer.effectAllowed = "move";
      ev.dataTransfer.setData("text/plain", String(index)); // some browsers require data to be set
    });
    chip.addEventListener("dragend", () => {
      chip.classList.remove("dragging");
      this.list.querySelectorAll(".file-chip").forEach((c) => {
        c.classList.remove("drag-over-top", "drag-over-bottom");
      });
    });
    chip.addEventListener("dragover", (ev) => {
      ev.preventDefault();
      if (this._dragFromIndex === null || this._dragFromIndex === index) return;
      const rect = chip.getBoundingClientRect();
      const before = ev.clientY - rect.top < rect.height / 2;
      chip.classList.toggle("drag-over-top", before);
      chip.classList.toggle("drag-over-bottom", !before);
    });
    chip.addEventListener("dragleave", () => {
      chip.classList.remove("drag-over-top", "drag-over-bottom");
    });
    chip.addEventListener("drop", (ev) => {
      ev.preventDefault();
      ev.stopPropagation(); // don't let this bubble to the dropzone's OS-file drop handler
      if (this._dragFromIndex === null || this._dragFromIndex === index) return;
      const rect = chip.getBoundingClientRect();
      const before = ev.clientY - rect.top < rect.height / 2;
      let targetIndex = before ? index : index + 1;
      if (this._dragFromIndex < targetIndex) targetIndex -= 1;
      this.moveFile(this._dragFromIndex, targetIndex);
      this._dragFromIndex = null;
    });

    return chip;
  }
}

// ---------------------------------------------------------------------
// Console / job-status helpers shared by all tool panels
// ---------------------------------------------------------------------
function logLine(bodyId, message, cls = "") {
  const body = document.getElementById(bodyId);
  const line = document.createElement("div");
  line.className = "console-line " + cls;
  line.textContent = message;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
}

function setStatus(dotId, textId, state, label) {
  const dot = document.getElementById(dotId);
  const text = document.getElementById(textId);
  dot.className = "console-dot " + state;
  text.textContent = label;
}

function showResult(bannerId, ok, message, outputPath) {
  const el = document.getElementById(bannerId);
  el.className = "result-banner visible " + (ok ? "ok" : "error");
  el.innerHTML = `<span>${message}</span>`;
  if (ok && outputPath) {
    const openBtn = document.createElement("button");
    openBtn.className = "btn";
    openBtn.textContent = "Open folder";
    openBtn.addEventListener("click", () => api().open_folder(outputPath));
    el.appendChild(openBtn);
  }
}

// =======================================================================
// CONVERTER
// =======================================================================
const convZone = new FileDropZone({
  zoneId: "conv-dropzone",
  listId: "conv-file-list",
  fileTypes: ["Convertible Files (*.csv;*.xlsx;*.xls;*.txt)", "All files (*.*)"],
});

function convExtFor(type) {
  return { csv: ".csv", xlsx: ".xlsx", txt: ".txt" }[type] || "";
}

document.getElementById("conv-input-type").addEventListener("change", (e) => {
  document.getElementById("conv-type-hint").textContent = convExtFor(e.target.value) + " files";
  convZone.clear();
});

document.getElementById("conv-run-btn").addEventListener("click", async () => {
  const inputType = document.getElementById("conv-input-type").value;
  const outputType = document.getElementById("conv-output-type").value;
  const outputFolder = document.getElementById("conv-output-folder").value.trim();

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!convZone.files.length) return toast("Drop at least one file to convert.");

  document.getElementById("conv-console").classList.add("visible");
  document.getElementById("conv-result").classList.remove("visible");
  document.getElementById("conv-log").innerHTML = "";
  document.getElementById("conv-progress-fill").style.width = "0%";
  setStatus("conv-dot", "conv-status-text", "running", "Converting…");
  document.getElementById("conv-run-btn").disabled = true;

  await api().run_converter(convZone.files, outputFolder, inputType, outputType);
});

// =======================================================================
// COST UPDATER
// =======================================================================
const cuZone = new FileDropZone({
  zoneId: "cu-dropzone",
  listId: "cu-file-list",
  multiple: false,
  fileTypes: ["CSV Files (*.csv)", "All files (*.*)"],
  accept: (p) => p.toLowerCase().endsWith(".csv"),
});

async function loadCostUpdaterSettings() {
  const isV2 = document.getElementById("cu-version-toggle").checked;
  const filename = isV2 ? "costupdater2_settings.txt" : "costupdater_settings.txt";
  const content = await api().get_settings(filename);
  document.getElementById("cu-settings").value = content;
}
document.getElementById("cu-version-toggle").addEventListener("change", loadCostUpdaterSettings);
whenApiReady(loadCostUpdaterSettings);

document.getElementById("cu-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("cu-output-folder").value.trim();
  const isV2 = document.getElementById("cu-version-toggle").checked;
  const settingsContent = document.getElementById("cu-settings").value;
  const filename = isV2 ? "costupdater2_settings.txt" : "costupdater_settings.txt";

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!cuZone.files.length) return toast("Drop the CSV file to process.");

  await api().save_settings(filename, settingsContent);

  document.getElementById("cu-console").classList.add("visible");
  document.getElementById("cu-result").classList.remove("visible");
  document.getElementById("cu-log").innerHTML = "";
  setStatus("cu-dot", "cu-status-text", "running", "Running…");
  document.getElementById("cu-run-btn").disabled = true;

  await api().run_costupdater(cuZone.files[0], outputFolder, settingsContent, isV2 ? 2 : 1);
});

// =======================================================================
// RESTOCK
// =======================================================================
const EXCEL_TYPES = ["Excel Files (*.xlsx;*.xls)", "All files (*.*)"];
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
  // Mirroring the original tool: turning restock on forces export on too.
  if (e.target.checked === false && document.getElementById("rs-restock-toggle").checked) {
    document.getElementById("rs-restock-toggle").checked = false;
  }
  updateRestockCardVisibility();
});
document.getElementById("rs-restock-toggle").addEventListener("change", (e) => {
  if (e.target.checked) document.getElementById("rs-export-toggle").checked = true;
  updateRestockCardVisibility();
});
updateRestockCardVisibility();

async function loadRestockSettings() {
  const content = await api().get_settings("restock_settings.txt");
  document.getElementById("rs-settings").value = content;
}
whenApiReady(loadRestockSettings);

document.getElementById("rs-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("rs-output-folder").value.trim();
  const saveName = document.getElementById("rs-save-name").value.trim() || "restock_sonuc";
  const settingsContent = document.getElementById("rs-settings").value;
  const doExport = document.getElementById("rs-export-toggle").checked;
  const doRestock = document.getElementById("rs-restock-toggle").checked;

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!rsHamZone.files.length) return toast("Drop at least one raw supplier file.");
  if (doExport && !rsExportZone.files.length) return toast("Export step is on — drop export file(s).");
  if (doRestock && !rsRestockZone.files.length) return toast("Restock step is on — drop the main workbook.");

  await api().save_settings("restock_settings.txt", settingsContent);
  api().set_memory_value("rs-save-name", saveName);

  document.getElementById("rs-console").classList.add("visible");
  document.getElementById("rs-result").classList.remove("visible");
  document.getElementById("rs-log").innerHTML = "";
  document.getElementById("rs-progress-fill").style.width = "0%";
  setStatus("rs-dot", "rs-status-text", "running", "Running…");
  document.getElementById("rs-run-btn").disabled = true;

  await api().run_restock(
    rsHamZone.files,
    rsExportZone.files,
    rsRestockZone.files,
    doExport,
    doRestock,
    saveName,
    outputFolder
  );
});

// =======================================================================
// TSV CONVERTER
// =======================================================================
const tsvZone = new FileDropZone({
  zoneId: "tsv-dropzone",
  listId: "tsv-file-list",
  fileTypes: ["TSV/Text Files (*.tsv;*.txt)", "All files (*.*)"],
});

document.getElementById("tsv-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("tsv-output-folder").value.trim();
  const saveName = document.getElementById("tsv-save-name").value.trim() || "Converted_File";

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!tsvZone.files.length) return toast("Drop at least one file to convert.");

  document.getElementById("tsv-console").classList.add("visible");
  document.getElementById("tsv-result").classList.remove("visible");
  document.getElementById("tsv-log").innerHTML = "";
  setStatus("tsv-dot", "tsv-status-text", "running", "Converting…");
  document.getElementById("tsv-run-btn").disabled = true;

  await api().run_tsv(tsvZone.files, outputFolder, saveName);
});

// =======================================================================
// ORDER CREATOR
// =======================================================================
const ocRestockZone = new FileDropZone({ zoneId: "oc-restock-dropzone", listId: "oc-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const ocOrderformZone = new FileDropZone({ zoneId: "oc-orderform-dropzone", listId: "oc-orderform-file-list", multiple: false, fileTypes: EXCEL_TYPES });

document.getElementById("oc-template-btn").addEventListener("click", () => api().open_template_folder());

async function loadOrderCreateSettings() {
  const content = await api().get_settings("ordercreate_settings.txt");
  document.getElementById("oc-settings").value = content;
}
whenApiReady(loadOrderCreateSettings);

document.getElementById("oc-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("oc-output-folder").value.trim();
  const settingsContent = document.getElementById("oc-settings").value;

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!ocRestockZone.files.length) return toast("Drop the restock file.");
  if (!ocOrderformZone.files.length) return toast("Drop the order form file.");

  await api().save_settings("ordercreate_settings.txt", settingsContent);

  document.getElementById("oc-console").classList.add("visible");
  document.getElementById("oc-result").classList.remove("visible");
  document.getElementById("oc-log").innerHTML = "";
  setStatus("oc-dot", "oc-status-text", "running", "Running…");
  document.getElementById("oc-run-btn").disabled = true;

  await api().run_order_create(ocRestockZone.files, ocOrderformZone.files, outputFolder, settingsContent);
});

// =======================================================================
// INVOICE PROCESSOR
// =======================================================================
const invZone = new FileDropZone({
  zoneId: "inv-dropzone",
  listId: "inv-file-list",
  fileTypes: ["CSV Files (*.csv)", "All files (*.*)"],
});

async function loadInvoiceSettings() {
  const content = await api().get_settings("invoice_settings.txt");
  document.getElementById("inv-settings").value = content;
}
whenApiReady(loadInvoiceSettings);

document.getElementById("inv-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("inv-output-folder").value.trim();
  const settingsContent = document.getElementById("inv-settings").value;
  const deleteZeros = document.getElementById("inv-delzero-toggle").checked;

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!invZone.files.length) return toast("Drop at least one invoice CSV.");

  await api().save_settings("invoice_settings.txt", settingsContent);

  document.getElementById("inv-console").classList.add("visible");
  document.getElementById("inv-result").classList.remove("visible");
  document.getElementById("inv-log").innerHTML = "";
  setStatus("inv-dot", "inv-status-text", "running", "Running…");
  document.getElementById("inv-run-btn").disabled = true;

  await api().run_invoice(invZone.files, outputFolder, settingsContent, deleteZeros);
});

// =======================================================================
// SHIPMENT CREATOR
// =======================================================================
const scInvoiceZone = new FileDropZone({ zoneId: "sc-invoice-dropzone", listId: "sc-invoice-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const scOrderformZone = new FileDropZone({ zoneId: "sc-orderform-dropzone", listId: "sc-orderform-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const scRestockZone = new FileDropZone({ zoneId: "sc-restock-dropzone", listId: "sc-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });

async function loadShipmentSettings() {
  const content = await api().get_settings("shipment_settings.txt");
  document.getElementById("sc-settings").value = content;
}
whenApiReady(loadShipmentSettings);

document.getElementById("sc-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("sc-output-folder").value.trim();
  const saveName = document.getElementById("sc-save-name").value.trim() || "shipment_sonuc";
  const dcCode = document.getElementById("sc-dc-code").value.trim();
  const settingsContent = document.getElementById("sc-settings").value;

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!dcCode) return toast("Enter a DC code.");
  if (!scInvoiceZone.files.length) return toast("Drop the invoice file.");
  if (!scOrderformZone.files.length) return toast("Drop the order form file.");
  if (!scRestockZone.files.length) return toast("Drop the restock file.");

  await api().save_settings("shipment_settings.txt", settingsContent);
  api().set_memory_value("sc-save-name", saveName);
  api().set_memory_value("sc-dc-code", dcCode);

  document.getElementById("sc-console").classList.add("visible");
  document.getElementById("sc-result").classList.remove("visible");
  document.getElementById("sc-log").innerHTML = "";
  setStatus("sc-dot", "sc-status-text", "running", "Running…");
  document.getElementById("sc-run-btn").disabled = true;

  await api().run_shipment_creator(
    scInvoiceZone.files,
    scOrderformZone.files,
    scRestockZone.files,
    dcCode,
    saveName,
    outputFolder,
    settingsContent
  );
});

// =======================================================================
// FUTURE PRICE
// =======================================================================
const fpRestockZone = new FileDropZone({ zoneId: "fp-restock-dropzone", listId: "fp-restock-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const fpFutureZone = new FileDropZone({ zoneId: "fp-future-dropzone", listId: "fp-future-file-list", multiple: false, fileTypes: EXCEL_TYPES });

document.getElementById("fp-run-btn").addEventListener("click", async () => {
  const outputFolder = document.getElementById("fp-output-folder").value.trim();
  const saveName = document.getElementById("fp-save-name").value.trim() || "Future_Price_Sonuc";

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!fpRestockZone.files.length) return toast("Drop the restock file.");
  if (!fpFutureZone.files.length) return toast("Drop the future price file.");

  api().set_memory_value("fp-save-name", saveName);

  document.getElementById("fp-console").classList.add("visible");
  document.getElementById("fp-result").classList.remove("visible");
  document.getElementById("fp-log").innerHTML = "";
  setStatus("fp-dot", "fp-status-text", "running", "Running…");
  document.getElementById("fp-run-btn").disabled = true;

  await api().run_future_price(fpRestockZone.files[0], fpFutureZone.files[0], saveName, outputFolder);
});

// =======================================================================
// INVOICE FINDER
// =======================================================================
const ifAllinvoicesZone = new FileDropZone({ zoneId: "if-allinvoices-dropzone", listId: "if-allinvoices-file-list", multiple: false, fileTypes: EXCEL_TYPES });
const ifSourceZone = new FileDropZone({ zoneId: "if-source-dropzone", listId: "if-source-file-list", multiple: false, fileTypes: EXCEL_TYPES });

// Mirrors the original app's switch: checked/"on" = date mode (default),
// unchecked/"off" = UPC mode. Toggling swaps which card is visible, same
// as the original's upc_active()/upc_deactive() grid show-hide logic.
function updateInvoiceFinderMode() {
  const isDateMode = document.getElementById("if-mode-toggle").checked;
  document.getElementById("if-date-mode-card").style.display = isDateMode ? "" : "none";
  document.getElementById("if-upc-mode-card").style.display = isDateMode ? "none" : "";
  document.getElementById("if-mode-label").textContent = isDateMode
    ? "Mode: search by date (using pasted Amazon data)"
    : "Mode: search by UPC list";
}
document.getElementById("if-mode-toggle").addEventListener("change", updateInvoiceFinderMode);
updateInvoiceFinderMode();

document.getElementById("if-instructions-btn").addEventListener("click", async () => {
  const modal = document.getElementById("if-instructions-modal");
  modal.classList.add("visible");
  const text = await api().get_invoice_finder_instructions();
  document.getElementById("if-instructions-body").textContent = text || "No instructions found.";
});
document.getElementById("if-instructions-close").addEventListener("click", () => {
  document.getElementById("if-instructions-modal").classList.remove("visible");
});
document.getElementById("if-instructions-modal").addEventListener("click", (e) => {
  if (e.target.id === "if-instructions-modal") e.target.classList.remove("visible");
});

document.getElementById("if-run-btn").addEventListener("click", async () => {
  const isDateMode = document.getElementById("if-mode-toggle").checked;
  const outputFolder = document.getElementById("if-output-folder").value.trim();
  const invoiceFolder = document.getElementById("if-invoice-folder").value.trim();

  if (!outputFolder) return toast("Pick a destination folder first.");
  if (!invoiceFolder) return toast("Enter the invoice PDF folder.");
  if (!ifAllinvoicesZone.files.length) return toast("Drop the ALL INVOICES file.");

  api().set_memory_value("if-output-folder", outputFolder);
  api().set_memory_value("if-invoice-folder", invoiceFolder);

  document.getElementById("if-console").classList.add("visible");
  document.getElementById("if-result").classList.remove("visible");
  document.getElementById("if-log").innerHTML = "";
  setStatus("if-dot", "if-status-text", "running", "Running…");
  document.getElementById("if-run-btn").disabled = true;

  if (isDateMode) {
    const date = document.getElementById("if-date").value.trim();
    if (!date) {
      toast("Enter a cutoff date.");
      document.getElementById("if-run-btn").disabled = false;
      return;
    }
    if (!ifSourceZone.files.length) {
      toast("Drop the Amazon source file.");
      document.getElementById("if-run-btn").disabled = false;
      return;
    }
    await api().run_invoice_finder_date_mode(
      ifSourceZone.files[0],
      ifAllinvoicesZone.files[0],
      invoiceFolder,
      outputFolder,
      date
    );
  } else {
    const upcs = document.getElementById("if-upcs").value.trim();
    const months = document.getElementById("if-months").value.trim();
    if (!upcs) {
      toast("Enter at least one UPC.");
      document.getElementById("if-run-btn").disabled = false;
      return;
    }
    if (!months) {
      toast("Enter a months-back value (0 for all time).");
      document.getElementById("if-run-btn").disabled = false;
      return;
    }
    await api().run_invoice_finder_upc_mode(
      ifAllinvoicesZone.files[0],
      invoiceFolder,
      outputFolder,
      upcs,
      months
    );
  }
});

// =======================================================================
// EXPIRATION
// =======================================================================
// Credentials don't go through the generic text-input memory restore (the
// password field is type="password", which that loop already skips) —
// they're loaded explicitly through get_expiration_credentials(), which
// reads the username from memory and the password from the OS credential
// vault via keyring (see app.py's get_saved_credentials()).
async function loadExpirationCredentials() {
  const creds = await api().get_expiration_credentials();
  if (creds.username) document.getElementById("exp-username").value = creds.username;
  if (creds.password) document.getElementById("exp-password").value = creds.password;
}
whenApiReady(loadExpirationCredentials);

document.getElementById("exp-run-btn").addEventListener("click", async () => {
  const username = document.getElementById("exp-username").value.trim();
  const password = document.getElementById("exp-password").value;
  const shipmentIds = document.getElementById("exp-shipment-ids").value.trim();
  const outputFolder = document.getElementById("exp-output-folder").value.trim();
  const remember = document.getElementById("exp-remember-toggle").checked;

  if (!username || !password) return toast("Enter your username and password.");
  if (!shipmentIds) return toast("Enter at least one shipment ID.");
  if (!outputFolder) return toast("Pick a destination folder first.");

  document.getElementById("exp-console").classList.add("visible");
  document.getElementById("exp-result").classList.remove("visible");
  document.getElementById("exp-log").innerHTML = "";
  setStatus("exp-dot", "exp-status-text", "running", "Running…");
  document.getElementById("exp-run-btn").disabled = true;

  await api().run_expiration(username, password, shipmentIds, outputFolder, remember);
});

// =======================================================================
// Shared progress / completion events fired from Python (see app.py _emit)
// =======================================================================
// Each tool listens globally and routes by checking which console is "running".
// Since only one job runs at a time per tool in this simple version, we map
// the currently-active tool by checking button disabled state.

const TOOLS = [
  { btn: "conv-run-btn", log: "conv-log", dot: "conv-dot", status: "conv-status-text", result: "conv-result", fill: "conv-progress-fill" },
  { btn: "tsv-run-btn", log: "tsv-log", dot: "tsv-dot", status: "tsv-status-text", result: "tsv-result", fill: null },
  { btn: "cu-run-btn", log: "cu-log", dot: "cu-dot", status: "cu-status-text", result: "cu-result", fill: null },
  { btn: "rs-run-btn", log: "rs-log", dot: "rs-dot", status: "rs-status-text", result: "rs-result", fill: "rs-progress-fill" },
  { btn: "fp-run-btn", log: "fp-log", dot: "fp-dot", status: "fp-status-text", result: "fp-result", fill: null },
  { btn: "oc-run-btn", log: "oc-log", dot: "oc-dot", status: "oc-status-text", result: "oc-result", fill: null },
  { btn: "inv-run-btn", log: "inv-log", dot: "inv-dot", status: "inv-status-text", result: "inv-result", fill: null },
  { btn: "sc-run-btn", log: "sc-log", dot: "sc-dot", status: "sc-status-text", result: "sc-result", fill: null },
  { btn: "if-run-btn", log: "if-log", dot: "if-dot", status: "if-status-text", result: "if-result", fill: null },
  { btn: "exp-run-btn", log: "exp-log", dot: "exp-dot", status: "exp-status-text", result: "exp-result", fill: null },
];


function activeTool() {
  return TOOLS.find((t) => document.getElementById(t.btn).disabled) || null;
}

window.addEventListener("job-log", (e) => {
  const t = activeTool();
  if (!t) return;
  const { message, color, percent } = e.detail;
  let cls = "";
  if (color === "red") cls = "error";
  else if (color === "#90EE90") cls = "ok";
  else if (color === "yellow") cls = "warn";
  logLine(t.log, message, cls);
  if (t.fill && typeof percent === "number") {
    document.getElementById(t.fill).style.width = percent + "%";
  }
});

window.addEventListener("job-done", (e) => {
  const t = activeTool();
  if (!t) return;
  const { ok, message, output_path } = e.detail;
  logLine(t.log, message, ok ? "ok" : "error");
  setStatus(t.dot, t.status, ok ? "success" : "error", ok ? "Done" : "Failed");
  if (t.fill) document.getElementById(t.fill).style.width = "100%";
  showResult(t.result, ok, message, output_path);
  document.getElementById(t.btn).disabled = false;
});

// =======================================================================
// UPDATES VIEW
// =======================================================================

const updatesView = {
  checkBtn: null,
  installBtn: null,
  notesBtn: null,
  statusEl: null,
  progressEl: null,
  progressFill: null,
  badge: null,
  versionEl: null,
  latestData: null,
  currentVersion: "v1.2.4",  // keep in sync with Python CURRENT_VERSION

  init() {
    this.checkBtn = document.getElementById("updates-check-btn");
    this.installBtn = document.getElementById("updates-install-btn");
    this.notesBtn = document.getElementById("updates-notes-btn");
    this.statusEl = document.getElementById("updates-status");
    this.progressEl = document.getElementById("updates-progress");
    this.progressFill = document.getElementById("updates-progress-fill");
    this.badge = document.getElementById("update-badge");
    this.versionEl = document.getElementById("updates-current-version");

    if (this.versionEl) this.versionEl.textContent = this.currentVersion;
    if (this.checkBtn) this.checkBtn.addEventListener("click", () => this.check());
    if (this.installBtn) this.installBtn.addEventListener("click", () => this.install());
    if (this.notesBtn) this.notesBtn.addEventListener("click", () => this.showNotes());
  },

  async check() {
    if (this.checkBtn) this.checkBtn.disabled = true;
    if (this.statusEl) { this.statusEl.textContent = "Checking…"; this.statusEl.className = ""; }
    if (this.installBtn) this.installBtn.style.display = "none";
    if (this.notesBtn) this.notesBtn.style.display = "none";
    if (this.progressEl) this.progressEl.style.display = "none";
    await api().run_check_for_updates();
  },

  install() {
    if (!this.latestData || !this.latestData.assets || !this.latestData.assets.length) return;
    // Prefer a .exe asset; fall back to the first asset
    const asset = this.latestData.assets.find((a) => a.name && a.name.endsWith(".exe"))
      || this.latestData.assets[0];
    if (!asset) return;
    if (this.statusEl) { this.statusEl.textContent = "Downloading…"; this.statusEl.className = ""; }
    if (this.progressEl) this.progressEl.style.display = "block";
    if (this.installBtn) this.installBtn.disabled = true;
    if (this.checkBtn) this.checkBtn.disabled = true;
    api().run_download_update(asset.browser_download_url);
  },

  showNotes() {
    const modal = document.getElementById("if-instructions-modal");
    const titleEl = document.querySelector("#if-instructions-modal .modal-title");
    const bodyEl = document.getElementById("if-instructions-body");
    if (!modal) return;
    if (titleEl) titleEl.textContent = `Release Notes — ${this.latestData?.version || ""}`;
    if (bodyEl) bodyEl.textContent = this.latestData?.notes || "(No release notes available.)";
    modal.classList.add("visible");
  },
};

window.addEventListener("update-status", (e) => {
  const d = e.detail;
  switch (d.state) {
    case "no-internet":
      if (updatesView.statusEl) { updatesView.statusEl.textContent = "No internet connection."; updatesView.statusEl.className = "error"; }
      if (updatesView.checkBtn) updatesView.checkBtn.disabled = false;
      break;
    case "check-failed":
      if (updatesView.statusEl) { updatesView.statusEl.textContent = "Could not reach GitHub. Try again later."; updatesView.statusEl.className = "error"; }
      if (updatesView.checkBtn) updatesView.checkBtn.disabled = false;
      break;
    case "up-to-date":
      if (updatesView.statusEl) { updatesView.statusEl.textContent = `You're up to date (v${d.version}).`; updatesView.statusEl.className = "ok"; }
      if (updatesView.checkBtn) updatesView.checkBtn.disabled = false;
      break;
    case "update-available":
      updatesView.latestData = d;
      if (updatesView.statusEl) { updatesView.statusEl.textContent = `New version available: ${d.version}`; updatesView.statusEl.className = "warn"; }
      if (updatesView.installBtn) updatesView.installBtn.style.display = "";
      if (updatesView.notesBtn) updatesView.notesBtn.style.display = "";
      if (updatesView.versionEl) { updatesView.versionEl.textContent = updatesView.currentVersion; updatesView.versionEl.classList.add("new"); }
      if (updatesView.checkBtn) updatesView.checkBtn.disabled = false;
      break;
  }
});

window.addEventListener("update-download-progress", (e) => {
  const d = e.detail;
  if (d.error) {
    if (updatesView.statusEl) { updatesView.statusEl.textContent = d.error; updatesView.statusEl.className = "error"; }
    if (updatesView.installBtn) updatesView.installBtn.disabled = false;
    if (updatesView.checkBtn) updatesView.checkBtn.disabled = false;
    return;
  }
  if (d.message && updatesView.statusEl) updatesView.statusEl.textContent = d.message;
  if (typeof d.percent === "number" && updatesView.progressFill) {
    updatesView.progressFill.style.width = d.percent + "%";
    if (updatesView.progressEl) updatesView.progressEl.style.display = "block";
  }
});

window.addEventListener("update-badge", (e) => {
  const d = e.detail;
  updatesView.latestData = d;
  if (updatesView.badge) {
    updatesView.badge.textContent = d.version;
    updatesView.badge.classList.add("visible");
  }
  // Pre-enable install/notes buttons so user can jump straight in
  if (updatesView.installBtn) updatesView.installBtn.style.display = "";
  if (updatesView.notesBtn) updatesView.notesBtn.style.display = "";
  if (updatesView.versionEl) updatesView.versionEl.classList.add("new");
});

// Initialize once pywebview API is ready
whenApiReady(() => updatesView.init());