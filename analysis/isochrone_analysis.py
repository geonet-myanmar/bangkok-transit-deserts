import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dist" / "data.json"
OUTPUT_DIR = ROOT / "analysis" / "outputs"

WALK_BANDS = [
    (400, "5_min"),
    (800, "10_min"),
    (1200, "15_min"),
]

GRID_STEP_M = 250
URBAN_PROXY_RADIUS_M = 2000
URBAN_PROXY_MIN_STATIONS = 2
TOP_CLUSTER_COUNT = 12
EARTH_RADIUS_M = 6_371_000


def load_stations(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        stations = json.load(handle)

    for station in stations:
        station["lat"] = float(station["geoLat"])
        station["lon"] = float(station["geoLng"])

    return stations


def build_projection(stations: list[dict]):
    mean_lat = sum(station["lat"] for station in stations) / len(stations)
    mean_lon = sum(station["lon"] for station in stations) / len(stations)
    lat0_rad = math.radians(mean_lat)

    def project(lat: float, lon: float) -> tuple[float, float]:
        x = math.radians(lon - mean_lon) * math.cos(lat0_rad) * EARTH_RADIUS_M
        y = math.radians(lat - mean_lat) * EARTH_RADIUS_M
        return x, y

    def unproject(x: float, y: float) -> tuple[float, float]:
        lat = math.degrees(y / EARTH_RADIUS_M) + mean_lat
        lon = math.degrees(x / (EARTH_RADIUS_M * math.cos(lat0_rad))) + mean_lon
        return lat, lon

    return project, unproject


def squared_distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def circle_polygon(
    center_lat: float,
    center_lon: float,
    radius_m: float,
    segments: int = 48,
) -> list[list[float]]:
    lat_rad = math.radians(center_lat)
    lat_scale = 111_320
    lon_scale = 111_320 * math.cos(lat_rad)
    coords = []
    for index in range(segments):
        theta = (2 * math.pi * index) / segments
        dx = math.cos(theta) * radius_m
        dy = math.sin(theta) * radius_m
        lon = center_lon + (dx / lon_scale)
        lat = center_lat + (dy / lat_scale)
        coords.append([lon, lat])
    coords.append(coords[0])
    return coords


def square_polygon(lat: float, lon: float, step_m: float) -> list[list[float]]:
    lat_scale = 111_320
    lon_scale = 111_320 * math.cos(math.radians(lat))
    half = step_m / 2
    dx = half / lon_scale
    dy = half / lat_scale
    return [
        [lon - dx, lat - dy],
        [lon + dx, lat - dy],
        [lon + dx, lat + dy],
        [lon - dx, lat + dy],
        [lon - dx, lat - dy],
    ]


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(origin, point_a, point_b):
        return (
            (point_a[0] - origin[0]) * (point_b[1] - origin[1])
            - (point_a[1] - origin[1]) * (point_b[0] - origin[0])
        )

    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def write_geojson(path: Path, features: list[dict]) -> None:
    collection = {"type": "FeatureCollection", "features": features}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(collection, handle, ensure_ascii=False, indent=2)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def nearest_station_summary(
    sample_points_xy: list[tuple[float, float]],
    stations: list[dict],
    count: int = 3,
) -> list[dict]:
    ranked = []
    for station in stations:
        distance_m = min(
            math.sqrt(squared_distance(sample_point, station["xy"]))
            for sample_point in sample_points_xy
        )
        ranked.append((distance_m, station))
    ranked.sort(key=lambda item: item[0])

    summaries = []
    for distance_m, station in ranked[:count]:
        summaries.append(
            {
                "stationId": station["stationId"],
                "nameEng": station["nameEng"],
                "lineNameEng": station["lineNameEng"],
                "distance_m": round(distance_m, 1),
            }
        )
    return summaries


def classify_distance_band(distance_m: float) -> str:
    if distance_m <= 400:
        return "within_5_min"
    if distance_m <= 800:
        return "within_10_min"
    if distance_m <= 1200:
        return "within_15_min"
    return "beyond_15_min"


def build_grid_analysis(stations: list[dict], unproject):
    xs = [station["xy"][0] for station in stations]
    ys = [station["xy"][1] for station in stations]

    min_x = int(min(xs) - URBAN_PROXY_RADIUS_M)
    max_x = int(max(xs) + URBAN_PROXY_RADIUS_M)
    min_y = int(min(ys) - URBAN_PROXY_RADIUS_M)
    max_y = int(max(ys) + URBAN_PROXY_RADIUS_M)

    core_cells = []
    desert_cells = []

    for grid_x in range(min_x, max_x + 1, GRID_STEP_M):
        for grid_y in range(min_y, max_y + 1, GRID_STEP_M):
            nearby_count = 0
            nearest_distance = None

            for station in stations:
                distance_sq = squared_distance((grid_x, grid_y), station["xy"])
                if nearest_distance is None or distance_sq < nearest_distance:
                    nearest_distance = distance_sq
                if distance_sq <= URBAN_PROXY_RADIUS_M * URBAN_PROXY_RADIUS_M:
                    nearby_count += 1

            if nearby_count < URBAN_PROXY_MIN_STATIONS:
                continue

            nearest_distance_m = math.sqrt(nearest_distance)
            lat, lon = unproject(grid_x, grid_y)
            cell = {
                "xy": (grid_x, grid_y),
                "lat": lat,
                "lon": lon,
                "nearest_distance_m": nearest_distance_m,
                "nearby_station_count": nearby_count,
                "distance_band": classify_distance_band(nearest_distance_m),
            }
            core_cells.append(cell)

            if nearest_distance_m > 1200:
                desert_cells.append(cell)

    return core_cells, desert_cells


def cluster_deserts(desert_cells: list[dict], stations: list[dict], unproject):
    lookup = {cell["xy"]: cell for cell in desert_cells}
    visited = set()
    clusters = []
    neighbors = [
        (GRID_STEP_M, 0),
        (-GRID_STEP_M, 0),
        (0, GRID_STEP_M),
        (0, -GRID_STEP_M),
    ]

    for key in lookup:
        if key in visited:
            continue

        stack = [key]
        visited.add(key)
        cluster_cells = []

        while stack:
            current = stack.pop()
            cluster_cells.append(lookup[current])
            for offset_x, offset_y in neighbors:
                adjacent = (current[0] + offset_x, current[1] + offset_y)
                if adjacent in lookup and adjacent not in visited:
                    visited.add(adjacent)
                    stack.append(adjacent)

        centroid_x = sum(cell["xy"][0] for cell in cluster_cells) / len(cluster_cells)
        centroid_y = sum(cell["xy"][1] for cell in cluster_cells) / len(cluster_cells)
        centroid_lat, centroid_lon = unproject(centroid_x, centroid_y)
        avg_distance = sum(cell["nearest_distance_m"] for cell in cluster_cells) / len(cluster_cells)
        max_distance = max(cell["nearest_distance_m"] for cell in cluster_cells)
        nearby_station_count = (
            sum(cell["nearby_station_count"] for cell in cluster_cells) / len(cluster_cells)
        )
        nearest_stations = nearest_station_summary(
            [cell["xy"] for cell in cluster_cells],
            stations,
        )

        corners = []
        half = GRID_STEP_M / 2
        for cell in cluster_cells:
            x, y = cell["xy"]
            corners.extend(
                [
                    (x - half, y - half),
                    (x + half, y - half),
                    (x + half, y + half),
                    (x - half, y + half),
                ]
            )

        hull_xy = convex_hull(corners)
        hull_lonlat = []
        for x, y in hull_xy:
            lat, lon = unproject(x, y)
            hull_lonlat.append([lon, lat])
        if hull_lonlat:
            hull_lonlat.append(hull_lonlat[0])

        clusters.append(
            {
                "cluster_id": "",
                "cell_count": len(cluster_cells),
                "area_sq_km": round(len(cluster_cells) * GRID_STEP_M * GRID_STEP_M / 1_000_000, 3),
                "centroid_lat": round(centroid_lat, 6),
                "centroid_lon": round(centroid_lon, 6),
                "avg_distance_to_station_m": round(avg_distance, 1),
                "max_distance_to_station_m": round(max_distance, 1),
                "avg_nearby_station_count": round(nearby_station_count, 1),
                "nearest_stations": nearest_stations,
                "geometry": hull_lonlat,
            }
        )

    clusters.sort(
        key=lambda cluster: (
            cluster["cell_count"],
            cluster["avg_distance_to_station_m"],
        ),
        reverse=True,
    )

    for index, cluster in enumerate(clusters, start=1):
        cluster["cluster_id"] = f"D{index:02d}"

    return clusters


def build_station_features(stations: list[dict]) -> list[dict]:
    features = []
    for station in stations:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "stationId": station["stationId"],
                    "name": station["name"],
                    "nameEng": station["nameEng"],
                    "lineNameEng": station["lineNameEng"],
                    "lineServiceName": station["lineServiceName"],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [station["lon"], station["lat"]],
                },
            }
        )
    return features


