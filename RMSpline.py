import pickle
import numpy

class RMSpline:
    def __init__(self, spline, x, y):
        self.spline = spline

        residuals = y - self.spline(x)
        self.bias_correction = 0.5 * numpy.var(residuals) * numpy.log(10) ** 2

    def __call__(self, x):
        values = self.spline(x)
        values = numpy.where(x < -0.24847484748474846, 0.037222357827663796, values)
        values = numpy.where(x > 1.9305430543054305, 3.7919304730817944, values)

        return values

    predict = __call__

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)