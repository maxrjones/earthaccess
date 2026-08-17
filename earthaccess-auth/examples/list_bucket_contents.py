# /// script
# requires-python = ">=3.11"
# dependencies = ["earthaccess-auth[obstore]"]
#
# [tool.uv.sources]
# # TODO: switch to a released earthaccess-auth once this branch merges
# earthaccess-auth = { git = "https://github.com/maxrjones/earthaccess", subdirectory = "earthaccess-auth", branch = "claude/earthaccess-auth-poc" }
# ///
"""List the contents of an S3 bucket prefix.

Useful for exploring what a DAAC's cloud bucket actually contains before
building a granule URL by hand, or for a quick sanity check that S3
credentials work at all.
"""

import obstore
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

for obj in obstore.list(store, prefix="ATLAS/ATL03/006/2020/01/01"):
    print(obj["path"], obj["size"])
