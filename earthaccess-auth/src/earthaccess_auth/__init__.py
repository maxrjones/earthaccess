"""NASA Earthdata Login (EDL) authentication core, extracted from earthaccess.

Runtime dependencies are requests, tinynetrc, and typing-extensions only.
fsspec and obstore integrations live under `earthaccess_auth.adapters`
behind optional extras.
"""

import logging

from earthaccess_auth.auth import (
    Auth,
    SessionWithHeaderRedirection,
    netrc_path,
)
from earthaccess_auth.daac import DAACS
from earthaccess_auth.exceptions import (
    LoginAttemptFailure,
    LoginStrategyUnavailable,
)
from earthaccess_auth.system import PROD, UAT, System

__all__ = [
    "Auth",
    "DAACS",
    "PROD",
    "UAT",
    "LoginAttemptFailure",
    "LoginStrategyUnavailable",
    "SessionWithHeaderRedirection",
    "System",
    "login",
    "netrc_path",
]

logger = logging.getLogger(__name__)


def login(strategy: str = "all", persist: bool = False, system: System = PROD) -> Auth:
    """Authenticate with EDL and return an Auth instance.

    Mirrors `earthaccess.login`, including the `"all"` fallback chain
    (environment, then netrc, then interactive), which on main lives in
    `earthaccess.api.login` rather than on Auth. Unlike earthaccess there is
    no module-level singleton — callers hold the returned Auth themselves.
    """
    auth = Auth()

    if strategy == "all":
        for strategy_name in ["environment", "netrc", "interactive"]:
            try:
                auth.login(strategy=strategy_name, persist=persist, system=system)
            except LoginStrategyUnavailable as err:
                logger.debug(err)
                continue

            if auth.authenticated:
                break
    else:
        auth.login(strategy=strategy, persist=persist, system=system)

    return auth
