# Connecting Nusantara — connectingnusantara.com

Static website for the Nusantara Data 2.0 research platform (SRG Tipe D 2026, DRPM ITS).
No build step: every page is plain HTML/CSS/JS, hosted on Vercel.

## Pages
- `/` home · `/explorer/` Data Explorer v2 (all 90 datasets) · `/analysis/` inequality indices + province profiles
- `/katalog/` DCAT catalogue, CSV/JSON downloads, glossary · `/riset/` method, data-quality findings, publications
- `/tentang/` team, funding · `/arsip-v1/` Nusantara Data 1.0 (2025, built by students)

## Updating the data
Data comes from the research pipeline in `Tmp-Work/Research/SRG-HANIM/icttracker/`:
```
python3 scripts/build_metadata_catalog.py && python3 scripts/build_warehouse.py
python3 scripts/export_site_data.py      # writes data/ in this folder
```
Then commit and push; Vercel redeploys in about a minute.

## Editing text
Pages are HTML in each folder's `index.html`. Shared header/footer: `assets/site.js`. Styles: `assets/style.css`.