def build_isochrone_features(stations: list[dict]) -> list[dict]:
    features = []
    for station in stations:
        for radius_m, label in WALK_BANDS:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "stationId": station["stationId"],
                        "nameEng": station["nameEng"],
                        "lineNameEng": station["lineNameEng"],
                        "walk_band": label,
                        "radius_m": radius_m,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [circle_polygon(station["lat"], station["lon"], radius_m)],
                    },
                }
            )
    return features


def build_core_grid_features(core_cells: list[dict]) -> list[dict]:
    features = []
    for cell in core_cells:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "distance_band": cell["distance_band"],
                    "nearest_distance_m": round(cell["nearest_distance_m"], 1),
                    "nearby_station_count": cell["nearby_station_count"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [square_polygon(cell["lat"], cell["lon"], GRID_STEP_M)],
                },
            }
        )
    return features


def build_desert_features(clusters: list[dict]) -> list[dict]:
    features = []
    for cluster in clusters[:TOP_CLUSTER_COUNT]:
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "cluster_id": cluster["cluster_id"],
                    "area_sq_km": cluster["area_sq_km"],
                    "cell_count": cluster["cell_count"],
                    "centroid_lat": cluster["centroid_lat"],
                    "centroid_lon": cluster["centroid_lon"],
                    "avg_distance_to_station_m": cluster["avg_distance_to_station_m"],
                    "max_distance_to_station_m": cluster["max_distance_to_station_m"],
                    "avg_nearby_station_count": cluster["avg_nearby_station_count"],
                    "anchor_1": cluster["nearest_stations"][0]["nameEng"],
                    "anchor_2": cluster["nearest_stations"][1]["nameEng"],
                    "anchor_3": cluster["nearest_stations"][2]["nameEng"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [cluster["geometry"]],
                },
            }
        )
    return features


