import pandas

data = pandas.read_csv('Exoplanet Discovering/TIC ID Data/tess80tce.csv')

indicies = data.groupby('ticid')['tce_period'].transform(lambda x: (x > 10 ** 0.5) & (x < 10 ** 1.5).all())
data = data.loc[indicies]

indicies = data.groupby('ticid')['tce_depth'].transform(lambda x: (x < 75000).all())
data = data.loc[indicies]

ids = data['ticid'].drop_duplicates().sample(frac = 1).reset_index(drop = True)

completed_ids = pandas.read_csv('Exoplanet Discovering/IDs/completed_tic_ids.csv')['ticid']
tois = pandas.read_csv('Exoplanet Discovering/TIC ID Data/exofop_tess_tois.csv')['TIC ID'].astype(int)

ids = ids[~ids.isin(completed_ids)]
ids = ids[~ids.isin(tois)]

ids.to_csv('tic_ids.csv', index = False)