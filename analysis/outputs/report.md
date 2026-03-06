# Service Area & Accessibility Analysis (Approximate Isochrones)

## Method
- Input: `dist/data.json` from this repository.
- Walking catchments were approximated as 400 m, 800 m, and 1,200 m radius buffers around each station.
- Because the repository does not include a pedestrian street network or a population layer, this is a geometric accessibility analysis rather than a true network-constrained OSM walk-time model.
- The urban-core proxy was defined as grid cells (250 m resolution) with at least 2 stations within 2.0 km.
- Candidate transit deserts are urban-proxy cells farther than 1.2 km from every station.

## Coverage Summary
- Stations analyzed: 125
- Urban-proxy study area: 362.188 sq km
- Within 5 minutes (~400 m): 15.1%
- Within 10 minutes (~800 m): 45.9%
- Within 15 minutes (~1.2 km): 71.0%
- Beyond 15 minutes: 29.0%

## Largest Candidate Transit Deserts
- D01: 14.938 sq km, centroid (13.692101, 100.551633), mean nearest-station distance 1518.9 m. Anchors: Punnawithi, EkKamai, Bearing.
- D02: 12.188 sq km, centroid (13.878027, 100.583418), mean nearest-station distance 1518.1 m. Anchors: Phahon Yothin 24, Saphan Mai, Ha Yaek Lat Phrao.
- D03: 10.688 sq km, centroid (13.771462, 100.511216), mean nearest-station distance 1499.2 m. Anchors: Sanam Pao, Bang Sue, Bang Khun Non.
- D04: 9.938 sq km, centroid (13.868912, 100.608682), mean nearest-station distance 1530.9 m. Anchors: Sena Nikhom, Bhumibol Adulyadej Hospital, Lat Phrao.
- D05: 8.438 sq km, centroid (13.757023, 100.587972), mean nearest-station distance 1489.6 m. Anchors: Ramkhamhaeng, EkKamai, Huai Khwang.
- D06: 8.188 sq km, centroid (13.657038, 100.613622), mean nearest-station distance 1509.4 m. Anchors: Srinagarindra, Bang Na, Bearing.
- D07: 4.625 sq km, centroid (13.807068, 100.499583), mean nearest-station distance 1475.1 m. Anchors: Sirindhorn, Bang Pho, Wong Sawang.
- D08: 4.562 sq km, centroid (13.731529, 100.439762), mean nearest-station distance 1513.9 m. Anchors: Phetkasem 48, Fai Chai, Bang Phai.
- D09: 4.125 sq km, centroid (13.887411, 100.447874), mean nearest-station distance 1492.3 m. Anchors: Bang Rak Yai, Bang Rak Noi Tha It, Khlong Bang Phai.
- D10: 3.75 sq km, centroid (13.590907, 100.587869), mean nearest-station distance 1499.2 m. Anchors: Pak Nam, Sai Luat, Chang Erawan.
- D11: 3.312 sq km, centroid (13.851505, 100.489697), mean nearest-station distance 1493.0 m. Anchors: Phra Nang Klao Bridge, Yaek Nonthaburi 1, Sai Ma.
- D12: 2.938 sq km, centroid (13.862099, 100.442521), mean nearest-station distance 1506.5 m. Anchors: Bang Phlu, Sai Ma, Sam Yaek Bang Yai.

## Interpretation
- The strongest gaps appear in areas where multiple corridors are nearby but no station falls within a 15-minute walk.
- Several pockets are on the periphery of long radial lines, especially where station spacing increases outside the core.
- These results are suitable for screening and prioritization, but not for final planning decisions without a real walk network and an external density or land-use layer.
