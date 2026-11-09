// Nusantara Data 2.0 — Data Explorer
(async function () {
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmtN = (v) => v == null ? "–" : Number(v).toLocaleString("id-ID", { maximumFractionDigits: Math.abs(v) >= 1000 ? 0 : 2 });

  // Approximate geographic tile positions [col, row] on an 18 × 8 grid
  const TILE = {
    "11": [0, 0, "ACE"], "12": [1, 1, "SUT"], "13": [1, 2, "SUB"], "14": [2, 2, "RIA"], "21": [4, 2, "KEP"], "15": [2, 3, "JAM"],
    "17": [1, 3, "BEN"], "19": [4, 3, "BAB"], "16": [2, 4, "SUS"], "18": [3, 5, "LAM"], "36": [4, 6, "BAN"], "31": [5, 5, "DKI"],
    "32": [5, 6, "JBR"], "33": [6, 6, "JTG"], "34": [6, 7, "DIY"], "35": [7, 6, "JTM"], "51": [8, 6, "BAL"], "52": [9, 6, "NTB"],
    "53": [10, 6, "NTT"], "61": [6, 2, "KBR"], "65": [8, 1, "KUT"], "64": [8, 2, "KTM"], "62": [7, 3, "KTG"], "63": [8, 3, "KSL"],
    "75": [10, 1, "GOR"], "71": [11, 1, "SUL"], "72": [10, 2, "STG"], "76": [9, 3, "SBR"], "73": [10, 3, "SSL"], "74": [11, 4, "STR"],
    "82": [13, 1, "MLU"], "81": [13, 3, "MAL"], "92": [14, 2, "PBD"], "91": [15, 2, "PBR"], "94": [17, 2, "PAP"], "96": [16, 3, "PTG"],
    "97": [17, 3, "PPG"], "95": [17, 4, "PSL"]
  };

  let catalog, regions, regionName = {}, current = null, selected = null;
  const state = { theme: "", ds: "", cat: 0, year: "" };
  try {
    [catalog, regions] = await Promise.all([fetch("../data/catalog.json").then((r) => r.json()), fetch("../data/regions.json").then((r) => r.json())]);
  } catch (e) {
    $("view").innerHTML = `<div class="card empty">Data tidak dapat dimuat. Buka halaman ini melalui server web (bukan file lokal).</div>`;
    return;
  }
  regions.forEach((r) => (regionName[r.bps_code] = r.region_name));

  // read state from URL hash (#ds=...&cat=..&year=..&prov=..)
  const h = new URLSearchParams(location.hash.slice(1));
  state.ds = h.get("ds") || "ND2-BPS-STI2024-L10";
  state.cat = +(h.get("cat") || 0);
  state.year = h.get("year") || "";
  selected = h.get("prov") || null;

  const themes = [...new Set(catalog.map((d) => d.theme))];
  const byId = Object.fromEntries(catalog.map((d) => [d.identifier, d]));
  if (!byId[state.ds]) state.ds = "ND2-BPS-STI2024-L10";
  state.theme = byId[state.ds].theme;

  const shortTitle = (d) => d.title_id.replace(/,\s*\d{4}(–\d{4})?$/, "").replace(/^Persentase /, "% ");
  function fillThemes() {
    $("theme").innerHTML = themes.map((t) => `<option ${t === state.theme ? "selected" : ""}>${esc(t)}</option>`).join("");
  }
  function fillDatasets() {
    const list = catalog.filter((d) => d.theme === state.theme);
    $("dataset").innerHTML = list.map((d) => `<option value="${d.identifier}" ${d.identifier === state.ds ? "selected" : ""}>${esc(shortTitle(d))}${d.spatial_resolution === "Provinsi" ? "" : " · " + esc(d.spatial_resolution)}</option>`).join("");
    if (!list.some((d) => d.identifier === state.ds)) state.ds = list[0].identifier;
  }
  function fillCatYear() {
    const m = current.meta;
    $("category").innerHTML = m.categories.map((c, i) => `<option value="${i}" ${i === state.cat ? "selected" : ""}>${esc(c)}</option>`).join("");
    $("category").disabled = m.categories.length < 2;
    const years = m.years.length ? m.years.map(String) : ["-"];
    if (!years.includes(state.year)) state.year = years[years.length - 1];
    $("year").innerHTML = years.map((y) => `<option ${y === state.year ? "selected" : ""} value="${y}">${y === "-" ? "—" : y}</option>`).join("");
    $("year").disabled = years.length < 2;
  }
  function writeHash() {
    const p = new URLSearchParams({ ds: state.ds, cat: state.cat, year: state.year });
    if (selected) p.set("prov", selected);
    history.replaceState(null, "", "#" + p.toString());
  }

  async function loadDataset() {
    current = await fetch(`../data/datasets/${state.ds}.json`).then((r) => r.json());
    if (state.cat >= current.meta.categories.length) state.cat = 0;
    fillCatYear();
    render();
  }

  const cellsFor = (cat, year) => {
    const v = current.values[String(cat)] || {};
    const out = {};
    for (const [code, ys] of Object.entries(v)) out[code] = ys[year] ?? ys["-"] ?? null;
    return out;
  };
  const isProvincial = () => current.meta.spatial_resolution === "Provinsi";

  function quantileBreaks(vals, n = 6) {
    const s = vals.filter((v) => v != null).sort((a, b) => a - b);
    if (!s.length) return [];
    return Array.from({ length: n - 1 }, (_, i) => s[Math.floor(((i + 1) * s.length) / n)]);
  }
  const classOf = (v, br) => (v == null ? -1 : br.filter((b) => v >= b).length);

  function render() {
    writeHash();
    const m = current.meta;
    $("ds-title").textContent = m.title_id;
    $("meta-line").innerHTML = [
      `<span>${esc(m.title_en)}</span>`,
      `<span>Satuan: <strong>${esc(m.measure_unit)}</strong></span>`,
      `<span>Unit: ${esc(m.unit_of_observation)}</span>`,
      `<span>Sumber: ${esc(m.source_survey)} · ${esc(m.source_publication)}</span>`,
      `<span><a href="../${m.csv}" download>Unduh CSV</a> · <a href="../${m.json}">JSON</a> · <a href="../katalog/#${m.identifier}">Metadata</a></span>`
    ].join("");
    isProvincial() ? renderProvincial() : renderNational();
  }

  // ---------- provincial view ----------
  function renderProvincial() {
    const m = current.meta, cat = state.cat, year = state.year;
    const cells = cellsFor(cat, year);
    const provs = Object.keys(TILE);
    const vals = provs.map((c) => cells[c]);
    const br = quantileBreaks(vals);
    const nat = cells["00"];
    const avail = vals.filter((v) => v != null);
    const sorted = provs.filter((c) => cells[c] != null).sort((a, b) => cells[b] - cells[a]);
    const max = Math.max(...avail, nat ?? 0) || 1;
    const top = sorted[0], bot = sorted[sorted.length - 1];
    const kpis = `<div class="kpis">
      <div class="card"><div class="v">${fmtN(nat)}</div><div class="l">Indonesia${year !== "-" ? " · " + year : ""}</div></div>
      <div class="card"><div class="v">${fmtN(cells[top])}</div><div class="l">Tertinggi: ${esc(regionName[top] || "")}</div></div>
      <div class="card"><div class="v">${fmtN(cells[bot])}</div><div class="l">Terendah: ${esc(regionName[bot] || "")}</div></div></div>`;
    const tiles = provs.map((c) => {
      const [x, y, ab] = TILE[c], k = classOf(cells[c], br);
      return `<button class="tile${k >= 3 ? " dark-text" : ""}" data-code="${c}" aria-pressed="${c === selected}"
        style="grid-column:${x + 1};grid-row:${y + 1};${k >= 0 ? `background:var(--seq-${k})` : ""}"
        aria-label="${esc(regionName[c])}: ${fmtN(cells[c])}">${ab}</button>`;
    }).join("");
    const legend = br.length ? `<div class="legend">${[...Array(6).keys()].map((k) => `<span class="sw" style="background:var(--seq-${k})"></span>`).join("")}
      <span>${fmtN(avail.length ? Math.min(...avail) : null)} → ${fmtN(avail.length ? Math.max(...avail) : null)}</span>
      <span class="sw" style="background:var(--na);margin-left:10px"></span><span>tidak ada data</span></div>` : "";
    const rankRows = [["00", nat], ...sorted.map((c) => [c, cells[c]])].filter(([c, v]) => v != null).map(([c, v], i) => `
      <div class="rank-row${c === "00" ? " national" : ""}${c === selected ? " sel" : ""}" data-code="${c}">
        <span class="muted small">${c === "00" ? "" : i}</span>
        <span>${esc(regionName[c])}<div class="bar" style="width:${Math.max(2, (100 * v) / max)}%"></div></span>
        <span class="num">${fmtN(v)}</span></div>`).join("");
    const missing = provs.filter((c) => cells[c] == null).map((c) => regionName[c]);
    $("view").innerHTML = `${kpis}
      <div class="layout">
        <div class="card"><p class="chart-title">${esc(m.categories[cat])}${year !== "-" ? " · " + year : ""}</p>
          <div class="tilemap" role="group" aria-label="Peta petak provinsi">${tiles}</div>${legend}
          ${missing.length ? `<p class="small muted" style="margin:8px 0 0">Tanpa data: ${esc(missing.join(", "))}${missing.some((n) => /Papua (Barat Daya|Selatan|Tengah|Pegunungan)/.test(n)) ? " (provinsi hasil pemekaran 2022)" : ""}.</p>` : ""}
          <div id="detail" style="margin-top:18px"></div></div>
        <div class="card"><p class="chart-title">Peringkat provinsi</p><div class="rank">${rankRows}</div></div>
      </div>`;
    const tip = $("tip");
    document.querySelectorAll(".tile").forEach((t) => {
      t.addEventListener("mousemove", (e) => { tip.style.display = "block"; tip.style.left = e.clientX + 12 + "px"; tip.style.top = e.clientY + 12 + "px";
        tip.textContent = `${regionName[t.dataset.code]}: ${fmtN(cells[t.dataset.code])}`; });
      t.addEventListener("mouseleave", () => (tip.style.display = "none"));
      t.addEventListener("click", () => selectProv(t.dataset.code));
    });
    document.querySelectorAll(".rank-row").forEach((r) => r.addEventListener("click", () => selectProv(r.dataset.code)));
    renderDetail();
  }
  function selectProv(code) { selected = selected === code ? null : code; render(); }

  function renderDetail() {
    const el = $("detail"); if (!el) return;
    const m = current.meta, code = selected || "00", name = regionName[code];
    const parts = [];
    if (m.years.length > 1) {
      const series = [{ name: "Indonesia", color: "var(--accent-2)", pts: m.years.map((y) => [y, current.values[state.cat]?.["00"]?.[y] ?? null]) }];
      if (selected && selected !== "00") series.unshift({ name, color: "var(--accent)", pts: m.years.map((y) => [y, current.values[state.cat]?.[selected]?.[y] ?? null]) });
      parts.push(`<p class="chart-title">Tren ${esc(selected ? name : "nasional")}${selected ? " vs Indonesia" : ""}</p>${lineChart(series)}`);
    }
    if (m.categories.length > 1) {
      const items = m.categories.map((c, i) => [c, current.values[i]?.[code]?.[state.year] ?? current.values[i]?.[code]?.["-"] ?? null]);
      parts.push(`<p class="chart-title">Semua kategori · ${esc(name)}${state.year !== "-" ? " · " + state.year : ""}</p>${barList(items, state.cat)}`);
    }
    if (!selected) parts.push(`<p class="small muted">Klik provinsi untuk membandingkan dengan Indonesia.</p>`);
    el.innerHTML = parts.join("");
  }

  // ---------- national / island view ----------
  function renderNational() {
    const m = current.meta;
    const codes = [...new Set(Object.values(current.values).flatMap((v) => Object.keys(v)))];
    const islands = codes.filter((c) => c.startsWith("ISL"));
    let html = "";
    if (islands.length) {
      const items = islands.map((c) => [regionName[c], current.values[state.cat]?.[c]?.[state.year] ?? null]);
      html += `<div class="card"><p class="chart-title">${esc(m.categories[state.cat])} menurut kelompok pulau · ${state.year}</p>${barList(items, -1)}</div>`;
      if (m.categories.length > 1) {
        const rows = islands.map((c) => `<tr><td>${esc(regionName[c])}</td>${m.categories.map((_, i) => `<td class="num">${fmtN(current.values[i]?.[c]?.[state.year])}</td>`).join("")}</tr>`).join("");
        html += `<div class="card" style="margin-top:16px"><div class="table-wrap"><table><thead><tr><th>Pulau</th>${m.categories.map((c) => `<th class="num">${esc(c)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></div></div>`;
      }
    } else {
      const multiYear = m.years.length > 1;
      // only combine categories measured in the same unit (label suffix "[unit]")
      const unitOf = (l) => (l.match(/\[([^\]]+)\]$/) || [, ""])[1];
      const sameUnit = m.categories.map((_, i) => i).filter((i) => unitOf(m.categories[i]) === unitOf(m.categories[state.cat]));
      if (multiYear) {
        const palette = ["var(--accent)", "var(--accent-2)", "var(--seq-2)", "var(--seq-5)", "#8a6fb3", "#b38a2e"];
        const cats = sameUnit.length <= 6 ? sameUnit : [state.cat];
        const series = cats.map((i, k) => ({ name: m.categories[i], color: palette[k % palette.length], pts: m.years.map((y) => [y, current.values[i]?.["00"]?.[y] ?? null]) }));
        html += `<div class="card"><p class="chart-title">Tren nasional</p>${lineChart(series, 320)}</div>`;
      }
      const items = sameUnit.map((i) => [m.categories[i], current.values[i]?.["00"]?.[state.year] ?? current.values[i]?.["00"]?.["-"] ?? null]);
      html += `<div class="card" style="margin-top:16px"><p class="chart-title">Indonesia · ${state.year === "-" ? "" : state.year}</p>${barList(items, sameUnit.indexOf(state.cat))}</div>`;
    }
    $("view").innerHTML = html;
  }

  // ---------- small SVG charts ----------
  function lineChart(series, H = 220) {
    const W = 640, P = { l: 52, r: 16, t: 12, b: 28 };
    const all = series.flatMap((s) => s.pts.map((p) => p[1])).filter((v) => v != null);
    if (!all.length) return `<p class="small muted">Tidak ada data deret waktu.</p>`;
    const xs = series[0].pts.map((p) => p[0]);
    let lo = Math.min(...all), hi = Math.max(...all); const pad = (hi - lo) * 0.12 || Math.abs(hi) * 0.1 || 1; lo -= pad; hi += pad;
    if (lo > 0 && lo < (hi - lo)) lo = 0;
    const x = (i) => P.l + (i * (W - P.l - P.r)) / Math.max(1, xs.length - 1);
    const y = (v) => H - P.b - ((v - lo) / (hi - lo)) * (H - P.t - P.b);
    const ticks = Array.from({ length: 5 }, (_, i) => lo + ((hi - lo) * i) / 4);
    let svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Grafik garis">`;
    svg += ticks.map((t) => `<line x1="${P.l}" x2="${W - P.r}" y1="${y(t)}" y2="${y(t)}" stroke="var(--border)"/><text x="${P.l - 6}" y="${y(t) + 4}" text-anchor="end">${fmtN(t)}</text>`).join("");
    svg += xs.map((v, i) => `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${v}</text>`).join("");
    for (const s of series) {
      const pts = s.pts.map((p, i) => (p[1] == null ? null : [x(i), y(p[1]), p[1]])).filter(Boolean);
      svg += `<polyline fill="none" stroke="${s.color}" stroke-width="2.5" points="${pts.map((p) => p[0] + "," + p[1]).join(" ")}"/>`;
      svg += pts.map((p) => `<circle cx="${p[0]}" cy="${p[1]}" r="3.5" fill="${s.color}"><title>${esc(s.name)}: ${fmtN(p[2])}</title></circle>`).join("");
    }
    svg += `</svg>`;
    const legend = `<div class="legend">${series.map((s) => `<span class="sw" style="background:${s.color};height:4px"></span><span>${esc(s.name)}</span>`).join("&nbsp;&nbsp;")}</div>`;
    return svg + legend;
  }
  function barList(items, hi) {
    const vals = items.map((i) => i[1]).filter((v) => v != null);
    const max = Math.max(...vals.map(Math.abs), 0) || 1;
    return items.map(([label, v], i) => `<div class="rank-row" style="grid-template-columns:minmax(0,1.4fr) minmax(0,1fr) 70px;cursor:default${i === hi ? ";font-weight:700" : ""}">
      <span>${esc(label)}</span><span><div class="bar" style="width:${v == null ? 0 : Math.max(1, (100 * Math.abs(v)) / max)}%;${v < 0 ? "background:var(--accent-2)" : ""}"></div></span>
      <span class="num">${fmtN(v)}</span></div>`).join("");
  }

  // ---------- wiring ----------
  $("theme").addEventListener("change", (e) => { state.theme = e.target.value; fillDatasets(); state.ds = $("dataset").value; state.cat = 0; state.year = ""; loadDataset(); });
  $("dataset").addEventListener("change", (e) => { state.ds = e.target.value; state.cat = 0; state.year = ""; loadDataset(); });
  $("category").addEventListener("change", (e) => { state.cat = +e.target.value; render(); });
  $("year").addEventListener("change", (e) => { state.year = e.target.value; render(); });
  // links that change only the hash (e.g. from the catalogue) reload the view
  window.addEventListener("hashchange", () => location.reload());
  fillThemes(); fillDatasets(); loadDataset();
})();
