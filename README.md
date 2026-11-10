# Connecting Nusantara — connectingnusantara.com

Static website for the Nusantara Data 2.0 research platform (SRG Tipe D 2026, DRPM ITS).
No build step: every page is plain HTML/CSS/JS, hosted on Vercel.

## Pages
- `/` home · `/explorer/` Data Explorer v2 (all 90 datasets) · `/analysis/` inequality indices + province profiles
- `/katalog/` DCAT catalogue, CSV/JSON downloads, glossary · `/riset/` method, data-quality findings, publications
- `/tentang/` about · `/riset/` research projects (one page each, from `content/riset/*.md`)

## Updating the data
Data comes from the research pipeline in `Tmp-Work/Research/SRG-HANIM/icttracker/`:
```
python3 scripts/build_metadata_catalog.py && python3 scripts/build_warehouse.py
python3 scripts/export_site_data.py      # writes data/ in this folder
```
Then commit and push; Vercel redeploys in about a minute.

## Editing text
Pages are HTML in each folder's `index.html`. Shared header/footer: `assets/site.js`. Styles: `assets/style.css`.

## Platform structure (since 2026-11-10)
Connecting Nusantara is the ongoing platform; Nusantara Data 2.0 is one project on it.
Menu: Beranda · Data (`/explorer/`, `/katalog/`) · Analisis · Kebijakan · Artikel · Riset · Tentang.

### Adding an article or progress update ("Kabar")
1. Add `content/artikel/<slug>.md` with front matter:
   `title`, `date` (YYYY-MM-DD), `category` (Kabar | Konsep | Data & Statistik | Regulasi | Aksesibilitas),
   `lang` (id/en), `tags` (comma-separated), `summary`, `hero` (e.g. `assets/artikel/<slug>.jpg`, optional).
2. Write the body in Markdown (## headings, lists, **bold**, *italic*, [links](url), ![caption](../../assets/artikel/img.jpg)).
3. Run `python3 tools/build_content.py` → regenerates `artikel/`, `kebijakan/`, `data/artikel.json`, `feed.xml`.

### Adding a regulation
Add an item to `content/kebijakan.json` (category, type, number, title, short, meaning, year, status, `articles`: list of review slugs), then run the build. A new policy review = an article with `category: Regulasi`, plus its slug in that regulation's `articles` list.

Old Wix URLs (/post/…, /blog, /about, /general-6, /s-projects-basic) redirect via `vercel.json`.
The 5 old blog posts were migrated from Wix on 2026-11-10 (originals: `migrated_from` in each file);
"Urban households owned more cell phones in 2022" was image-only and was not migrated.

### Before every deploy
Run `python3 tools/build_content.py` (it also runs `tools/stamp_assets.py`). The stamp adds `?v=<hash>` to the
style.css / site.js links so visitors' browsers never show a new page with an old stylesheet.

### Province map (Data page)
`data/peta-provinsi.json` is built by `python3 tools/build_map.py` from `content/geo/indonesia-38-provinces.geojson`
("Indonesia GeoJSON & TopoJSON Maps (38 Provinces)", denyherianto, CC BY 4.0 — credited under the map).
The four new Papua provinces carry old codes in that file, so provinces are matched to BPS codes by name.

### Adding a research project (each year)
Add `content/riset/<slug>.md` with front matter: `title`, `subtitle`, `year`, `status` (Berjalan | Selesai), `funder` (optional),
`summary`, `hero` (optional image), `format` (`html` or Markdown), `order` (tie-break within a year). Then run `python3 tools/build_content.py`.
The overview /riset/ lists projects newest first; a status filter appears automatically once projects have different statuses.