def build_summary(stations: list[dict], core_cells: list[dict], clusters: list[dict]) -> dict:
    band_counts = {label: 0 for _, label in WALK_BANDS}
    for cell in core_cells:
        if cell["nearest_distance_m"] <= 400:
            band_counts["5_min"] += 1
        if cell["nearest_distance_m"] <= 800:
            band_counts["10_min"] += 1
        if cell["nearest_distance_m"] <= 1200:
            band_counts["15_min"] += 1

    core_area_sq_km = len(core_cells) * GRID_STEP_M * GRID_STEP_M / 1_000_000
    beyond_15_count = sum(1 for cell in core_cells if cell["nearest_distance_m"] > 1200)

    return {
        "station_count": len(stations),
        "core_cells": len(core_cells),
        "core_area_sq_km": round(core_area_sq_km, 3),
        "coverage": {
            "5_min_cells": band_counts["5_min"],
            "5_min_share_pct": round((band_counts["5_min"] / len(core_cells)) * 100, 1),
            "10_min_cells": band_counts["10_min"],
            "10_min_share_pct": round((band_counts["10_min"] / len(core_cells)) * 100, 1),
            "15_min_cells": band_counts["15_min"],
            "15_min_share_pct": round((band_counts["15_min"] / len(core_cells)) * 100, 1),
            "beyond_15_min_cells": beyond_15_count,
            "beyond_15_min_share_pct": round((beyond_15_count / len(core_cells)) * 100, 1),
        },
        "urban_proxy": {
            "radius_m": URBAN_PROXY_RADIUS_M,
            "min_station_count": URBAN_PROXY_MIN_STATIONS,
            "grid_step_m": GRID_STEP_M,
        },
        "top_deserts": [
            {
                "cluster_id": cluster["cluster_id"],
                "area_sq_km": cluster["area_sq_km"],
                "centroid_lat": cluster["centroid_lat"],
                "centroid_lon": cluster["centroid_lon"],
                "avg_distance_to_station_m": cluster["avg_distance_to_station_m"],
                "max_distance_to_station_m": cluster["max_distance_to_station_m"],
                "anchor_stations": [item["nameEng"] for item in cluster["nearest_stations"]],
            }
            for cluster in clusters[:TOP_CLUSTER_COUNT]
        ],
    }


