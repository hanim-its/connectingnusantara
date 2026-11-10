"""Build data/peta-provinsi.json (SVG paths for 38 provinces, keyed by BPS code) from
content/geo/indonesia-38-provinces.geojson.
Source: "Indonesia GeoJSON & TopoJSON Maps (38 Provinces)" by denyherianto, CC BY 4.0
(github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces). Changes: projected,
simplified, tiny islets dropped, province codes re-matched to BPS codes by name.
Run: python3 tools/build_map.py"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 1000                       # SVG width; height follows the aspect ratio
TOL = 0.9                      # simplification tolerance in SVG px
MIN_AREA = 2.0                 # drop rings smaller than this (px^2), except a province's largest ring


def dp(pts, tol):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy) or 1e-9
    i, dmax = 0, 0
    for k in range(1, len(pts) - 1):
        d = abs(dy * pts[k][0] - dx * pts[k][1] + x2 * y1 - y2 * x1) / n
        if d > dmax: i, dmax = k, d
    if dmax <= tol: return [pts[0], pts[-1]]
    return dp(pts[: i + 1], tol)[:-1] + dp(pts[i:], tol)


def simplify_ring(r):
    # closed ring: first == last, so simplify the two halves separately
    if len(r) < 8: return r
    m = len(r) // 2
    return dp(r[: m + 1], TOL)[:-1] + dp(r[m:], TOL)


def area(r):
    return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2


def main():
    regions = json.load(open(os.path.join(ROOT, "data/regions.json"), encoding="utf-8"))
    code_by_name = {r["region_name"].lower(): r["bps_code"] for r in regions if r.get("bps_code") and r["bps_code"] != "00" and r.get("region_level") == "Provinsi"}
    gj = json.load(open(os.path.join(ROOT, "content/geo/indonesia-38-provinces.geojson"), encoding="utf-8"))
    alias = {"daerah istimewa yogyakarta": "di yogyakarta", "kepulauan bangka belitung": "kep. bangka belitung"}

    def code_for(name):
        n = name.lower().strip()
        for cand in (n, alias.get(n, ""), n.replace("daerah istimewa ", "di ")):
            if cand in code_by_name: return code_by_name[cand]
        for k, v in code_by_name.items():
            if k.replace(" ", "") == n.replace(" ", ""): return v
        raise SystemExit(f"no BPS code for {name!r}")

    lons, lats = [], []
    for f in gj["features"]:
        geom = f["geometry"]; polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for x, y in poly[0]: lons.append(x); lats.append(y)
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    sx = W / ((lon1 - lon0) * k); H = round((lat1 - lat0) * sx)
    proj = lambda x, y: ((x - lon0) * k * sx, (lat1 - y) * sx)

    out, centers = {}, {}
    for f in gj["features"]:
        code = code_for(f["properties"]["PROVINSI"])
        geom = f["geometry"]; polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        rings = [[proj(x, y) for x, y in poly[0]] for poly in polys]
        rings = [simplify_ring(r) for r in rings]
        rings = [r for r in rings if len(r) >= 4]
        biggest = max(rings, key=area)
        keep = [r for r in rings if area(r) >= MIN_AREA or r is biggest]
        out[code] = "".join("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in r) + "Z" for r in keep)
        cx = sum(p[0] for p in biggest) / len(biggest); cy = sum(p[1] for p in biggest) / len(biggest)
        centers[code] = [round(cx, 1), round(cy, 1)]
    assert len(out) == 38, len(out)
    json.dump({"viewBox": f"0 0 {W} {H}", "paths": out, "centers": centers,
               "attribution": "Batas provinsi: Indonesia GeoJSON & TopoJSON Maps (38 Provinces), CC BY 4.0, disederhanakan."},
              open(os.path.join(ROOT, "data/peta-provinsi.json"), "w", encoding="utf-8"), separators=(",", ":"))
    print("38 provinces,", os.path.getsize(os.path.join(ROOT, "data/peta-provinsi.json")) // 1024, "KB, viewBox", W, H)


if __name__ == "__main__":
    main()
