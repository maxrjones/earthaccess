# List the contents of an S3 bucket

Useful for exploring what a DAAC's cloud bucket actually contains before you
build a granule URL by hand, or for a quick sanity check that your S3
credentials work at all.

=== "obstore"

    ```python
    import obstore
    from obstore.store import S3Store

    from earthaccess_auth.adapters.obstore import s3_credential_provider

    credential_provider = s3_credential_provider(
        auth,
        credentials_endpoint="https://data.nsidc.earthdatacloud.nasa.gov/s3credentials",
    )
    store = S3Store(
        "nsidc-cumulus-prod-protected",
        region="us-west-2",
        credential_provider=credential_provider,
    )

    for obj in obstore.list(store, prefix="ATLAS/ATL03/006/2020/01/01"):
        print(obj["path"], obj["size"])
    ```

    `obstore.list()` returns a lazily-paginated stream of `ObjectMeta` dicts
    (`path`, `size`, `last_modified`, `e_tag`) — iterating it fetches pages as
    needed rather than loading the whole prefix into memory up front.

=== "fsspec (s3fs)"

    ```python
    import s3fs

    creds = auth.get_s3_credentials(daac="NSIDC")
    fs = s3fs.S3FileSystem(
        key=creds["accessKeyId"],
        secret=creds["secretAccessKey"],
        token=creds["sessionToken"],
    )

    for path in fs.ls("nsidc-cumulus-prod-protected/ATLAS/ATL03/006/2020/01/01"):
        print(path, fs.info(path)["size"])
    ```

    `fs.ls()` returns immediately with the full listing for that prefix
    (non-recursive by default); use `fs.find()` if you need to walk
    subdirectories too.

Both examples assume `auth = earthaccess_auth.login()` has already run — see
[Get S3 credentials and bearer tokens](s3-credentials-and-bearer-token.md).
