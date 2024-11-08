import numpy as np

class CalibrationManager:
    def __init__(self):
        # Calibration matrices
        self.norm_C1_inv = np.array([[34685, -6.0667, -34.774],
                                    [804.64, 21210, 225.29],
                                    [-1387.3, 73.623, 38938]])
        
        self.norm_C1_inv_C2 = np.array([[0.00090131, 0.00071979, -0.00059586],
                                       [-0.0085693, -0.00072414, -0.00050641],
                                       [-0.00079632, 0.028777, -9.6631e-06]])

        self.side_C_inv = np.array([[-34668, 49.226, 41.308],
                                   [-837.96, 21224, -15.823],
                                   [1395.9, -399.31, -38930]])
        
        self.side_C1_inv_C2 = np.array([[-0.0016532, 0.00094694, 0.00058309],
                                       [-0.0025937, 0.00027556, -0.0010782],
                                       [0.0014352, -0.001701, 2.3735e-05]])
        
        self.current_calibration = 'Normal'

    def calibrate_forces(self, voltage_matrix):
        """Apply calibration based on the current configuration."""
        R = voltage_matrix.reshape((3, 1))
        
        if self.current_calibration == 'Normal':
            term1 = np.dot(self.norm_C1_inv, R)
            C1_inv_abs = np.abs(self.norm_C1_inv)
            magnitude_term = np.dot(C1_inv_abs, R)
            term2 = np.dot(self.norm_C1_inv_C2, magnitude_term)
        else:  # Side configuration
            term1 = np.dot(self.side_C_inv, R)
            C1_inv_abs = np.abs(self.side_C_inv)
            magnitude_term = np.dot(C1_inv_abs, R)
            term2 = np.dot(self.side_C1_inv_C2, magnitude_term)

        return term1 - term2

    def set_configuration(self, config):
        """Change calibration configuration."""
        self.current_calibration = config