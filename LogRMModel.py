import pickle
import numpy

class LogRMModel:
    def __init__(self, model, x, y):
        self.model = model
        self.model = self.model
        self.x = x
        self.y = y

        self.residuals = self.y - self.model(self.x)
        self.x_min, self.x_max, self.y_min, self.y_max = None, None, None, None

        self.calculate_spread()

    def calculate_spread(self):
        self.error = numpy.std(self.residuals)
        return self.error

    def override_min(self, x_min, y_min):
        self.x_min = x_min
        self.y_min = y_min

    def override_max(self, x_max, y_max):
        self.x_max = x_max
        self.y_max = y_max

    def __call__(self, x):
        values = self.model(x)

        if self.x_min is not None:
            # cand: -0.24847484748474846, 0.037222357827663796
            # conf: -0.27340234023402343, -0.012958092354665158
            values = numpy.where(x < self.x_min, (1 / 0.279) * numpy.log10((10 ** x) / 1.008), values)

        if self.x_max is not None:
            # cand: -0.28082808280828087, 0.07569592990185732
            values = numpy.where(x > self.x_max, (1 / 0.881) * numpy.log10((10 ** x) / 0.00157), values)

        return values

    predict = __call__
    def predict_linear(self, linear_x):
        y = self.__call__(numpy.log10(linear_x))

        return numpy.power(10, y)

    def save(self, filepath):
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)