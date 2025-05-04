import json
import math
import datetime
import numpy
import pickle
from astroquery.mast import Catalogs
from scipy.optimize import least_squares
import batman

class Exoplanet:
    def __init__(self, host_star_name, letter = 'b'):
        if host_star_name != '' and letter != '':
            self.host_star = {'name': host_star_name}
            self.letter = letter
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

        exoplanet.remove_none()

        exoplanet.id_num = int(exoplanet.host_star['name'].split(' ')[1])

        return exoplanet

    def to_json(self, filepath):
        attributes = {attr: getattr(self, attr) for attr in self.__dict__}
        result = json.dumps(attributes, indent = 4, sort_keys = True)
        result = result.replace('NaN', 'null')

        self = self.remove_nan()

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

        SRADIUS_ERADIUS = 109.2
        DAY_SECOND = 86400
        METER_AU = 6.68458712 * 10 ** -12
        SRADIUS_METER = 6.957 * 10 ** 8
        SMASS_KG = 1.98847 * 10 ** 30

        self.host_star['r_earth'] = self.host_star['radius'] * SRADIUS_ERADIUS

        self.r_planet_over_star = math.sqrt(self.transit_depth)
        self.radius = self.host_star['r_earth'] * self.r_planet_over_star

        self.mass = self.predict_mass(self.radius)

        self.semi_major_axis_meters = (
            (((self.period * DAY_SECOND) ** 2) * (6.674 * 10 ** -11) * (self.host_star['mass'] * SMASS_KG)) /
            (4 * math.pi ** 2)
        ) ** (1 / 3)

        self.semi_major_axis_au = self.semi_major_axis_meters * METER_AU
        self.sma_over_r_star = self.semi_major_axis_meters / (self.host_star['radius'] * SRADIUS_METER)

        self.t_equilibrium = self.host_star['teff'] * math.sqrt(
            (self.host_star['radius'] * SRADIUS_METER) / (2 * self.semi_major_axis_meters)
        )

        # self.impact_parameter = math.asin(
        #     math.sqrt(
        #         (((self.host_star['radius'] * (1 + self.r_planet_over_star) * SRADIUS_METER) ** 2) - (self.semi_major_axis_meters ** 2)) /
        #         ((self.semi_major_axis_meters ** 2) * (math.sin(math.pi * (self.transit_duration * 3600) / (self.period * 86400)) ** 2))
        #     )
        # )

        try:
            self.impact_parameter = math.sqrt((1 + self.r_planet_over_star) ** 2 - (self.host_star['radius'] * SRADIUS_METER * self.period * 86400 / (math.pi * self.semi_major_axis_meters * self.transit_duration * 3600)) ** 2)

        except:
            self.impact_parameter = math.nan

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
            'sma': self.semi_major_axis_au,
            'imp': self.impact_parameter
            }
        )

        self.parameters.update({
            'target': f'TIC{self.id_num}.{self.exoplanet_num:02d}',
            'flag': 'newctoi',
            'disp': 'PC',
            'tag': f'{datetime.datetime.now().strftime('%Y%m%d')}_kzhu_autotag-1_{self.id_num}',
        })

        self.remove_nan()

        self.csv_string = \
        '{target}|{flag}|{disp}|{period}|{period_unc}|{epoch}|{epoch_unc}|{depth}|{depth_unc}|{duration}|{duration_unc}|||||' \
        '{r_planet}||||{radius}||{mass}||{temp}||||||{sma}||||||||||{tag}||0|From TCE reviewed by Kevin Zhu'.format(**self.parameters)
        self.csv_string = self.csv_string.replace('NaN', '')
        self.csv_string = self.csv_string.replace('nan', '')

    '''
    This doesn't seem to work, so we can find the impact parameter by the formula since it assumes eccentricity as 0 anyways.
    In the next version of this where everything is in one, hopefully I can do it better and use the transit modeling.
    @staticmethod
    def transit_model(params, t):
        period, t0, rp_rs, a_rs, b, u1, u2 = params
        params_batman = batman.TransitParams()
        params_batman.t0 = t0
        params_batman.per = period
        params_batman.rp = rp_rs
        params_batman.a = a_rs
        params_batman.inc = numpy.degrees(numpy.arccos(b / a_rs))
        params_batman.ecc = 0
        params_batman.w = 90
        params_batman.u = [u1, u2]  # limb-darkening coefficients
        params_batman.limb_dark = 'quadratic'

        m = batman.TransitModel(params_batman, t)
        model_flux = m.light_curve(params_batman)

        return model_flux

    def calculate_using_transit_model(self, lightcurve):
        self.calculate_attributes() # get initial guesses

        def error(params, t, flux, flux_err):
            model_flux = Exoplanet.transit_model(params, t)

            return (model_flux - flux) / flux_err

        lightcurve = lightcurve.remove_nans()
        time = lightcurve['time'].value
        flux = lightcurve['flux'].value
        flux_err = lightcurve['flux_err'].value

        result = least_squares(
            error,
            x0 = [self.period, self.transit_time, self.r_planet_over_star, self.sma_over_r_star, 0.5, 0.1, 0.3],
            args = (time, flux, flux_err),
            bounds = (
                [0.1, self.transit_time - 1, 0.0001, 1.0, 0.0, 0.0, 0.0],   # Lower bounds
                [35.0, self.transit_time + 1, 0.2, 100.0, 1.5, 1.0, 1.0]    # Upper bounds
            )
        )

        best_fit_params = result.x

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
            'sma': self.semi_major_axis_au,
            }
        )

        self.best_fit_params = best_fit_params

        return best_fit_params
    '''

    def get_spline(self): # cannot add to attributes since json serializable
        with open('radius_mass_spline.pkl', 'rb') as file:
            model = pickle.load(file)

        return model

    def predict_mass(self, radius):
        spline = self.get_spline()

        return 10 ** spline(numpy.log10(radius))

    def remove_none(self, obj = None):
        if obj is None:
            obj = self.__dict__

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    self.remove_none(value)
                elif value is None:
                    obj[key] = math.nan

    def remove_nan(self, obj = None):
        if obj is None:
            obj = self.__dict__

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    self.remove_nan(value)
                elif isinstance(value, float) and math.isnan(value):
                    obj[key] = None

    def add_stellar_parameters(self):
        pass
        # mast catalogs TIC
        # see which sectors are in