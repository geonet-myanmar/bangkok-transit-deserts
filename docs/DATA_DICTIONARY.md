# Data Dictionary

This document describes the files included in this standalone analysis repository.

Source dataset origin:

- https://github.com/Gusb3ll/thailand-public-train-data

## Input data

### `dist/data.json`

Processed station dataset used directly by `analysis/isochrone_analysis.py`.

| Field | Type | Description |
| --- | --- | --- |
| `stationId` | string | Station code |
| `name` | string | Station name in Thai |
| `nameEng` | string | Station name in English |
| `geoLat` | string | Latitude in WGS84 |
| `geoLng` | string | Longitude in WGS84 |
| `lineName` | string | Line name in Thai |
| `lineNameEng` | string | Line name in English |
| `lineColorHex` | string | Hex line color |
| `lineServiceName` | string | Service family |

This file is the direct input to the analysis.

## Analysis outputs

All outputs are written to `analysis/outputs/`.

### `stations.geojson`

Station points exported as GeoJSON.

Properties:

| Field | Type | Description |
| --- | --- | --- |
| `stationId` | string | Station code |
| `name` | string | Thai station name |
| `nameEng` | string | English station name |
| `lineNameEng` | string | English line name |
| `lineServiceName` | string | Service family |

### `isochrones_approx.geojson`

Approximate circular walking catchments for each station.

Properties:

| Field | Type | Description |
| --- | --- | --- |
| `stationId` | string | Station code |
| `nameEng` | string | English station name |
| `lineNameEng` | string | English line name |
| `walk_band` | string | One of `5_min`, `10_min`, `15_min` |
| `radius_m` | number | Buffer radius in meters |

### `core_accessibility_grid.geojson`

250 m grid over the study area used to classify accessibility.

Properties:

| Field | Type | Description |
| --- | --- | --- |
| `distance_band` | string | `within_5_min`, `within_10_min`, `within_15_min`, or `beyond_15_min` |
| `nearest_distance_m` | number | Distance from cell center to nearest station |
| `nearby_station_count` | integer | Number of stations within the urban-proxy radius |

### `transit_deserts.geojson`

Polygons representing the top candidate transit-desert clusters.

Properties:

| Field | Type | Description |
| --- | --- | --- |
| `cluster_id` | string | Cluster identifier such as `D01` |
| `area_sq_km` | number | Cluster area in square kilometers |
| `cell_count` | integer | Number of 250 m grid cells in the cluster |
| `centroid_lat` | number | Cluster centroid latitude |
| `centroid_lon` | number | Cluster centroid longitude |
| `avg_distance_to_station_m` | number | Mean nearest-station distance across cluster cells |
| `max_distance_to_station_m` | number | Maximum nearest-station distance across cluster cells |
| `avg_nearby_station_count` | number | Average number of stations within the urban-proxy radius |
| `anchor_1` | string | Example nearby station at the desert edge |
| `anchor_2` | string | Example nearby station at the desert edge |
| `anchor_3` | string | Example nearby station at the desert edge |

### `transit_deserts.csv`

Tabular version of the top desert clusters with station anchors and edge distances.

Columns:

| Field | Type | Description |
| --- | --- | --- |
| `cluster_id` | string | Cluster identifier |
| `area_sq_km` | number | Cluster area |
| `centroid_lat` | number | Centroid latitude |
| `centroid_lon` | number | Centroid longitude |
| `avg_distance_to_station_m` | number | Mean nearest-station distance |
| `max_distance_to_station_m` | number | Maximum nearest-station distance |
| `avg_nearby_station_count` | number | Mean nearby-station count within the urban proxy |
| `anchor_1_name` | string | First anchor station name |
| `anchor_1_line` | string | First anchor line name |
| `anchor_1_distance_m` | number | Minimum edge distance from the cluster to the first anchor station |
| `anchor_2_name` | string | Second anchor station name |
| `anchor_2_line` | string | Second anchor line name |
| `anchor_2_distance_m` | number | Minimum edge distance from the cluster to the second anchor station |
| `anchor_3_name` | string | Third anchor station name |
| `anchor_3_line` | string | Third anchor line name |
| `anchor_3_distance_m` | number | Minimum edge distance from the cluster to the third anchor station |

### `summary.json`

Machine-readable summary of the latest analysis run.

Top-level keys:

| Key | Description |
| --- | --- |
| `station_count` | Number of stations analyzed |
| `core_cells` | Number of grid cells in the urban-proxy study area |
| `core_area_sq_km` | Total area of the study grid |
| `coverage` | Coverage metrics for 5, 10, and 15 minute thresholds |
| `urban_proxy` | Parameters used to define the study area |
| `top_deserts` | Summary records for the top candidate desert clusters |

### `report.md`

Short narrative report summarizing method, coverage, key gaps, and limitations.

## Script

### `analysis/isochrone_analysis.py`

Runs the accessibility workflow and exports GeoJSON, CSV, JSON, and Markdown outputs.
