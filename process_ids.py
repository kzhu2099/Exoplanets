import pandas

parent_folder = 'CTOI Creation'
data_path = f'{parent_folder}/TIC ID Data/tess_tce_60s.csv'
data = pandas.read_csv(data_path)

indicies = data.groupby('ticid')['tce_depth'].transform(lambda x: (x < 75000).all())
data = data.loc[indicies]

indicies = data.groupby('ticid')['tce_period'].transform(lambda x: ((x > 10 ** 0.5) & (x < 10 ** 1)).any())
data = data.loc[indicies]

ids = data['ticid'].drop_duplicates().reset_index(drop = True)

completed_ids = pandas.read_csv(f'{parent_folder}/Current IDs/completed_tic_ids.csv')['ticid']
tois = pandas.read_csv(f'{parent_folder}/TIC ID Data/exofop_tess_tois.csv')['TIC ID'].astype(int)

ids = ids[~ids.isin(completed_ids)]
ids = ids[~ids.isin(tois)]

ids.to_csv(f'{parent_folder}/Current IDs/tic_ids_small_period.csv', index = False)

data = pandas.read_csv(data_path)

indicies = data.groupby('ticid')['tce_depth'].transform(lambda x: (x < 75000).all())
data = data.loc[indicies]

indicies = data.groupby('ticid')['tce_period'].transform(lambda x: ((x > 10 ** 1) & (x < 10 ** 1.7)).any())
data = data.loc[indicies]

ids = data['ticid'].drop_duplicates().reset_index(drop = True)

completed_ids = pandas.read_csv(f'{parent_folder}/Current IDs/completed_tic_ids.csv')['ticid']
tois = pandas.read_csv(f'{parent_folder}/TIC ID Data/exofop_tess_tois.csv')['TIC ID'].astype(int)

ids = ids[~ids.isin(completed_ids)]
ids = ids[~ids.isin(tois)]

ids.to_csv(f'{parent_folder}/Current IDs/tic_ids_large_period.csv', index = False)