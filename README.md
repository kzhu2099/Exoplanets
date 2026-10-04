# Exoplanets

This is where I keep my work with TESS exoplanet candidates.

I started with scripts for looking through transit signals. As I kept working, I added candidate review, light-curve processing, false-positive checks, stellar analysis, and experiments with exoplanet characterization. Some of the older work is still here because I want the repository to show how the project developed, not just the final version of it.

## Code

`FinnyExoplanetAnalyzer.py` is the main TESS light-curve analysis code. It finds and combines TESS observations, searches for periods with BLS, folds the data, builds transit models, and saves candidate results.

`Exoplanet.py` stores candidate and host-star parameters and calculates quantities used when looking at a candidate's physical properties.

`analyze_candidates.py` is the interactive candidate-review script. It shows the light curve and periodogram for selected TICs, lets me adjust the search, and saves candidates for later processing.

`analyze_stars.py` runs the analysis over larger lists of TICs and saves the results from each run.

`email_ctois.py` collects CTOI information from ExoFOP and sends the results by email.

## Notebooks

`process_ids.ipynb` works through TESS TCE data and filters targets before they are analyzed.

`process_ctois.ipynb` takes saved candidates, adds host-star information, and prepares the files used for CTOI uploads.

`analyze_triceratops.ipynb` checks candidates with TRICERATOPS and looks at the false-positive scenarios.

`analyze_optimized.ipynb` contains experiments for checking candidate signals, including possible V-shaped events, secondary eclipses, contamination, period problems, and other reasons a transit signal might not be planetary.

`analyze_variables.ipynb` looks at variability in TESS target-pixel data using Lomb-Scargle periodograms.

`correlation.ipynb` uses confirmed exoplanet measurements from the NASA Exoplanet Archive to explore relationships between planetary properties.

## CTOI Creation

`Candidates/` contains saved candidate analyses.

`Current IDs/` contains the lists used to keep track of which TICs were being analyzed.

`Mass Analysis/` contains the larger analysis runs. The `2025/` directory is kept as a record of the work from that year, with each run stored under its date.

`Results/` contains the saved outputs. The folders inside it separate the general data, false-positive results, and files prepared for uploads.

`Source Data/` contains the TESS and ExoFOP tables used to build and filter candidate lists.

## ExoRM

`Paper Material/ExoRM/` contains the figures, tables, and notebooks from my ExoRM mass-radius modeling work.

## Notes

This is research code, not a finished software package. Some of the experiments worked and some did not. I have kept older code and analysis because it records what I actually tried.
