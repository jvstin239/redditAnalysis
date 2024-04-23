import numpy as np

class Analyzer():
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.arr = np.array(raw_data)

    def get_arr(self):
        return self.arr