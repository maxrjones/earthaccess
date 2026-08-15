"""EDL authentication. The implementation lives in the earthaccess-auth distribution."""

from earthaccess_auth.auth import (
    Auth,
    BasicAuthResponseHook,
    SessionWithHeaderRedirection,
    netrc_path,
)

__all__ = [
    "Auth",
    "BasicAuthResponseHook",
    "SessionWithHeaderRedirection",
    "netrc_path",
]
