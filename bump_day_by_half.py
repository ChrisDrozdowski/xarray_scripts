# Usage
# =====
# Script bumps up the `time` variable in a NetCDF file
# by half a day.
# Instructions:
#   1. Run this script.
#   2. You will be prompted for an input file.
#   3. You will then be prompted for an output file.
#       You CANNOT overwrite the input file. I chose this
#       because processing time and memory is much greater.

import xarray as xr
import utils


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
ds = xr.open_dataset(file_in, engine='netcdf4', mask_and_scale=False, decode_times=False)

# If there is a `time` variable, bump up the raw
# values by 0.5.
if 'time' in ds.variables:
    ds['time'] = ds['time'] + 0.5

# Get default encodings for use with Dataset::to_netcdf() method
encodings = utils.get_to_netcdf_encodings(ds=ds, comp_level=4)

# Save Dataset to file with encodings
ds.to_netcdf(path=file_out, engine='netcdf4', encoding=encodings)

# Close Dataset file
ds.close()

print('Done!!!')
