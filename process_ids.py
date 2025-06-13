import pandas

parent_folder = 'CTOI Creation'
data_path = f'{parent_folder}/TIC ID Data/tess_tce_80s.csv'
data = pandas.read_csv(data_path)

indicies = data.groupby('ticid')['tce_depth'].transform(lambda x: (x < 75000).all())
data = data.loc[indicies]

indicies = data.groupby('ticid')['tce_period'].transform(lambda x: ((x > 10 ** 0.3) & (x < 10 ** 1)).all())
data = data.loc[indicies]

ids = data['ticid'].drop_duplicates().reset_index(drop = True)

completed_ids = pandas.read_csv(f'{parent_folder}/Current IDs/completed_tic_ids.csv')['ticid']
tois = pandas.read_csv(f'{parent_folder}/TIC ID Data/exofop_tess_tois.csv')['TIC ID'].astype(int)

ids = ids[~ids.isin(completed_ids)]
ids = ids[~ids.isin(tois)]

ids.to_csv(f'{parent_folder}/Current IDs/tic_ids_short_period.csv', index = False)

data = pandas.read_csv(data_path)

indicies = data.groupby('ticid')['tce_depth'].transform(lambda x: (x < 75000).all())
data = data.loc[indicies]

indicies = data.groupby('ticid')['tce_period'].transform(lambda x: ((x > 10 ** 1) & (x < 10 ** 1.7)).all()) # using any means that some will be skipped if it was alreayd proessed in the short ones
data = data.loc[indicies]

ids = data['ticid'].drop_duplicates().reset_index(drop = True)

completed_ids = pandas.read_csv(f'{parent_folder}/Current IDs/completed_tic_ids.csv')['ticid']
tois = pandas.read_csv(f'{parent_folder}/TIC ID Data/exofop_tess_tois.csv')['TIC ID'].astype(int)

ids = ids[~ids.isin(completed_ids)]
ids = ids[~ids.isin(tois)]

ids.to_csv(f'{parent_folder}/Current IDs/tic_ids_long_period.csv', index = False)