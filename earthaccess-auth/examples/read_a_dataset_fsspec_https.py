# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "earthaccess-auth[fsspec]",
#     "xarray",
#     "h5netcdf",
# ]
#
# [tool.uv.sources]
# # TODO: switch to a released earthaccess-auth once this branch merges
# earthaccess-auth = { git = "https://github.com/maxrjones/earthaccess", subdirectory = "earthaccess-auth", branch = "poc/earthaccess-auth" }
# ///
"""Read an on-prem (non-S3) granule into xarray over HTTPS via fsspec.

For when you're already using fsspec elsewhere: no obspec-utils, no
obstore, just the [fsspec] extra. Use this when the data isn't in NASA's
Earthdata Cloud, or when running outside us-west-2 and cross-region S3
egress isn't worth paying for.
"""

import xarray as xr

import earthaccess_auth
from earthaccess_auth.adapters.fsspec import get_fsspec_https_session

auth = earthaccess_auth.login()
fs = get_fsspec_https_session(auth)

url = "https://data.ornldaac.earthdata.nasa.gov/protected/daymet/Daymet_Daily_V4R1/data/daymet_v4_daily_pr_dayl_1950.nc"
ds = xr.open_dataset(fs.open(url), engine="h5netcdf")
print(ds)
