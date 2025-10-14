# app/utils.py
# Helper utility functions for the application
import numpy as np

def convert_numpy_to_python(data):
    """
    Recursively converts NumPy types in a dictionary or list to native Python types
    to ensure JSON serializability.
    """
    if isinstance(data, dict):
        return {key: convert_numpy_to_python(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_python(element) for element in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.generic):
        # Catches numpy types like np.int64, np.float64, etc.
        return data.item()
    else:
        return data