import os
import astroalign as aa
from astropy.io import fits

# Example usage
folders = [
    'Exoplanet Contribution/2025/April 2025/TrES3_2013APRIL20',
    'Exoplanet Contribution/2025/April 2025/TrES3_2014SEPTEMBER5',
    'Exoplanet Contribution/2025/April 2025/WASP52_2020AUGUST10'
]

for main_folder in folders:
    input_folder = f'{main_folder}/fits'
    output_folder = f'{main_folder}/fits_aligned' # easy copy-paste to make the folders

    # Get all FITS files in the folder
    files = [f for f in os.listdir(input_folder)]

    # Make sure the output folder exists
    os.makedirs(output_folder, exist_ok = True)

    # Read and align images
    reference_image = None  # We'll use the first image as the reference

    successful_alignments = 0
    for i, file in enumerate(files):
        try:
            file_path = os.path.join(input_folder, file)
            # file = file[:-3] # makes it a .FITS, works but increases file size by a lot lot
            with fits.open(file_path) as hdul:
                image_data = hdul[0].data
                header = hdul[0].header  # Get the header from the original FITS file

                if reference_image is None:  # Set the first image as reference
                    output_file = os.path.join(output_folder, file)
                    hdu = fits.PrimaryHDU(image_data, header = header)
                    hdu.writeto(output_file, overwrite = True)

                    reference_image = image_data

                else:
                    # Align the current image with the reference image
                    aligned_image, _ = aa.register(image_data, reference_image)

                    # Save the aligned image along with its updated header
                    output_file = os.path.join(output_folder, file)
                    hdu = fits.PrimaryHDU(aligned_image, header = header)
                    hdu.writeto(output_file, overwrite = True)

            print(f'Image {i + 1} / {len(files)} aligned and updated: {file}')
            successful_alignments += 1

        except Exception as e:
            print(f'Image {i + 1} / {len(files)} alignment failed, skipping this file. Error: {e}')
            continue

    print(f'Aligned {successful_alignments} images successfully and saved to \'{output_folder}\'')