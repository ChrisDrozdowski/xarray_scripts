# Usage
# =====
# Script converts the calendar for a NetCDF file into the NetCDF
# standard calendar (`proleptic_gregorian`).
# Instructions:
#   1. Run this script.
#   2. You will be prompted for an input file.
#   3. You will then be prompted for an output file.
#       You CANNOT overwrite the input file. I chose this
#       because processing time and memory is much greater.

import xarray as xr
import utils
import warnings


# Main function to run
def main_func():
    # Select input file
    file_in = utils.get_open_path('Select input file')
    if not file_in:
        raise Exception('Input file selection aborted')

    # Select output file
    file_out = utils.get_save_path('Select output file')
    if not file_out:
        raise Exception('Output file selection aborted')


    # Set xarray to keep attributes for DataArrays and Datasets
    xr.set_options(keep_attrs=True)

    # Open file into a Dataset
    ds = xr.open_dataset(file_in, engine='netcdf4', mask_and_scale=False)

    # Convert calendar to standard one
    utils.convert_calendar(ds)

    # Add to file history
    utils.add_to_history(ds=ds, txt='Drozdowski: set calendar to standard', prepend=True)

    # No encodings because they interfere with calendar setting
    encodings = {}

    # Save Dataset to file with encodings
    ds.to_netcdf(path=file_out, engine='netcdf4', encoding=encodings)

    # Close Dataset file
    ds.close()

    print('Done!!!')


# Must run script this way to avoid potential RunTime warnings
# if Dask is involved.
# We'll simply ignore the warnings.
if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        main_func()