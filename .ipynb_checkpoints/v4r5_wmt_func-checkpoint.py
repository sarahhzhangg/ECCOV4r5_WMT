import numpy as np
from datetime import datetime, timedelta
from scipy import ndimage
import ecco_v4_py as ecco

grid_size = 1

grid_fp = '/home/dmenemen/eady-data1/grid/ECCO_V4r5/'
ecco_XC = ecco.read_llc_to_tiles(grid_fp, 'XC.data', less_output=True)
ecco_YC = ecco.read_llc_to_tiles(grid_fp, 'YC.data', less_output=True)

landmask_tiles = ecco.read_llc_to_tiles(grid_fp, 'hFacC.data', less_output=True)
landmask = ecco.llc_tiles_to_xda(landmask_tiles, var_type='c')
land_mask_wnans = np.where(landmask, 1, np.nan)

def iteration_to_date(iteration, base_iter=12, base_date='1992-01-01'):
    """
    Convert MITgcm iteration number to datetime.

    Parameters
    ----------
        iteration : int
            MITgcm iteration number
        base_iter : int
            The iteration corresponding to base_date (default: 12)
        base_date : str
            The date corresponding to base_iter, in 'YYYY-MM-DD' format

    Returns
    ----------
        datetime: Corresponding datetime object
    """
    # Convert base date string to datetime
    base_dt = datetime.strptime(base_date, '%Y-%m-%d')
    
    # Each iteration is 1 hour = 1/24 day
    hours_since_base = int(iteration) - base_iter
    return base_dt + timedelta(hours=hours_since_base)

def project_to_latlon_grid(lons, lats, data,
                           dx=grid_size, dy=grid_size,
                           mapping_method='nearest_neighbor',
                           radius_of_influence=112000,
                           user_lon_0=0,
                           user_lat_0=None,
                           lat_lim=50,
                           projection_type='robin',
                           less_output=True):
    """
    Edited version of ecco_v4_py.plot_proj_to_latlon_grid()
    Project data onto a regular lat/lon grid.
    Skips all plotting in ecco_v4_py.plot_proj_to_latlon_grid(); returns only the interpolated result.

    Parameters
    ----------
    lons, lats : ndarray
        Longitudes and latitudes of the data
    data : ndarray
        Data values
    dx, dy : float
        Resolution of output grid
    mapping_method : str
        'nearest_neighbor' or 'bin_average'
    radius_of_influence : float
        Max radius (in meters) to search for data to interpolate
    user_lon_0 : float
        Central longitude (used for smart date line splitting)
    projection_type : str
        Only used to infer whether it's polar stereographic or not

    Returns
    -------
    new_grid_lon_centers : ndarray
    new_grid_lat_centers : ndarray
    data_latlon_projection : ndarray
    """

    if projection_type == 'stereo' and user_lat_0 is None:
        user_lat_0 = 90 if lat_lim > 0 else -90

    ep = 1e-5  # small epsilon to avoid edge plotting issues
    lon_tmp_d = []

    if abs(user_lon_0) == 180:
        lon_tmp_d.append([ep, 180])
        lon_tmp_d.append([-180, -ep])
    elif user_lon_0 < 0:
        lon_tmp_d.append([-180, 180 + user_lon_0])
        lon_tmp_d.append([180 + user_lon_0 + ep, 180])
    elif user_lon_0 > 0:
        lon_tmp_d.append([-180 + user_lon_0, 180])
        lon_tmp_d.append([-180, -180 + user_lon_0 - ep])
    elif user_lon_0 == 0:
        lon_tmp_d.append([-180, 180])

    for ki, lon_limits in enumerate(lon_tmp_d):
        new_grid_lon_centers, new_grid_lat_centers, \
        new_grid_lon_edges, new_grid_lat_edges, \
        data_latlon_projection = ecco.resample_to_latlon(
            lons, lats, data,
            -90, 90, dy,
            lon_limits[0], lon_limits[1], dx,
            mapping_method=mapping_method,
            radius_of_influence=radius_of_influence
        )

        if ki == 0:
            new_grid_lon_centers_out = new_grid_lon_centers
            new_grid_lat_centers_out = new_grid_lat_centers
            data_latlon_projection_out = data_latlon_projection
        else:
            new_grid_lon_centers_out = np.append(new_grid_lon_centers_out, new_grid_lon_centers, axis=1)
            new_grid_lat_centers_out = np.append(new_grid_lat_centers_out, new_grid_lat_centers, axis=1)
            data_latlon_projection_out = np.append(data_latlon_projection_out, data_latlon_projection, axis=1)

    return new_grid_lon_centers_out, new_grid_lat_centers_out, data_latlon_projection_out

def load_reproject_values(varname, hr, 
                          grid_size=grid_size, 
                          v4r5_fp='/export/data1/szhang6/ECCO2/LLC90/v4r5_monthly/'):
    """
    Reads the binary ECCO data file for a given variable and time step, 
    applies land mask, and reprojects the tiled LLC90 data onto a 
    latitude/longitude grid.

    Parameters
    ----------
    varname : str
        Name of the ECCO variable to load (used to construct the filename).
    hr : int
        Time step (hour) identifier used to construct the date string in the
        filename. Will be zero-padded to 10 digits.

    Returns
    -------
    proj_vals : ndarray
        Array of variable values reprojected onto the lat/lon grid defined
        by `ecco_XC`, `ecco_YC`, and `grid_size`.
    """
    date_str = str(hr).zfill(10)
    fn = f'{varname}.{date_str}.data'
    
    tiles = ecco.read_llc_to_tiles(v4r5_fp, fn, less_output=True)
    tiles = tiles * land_mask_wnans
    proj_lons, proj_lats, proj_vals = project_to_latlon_grid(ecco_XC, ecco_YC, tiles, dx=grid_size, dy=grid_size)
    return proj_vals

def calculate_transformation_rate(rho, area, mask, rholevs, *args):
    """Equation 5 in Newsom et al. 2021"""
    return np.array(sum_inside_contours(rho,area,mask,rholevs,args))[:,1:]/ np.diff(rholevs) 

def sum_inside_contours(index_field, area, mask, index_levels, fields):
    """Calculates the integral in Equation 5"""
    di = np.diff(index_levels)
    sign = np.sign(di[0])
    assert np.all(np.sign(di)==sign)
    shape = index_field.shape
    labels = np.digitize(index_field.ravel(), index_levels, right=(sign==1))
    labels.shape = shape
    res = []
     
    if isinstance(fields, np.ndarray):
        fields = [fields,]
    for field in fields:
        assert field.shape == shape
        res.append( ndimage.sum(field,labels=labels, index=np.arange(len(index_levels))))
    if len(res)==1:
        return res[0]
    else:
        return res