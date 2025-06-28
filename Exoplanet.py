import json
import math
import datetime
import numpy
from scipy.optimize import least_squares
import batman
from ExoRM import ExoRM

class Exoplanet:
    def __init__(self, host_star_name, letter = 'b'):
        if host_star_name != '' and letter != '':
            self.host_star = {'name': host_star_name}
            self.letter = letter
            self.name = f'{host_star_name} {letter}'
            self.id_num = int(host_star_name.split(' ')[1])

        self.parameters = {}

    def add_periodogram_details(self, period, transit_time, transit_duration):
        self.period = period.value
        self.transit_time = transit_time.value.item()
        self.transit_duration = transit_duration.value

        self.triceratops = {
            'period': self.period,
            'transit_time': self.transit_time,
            'transit_duration': self.transit_duration
        }

    def add_transit_depth(self, transit_depth):
        self.transit_depth = transit_depth

        self.triceratops['transit_depth'] = self.transit_depth

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
        self.remove_nan()

        attributes = {attr: getattr(self, attr) for attr in self.__dict__}
        result = json.dumps(attributes, indent = 4, sort_keys = True)
        result = result.replace('NaN', 'null')

        if filepath is not None:
            with open(filepath, 'w') as file:
                file.write(result)

        return result

    def add_host_star_attributes(self, **kwargs):
        self.host_star.update(**kwargs)

    def calculate_attributes(self):
        self.epoch = self.transit_time + 2457000
        self.transit_depth_ppm = self.transit_depth * 1e6
        self.transit_depth_unc_ppm = self.transit_depth_unc * 1e6

        SRADIUS_ERADIUS = 109.2
        DAY_SECOND = 86400
        METER_AU = 6.68458712e-12
        SRADIUS_METER = 6.957e8
        SMASS_KG = 1.98847e30

        self.host_star['r_earth'] = self.host_star['radius'] * SRADIUS_ERADIUS

        # Use modeled value if available

        if hasattr(self, 'model_params') and self.model_params and len(self.model_params) > 5 and not math.isnan(self.model_params[5]):
            self.r_planet_over_star = self.model_params[5]
            self.radius_source = 'model_fit'

        else:
            self.r_planet_over_star = math.sqrt(self.transit_depth)
            self.radius_source = 'sqrt_depth'

        self.radius = self.host_star['r_earth'] * self.r_planet_over_star

        self.mass, self.min_mass, self.max_mass = self.predict_mass(self.radius)
        self.mass_unc_lower = self.mass - self.min_mass
        self.mass_unc_higher = self.max_mass - self.mass
        self.mass_unc = numpy.abs(self.mass_unc_higher + self.mass_unc_lower) / 2

        self.semi_major_axis_meters = (
            (((self.period * DAY_SECOND) ** 2) * 6.674e-11 * (self.host_star['mass'] * SMASS_KG)) /
            (4 * math.pi ** 2)
        ) ** (1 / 3)

        self.semi_major_axis_au = self.semi_major_axis_meters * METER_AU
        self.sma_over_r_star = self.semi_major_axis_meters / (self.host_star['radius'] * SRADIUS_METER)

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
            'mass_unc_lower': self.mass_unc_lower,
            'mass_unc_higher': self.mass_unc_higher,
            'mass_unc': self.mass_unc,
            'temp': self.t_equilibrium,
            'sma': self.semi_major_axis_au,
        })

    def make_csv_string(self):
        self.parameters.update({
            'target': f'TIC{self.id_num}.{self.exoplanet_num:02d}',
            'flag': 'newctoi',
            'disp': 'PC',
            'tag': f'{datetime.datetime.now().strftime('%Y%m%d')}_kzhu_autotag-1_{self.id_num}',
        })

        self.csv_string = \
        '{target}|{flag}|{disp}|{period}|{period_unc}|{epoch}|{epoch_unc}|{depth}|{depth_unc}|{duration}|{duration_unc}|||{imp}||' \
        '{r_planet}||||{radius}||{mass}|{mass_unc}|{temp}||||||{sma}||{ecc}||{arg_peri}||||||{tag}||0|From TCE reviewed by Kevin Zhu'.format(**self.parameters)

        self.csv_string = self.csv_string.replace('NaN', '')
        self.csv_string = self.csv_string.replace('nan', '')

    @staticmethod
    def transit_model(params, t):
        period, t0, rp_rs, a_rs, b, ecc, w, u1, u2 = params
        params_batman = batman.TransitParams()
        params_batman.t0 = t0
        params_batman.per = period
        params_batman.rp = rp_rs
        params_batman.a = a_rs
        params_batman.inc = numpy.degrees(numpy.arccos(b / a_rs))
        params_batman.ecc = ecc
        params_batman.w = w
        params_batman.u = [u1, u2]  # limb-darkening coefficients
        params_batman.limb_dark = 'quadratic'

        m = batman.TransitModel(params_batman, t)
        model_flux = m.light_curve(params_batman)

        return model_flux

    def calculate_all_parameters(self, lightcurve):
        self.calculate_attributes()

        if all(x is not None and not math.isnan(x) for x in [self.period, self.transit_time, self.r_planet_over_star, self.sma_over_r_star]):
            def error(params, t, flux, flux_err, constants):
                period, t0 = constants
                b, ecc, w, u1, u2, rp_rs, a_rs = params
                model_flux = Exoplanet.transit_model([period, t0, rp_rs, a_rs, b, ecc, w, u1, u2], t)
                return (model_flux - flux) / flux_err

            lightcurve = lightcurve.remove_nans()
            time = lightcurve['time'].value
            flux = lightcurve['flux'].value
            flux_err = numpy.nan_to_num(lightcurve['flux_err'].value, nan=1e-6)

            result = least_squares(
                error,
                x0 = [
                    0.5,      # b
                    0.0,      # ecc
                    90.0,     # omega
                    0.1, 0.3, # limb darkening
                    self.r_planet_over_star,  # rp/rs
                    self.sma_over_r_star      # a/rs
                ],
                args = (time, flux, flux_err, [self.period, self.transit_time]),
                bounds = (
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 1.0],  # lower
                    [1.0, 0.9, 360.0, 1.0, 1.0, 0.5, 100.0] # upper
                )
            )

            self.model_params = list(result.x)

            b, ecc, w, u1, u2, rp_rs, a_rs = self.model_params
            self.impact_parameter = b
            self.sma_over_r_star = a_rs
            self.r_planet_over_star = rp_rs  # ensure consistency

            self.parameters.update({
                'imp': b,
                'inc': numpy.degrees(numpy.arccos(b / a_rs)),
                'ecc': ecc,
                'arg_peri': w,
                'u1': u1,
                'u2': u2,
            })

            self.calculate_attributes()

        else:
            self.parameters.update({
                'imp': math.nan,
                'inc': math.nan,
                'ecc': math.nan,
                'arg_peri': math.nan,
                'u1': math.nan,
                'u2': math.nan
            })
            self.model_params = [math.nan] * 7

        return self.model_params

    def predict_mass(self, radius):
        erm = ExoRM()
        erm.load_trace()

        return list(float(x) for x in erm.predict_full_linear([radius]))

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