import pytest

from earthaccess_auth import Auth

obstore = pytest.importorskip("obstore")


def _authed() -> Auth:
    auth = Auth()
    auth.token = {"access_token": "test-token-abc"}
    auth.authenticated = True
    return auth


def test_s3_credential_provider_construction():
    from obstore.auth.earthdata import (  # noqa: PLC0415
        NasaEarthdataCredentialProvider,
    )

    from earthaccess_auth.adapters.obstore import (  # noqa: PLC0415
        s3_credential_provider,
    )

    provider = s3_credential_provider(
        _authed(), "https://data.nsidc.earthdatacloud.nasa.gov/s3credentials"
    )
    assert isinstance(provider, NasaEarthdataCredentialProvider)
    # __init__ only stores config; it performs no network I/O (that happens
    # lazily in __call__), so it is safe to assert the wiring directly.
    assert provider._auth == "test-token-abc"
    assert (
        provider._credentials_url
        == "https://data.nsidc.earthdatacloud.nasa.gov/s3credentials"
    )


def test_http_client_options_accepted_by_obstore():
    from earthaccess_auth.adapters.obstore import (  # noqa: PLC0415
        http_client_options,
    )

    options = http_client_options(_authed())
    assert options == {"default_headers": {"authorization": "Bearer test-token-abc"}}
    # Constructing a store with these options proves the key is real; no
    # network I/O happens at construction time.
    store = obstore.store.HTTPStore.from_url(
        "https://example.com", client_options=options
    )
    assert store is not None
