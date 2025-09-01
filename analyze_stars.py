from FinnyExoplanetAnalyzer import FinnyExoplanetAnalyzer

import datetime
import time

import pandas

short_period = False

successful_stars_target = 50
successful_stars = 0

parent_folder = 'CTOI Creation'
id_type = 'TIC'
ids_filepath = f'{parent_folder}/Current IDs/tic_ids_60_69_' + ('short_period.csv' if short_period else 'long_period.csv')
completed_ids_filepath = f'{parent_folder}/Current IDs/completed_tic_ids.csv'

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
        id_num = ids.iloc[0]
        ids = ids.drop(0).reset_index(drop = True)

        if id_num in completed_ids.values:
            print(f'{id_type} {id_num} is already in the completed IDs, continuing to next...')

            if len(ids) <= 0:
                print(f'No more {id_type} IDs, finishing program.')
                break

            continue

        completed_ids.loc[len(completed_ids)] = id_num

        star_id = f'{id_type} {id_num}'
        analyzer = FinnyExoplanetAnalyzer(star_id, auto_mode = True, auto_folder = auto_folder)

        print('-' * 50)
        print(f'Requesting data for {star_id} ({successful_stars + 1} / {successful_stars_target}).')

        # analyzer.plot_tesscut()

        light_curve = analyzer.create_light_curve(limit = 5)

        if light_curve is None:
            print(f'No data that matches the filter for {star_id} or there was an error, continuing to next star for efficiency.')
            continue

        else:
            successful_stars += 1
            print('-' * 50)
            print(f'Analyzing {star_id} ({successful_stars} / {successful_stars_target}).')

        analyzer.plot_individual_light_curves(limit = 5) # higher limit means that it must already have been looked at a lot, and if I can't find it in the first few it must not be there
        # analyzer.plot_first_light_curve()
        # analyzer.plot_collection()

        analyzer.plot_stitched_light_curve()

        log_searchsize = [0.2, 1.1, 4] if short_period else [0.75, 1.75, 4] # buffer
        # the short period is from 0.3 to 1, but they could be inaccurate
        # long period includes is only long ones (1 - 1.7)

        analyzer.create_periodogram(log_searchsize = log_searchsize)
        analyzer.plot_periodogram()

        analyzer.create_transit_model(analyzer.exoplanet_letter)

        analyzer.fold_light_curve()
        # analyzer.plot_folded_light_curve()
        analyzer.plot_single_view()

        analyzer.get_transit_depth()
        # analyzer.plot_transit_depth()

        analyzer.is_exoplanet()
        analyzer.save(auto_folder)

        ids.to_csv(ids_filepath, index = False)
        completed_ids.to_csv(completed_ids_filepath, index = False) # only after it is fully done, remnve them

        if len(ids) <= 0:
            print(f'No more {id_type} IDs, finishing program.')
            break

        elif successful_stars >= successful_stars_target:
            print('Target amount of stars analyzed, finishing program.')
            break

    ids.to_csv(ids_filepath, index = False)
    completed_ids.to_csv(completed_ids_filepath, index = False)

    print('Thank you for using the Finny Exoplanet Analyzer.')
    print(f'Automatic analysis of {successful_stars} stars completed after {time.time() - start_time:.3f} seconds')