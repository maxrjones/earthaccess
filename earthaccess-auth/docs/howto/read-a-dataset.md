# Read a dataset with xarray

Every NASA Earthdata granule is served from one of two places: a plain
HTTPS URL (on-prem DAAC archives), or an S3 bucket in `us-west-2` (NASA
Earthdata Cloud, for clients running in that same region). Once you're
authenticated, `earthaccess-auth` gets you a session or a credential
provider for either. How you hand that to `xarray` depends on which
optional backend you've installed.

=== "obstore (S3)"

    Requires the `obstore` extra: `pip install earthaccess-auth[obstore]`.

    `obstore` exposes an fsspec-compatible store (`obstore.fsspec.FsspecStore`)
    that `xarray`/`h5netcdf` can open directly, backed by obstore's fast Rust
    S3 client instead of `s3fs`.

    ```python
    import earthaccess_auth
    import obstore.fsspec
    import xarray as xr
    from earthaccess_auth.adapters.obstore import s3_credential_provider

    auth = earthaccess_auth.login()

    credential_provider = s3_credential_provider(
        auth,
        credentials_endpoint="https://data.nsidc.earthdatacloud.nasa.gov/s3credentials",
    )

    fs = obstore.fsspec.FsspecStore(
        "s3",
        config={"bucket": "nsidc-cumulus-prod-protected", "region": "us-west-2"},
        credential_provider=credential_provider,
    )

    ds = xr.open_dataset(
        fs.open("ATLAS/ATL03/006/2020/01/01/ATL03_20200101T000106_00650601_006_01.h5"),
        engine="h5netcdf",
    )
    ```

=== "fsspec (HTTPS)"

    Requires the `fsspec` extra: `pip install earthaccess-auth[fsspec]`.

    Use this when the granule is only available on-prem (no S3 bucket), or
    when you're running outside `us-west-2` and don't want to pay cross-region
    S3 egress.

    ```python
    import earthaccess_auth
    import xarray as xr
    from earthaccess_auth.adapters.fsspec import get_fsspec_https_session

    auth = earthaccess_auth.login()
    fs = get_fsspec_https_session(auth)

    url = "https://daac.ornl.gov/daacdata/npp/grassland/NPP_BCN/data/example.nc"
    ds = xr.open_dataset(fs.open(url), engine="h5netcdf")
    ```

=== "fsspec (S3)"

    Requires `pip install earthaccess-auth[fsspec] s3fs`. `earthaccess-auth`
    doesn't ship an S3 adapter for `fsspec` itself; that's what the `obstore`
    extra is for. But `get_s3_credentials()` returns a plain temporary AWS
    credential dict, and `s3fs` (like anything else `boto3`-shaped) accepts
    that directly.

    ```python
    import earthaccess_auth
    import s3fs
    import xarray as xr

    auth = earthaccess_auth.login()
    creds = auth.get_s3_credentials(daac="NSIDC")

    fs = s3fs.S3FileSystem(
        key=creds["accessKeyId"],
        secret=creds["secretAccessKey"],
        token=creds["sessionToken"],
    )

    url = "s3://nsidc-cumulus-prod-protected/ATLAS/ATL03/006/2020/01/01/ATL03_20200101T000106_00650601_006_01.h5"
    ds = xr.open_dataset(fs.open(url), engine="h5netcdf")
    ```

!!! note "S3 credentials are DAAC-scoped and short-lived"

    `get_s3_credentials()` / `s3_credential_provider()` return credentials
    valid for one DAAC's cloud bucket(s), for about an hour. If you're reading
    granules from more than one DAAC, fetch credentials per DAAC; if a read
    fails with an auth error partway through a long-running job, get fresh
    credentials rather than retrying with the ones you have.

See [Choosing a backend](../explanation/choosing-a-backend.md) for how to
decide between these three.
