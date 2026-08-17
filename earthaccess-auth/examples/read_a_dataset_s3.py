# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "earthaccess-auth[obstore]",
#     "obspec-utils",
#     "xarray",
#     "h5netcdf",
# ]
#
# [tool.uv.sources]
# # TODO: switch to a released earthaccess-auth once this branch merges
# earthaccess-auth = { git = "https://github.com/maxrjones/earthaccess", subdirectory = "earthaccess-auth", branch = "claude/earthaccess-auth-poc" }
# ///
"""Read an S3-hosted granule into xarray via obstore + obspec-utils.

Fastest path for data in NASA's Earthdata Cloud, when running inside AWS
us-west-2 (same-region S3 reads avoid cross-region egress).
"""

import xarray as xr
from obspec_utils.readers import EagerStoreReader
from obstore.store import S3Store

import earthaccess_auth
from earthaccess_auth.adapters.obstore import s3_credential_provider

auth = earthaccess_auth.login()

credential_provider = s3_credential_provider(
    auth,
    credentials_endpoint="https://data.nsidc.earthdatacloud.nasa.gov/s3credentials",
)
store = S3Store(
    "nsidc-cumulus-prod-protected",
    region="us-west-2",
    credential_provider=credential_provider,
)

path = "ATLAS/ATL03/006/2020/01/01/ATL03_20200101T000106_00650601_006_01.h5"
reader = EagerStoreReader(store, path)
ds = xr.open_dataset(reader, engine="h5netcdf")
print(ds)
