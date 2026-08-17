# Read a dataset with xarray

Every NASA Earthdata granule is served from one of two places: a plain
HTTPS URL (on-prem DAAC archives), or an S3 bucket in `us-west-2` (NASA
Earthdata Cloud, for clients running in that same region). Once you're
authenticated, `earthaccess-auth` gets you a credential provider or a
headers dict for either, and
[obspec-utils](https://github.com/developmentseed/obspec-utils)'s
`EagerStoreReader` wraps either backend with the same file-like interface,
so the `xarray.open_dataset` call underneath doesn't change between them.

=== "obstore (S3)"

    Requires the `obstore` extra plus `obspec-utils`:
    `pip install earthaccess-auth[obstore] obspec-utils`.

    ```python
    --8<-- "examples/read_a_dataset_s3.py"
    ```

=== "obspec-utils (HTTPS)"

    Requires the `obstore` extra (for `http_client_options`) plus
    `obspec-utils` and `aiohttp`:
    `pip install earthaccess-auth[obstore] obspec-utils aiohttp`.

    Use this when the granule is only available on-prem (no S3 bucket), or
    when you're running outside `us-west-2` and don't want to pay
    cross-region S3 egress.

    ```python
    --8<-- "examples/read_a_dataset_https.py"
    ```

Both scripts live in
[`examples/`](https://github.com/earthaccess-dev/earthaccess/tree/main/earthaccess-auth/examples)
and declare their own dependencies ([PEP 723](https://peps.python.org/pep-0723/)),
so `uv run examples/read_a_dataset_s3.py` works standalone, no separate
install step required.

!!! note "S3 credentials are DAAC-scoped and short-lived"

    `get_s3_credentials()` / `s3_credential_provider()` return credentials
    valid for one DAAC's cloud bucket(s), for about an hour. If you're reading
    granules from more than one DAAC, fetch credentials per DAAC; if a read
    fails with an auth error partway through a long-running job, get fresh
    credentials rather than retrying with the ones you have.

See [Choosing a backend](../explanation/choosing-a-backend.md) for how to
decide between these two.
