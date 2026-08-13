"""obstore integration (extra: earthaccess-auth[obstore]).

obstore already ships EDL-to-S3 credential exchange in
`obstore.auth.earthdata`; this module bridges to it rather than duplicating
it, and adds the HTTP-headers case obstore's provider does not cover.
"""

from typing import Any

# Re-exported so consumers have one import root for EDL auth. Long term the
# implementation could migrate here and obstore could depend on this package
# instead (open question in the README).
from obstore.auth.earthdata import (  # noqa: F401
    NasaEarthdataAsyncCredentialProvider,
    NasaEarthdataCredentialProvider,
)

from earthaccess_auth.auth import Auth


def s3_credential_provider(
    auth: Auth,
    credentials_endpoint: str,
) -> NasaEarthdataCredentialProvider:
    """Build obstore's EDL S3 credential provider from an authenticated Auth.

    Feeds the Auth token to the provider so consumers do not configure EDL
    twice; the endpoint comes from the DAAC registry (see daac.py).
    """
    return NasaEarthdataCredentialProvider(
        credentials_endpoint,
        token=auth.token["access_token"],
    )


def http_client_options(auth: Auth) -> dict[str, Any]:
    """Default-header client options for HTTPS stores fronting EDL-protected data.

    Usable for obstore HTTP stores and any store config that accepts plain
    headers — e.g. icechunk's `http_store(headers=...)` for virtual chunk
    containers (the titiler-multidim case).

    SKETCH NOTE: verify the exact obstore client-option key for default
    headers against the obstore version targeted.
    """
    return {"default_headers": {"authorization": f"Bearer {auth.token['access_token']}"}}
