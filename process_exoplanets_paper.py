from Exoplanet import Exoplanet
import datetime
import pandas
import os

data_paths = []

with open('Exoplanet Discovering/candidate_data_paths.txt', 'r+') as file:
    data_paths.extend([file_name.strip() for file_name in file.readlines()])
    file.seek(0)

for path in data_paths:
    e = Exoplanet.load_from_json(path)

    url = f'https://exofop.ipac.caltech.edu/tess/download_stellar.php?id={e.id_num}'
    data = pandas.read_csv(url, delimiter = '|')

    e.add_host_star_attributes(
        radius = data['Radius (R_Sun)'].to_list()[0],
        mass = data['Mass (M_Sun)'].to_list()[0],
        teff = data['Teff (K)'].to_list()[0]
    )

    e.calculate_attributes()

    e.to_json(f'Exoplanet Discovering/Paper Materials/Data/{e.host_star['name']} Exoplanet {e.letter}.json')

with open('Exoplanet Discovering/candidate_data_paths.txt', 'r+') as file:
    file.truncate(0)