# Methodology

This document explains how the accessibility analysis in this repository works and how to interpret the outputs.

## Objective

Measure how effectively the rail network serves nearby urban areas by estimating whether places are within a 5, 10, or 15 minute walk of any station, then identify candidate transit deserts beyond that threshold.

## Input data

The analysis uses the processed station dataset in `dist/data.json`.

Each record provides:

- Station identifier
- Thai and English station names
- Latitude and longitude
- Line name
- Service family

The repository does not include:

- A street or pedestrian network
- Sidewalk connectivity data
- A population-density layer
- A land-use or building-footprint layer

That absence drives the main methodological limitation of this study.

## Analysis workflow

### 1. Load station points

The script reads `dist/data.json` and converts coordinate strings into numeric latitude and longitude values.

### 2. Project the coordinates

To support meter-based distance calculations, the script converts station coordinates to a local planar approximation using an equirectangular projection centered on the mean latitude and longitude of the dataset.

This is acceptable for a city-scale screening analysis and avoids introducing heavier GIS dependencies.

### 3. Generate approximate station isochrones

For each station, the script creates circular polygons for:

- 400 m
- 800 m
- 1,200 m

These correspond to approximate walking times of:

- 5 minutes
- 10 minutes
- 15 minutes

These are straight-line distance buffers, not network-constrained travel-time isochrones.

### 4. Build the study-area grid

The script creates a 250 m grid across the network extent, expanded by 2 km in all directions.

Each grid cell is evaluated against all stations to calculate:

- Distance to the nearest station
- Count of stations within 2 km

### 5. Define an urban-core proxy

Because the repository does not include a density layer, the analysis approximates potentially urbanized service territory using a station-proximity rule:

- Keep only cells with at least 2 stations within 2 km

This does not measure density directly. It is a proxy intended to avoid labeling remote edge cells as transit deserts just because they lie inside the bounding box.

### 6. Classify accessibility

Each retained grid cell is assigned to one of four categories:

- `within_5_min`: nearest station at or below 400 m
- `within_10_min`: nearest station above 400 m and at or below 800 m
- `within_15_min`: nearest station above 800 m and at or below 1,200 m
- `beyond_15_min`: nearest station above 1,200 m

### 7. Detect candidate transit deserts

Grid cells classified as `beyond_15_min` are grouped into clusters using four-direction adjacency on the 250 m grid.

For each cluster, the script calculates:

- Area in square kilometers
- Centroid coordinates
- Mean nearest-station distance
- Maximum nearest-station distance
- Average nearby-station count inside the urban-core proxy
- Three nearby edge stations used as anchor references

### 8. Export outputs

The script writes:

- Station points
- Approximate isochrones
- Accessibility grid
- Candidate transit-desert polygons
- CSV summary of top desert clusters
- JSON summary statistics
- Markdown report

## Current parameter values

| Parameter | Value |
| --- | ---: |
| Grid size | 250 m |
| Urban-proxy radius | 2,000 m |
| Minimum stations for urban proxy | 2 |
| 5 minute threshold | 400 m |
| 10 minute threshold | 800 m |
| 15 minute threshold | 1,200 m |
| Exported top desert clusters | 12 |

## Current findings

Latest summary from `analysis/outputs/summary.json`:

| Metric | Value |
| --- | ---: |
| Stations analyzed | 125 |
| Urban-proxy study area | 362.188 sq km |
| Within 5 minutes | 15.1% |
| Within 10 minutes | 45.9% |
| Within 15 minutes | 71.0% |
| Beyond 15 minutes | 29.0% |

These figures indicate that most of the proxied urban-core area is within a 15 minute walk of a station, but a substantial minority remains beyond that threshold.

## Interpretation guidance

Use the results for:

- Screening-level planning discussions
- Identifying corridors or neighborhoods worth deeper study
- Comparing broad accessibility patterns across parts of the network
- Producing quick GIS visualizations from a lightweight data package

Do not use the results as a substitute for:

- Detailed pedestrian access modeling
- Ridership forecasting
- Station siting decisions
- Equity analysis without population and demographic overlays

## Limitations

### No true network routing

The method does not account for street layout, barriers, canals, highways, bridges, or missing crossings. A location 800 m away in straight-line distance may take much longer to reach on foot.

### No density or land-use layer

The repository contains no population raster, census polygon, or built-form layer. The urban-core proxy is only an approximation.

### Sensitivity to parameter choices

Changing:

- grid size
- urban-proxy radius
- minimum nearby-station threshold
- walk-distance thresholds

will change the size and shape of the detected gaps.

### Static dataset

The analysis reflects the station data stored in the repository. It is not a live system-status or recently updated infrastructure feed.

## Recommended next step for a higher-fidelity study

If you want a stronger planning-grade version of this workflow:

1. Add OpenStreetMap walkable street data through `osmnx`
2. Snap stations to the pedestrian network
3. Compute true network-constrained travel-time isochrones
4. Overlay census, population, or building-density data
5. Rank uncovered areas by population served rather than area alone
