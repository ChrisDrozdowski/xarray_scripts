# Usage
# =====
# Script adds a missing `time` dimension to data variables in EarthData
# NetCDF file(s) based on date component embedded in file name.
# Instructions:
#   1. Put all *.NC files you want to process into an input folder.
#   2. Run this script.
#   3. You will be prompted for an input folder.
#   4. You will then be prompted for an output folder.
#       Do NOT choose the input folder.
#
# Note: FILE NAMES MUST HAVE A PARSABLE DATE COMPONENT or they are skipped
# with a printed notification.
#
# Note: The date parsing algorithm is based on examining various file
#   names and may be a bit fragile.

import xarray as xr
import utils
import glob
import os
import pandas as pd
import re
import warnings


def dt_from_filename(fname):
    '''
    Extract date from file name and return PAndas DateTime
    if valid, or None if invalid
    
    Example file names:
    Daily: T2021014.L3m_DAY_CHL.x_chlor_a.nc (yyyydoy * 1
    Monthly: C19800011980031.L3m_MO_CHL.x_chlor_a.nc (yyyydoy * 2)
    Seasonal: A20163562017079.L3m_SNWI_CHL.x_chlor_a.nc (yyyydoy * 2)
    Yearly: AQUA_MODIS.20150101_20151231.L3m.YR.SST.x_sst.nc (yyyymmdd * 2)
    '''
    try:
        # Order matters below
        date = None
        if date is None:
            # 2 matches of 8 numbers is yearly (yyyymmdd * 2)
            matches = re.findall(r'\d{8}', fname)
            if matches and len(matches) == 2:
                date = pd.to_datetime(matches[0], format='%Y%m%d')
        if date is None:
            # 2 matches of 7 numbers is monthly or seasonal (yyyydoy * 2)
            matches = re.findall(r'\d{7}', fname)
            if matches and len(matches) == 2:
                date = pd.to_datetime(matches[0], format='%Y%j')
        if date is None:
            # 1 match of 7 numbers is daily  (yyyydoy * 1)
            matches = re.findall(r'\d{7}', fname)
            if matches and len(matches) == 1:
                date = pd.to_datetime(matches[0], format='%Y%j')
        return date
    except:
        return None


# Main function to run
def main_func():
    # Select input folder
    fldr_in = utils.get_folder_path('Select input folder')
    if not fldr_in:
        raise Exception('Input folder selection aborted')
    fldr_in += r'*.nc'

    # Select output folder
    fldr_out = utils.get_folder_path('Select output folder')
    if not fldr_out:
        raise Exception('Output folder selection aborted')


    # Set xarray to keep attributes for DataArrays and Datasets
    xr.set_options(keep_attrs=True)

    # Iterate all *.NC files in input folder
    files = glob.glob(fldr_in)
    for path in files:
        # Get only file name, no folder
        file = os.path.basename(path)

        # Extract date from file name into a Pandas DateTime
        # Skip with printout if not parsable date component
        pdt = dt_from_filename(file)
        if pdt is None:
            print(f'File: {file} is missing date component in file name. Skipped')
            continue

        # Open full path file into a Dataset
        ds = xr.open_dataset(path, engine='netcdf4', mask_and_scale=False)

        # Add a time dimension/variable based on extracted DateTime
        # and convert DataArray to Dataset
        ds = ds.expand_dims({'time': [pdt]})

        # Add some attributes to time variable
        ds.time.attrs['long_name'] = 'time'
        ds.time.attrs['standard_name'] = 'time'
        ds.time.attrs['axis'] = 'T'
        ds.time.attrs['Descript'] = 'Time'

        # About time units:
        # You'll see the time units will be `days since ...`
        # This is correct because CF Conventions have special meanings
        # for `months since...` and `years since ...`
        # Time units are automatically generated

        # Convert calendar to standard one
        utils.convert_calendar(ds)

        # Add to file history
        utils.add_to_history(ds=ds, txt='Drozdowski: add time dimension based on file name', prepend=True)
        utils.add_to_history(ds=ds, txt='Drozdowski: set calendar to standard', prepend=True)

        # Get defult encodings for use with Dataset::to_netcdf() method
        encodings = utils.get_to_netcdf_encodings(ds=ds, comp_level=4)

        # Assign file name same as current input file but in output folder.
        file_out = fldr_out + file

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