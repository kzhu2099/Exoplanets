import json
import math
import datetime

class Exoplanet:
    def __init__(self, host_star_name, letter = 'b'):
        if host_star_name != '' and letter != '':
            self.host_star = {'name': host_star_name}
            self.name = f'{host_star_name} {letter}'
            self.id_num = int(host_star_name.split(' ')[1])

    def add_periodogram_details(self, period, transit_time, transit_duration):
        self.period = period.value
        self.transit_time = transit_time.value.item()
        self.transit_duration = transit_duration.value

    def add_transit_depth(self, transit_depth):
        self.transit_depth = transit_depth

    def add(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def load_from_json(filepath):
        exoplanet = Exoplanet('', '')

        with open(filepath, 'r') as file:
            data = json.loads(file.read())
            for key, value in data.items():
                setattr(exoplanet, key, value)

        exoplanet.id_num = int(exoplanet.host_star['name'].split(' ')[1])

        return exoplanet

    def to_json(self, filepath):
        attributes = {attr: getattr(self, attr) for attr in self.__dict__}
        result = json.dumps(attributes, indent = 4, sort_keys = True)

        if filepath is not None:
            with open(filepath, 'w') as file:
                file.write(result)

        return result

    def add_host_star_attributes(self, radius, mass, teff):
        self.host_star['radius'] = radius
        self.host_star['mass'] = mass
        self.host_star['teff'] = teff

    def calculate_attributes(self):
        self.parameters = {}
        self.epoch = self.transit_time + 2457000
        self.transit_depth_ppm = self.transit_depth * 10 ** 6
        self.transit_depth_unc_ppm = self.transit_depth_unc * 10 ** 6

        SMASS_EMASS = 109.2
        DAY_SECOND = 86400
        METER_AU = 6.68458712 * 10 ** -12
        SRADIUS_METER = 6.957 * 10 ** 8
        SMASS_KG = 1.98847 * 10 ** 30

        self.host_star['r_earth'] = self.host_star['radius'] * SMASS_EMASS

        self.r_planet_over_star = math.sqrt(self.transit_depth)
        self.radius = self.host_star['r_earth'] * self.r_planet_over_star

        self.mass = self.radius ** 3

        self.semi_major_axis_meters = (
            (((self.period * DAY_SECOND) ** 2) * (6.674 * 10 ** -11) * (self.host_star['mass'] * SMASS_KG)) /
            (4 * math.pi ** 2)
        ) ** (1 / 3)

        self.semi_major_axis_au = self.semi_major_axis_meters * METER_AU

        self.t_equilibrium = self.host_star['teff'] * math.sqrt(
            (self.host_star['radius'] * SRADIUS_METER) / (2 * self.semi_major_axis_meters)
        )

        self.parameters.update({
            'period': self.period,
            'period_unc': self.period_unc,
            'epoch': self.epoch,
            'epoch_unc': self.transit_time_unc,
            'depth': self.transit_depth_ppm,
            'depth_unc': self.transit_depth_unc_ppm,
            'duration': self.transit_duration,
            'duration_unc': self.transit_duration_unc,
            'r_planet': self.r_planet_over_star,
            'radius': self.radius,
            'mass': self.mass,
            'temp': self.t_equilibrium,
            'sma': self.semi_major_axis_au
            }
        )

        self.parameters.update({
            'target': f'TIC{self.id_num}.{self.exoplanet_num:02d}',
            'flag': 'newctoi',
            'disp': 'PC',
            'tag': f'{datetime.datetime.now().strftime('%Y%m%d')}_kzhu_autotag-1_{self.id_num}',
        })

        self.remove_nan_parameters()

        self.csv_string = \
        '{target}|{flag}|{disp}|{period}|{period_unc}|{epoch}|{epoch_unc}|{depth}|{depth_unc}|{duration}|{duration_unc}|||||' \
        '{r_planet}||||{radius}||{mass}||{temp}||||||{sma}||||||||||{tag}||0|From TCE reviewed by Kevin Zhu'.format(**self.parameters)

    def remove_nan_parameters(self):
        for key, value in self.parameters.items():
            if type(value) == float and math.isnan(value):
                self.parameters[key] = ''