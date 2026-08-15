# earthaccess-auth (proof of concept)

A minimal-dependency distribution containing only the NASA Earthdata Login (EDL) authentication core of earthaccess: login strategies, token lifecycle, per-DAAC S3 credential exchange, and the redirect-safe requests session. Integrations with fsspec and obstore are optional extras, so auth-only consumers install none of the search/download stack.

## Motivation

Several downstream services need EDL auth and nothing else from earthaccess. Two concrete examples from the titiler ecosystem:

- titiler-multidim needs a bearer token string to inject into icechunk virtual chunk container headers. It deploys as an AWS Lambda zip, where earthaccess's transitive dependencies (s3fs, fsspec, python-cmr, pqdm, tenacity, ...) count against the 250 MB unpacked limit for the sake of ~500 lines of auth logic.
- titiler-cmr uses `earthaccess.login()` plus `get_fsspec_https_session()` and `get_s3_credentials()`; it uses CMR search too, so it keeps full earthaccess, but its auth usage is exactly the surface extracted here.

obstore has independently grown `obstore.auth.earthdata` (EDL to temporary S3 credential exchange, sync and async, with refresh). Without a shared auth core, EDL logic now lives in at least two places and drifts. This package is the proposed single home; the obstore extra bridges to (not duplicates) obstore's provider.

## What moved, what stayed

Moved into `earthaccess_auth` essentially verbatim (~630 lines total, runtime deps only `requests`, `tinynetrc`, and `typing_extensions`):

| Source (earthaccess) | Destination (earthaccess_auth) | Delta from main |
| --- | --- | --- |
| `auth.py` (`netrc_path`, `BasicAuthResponseHook`, `SessionWithHeaderRedirection`, `Auth`) | `auth.py` | imports retargeted; User-Agent reports the earthaccess-auth version |
| `daac.py` (DAAC registry, `find_provider`, ...) | `daac.py` | none |
| `system.py` (`PROD`, `UAT`, `System`) | `system.py` | CMR base URLs inlined as literals — main takes them from python-cmr, which must not become a dependency here |
| `exceptions.py` (`LoginStrategyUnavailable`, `LoginAttemptFailure` only) | `exceptions.py` | the download-stack exceptions stay in earthaccess |

`earthaccess_auth.login()` additionally absorbs the `"all"` fallback chain (environment, netrc, interactive), which on main lives in `earthaccess.api.login` rather than on `Auth` — without the module-level singleton earthaccess maintains.

New, thin, behind extras:

- `earthaccess_auth.adapters.fsspec` — `get_fsspec_https_session(auth)`, the bearer-token `HTTPFileSystem` currently built in `earthaccess/store.py` (including the `trust_env: False` requirement).
- `earthaccess_auth.adapters.obstore` — re-exports `obstore.auth.earthdata.NasaEarthdataCredentialProvider` for S3 direct access, and adds `http_client_options(auth)` returning default headers for obstore HTTP stores (and any other consumer that just needs headers, e.g. icechunk `http_store`).

Stayed in earthaccess: everything else. `earthaccess/auth.py`, `system.py`, and `daac.py` are now re-export shims, `earthaccess/exceptions.py` re-exports the two login exceptions, and earthaccess depends on `earthaccess-auth`, so no import path broke and there is exactly one implementation. The earthaccess-side plan — shims, dependency edits, test split, and the two-distribution publish workflow — is in [MIGRATION.md](MIGRATION.md).

## Install matrix

```
pip install earthaccess-auth            # requests + tinynetrc + typing_extensions only
pip install earthaccess-auth[fsspec]    # + fsspec/aiohttp HTTPS session
pip install earthaccess-auth[obstore]   # + obstore credential provider bridge
pip install earthaccess                 # unchanged UX; depends on earthaccess-auth
```

## Example: the titiler-multidim case

```python
import earthaccess_auth

auth = earthaccess_auth.login(strategy="environment")
token = auth.token["access_token"]  # inject into icechunk http_store headers
```

## Repo mechanics

Sketched as a second distribution in the earthaccess repo (`earthaccess-auth/` with its own `pyproject.toml`, src layout), released in lockstep with earthaccess. Alternatives: a separate repo (looser coupling, more release ceremony) or a single distribution with heavy deps demoted to extras (`earthaccess[full]`) — simpler packaging but a breaking install-time change for every existing user, since bare `earthaccess` would lose search/download.

## Open questions

- Governance: does the earthaccess team want to own a second distribution, and does the import name `earthaccess_auth` vs a namespace package matter to them?
- Does obstore want to depend on this core someday (replacing its `_refresh_with_basic_auth` path), or remain standalone with this package only bridging to it?
- Python floor: earthaccess requires >=3.12; a standalone auth core may want a lower floor for broader reuse.
- Should the token surface be formalized (e.g. a `bearer_token() -> str` method with expiry metadata) instead of exposing the raw `token` dict?
- Should the deprecated no-op `Auth.refresh_tokens` carry over at all? A brand-new package could omit it (dropping the typing_extensions dependency) and let the earthaccess shim keep the deprecated method for its own back-compat.
- User-Agent on EDL requests: reporting `earthaccess-auth v{x}` loses the `earthaccess v{x}` string server-side metrics may key on — see MIGRATION.md.
