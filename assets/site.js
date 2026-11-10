// Shared header, footer and theme toggle for all pages.
(function () {
  const base = document.documentElement.dataset.base || "./";
  const page = document.documentElement.dataset.page || "";
  try { const t = localStorage.getItem("cn-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  const links = [
    ["", "Beranda"], ["explorer/", "Data"], ["analysis/", "Analisis"], ["kebijakan/", "Kebijakan"],
    ["artikel/", "Artikel"], ["riset/", "Riset"], ["tentang/", "Tentang"]
  ];
  const header = document.createElement("header");
  header.className = "site-header";
  header.innerHTML = `<div class="wrap">
    <a class="brand" href="${base}"><span class="brand-mark">N</span><span>Connecting Nusantara<small>Digital Equity · Indonesia</small></span></a>
    <nav class="nav" aria-label="Menu utama">${links.map(([href, label]) =>
      `<a href="${base}${href}"${page === href || (href === "explorer/" && page === "katalog/") ? ' aria-current="page"' : ""}>${label}</a>`).join("")}</nav>
    <button class="theme-btn" type="button" aria-label="Ganti tema terang/gelap">◐</button></div>`;
  document.body.prepend(header);
  header.querySelector(".theme-btn").addEventListener("click", () => {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("cn-theme", next); } catch (e) {}
    document.dispatchEvent(new CustomEvent("themechange"));
  });
  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML = `<div class="wrap">
    <div><strong>Connecting Nusantara</strong> · Data dan kebijakan untuk kesetaraan digital Indonesia.</div>
    <div>© ${new Date().getFullYear()} Connecting Nusantara · <a href="${base}feed.xml">RSS</a></div>
  </div>`;
  document.body.append(footer);
})();

// Number formatting (Indonesian)
window.fmt = (v, d = 2) => v == null || isNaN(v) ? "–" :
  Number(v).toLocaleString("id-ID", { maximumFractionDigits: d, minimumFractionDigits: Math.abs(v) >= 1000 ? 0 : 0 });
