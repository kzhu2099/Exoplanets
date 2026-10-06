# Exoplanets

# Exoplanets

> **Past research project.** This project was developed primarily in 2025 as an earlier stage of my research. I focused on building Python tools to search TESS data for possible transiting exoplanets, analyze transit signals, and develop candidate-vetting workflows.

> This is no longer my active research repository. Since working on this project, I have moved on to other research questions and projects, including transit timing, binary-star and stellar-variability studies, asteroseismology, and other follow up projects. My current work is focused on characterizing and understanding systems rather than searching TESS data for new exoplanet candidates. Nonetheless, this project was still extremely important for my own growth and devlopment as a researcher.

This repository contains the code and results from that earlier TESS exoplanet-analysis work.

The project began as a place to develop and organize my TESS analysis code and came to include candidate analysis, mass estimation, CTOI work, exploratory notebooks, and the results produced while running the different parts of the project.

## Python

### `FinnyExoplanetAnalyzer.py`

The main TESS light-curve analyzer. It retrieves TESS light curves from MAST, cleans and normalizes them, stitches observations from different sectors, and searches for transit signals with Box Least Squares.

The BLS search starts with a broad period range and then searches around the strongest signal to refine the period and transit duration. The resulting signal can be folded, modeled, plotted, and measured.

The analyzer also supports masking a detected transit before running another search. This lets me look for additional periodic signals in the same target rather than only keeping the strongest signal in the periodogram.

### `Exoplanet.py`

Contains the candidate object and the calculations used after finding a transit signal.

The class stores the measured transit and host-star properties and calculates quantities such as \(R_p/R_\star\), planetary radius, estimated mass, semi-major axis, and equilibrium temperature.

For transit fitting, it uses `batman` and `scipy.optimize.least_squares`. The transit model includes the orbital geometry and quadratic limb darkening, and the fitted transit parameters are then used for the physical-parameter calculations. Masses are estimated with ExoRM.

This is also where the candidate information is converted into the format used later in the CTOI processing.

### `analyze_candidates.py`

Used for working through individual targets. It runs the main analyzer, saves the diagnostic products, and lets me inspect candidates and rerun the search when the initial period or signal is not convincing.

### `analyze_stars.py`

Runs the same analysis over larger target lists. It keeps track of completed targets and saves the resulting light curves, periodograms, candidate data, and other products.

## Notebooks

### `analyze_optimized.ipynb`

Additional candidate-vetting work developed around the main analyzer. This contains tests for things such as transit shape, odd/even transit depths, secondary eclipses, harmonics, stellar variability, contamination, and cases where the initial period or physical parameters need another look.

It also contains experiments with different detrending and outlier-removal approaches for difficult light curves.

### `analyze_triceratops.ipynb`

False-positive analysis using TRICERATOPS.

The notebook takes candidate transit signals and compares different astrophysical explanations for them, including planetary and eclipsing-binary scenarios involving the target or nearby stars. It uses the target's TESS data together with information about neighboring sources when calculating the scenario probabilities.

### `analyze_variables.ipynb`

Used to investigate periodic stellar variability separately from the transit search. It uses Lomb-Scargle periodograms on TESS light curves and folds the data on the resulting periods. I also use it to check harmonic interpretations of signals that may not have an obvious single period.

### `process_ctois.ipynb`

Processes the candidates produced by the earlier analysis.

It retrieves additional stellar information from MAST and can work directly with TESS target-pixel files. The notebook constructs aperture light curves from the pixels and includes a PCA-based correction with `DesignMatrix` and `RegressionCorrector`. The corrected light curves can then be passed back into the transit model in `Exoplanet.py`.

It also handles the candidate JSON data, generated plots, and tabular files used in the CTOI workflow.

### `process_ids.ipynb`

Prepares the target lists used by the rest of the project. It combines the relevant TESS candidate and TCE information, cleans the TIC IDs, removes duplicates, and produces the lists used by the analysis scripts.

### `correlation.ipynb`

Exploratory work using the NASA Exoplanet Archive. It is separate from the TESS candidate pipeline and is used to look at relationships between properties of known exoplanets.

## `CTOI Creation`

This is the main archive of the results produced while running the candidate and mass-analysis workflow.

Rather than putting all of the output into one directory, the work is grouped by analysis type and then by when the analysis was run. This makes it possible to keep results from different stages of the project without replacing earlier work.

### `CTOI Creation/Mass Analysis`

This contains the outputs from the mass and candidate analysis.

The directory is organized chronologically. The folders are separated by year and month, and individual analysis runs are stored under their run date. Within a run, different kinds of products are kept separately.

`stitched_light_curves/` contains the combined TESS light curves produced from the available observations for each target. These are the working light curves used for the later period and transit analysis.

`transit_depths/` contains the plots and measurements used to inspect the depth of the detected transit signals. The transit depth is one of the main quantities used later to estimate \(R_p/R_\star\) and the planetary radius.

As the analysis developed, additional output folders were added for other products. The dated structure is intentional: these files are research outputs and intermediate results, not just temporary files that can always be regenerated in exactly the same form.

## `Paper Material/ExoRM`

Contains the material associated with my ExoRM work, including the analysis used to develop and test the mass-radius model.

## Other files

### `exoplanets.csv`

A local copy of the exoplanet catalog used for the broader population analysis.

### `email_ctois.py`

Utility code used for the administrative side of the CTOI workflow.

## Dependencies

The main TESS analysis uses Lightkurve, Astropy, astroquery, batman, SciPy, wotan, TRICERATOPS, and ExoRM.

The code was written around my own research workflow, so some scripts contain local paths or assumptions that may need to be changed when running them elsewhere.
