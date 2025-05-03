from Exoplanet import Exoplanet
import datetime
from astroquery.mast import Catalogs
import os

data_paths = []

with open('Exoplanet Discovering/candidate_data_paths.txt', 'r+') as file:
    data_paths.extend([file_name.strip() for file_name in file.readlines()])
    file.seek(0)

base_folder = datetime.datetime.now().strftime('Exoplanet Discovering/File Uploads/%Y/%B, %Y')
os.makedirs(base_folder, exist_ok = True)

planet_params_path = ''
for i in range(1, 100):
    planet_params_path = datetime.datetime.now().strftime(f'{base_folder}/params_planet_{datetime.datetime.now().strftime('%Y%m%d')}_{i:03d}.txt')

    if not os.path.exists(planet_params_path):
        break

for path in data_paths:
    e = Exoplanet.load_from_json(path)

    data = Catalogs.query_object(f'TIC {e.id_num}', catalog = 'TIC')[0]

    e.add_host_star_attributes(
        radius = data['rad'],
        mass = data['mass'],
        teff = data['Teff']
    )

    e.calculate_attributes()

    e.to_json(f'Exoplanet Discovering/CTOI JSON/{e.host_star['name']} Exoplanet {e.letter}.json')

    with open(planet_params_path, 'a') as file:
        file.write(e.csv_string + '\n')

    link_prefix = 'https://exofop.ipac.caltech.edu/tess/target.php'
    with open(f'Exoplanet Discovering/uploaded_ctois.csv', 'a') as file:
        file.write(f'{datetime.datetime.now().strftime('%m-%d-%Y')},{e.id_num},{link_prefix}?id={e.id_num}\n')

    with open(f'Exoplanet Discovering/mytargets.txt', 'a') as file:
        file.write(f'{e.id_num}|A|30\n')

with open('Exoplanet Discovering/candidate_data_paths.txt', 'r+') as file:
    file.truncate(0)