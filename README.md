# Exoplanets

> Past independent research project; most of the work was done in 2025.

I started this repository while trying to find transit candidates in TESS data. It contains the Python tools and notebooks I wrote to download and process light curves, search for periodic dips, fit candidate signals, estimate planetary properties, and check possible false positives.

As the project grew, I added stellar-variability analysis, target-pixel corrections, CTOI processing, and some exploratory work with known exoplanets.

I no longer use this as my active research workspace. My more recent work has moved toward understanding known systems, including transit timing, binary stars, stellar variability, and asteroseismology. I have kept this repository as a record of the code and results from that earlier work.

## Analysis Workflow

The code covers several parts of the candidate-search process:

1. Transit searches: Download TESS light curves, clean and normalize the photometry, combine sectors, and search for periodic transit-like signals using Box Least Squares (BLS).
2. Transit fitting and candidate checks: Fold the light curves, fit transit models, estimate planet properties, and check transit shape, odd/even depths, secondary eclipses, harmonics, stellar variability, and contamination.
3. False-positive analysis: Use TRICERATOPS to compare possible planetary and eclipsing-binary explanations, including scenarios involving nearby stars.
4. Light curve correction: Experiment with detrending methods and construct aperture light curves from TESS target-pixel files, including PCA-based correction.
5. Processing and results: Organize target lists, candidate data, plots, light curves, and other outputs for later inspection.

These steps help assess transit candidates; they do not establish that a candidate is a confirmed planet.

## Python Scripts

### `FinnyExoplanetAnalyzer.py`

The main TESS light-curve analyzer.

It retrieves light curves from MAST, cleans and normalizes the photometry, combines observations from different sectors, and searches for periodic transit signals using BLS.

The search starts over a broad period range and then examines the strongest signal over a narrower range to refine the period and transit duration. The resulting signal can be folded, modeled, plotted, and measured.

The analyzer can also mask an identified transit before searching again. I used this to look for additional periodic signals in a target rather than stopping at the strongest signal.

### `Exoplanet.py`

Contains the candidate object and calculations performed after finding a transit signal.

The class stores transit and host-star properties and calculates quantities such as the planet-to-star radius ratio, planetary radius, estimated mass, semi-major axis, and equilibrium temperature.

Transit fitting uses `batman` and `scipy.optimize.least_squares`, with orbital geometry and quadratic limb darkening included in the model. The fitted parameters are then used to calculate the physical properties.

Masses are estimated with ExoRM rather than obtained from direct mass measurements. Candidate information is also converted into the format used for later CTOI processing.

### `analyze_candidates.py`

Runs the main analyzer on individual targets and saves diagnostic products. I used it to inspect candidates, review questionable signals, and rerun searches when the initial period or detection was not convincing.

### `analyze_stars.py`

Runs the analysis over larger target lists. It tracks completed targets and saves the resulting light curves, periodograms, candidate information, and other outputs.

## Notebooks

### `analyze_optimized.ipynb`

Additional candidate-vetting work built around the main analyzer.

It examines transit shape, odd/even depth differences, secondary eclipses, harmonics, stellar variability, contamination, and cases where the initial period or physical parameters need another look.

It also contains experiments with different detrending and outlier-removal methods for difficult light curves.

### `analyze_triceratops.ipynb`

Uses TRICERATOPS to examine possible false positives.

The notebook compares planetary and eclipsing-binary scenarios involving the target or nearby stars, using TESS observations and information about neighboring sources to calculate scenario probabilities.

### `analyze_variables.ipynb`

Investigates periodic stellar variability separately from the transit search.

It uses Lomb-Scargle periodograms on TESS light curves and folds the observations on the resulting periods. I also used it to examine harmonic interpretations of signals that did not have an obvious single-period explanation.

### `process_ctois.ipynb`

Processes candidates produced by the earlier analysis.

It retrieves additional stellar information from MAST and can work directly with TESS target-pixel files. The notebook constructs aperture light curves from pixel data and applies PCA-based correction using `DesignMatrix` and `RegressionCorrector`.

The corrected light curves can then be passed back into the transit model in `Exoplanet.py`. The notebook also handles candidate JSON data, plots, and tabular files used in the CTOI workflow.

### `process_ids.ipynb`

Prepares target lists for the other scripts. It combines relevant TESS candidate and TCE information, cleans TIC IDs, removes duplicates, and produces the lists used for analysis.

### `correlation.ipynb`

Exploratory analysis of known exoplanets using the NASA Exoplanet Archive. This notebook is separate from the TESS candidate-search workflow and examines relationships among planetary properties.

## Results Archive

### `CTOI Creation/`

Contains the outputs produced by the candidate-analysis and mass-analysis workflow. Results are grouped by analysis type and, where applicable, by the date of the run. This preserves outputs from different stages of the project.

### `CTOI Creation/Mass Analysis/`

Contains outputs from candidate and mass analysis, organized by year, month, and run date.

- **`stitched_light_curves/`** contains combined TESS light curves for the targets analyzed in each run.
- **`transit_depths/`** contains plots and measurements used to inspect detected transit signals and estimate planet-to-star radius ratios and planetary radii.

Other output folders were added as the analysis developed. Some files are intermediate results from a particular run, so the archive preserves the original outputs rather than replacing everything with the latest version.

## ExoRM Analysis Material

### `Paper Material/ExoRM/`

Contains material associated with the ExoRM project, including analysis used to develop and evaluate the mass-radius model.

The Python package and its development notebooks are in the separate [ExoRM repository](https://github.com/kzhu2099/ExoRM).

## Other Files

### `exoplanets.csv`

A local copy of exoplanet catalog data used in exploratory analyses of known planets and their properties.

### `email_ctois.py`

Utility script for the administrative side of the CTOI workflow.

## Dependencies

The main analysis uses:

- Lightkurve for TESS light-curve access and analysis
- Astropy and Astroquery for astronomical calculations and data queries
- batman for transit modeling
- SciPy for numerical optimization and scientific computations
- wotan for light-curve detrending
- TRICERATOPS for false-positive analysis
- ExoRM for experimental radius-to-mass estimates

Other scientific Python packages are used in individual scripts and notebooks.

## Running the Code

The scripts were written around my own research workflow. Some contain local paths or assumptions about the Python environment, and I have not verified that every part runs from a clean installation.

This repository is therefore best treated as a record of the analysis and its outputs, rather than a ready-to-run, maintained software package.
