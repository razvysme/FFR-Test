import numpy as np

def generate_normal_values(mean=25, lower_bound=15, upper_bound=35, size=1000):
    
    # Calculate the required standard deviation
    sd = (upper_bound - lower_bound) / 6  # Approximation for 99.7% within bounds

    # Generate normally distributed values
    values = np.random.normal(loc=mean, scale=sd, size=size)

    # Clip values to ensure they lie within the specified range
    return np.clip(values, lower_bound, upper_bound)