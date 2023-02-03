import numpy as np
from sklearn.linear_model import LinearRegression

class NonLinearReg():
    def __init__(self):
        self.order = 2
        self.mod = LinearRegression()

    def fit(self, X, y):
        X = np.vstack([X, X**2], axis=0)
        self.mod.fit(X,y)
        return self

    def predict(self, X):
        return self.mod.predict(X)

    def score(self, x, y):
        return self.mod.score(x, y)