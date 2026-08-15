"""Earthdata Environments/Systems module. Implementation lives in earthaccess-auth."""

from earthaccess_auth.system import (
    PROD,
    UAT,
    CMRBaseURL,
    EDLHostname,
    StatusApiURL,
    StatusURL,
    System,
)

__all__ = [
    "PROD",
    "UAT",
    "CMRBaseURL",
    "EDLHostname",
    "StatusApiURL",
    "StatusURL",
    "System",
]
