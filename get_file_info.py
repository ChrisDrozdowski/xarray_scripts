# Usage
# =====
# Script dumps info for a NetCDF file.
# Instructions:
#   1. Run this script.
#   2. You will be prompted for an input file.
#   3. Information about the file is dumped to stdout.

import xarray as xr
import utils


# Select input file
file_in = utils.get_open_path('Select input file')
if not file_in:
    raise Exception('Input file selection aborted')


# Set xarray to keep attributes for DataArrays and Datasets
xr.set_options(keep_attrs=True)

# Open file into a Dataset
ds = xr.open_dataset(file_in, engine='netcdf4', mask_and_scale=False)

# Dump info about file
print(ds.time.data)

# Close Dataset file
ds.close()
