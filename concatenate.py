# Usage
# =====
# Script concatenates multiple NetCDF files into one file.
# Instructions:
#   1. Put all *.NC files you want to process into an input folder.
#   2. Run this script.
#   3. You will be prompted for an input folder.
#   4. You will then be prompted for an output file.
#       Do NOT choose the input folder.
#
# Note: If large number of files, it may take quite some time to run.
#
# Note: All files to concatenate must have the same structure and
#   and variable dimensions. Also, all files must have a dimension
#   such as `time` in order for the concatenation to work.

import xarray as xr
import utils
import warnings


# Main function to run
def main_func():
    # Select input folder
    fldr_in = utils.get_folder_path('Select input folder')
    if not fldr_in:
        raise Exception('Input folder selection aborted')
    fldr_in += r'*.nc'

    # Select output file
    file_out = utils.get_save_path('Select output file')
    if not file_out:
        raise Exception('Output file selection aborted')


    # Set xarray to keep attributes for DataArrays and Datasets
    xr.set_options(keep_attrs=True)

    # This concatenates the files into a Dataset
    ds = xr.open_mfdataset(fldr_in, engine='netcdf4', mask_and_scale=False)

    # Convert calendar to standard one
    utils.convert_calendar(ds)

    # Add to file history
    utils.add_to_history(ds=ds, txt='Drozdowski concatenation of multiple files', prepend=True)
    utils.add_to_history(ds=ds, txt='Drozdowski: set calendar to standard', prepend=True)

    # Get default encodings for use with Dataset::to_netcdf() method
    encodings = utils.get_to_netcdf_encodings(ds=ds, comp_level=4)

    # Save Dataset to file with encodings
    ds.to_netcdf(path=file_out, engine='netcdf4', encoding=encodings)

    # No need to close files!

    print('Done!!!')


# Must run script this way to avoid potential RunTime warnings
# if Dask is involved.
# We'll simply ignore the warnings.
if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        main_func()