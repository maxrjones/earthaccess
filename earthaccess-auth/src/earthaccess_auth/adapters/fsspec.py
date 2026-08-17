"""Authenticated fsspec HTTPS filesystem (extra: earthaccess-auth[fsspec]).

This is `earthaccess.store.Store.get_fsspec_session` relocated so
fsspec consumers (e.g. titiler-cmr's external-access path) need no other
part of earthaccess.
"""

import fsspec

from earthaccess_auth.auth import Auth


def get_fsspec_https_session(auth: Auth) -> fsspec.AbstractFileSystem:
    """Return an HTTPFileSystem sending the EDL bearer token on every request.

    trust_env must stay False: if aiohttp also picks up ambient auth from the
    environment while a bearer token is present, EDL rejects the request.

    Raises:
        ValueError: If `auth` has not been authenticated (`auth.token is None`).
    """
    if auth.token is None:
        msg = "auth must be authenticated before use"
        raise ValueError(msg)
    token = auth.token["access_token"]
    client_kwargs = {
        "headers": {"Authorization": f"Bearer {token}"},
        "trust_env": False,
    }
    return fsspec.filesystem("https", client_kwargs=client_kwargs)
