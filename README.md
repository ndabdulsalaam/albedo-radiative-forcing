# Albedo-Radiative-Forcing Toolkit

## Background
Surface albedo—the fraction of incoming shortwave radiation reflected by the surface—modulates the planet’s energy balance. Brighter surfaces reduce absorbed solar energy; darker surfaces increase it. Top-of-atmosphere (TOA) radiative forcing quantifies this perturbation and is a key diagnostic in climate assessments.

## Model formulation
The toolkit uses a zero-dimensional shortwave energy balance to map albedo changes to TOA forcing:

- Insolation: `S0` (solar constant, ~1361 W m^-2)
- Geometry factor: `1/4` to distribute intercepted solar energy over Earth’s surface area
- Albedo perturbation: `Δα = α_final - α_initial`
- Affected area fraction: `f_area` (0–1)
- Forcing (downward positive): `ΔF_TOA ≈ - (S0 / 4) * Δα * f_area`

Surface classes (vegetation, desert, fresh/aged snow, urban, cropland) use literature-based broadband albedo ranges for baseline scenarios, with optional perturbations for sensitivity tests.

## Assumptions and limitations
- Zero-dimensional, global-mean scaling; does not resolve latitude/season/cloud variability.
- Instantaneous forcing only; no fast or slow feedbacks (clouds, water vapor, circulation).
- Broadband albedo; spectral and bidirectional reflectance effects are neglected.
- Uniform application over `f_area`; heterogeneous land cover and cloud masking are not represented.
- Clear-sky simplification; aerosol and cloud interactions are outside scope.

## Validation approach
Modeled forcing is compared to a first-order benchmark used in IPCC assessments: a unit albedo increase yields roughly `-340 W m^-2` at TOA (i.e., `-3.4 W m^-2` per +0.01 Δα) when scaled by `f_area`. A tolerance band (default ±20%) accounts for known uncertainties. The check is a sanity test, not a full evaluation of coupled feedbacks or regional processes.

## Relevance to climate mitigation research
Simple albedo perturbations inform rapid assessments of land-surface interventions (e.g., snow darkening, reforestation/deforestation brightness changes, cool roofs). This toolkit provides transparent, literature-grounded estimates for early-stage sensitivity analyses before more detailed Earth system modeling. It is not a substitute for coupled climate simulations.
