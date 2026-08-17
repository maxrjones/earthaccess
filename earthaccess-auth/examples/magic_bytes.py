# /// script
# requires-python = ">=3.11"
# dependencies = ["earthaccess-auth[obstore]"]
#
# [tool.uv.sources]
# # TODO: switch to a released earthaccess-auth once this branch merges
# earthaccess-auth = { git = "https://github.com/maxrjones/earthaccess", subdirectory = "earthaccess-auth", branch = "claude/earthaccess-auth-poc" }
# ///
"""Identify a granule's format from its magic bytes, without downloading it.

A byte-range request pulls just the first few bytes, cheap even for a
multi-gigabyte file.
"""

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
header = bytes(store.get_range(path, start=0, end=8))

if header == b"\x89HDF\r\n\x1a\n":
    print("HDF5 (or NetCDF-4)")
elif header[:3] == b"CDF":
    print(f"NetCDF classic, version {header[3]}")
else:
    print(f"unrecognized: {header!r}")
