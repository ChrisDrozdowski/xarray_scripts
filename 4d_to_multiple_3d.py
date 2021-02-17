# Usage
# =====
# Script looks for 4D variables in a NetCDF file and "explodes" them into
# individual 3D variables based on 2nd dimension (`lev`, `depth`, etc)
# Instructions:
#   1. Run this script.
#   2. You will be prompted for an input file.
#   3. You will then be prompted for an output file.
#       You CANNOT overwrite the input file. I chose this
#       because processing time and memory is much greater.

import xarray as xr
import utils
import warnings


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

    # Iterate each variable, looking for those with 4 dimensions
    for var_name in ds.data_vars:
        da = ds[var_name]
        dims = da.dims
        if len(dims) != 4:
            continue
        # Rearrange data so that 2nd dimension becomes 1st dimension
        da = da.transpose(dims[1], dims[0], dims[2], dims[3])
        n = 0
        # Get dimension data for 2nd dimension
        dims_data = da[dims[1]].data
        # Iterate each sub-DataArray in rearranged data
        for da_sub in da:
            # Assemble a name for the sub-DataArray
            name = da_sub.name + '_' + dims[1] + '_' + str(dims_data[n])
            # Assign sub-DataArray to a new variable in Dataset
            ds[name] = da_sub
            n += 1

    # Convert calendar to standard one
    utils.convert_calendar(ds)

    # Add to file history
    utils.add_to_history(ds=ds, txt='Drozdowski: explode 4D variables into multiple 3D variables', prepend=True)
    utils.add_to_history(ds=ds, txt='Drozdowski: set calendar to standard', prepend=True)

    # Get default encodings for use with Dataset::to_netcdf() method
    encodings = utils.get_to_netcdf_encodings(ds=ds, comp_level=4)

    # Save file with above encoding
    ds.to_netcdf(path=file_out, encoding=encodings)

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