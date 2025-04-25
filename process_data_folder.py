import os
import json
import shutil

paths = ['Exoplanet Contribution/2025/April 2025/TrES-3_2019-MARCH-23', 'Exoplanet Contribution/2025/April 2025/WASP-43_2019-MARCH-08']

for path in paths:
    data = os.path.basename(path).split('_')
    '''
    os.makedirs(f'{path}/output')
    os.makedirs(f'{path}/fits')

    for filename in os.listdir(path):
        if filename.endswith('.FITS.gz'):
            source = os.path.join(path, filename)
            new = os.path.join(path + '/fits', filename)
            shutil.move(source, new)'''

    inits = {
        'inits_guide': {
            'Title': 'EXOTIC\'s Initialization File',
            'Comment': 'Please answer all the following requirements below by following the format of the given',
            'Comment1': 'sample dataset HAT-P-32 b. Edit this file as needed to match the data wanting to be reduced.',
            'Comment2': 'Do not delete areas where there are quotation marks, commas, and brackets.',
            'Comment3': 'The inits_guide dictionary (these lines of text) does not have to be edited',
            'Comment4': 'and is only here to serve as a guide. Will be updated per user\'s advice.',
            'Image Calibrations Directory Guide': 'Enter in the path to image calibrations or enter in null for none.',
            'Planetary Parameters Guide': 'For planetary parameters that are not filled in, enter in null.',
            'Comparison Star(s) Guide': 'Up to 10 comparison stars can be added following the format given below.',
            'Obs. Latitude Guide': 'Indicate the sign (+ North, - South) before the degrees. Needs to be in decimal or HH:MM:SS format.',
            'Obs. Longitude Guide': 'Indicate the sign (+ East, - West) before the degrees. Needs to be in decimal or HH:MM:SS format.',
            'Plate Solution': 'For your image to be given a plate solution, type y.',
            'Plate Solution Disclaimer': 'One of your imaging files will be publicly viewable on nova.astrometry.net.',
            'Standard Filter': 'To use EXOTIC standard filters, type only the filter name.',
            'Custom Filter': 'To use a custom filter, enter in the FWHM in optional_info.',
            'Target Star RA': 'Must be in HH:MM:SS sexagesimal format.',
            'Target Star DEC': 'Must be in +/-DD:MM:SS sexagesimal format with correct sign at the beginning (+ or -).',
            'Demosaic Format': 'Optional control for handling Bayer pattern color images - to use, provide Bayer color patttern of your camera (RGGB, BGGR, GRBG, GBRG) - null (no color processing) is default',
            'Demosaic Output': 'Select how to process color data (gray for grayscale, red or green or blue for single color channel, blueblock for grayscale without blue, [ R, G, B ] for custom weights for mixing colors.  green is default',
            'Formatting of null': 'Due to the file being a .json, null is case sensitive and must be spelled as shown.',
            'Decimal Format': 'Leading zero must be included when appropriate (Ex: 0.32, .32 or 00.32 causes errors.).'
        },
        'user_info': {
            'Directory with FITS files': f'{path}/fits',
            'Directory to Save Plots': f'{path}/output',
            'AAVSO Observer Code (blank if none)': 'ZKEA',
            'Secondary Observer Codes (blank if none)': '',
            'Observation date': data[1],
            'Obs. Latitude': '+31.68',
            'Obs. Longitude': '+110.88',
            'Obs. Elevation (meters; Note: leave blank if unknown)': 1268.0,
            'Camera Type (CCD or DSLR)': 'CCD',
            'Pixel Binning': '1x1',
            'Filter Name (aavso.org/filters)': 'N/A',
            'Observing Notes': 'From Whipple Observatory',
            'Plate Solution? (y/n)': 'y',
            'Add Comparison Stars from AAVSO? (y/n)': 'y',
            'Target Star X & Y Pixel': '[200, 200]',
            'Comparison Star(s) X & Y Pixel': '[[150, 150], [300, 300]]',
            'Demosaic Format': None,
            'Demosaic Output': None,
            'Directory of Flats': None,
            'Directory of Darks': f'{path}/darks',
            'Directory of Biases': None
        },

        'optional_info': {
            'Filter Minimum Wavelength (nm)': 300.0,
            'Filter Maximum Wavelength (nm)': 1100.0
        }
    }

    with open(f'{path}/.json', 'w') as file:
        file.write(json.dumps(inits, indent = 4))