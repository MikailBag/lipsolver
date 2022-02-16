import numpy as np

def grid_search(f, a, b, s):
    """
    Searches for a minimum on a uniform grid
    Args:
        f: objective function
        a: left interval end
        b: right interval end
        s: step size
    Returns:
        found minimum as a tuple (x*, f(x*))
    """
    points = np.arange(a, b, s)
    xr = np.nan
    fr = np.nan
    for x in points:
        fn = f(x)
        if np.isnan(fr) or fn < fr:
            xr = x
            fr = fn
    return xr, fr