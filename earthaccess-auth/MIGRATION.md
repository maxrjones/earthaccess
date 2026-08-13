# earthaccess-side changes (sketch)

What changes inside the existing `earthaccess` package when `earthaccess_auth` becomes the single implementation. None of these edits are made in this sketch; this file is the plan for that PR.

## Shim modules

Each extracted module becomes a re-export, so every existing import path keeps working:

```python
# earthaccess/auth.py
from earthaccess_auth.auth import (  # noqa: F401
    Auth,
    BasicAuthResponseHook,
    SessionWithHeaderRedirection,
    netrc_path,
)

# earthaccess/system.py
from earthaccess_auth.system import (  # noqa: F401
    PROD,
    UAT,
    CMRBaseURL,
    EDLHostname,
    StatusApiURL,
    StatusURL,
    System,
)

# earthaccess/daac.py
from earthaccess_auth.daac import *  # noqa: F403
```

`earthaccess/exceptions.py` keeps its download-stack exceptions (`DownloadFailure`, `ServiceOutage`, `EulaNotAccepted`) as real code and re-exports `LoginStrategyUnavailable` and `LoginAttemptFailure` from `earthaccess_auth.exceptions`, so `except earthaccess.exceptions.LoginAttemptFailure` still catches what the core raises — they are the same class objects.

## Behavior notes for the shim PR

- `earthaccess.api.login` keeps its module-level singleton and `Store` wiring; only the `Auth` class it drives moves. Its `"all"` fallback loop stays (duplicated in `earthaccess_auth.login`, which has no singleton) — 15 lines of orchestration in two places is the accepted cost of the singleton staying out of the core.
- `earthaccess/system.py` on main takes CMR URLs from python-cmr (`CMR_OPS`/`CMR_UAT`); the core inlines those values as literals. The shim re-export therefore drops earthaccess's use of python-cmr *for System construction only* — python-cmr remains a full earthaccess dependency for search. If python-cmr ever changes those constants, the literals in `earthaccess_auth/system.py` must follow.
- The `User-Agent` header on EDL requests becomes `earthaccess-auth v{version}`. If keeping `earthaccess v{version}` in it matters for server-side metrics, `Auth` needs a user-agent parameter the earthaccess shim can set — decide during the PR.
- `earthaccess.__init__` re-exports `Auth` from `.auth`, which resolves through the shim unchanged.

## pyproject changes in earthaccess

- Add `earthaccess-auth` to `dependencies` (same-repo releases pin exact: `earthaccess-auth == {version}`, enforced by lockstep releases below).
- Remove `tinynetrc` from earthaccess's direct dependencies (only `auth.py` used it); `requests` stays (used by search/store directly).

## Tests

- `tests/unit/test_auth.py` moves to `earthaccess-auth/tests/test_auth.py` (import edits only; see that file).
- earthaccess keeps a minimal replacement `tests/unit/test_auth.py` asserting the shim: `from earthaccess import Auth; from earthaccess.exceptions import LoginAttemptFailure` resolve and are identical to the `earthaccess_auth` objects.
- Integration tests (`tests/integration/`) exercise auth through `earthaccess.login` and stay put.

## CI and release

- `test.yml` / `test-mindeps.yml`: add a job (or matrix dimension) running `earthaccess-auth`'s tests against its own minimal environment — this is the check that the core imports and passes tests *without* fsspec/obstore/python-cmr installed.
- `publish.yml`: build and publish both distributions from the same tag. `earthaccess-auth/pyproject.toml` already reads the version from the repo root via hatch-vcs (`raw-options = { root = ".." }`), so one tag versions both; the publish job gains a second `python -m build earthaccess-auth/` + upload step (separate PyPI project, own trusted-publisher config).
- Lockstep means every earthaccess release republishes earthaccess-auth even when auth didn't change; accepted for simplicity (the alternative — independent versioning in one repo — reintroduces the compatibility-matrix problem this extraction avoids).
