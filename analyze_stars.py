from FinnyExoplanetAnalyzer import FinnyExoplanetAnalyzer

import datetime
import time

import pandas

successful_stars_target = 50
successful_stars = 0

parent_folder = 'Exoplanet Discovering'
id_type = 'TIC'
ids_filepath = f'{parent_folder}/IDs/tic_ids_sector_60_69_filtered_tce.csv'
completed_ids_filepath = f'{parent_folder}/IDs/completed_tic_ids.csv'

start_time = time.time()
if __name__ == '__main__':
    print('Welcome to the Finny Exoplanet Analyzer to analyze many stars automatically!')
    ids = pandas.read_csv(ids_filepath)['ticid']
    completed_ids = pandas.read_csv(completed_ids_filepath)['ticid']

    if len(ids) == 0:
        print(f'No {id_type} ids available in {ids_filepath}')
        exit()

    auto_folder = datetime.datetime.now().strftime(f'{parent_folder}/Mass Analysis/%Y/%B, %Y/%B %d, %Y')

    while True:
        ids.to_csv(ids_filepath, index = False)
        completed_ids.to_csv(completed_ids_filepath, index = False) # only after it is fully done, remnve them

        star_id = ids.iloc[0]
        ids = ids.drop(0).reset_index(drop = True)
        completed_ids.loc[len(completed_ids)] = star_id

        star_id = f'{id_type} {star_id}'
        analyzer = FinnyExoplanetAnalyzer(star_id, auto_mode = True, auto_folder = auto_folder)

        print('-' * 50)
        print(f'Requesting data for {star_id} ({successful_stars + 1} / {successful_stars_target}).')

        # analyzer.plot_tesscut()
        
        light_curve = analyzer.create_light_curve(limit = 5)

        if light_curve is None:
            print(f'Error encountered when creating a light curve for {star_id}, continuing to next star.')
            continue

        else:
            successful_stars += 1
            print('-' * 50)
            print(f'Analyzing {star_id} ({successful_stars} / {successful_stars_target}).')

        analyzer.plot_collection()

        analyzer.plot_stitched_light_curve(overlay_masks = False, overlay_models = False)

        log_searchsize = [0.5, 1.5, 4]

        analyzer.create_periodogram(log_searchsize = log_searchsize)
        analyzer.plot_periodogram()

        analyzer.create_transit_model(analyzer.exoplanet_letter)

        analyzer.fold_light_curve()
        analyzer.plot_folded_light_curve()

        analyzer.get_transit_depth()
        analyzer.plot_transit_depth()

        analyzer.is_exoplanet()
        analyzer.save(auto_folder)

        if len(ids) <= 0:
            print(f'No more {id_type} IDs, finishing program.')
            break

        elif successful_stars >= successful_stars_target:
            print('Target amount of stars analyzed, finishing program.')
            break

    ids.to_csv(ids_filepath, index = False)
    completed_ids.to_csv(completed_ids_filepath, index = False)

    print('Thank you for using the Finny Exoplanet Analyzer.')
    print(f'Automatic analysis of stars {successful_stars} completed after {time.time() - start_time:.3f} seconds')