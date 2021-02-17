import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
import xarray as xr
import datetime


def get_open_path(title=''):
    '''
    Prompts user for path to open an NC file
    '''
    root = tk.Tk()
    root.withdraw()
    path = askopenfilename(filetypes=[('NetCDF', '.nc .nc4')], title=title)
    return path


def get_open_paths(title=''):
    '''
    Prompts user for path to open one or more NC files
    '''
    root = tk.Tk()
    root.withdraw()
    paths = askopenfilenames(filetypes=[('NetCDF', '.nc .nc4')], title=title)
    return [path for path in paths]


def get_save_path(title=''):
    '''
    Prompts user for path to save an NC file
    '''
    root = tk.Tk()
    root.withdraw()
    path = asksaveasfilename(filetypes=[('NetCDF', '*.nc')], title=title)
    if path and not path.endswith('.nc'):
        path += '.nc'
    return path


def get_folder_path(title=''):
    '''
    Prompts user for path to folder containing NC files
    '''
    root = tk.Tk()
    root.withdraw()
    path = askdirectory(title=title)
    if path:
        path += '/' # Append '/' to end of path
    return path


def get_to_netcdf_encodings(ds, comp_level=None):
    '''
    Returns default encodings for an xarray Dataset for
    use with Dataset::to_netcdf() method
    Parameters:
        ds          xarray Dataset
        comp_level  Level of compression: 0-9. If 0 no compression.
                    Compression starts with 1.
                    If None, then leave it up to xarray to decide.
    '''
    # A bit convoluted byt allows for adding new encodings in future
    # Merges two dicts of dicts based on keys in dict1
    def merge(dict1, dict2):
        for key in dict1:
            if key in dict2:
                dict1[key].update(dict2[key])
        return dict1

    # Map from Python datatype to default NetCDF _FillValue
    # See netCDF4.default_fillvals
    fillvalue_map = {
        'int8': -127, # i1
        'uint8': 255, # u1
        'int16': -32767, # i2
        'uint16': 65535, # u2
        'int32': -2147483647, # i4
        'uint32': 4294967295, # u4
        'int64': -9223372036854775806, # i8
        'uint64': 18446744073709551614, # u8
        'float32': 9.969209968386869e+36, # f4
        'float64': 9.969209968386869e+36, # f8
        'str': '\x00' # S1
    }
    # Real compression levels used for NetCDF
    real_comp_levels = [1,2,3,4,5,6,7,8,9]

    # Set up a base dict with key for all variables in ds set to empty dicts
    enc_base = {var_name:  {} for var_name in ds.variables}
    enc_fv = {} # Encodings for _FillValue
    enc_cl = {} # Encodings for compression level

    # Iterate each variable > 2 dimensions
    for var_name in ds.data_vars:
        # _FillValue encodings
        # Meant to fix when xarray makes them Python nan which
        # we don't want
        if len(ds[var_name].dims) > 2:
            # Test if _FillValue already exists. If not, add to encoding
            # using default value for data type
            if not '_FillValue' in ds[var_name].attrs:
                def_fv = fillvalue_map[ds[var_name].dtype.name]
                enc_fv[var_name] = dict(_FillValue=def_fv)
            else:
                pass
        else:
            enc_fv[var_name] = dict(_FillValue=None)

        # Compression encodings
        if len(ds[var_name].dims) > 2:
            if comp_level in real_comp_levels:
                enc_cl[var_name] = dict(zlib=True, complevel=comp_level)
            elif comp_level == 0:
                enc_cl[var_name] = dict(zlib=False)
            else:
                pass
        else:
            pass
    # Merge the dictionaries and return the merged one
    merged = merge(enc_base, enc_fv)
    merged = merge(merged, enc_cl)
    return merged


def add_to_history(ds, txt='', prepend=True):
    '''
    Adds text to `history` attribute for xarray Dataset
    '''
    hist = ''
    dt = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    if 'history' in ds.attrs:
        hist = ds.attrs['history']
        hist = hist.strip('\n')
    if prepend is True:
        hist = dt + ' ' + txt + '\n' + hist
    else:
        hist = hist + '\n' + dt + ' ' + txt
    ds.attrs['history'] = hist


def convert_calendar(ds, cal='proleptic_gregorian'):
    '''
    Sets `calendar` attribute for `time` variable for xarray Dataset
    to a specified one. Default 'proleptic_gregorian'
    '''
    if 'time' in ds.variables:
        ds.time.encoding['calendar'] = cal
