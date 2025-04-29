import os
import json
import math

data = []

for (dirpath, dirnames, filenames) in os.walk('Exoplanet Discovering/Paper Materials/Data'):
    for filepath in filenames:
        if filepath == '.DS_Store':
            continue

        with open(dirpath + '/' + filepath, 'r') as file:
            exoplanet = json.loads(file.read())

        if type(exoplanet) == list:
            continue

        data.append(exoplanet)

    break

with open('Exoplanet Discovering/Paper Materials/params_planet_20250429_update.txt', 'w') as file:
    for exoplanet in data:
        file.write(exoplanet['csv_string'] + '\n')

with open('Exoplanet Discovering/Paper Materials/Data/full.json', 'w') as file:
    string = json.dumps(data, indent = 4)
    string = string.replace('NaN', 'null')
    file.write(string)