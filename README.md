# Exoplanets

This is the repository I use for my TESS exoplanet work.

I started it while looking through TESS data for possible transit signals. Over time it turned into a collection of scripts and notebooks for processing light curves, reviewing candidates, checking possible false positives, working with stellar parameters, and experimenting with exoplanet characterization.

Some of this is research code and some of it is experimental. I have kept older notebooks and approaches here because they show how the analysis developed.

## Main code

`FinnyExoplanetAnalyzer.py` is the main TESS light-curve analysis class. It searches and selects TESS light curves, combines observations from different sectors, searches for periods with BLS, folds light curves, creates transit models, measures transit depths, and saves candidate results.

`Exoplanet.py` stores the candidate and host-star parameters and handles derived quantities such as planet radius, mass estimates from ExoRM, semi-major axis, equilibrium temperature, and fitted transit-model parameters.

`analyze_candidates.py` is the interactive candidate-review script. It runs the analyzer on selected TICs, shows the light curves and periodogram, lets me adjust the search and review the candidate, and saves candidates that I choose to keep.

`analyze_stars.py` runs the same general analysis over a larger list of TICs while keeping track of completed objects.

`email_ctois.py` downloads CTOI/ExoFOP information for selected targets and sends the resulting table by email.

## Notebooks

`process_ids.ipynb` works with TESS TCE data and filters out known or already-completed targets before producing TIC-ID lists for further analysis.

`process_ctois.ipynb` takes saved candidate results, adds host-star information from the TIC, optionally recalculates transit models, and produces the tables and files used for CTOI uploads.

`analyze_triceratops.ipynb` tests candidates with TRICERATOPS and examines the false-positive scenarios, including FPP and NFPP.

`analyze_optimized.ipynb` contains experiments in candidate vetting. I used it to check things such as V-shaped transits, possible secondary eclipses, period mistakes, contamination, centroids, unusually large inferred radii, and other signs that a signal might not be planetary.

`analyze_variables.ipynb` is an exploratory time-series notebook using TESS target-pixel data, stitched light curves, and Lomb-Scargle periodograms.

`correlation.ipynb` downloads confirmed exoplanet measurements from the NASA Exoplanet Archive, selects measurements with relatively small uncertainties, saves a local exoplanet data set, and explores relationships between planetary properties.

## Folders

`CTOI Creation/` contains the candidate-selection, analysis, and upload material.

`Paper Material/ExoRM/` contains material related to the ExoRM project.

## Notes

This is not meant to be a finished software package. Some of the code is old, some experiments did not work as intended, and some of the notebooks are mainly records of things I was trying at the time. I keep them here because the repository is also a record of how the project developed.
