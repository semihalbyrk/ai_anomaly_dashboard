# ---------------- utils_geo.py ----------------
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    """
    Return great-circle distance between (lat1,lon1) and arrays of (lat2,lon2)
    in **kilometres**.
    """
    R = 6371.0
    lat1, lon1 = np.radians(lat1), np.radians(lon1)
    lat2, lon2 = np.radians(lat2), np.radians(lon2)
    dlat  = lat2 - lat1
    dlon  = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))