def build_report(summary: dict, clusters: list[dict]) -> str:
    lines = [
        "# Service Area & Accessibility Analysis (Approximate Isochrones)",
        "",
        "## Method",
        "- Input: `dist/data.json` from this repository.",
        "- Walking catchments were approximated as 400 m, 800 m, and 1,200 m radius buffers around each station.",
        "- Because the repository does not include a pedestrian street network or a population layer, this is a geometric accessibility analysis rather than a true network-constrained OSM walk-time model.",
        f"- The urban-core proxy was defined as grid cells ({GRID_STEP_M} m resolution) with at least {URBAN_PROXY_MIN_STATIONS} stations within {URBAN_PROXY_RADIUS_M / 1000:.1f} km.",
        "- Candidate transit deserts are urban-proxy cells farther than 1.2 km from every station.",
        "",
        "## Coverage Summary",
        f"- Stations analyzed: {summary['station_count']}",
        f"- Urban-proxy study area: {summary['core_area_sq_km']} sq km",
        f"- Within 5 minutes (~400 m): {summary['coverage']['5_min_share_pct']}%",
        f"- Within 10 minutes (~800 m): {summary['coverage']['10_min_share_pct']}%",
        f"- Within 15 minutes (~1.2 km): {summary['coverage']['15_min_share_pct']}%",
        f"- Beyond 15 minutes: {summary['coverage']['beyond_15_min_share_pct']}%",
        "",
        "## Largest Candidate Transit Deserts",
    ]

    for cluster in clusters[:TOP_CLUSTER_COUNT]:
        anchors = ", ".join(item["nameEng"] for item in cluster["nearest_stations"])
        lines.append(
            f"- {cluster['cluster_id']}: {cluster['area_sq_km']} sq km, centroid "
            f"({cluster['centroid_lat']}, {cluster['centroid_lon']}), mean nearest-station distance "
            f"{cluster['avg_distance_to_station_m']} m. Anchors: {anchors}."
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "- The strongest gaps appear in areas where multiple corridors are nearby but no station falls within a 15-minute walk.",
            "- Several pockets are on the periphery of long radial lines, especially where station spacing increases outside the core.",
            "- These results are suitable for screening and prioritization, but not for final planning decisions without a real walk network and an external density or land-use layer.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stations = load_stations(DATA_PATH)
    project, unproject = build_projection(stations)

    for station in stations:
        station["xy"] = project(station["lat"], station["lon"])

    core_cells, desert_cells = build_grid_analysis(stations, unproject)
    clusters = cluster_deserts(desert_cells, stations, unproject)
    summary = build_summary(stations, core_cells, clusters)

    write_geojson(OUTPUT_DIR / "stations.geojson", build_station_features(stations))
    write_geojson(OUTPUT_DIR / "isochrones_approx.geojson", build_isochrone_features(stations))
    write_geojson(OUTPUT_DIR / "core_accessibility_grid.geojson", build_core_grid_features(core_cells))
    write_geojson(OUTPUT_DIR / "transit_deserts.geojson", build_desert_features(clusters))

    csv_rows = []
    for cluster in clusters[:TOP_CLUSTER_COUNT]:
        row = {
            "cluster_id": cluster["cluster_id"],
            "area_sq_km": cluster["area_sq_km"],
            "centroid_lat": cluster["centroid_lat"],
            "centroid_lon": cluster["centroid_lon"],
            "avg_distance_to_station_m": cluster["avg_distance_to_station_m"],
            "max_distance_to_station_m": cluster["max_distance_to_station_m"],
            "avg_nearby_station_count": cluster["avg_nearby_station_count"],
        }
        for index, station in enumerate(cluster["nearest_stations"], start=1):
            row[f"anchor_{index}_name"] = station["nameEng"]
            row[f"anchor_{index}_line"] = station["lineNameEng"]
            row[f"anchor_{index}_distance_m"] = station["distance_m"]
        csv_rows.append(row)

    write_csv(
        OUTPUT_DIR / "transit_deserts.csv",
        csv_rows,
        [
            "cluster_id",
            "area_sq_km",
            "centroid_lat",
            "centroid_lon",
            "avg_distance_to_station_m",
            "max_distance_to_station_m",
            "avg_nearby_station_count",
            "anchor_1_name",
            "anchor_1_line",
            "anchor_1_distance_m",
            "anchor_2_name",
            "anchor_2_line",
            "anchor_2_distance_m",
            "anchor_3_name",
            "anchor_3_line",
            "anchor_3_distance_m",
        ],
    )

    with (OUTPUT_DIR / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    report = build_report(summary, clusters)
    with (OUTPUT_DIR / "report.md").open("w", encoding="utf-8") as handle:
        handle.write(report)


if __name__ == "__main__":
    main()
