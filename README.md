# Bangkok Rail Accessibility Analysis

This repository packages a standalone accessibility analysis based on Bangkok-area rail station data.

It is not a republished copy of the original `thailand-public-train-data` repository. Instead, it contains:

- the analysis input dataset used for this study
- the Python script used to run the analysis
- the generated output files
- documentation describing the method and data

## Included in this repository

```text
.
|-- analysis/
|   |-- isochrone_analysis.py
|   `-- outputs/
|-- dist/
|   `-- data.json
|-- docs/
|   |-- DATA_DICTIONARY.md
|   `-- METHODOLOGY.md
|-- .gitignore
|-- LICENSE
|-- NOTICE.md
`-- README.md
```

## Input data file

The analysis script reads:

- `dist/data.json`

This file contains the processed station dataset used by the current analysis run.

## What the analysis does

The script in `analysis/isochrone_analysis.py`:

1. loads station points from `dist/data.json`
2. builds approximate walking catchments of 400 m, 800 m, and 1,200 m
3. evaluates accessibility on a 250 m grid
4. flags cells beyond 1.2 km from every station
5. clusters those cells into candidate transit-desert polygons
6. exports GeoJSON, CSV, JSON, and Markdown outputs

## Current outputs

The repository includes generated analysis outputs in `analysis/outputs/`:

- `stations.geojson`
- `isochrones_approx.geojson`
- `core_accessibility_grid.geojson`
- `transit_deserts.geojson`
- `transit_deserts.csv`
- `summary.json`
- `report.md`

## Latest summary

| Metric | Value |
| --- | ---: |
| Stations analyzed | 125 |
| Urban-proxy study area | 362.188 sq km |
| Within 5 minutes | 15.1% |
| Within 10 minutes | 45.9% |
| Within 15 minutes | 71.0% |
| Beyond 15 minutes | 29.0% |

Largest candidate transit-desert clusters:

| Cluster | Area (sq km) | Centroid | Example nearby stations |
| --- | ---: | --- | --- |
| D01 | 14.938 | 13.692101, 100.551633 | Punnawithi, EkKamai, Bearing |
| D02 | 12.188 | 13.878027, 100.583418 | Phahon Yothin 24, Saphan Mai, Ha Yaek Lat Phrao |
| D03 | 10.688 | 13.771462, 100.511216 | Sanam Pao, Bang Sue, Bang Khun Non |

## Running the analysis

The script uses only the Python standard library.

```bash
python analysis/isochrone_analysis.py
```

Running it will regenerate the files in `analysis/outputs/`.

## Documentation

- Data dictionary: `docs/DATA_DICTIONARY.md`
- Methodology: `docs/METHODOLOGY.md`
- Source attribution: `NOTICE.md`

## Attribution

This repository contains a derived analysis package built from a public Bangkok rail station dataset. See `NOTICE.md` for the original source reference and license context.

## License

See `LICENSE`.
