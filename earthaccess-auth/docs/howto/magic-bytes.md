# Identify a file from its magic bytes

NASA Earthdata granule filenames don't always advertise their format
reliably, and you don't want to download a multi-gigabyte file just to find
out it's HDF5 instead of NetCDF classic. Both backends let you fetch a byte
range without downloading the whole object, so you can read just the first
few bytes and check them against known file signatures:

| Format | Magic bytes (hex) | Magic bytes (ASCII) |
| --- | --- | --- |
| HDF5 (and NetCDF-4, which is HDF5-based) | `89 48 44 46 0d 0a 1a 0a` | `\x89HDF\r\n\x1a\n` |
| NetCDF classic (CDF-1/2) | `43 44 46 01` / `43 44 46 02` | `CDF\x01` / `CDF\x02` |
| NetCDF classic (CDF-5, 64-bit) | `43 44 46 05` | `CDF\x05` |
| GeoTIFF (little-endian) | `49 49 2a 00` | `II*\x00` |
| GeoTIFF (big-endian) | `4d 4d 00 2a` | `MM\x00*` |

Zarr has no comparable magic bytes. A Zarr store is a directory (or
prefix) of many small objects (`zarr.json`/`.zarray`, `.zmetadata`, chunk
files), not a single self-describing binary blob. "Is this Zarr?" means
checking whether a `zarr.json` or `.zarray` key exists at that prefix, not
sniffing bytes.

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

    path = "ATLAS/ATL03/006/2020/01/01/ATL03_20200101T000106_00650601_006_01.h5"
    header = bytes(obstore.get_range(store, path, start=0, end=8))

    if header == b"\x89HDF\r\n\x1a\n":
        print("HDF5 (or NetCDF-4)")
    elif header[:3] == b"CDF":
        print(f"NetCDF classic, version {header[3]}")
    else:
        print(f"unrecognized: {header!r}")
    ```

=== "fsspec"

    ```python
    with fs.open(url, "rb") as f:
        header = f.read(8)

    if header == b"\x89HDF\r\n\x1a\n":
        print("HDF5 (or NetCDF-4)")
    elif header[:3] == b"CDF":
        print(f"NetCDF classic, version {header[3]}")
    else:
        print(f"unrecognized: {header!r}")
    ```

    `fs` can be either the HTTPS session from
    [`get_fsspec_https_session`](../reference/api.md) or an `s3fs.S3FileSystem`
    built from `get_s3_credentials()`. Either way, `f.read(8)` only pulls the
    first 8 bytes over the wire, thanks to fsspec's range-request support.
