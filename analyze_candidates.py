from FinnyExoplanetAnalyzer import FinnyExoplanetAnalyzer
import time
import numpy

candidates = \
[
# 284611896,
# 55655482,
# 268290940,
# 176871438,
# 38850860,
# 62573638,
# 102625324,
# 279322914,
# 55727842,
# 342556321,
# 23689332,
# 73248090,
297701617,
76903841,
270462117,
441444256,
90083037,
234518605,
]

use_tesscuts = False

no = ['no', 'NO', 'n', 'N']
yes = ['yes', 'YES', 'y', 'Y']

start_time = time.time()
if __name__ == '__main__':
    print('Welcome to the Finny Exoplanet Analyzer for Exoplanet Candidates!')

    for i in range(len(candidates)):
        star_id = f'TIC {candidates[i]}'

        analyzer = FinnyExoplanetAnalyzer(f'{star_id}', use_tesscuts = use_tesscuts, auto_mode = True, auto_folder = f'Exoplanet Discovering/Candidates/{star_id}')

        print('-' * 50)
        print(f'Requesting data for {star_id} ({i + 1} / {len(candidates)}).')

        # analyzer.plot_tesscut()

        light_curve = analyzer.create_light_curve()
        if light_curve is None:
            print(f'Error encountered when a creating light curve for {star_id}.')
            print('Skipping this star.')
            continue

        else:
            print('-' * 50)
            print(f'Analyzing {star_id} ({i + 1} / {len(candidates)}).')

        analyzer.plot_collection()

        # if input('Do you want to process this star? ') not in yes:
        #     continue

        log_searchsize = [0, 1.5, 4]
        analyzer.plot_stitched_light_curve(overlay_masks = False, overlay_models = False)

        while True:
            analyzer.create_periodogram(log_searchsize = log_searchsize)
            analyzer.plot_periodogram()

            analyzer.create_transit_model(analyzer.exoplanet_letter)

            analyzer.fold_light_curve()
            analyzer.plot_folded_light_curve()

            if input('Would you like to confirm that this is an exoplanet candidate and continue on? ') in yes:
                analyzer.mask_exoplanet(analyzer.exoplanet_letter)
                analyzer.get_transit_depth()
                analyzer.plot_transit_depth()
                analyzer.is_exoplanet()

            if input('Continue analyzing the current star? ') in yes:
                analyzer.plot_stitched_light_curve(overlay_masks = True, overlay_models = False)
                log_searchsize = [numpy.log10(float(x.strip())) for x in input('Enter a new search size for the periodogram in the format min, max, num: ').split(',')]

            else:
                if len(analyzer.exoplanets) > 0 and input('Would you like to save this star\'s exoplanet(s)? ') in yes:
                    save_paths = analyzer.save(f'Exoplanet Discovering/Candidates/{analyzer.star}')
                    print(save_paths)
                    with open('Exoplanet Discovering/candidate_data_paths.txt', 'a') as file:
                        file.writelines(item + '\n' for item in save_paths)

                break

    print('Thank you for using the Finny Exoplanet Analyzer.')

    print(f'Automatic analysis of {len(candidates)} candidates completed after {time.time() - start_time:.3f} seconds')