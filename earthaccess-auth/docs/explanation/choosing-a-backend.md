# Choosing a backend

`earthaccess-auth` doesn't pick a data-access backend for you. It hands you
a token, a headers dict, or a credential provider, and you decide what to do
with it. This is how the two options shown in this documentation compare:

| | obstore (S3) | obspec-utils (HTTPS) |
| --- | --- | --- |
| Extra required | `earthaccess-auth[obstore]` | `earthaccess-auth[obstore]` + `obspec-utils` + `aiohttp` |
| Works outside `us-west-2` | Yes, but pays cross-region egress | Yes, that's its purpose |
| Works for on-prem (non-cloud) DAAC archives | No, on-prem archives aren't in S3 | Yes |
| Credential refresh on long-running jobs | Automatic (`s3_credential_provider`) | Doesn't apply; it's a bearer token, not S3 creds |
| Typical throughput for large binary reads | Fastest (Rust client, no GIL) | Good |
| Adapter shipped by `earthaccess-auth` | Yes (`adapters.obstore`) | Yes (`adapters.obstore.http_client_options`, consumed by `obspec_utils.stores.AiohttpStore`) |

Both backends implement the same [obspec](https://github.com/developmentseed/obspec)
store protocol, so `obspec_utils.readers.EagerStoreReader` wraps either one
identically — see [Read a dataset with xarray](../howto/read-a-dataset.md).
`obstore.store.S3Store` also covers bucket listing and byte-range reads on
its own; obspec-utils doesn't add anything there, so
[List the contents of an S3 bucket](../howto/list-bucket-contents.md) and
[Identify a file from its magic bytes](../howto/magic-bytes.md) use it
directly.

## Rules of thumb

If you're running in AWS `us-west-2` and the data is cloud-hosted, go
straight to S3 with `obstore`: fastest reads, automatic credential refresh.

If you're running anywhere else, or the collection is on-prem only, use
`obspec_utils.stores.AiohttpStore` with the headers dict from
`http_client_options`. Cross-region S3 reads are billed to the requester
and slower than same-region reads.

Already on `s3fs`? `get_s3_credentials()` returns a plain temporary AWS
credential dict that `s3fs.S3FileSystem` (like anything else `boto3`-shaped)
accepts directly — no separate adapter needed, just no automatic refresh:
re-call `get_s3_credentials()` yourself once credentials near expiry.

If you just need a token or headers and no file access at all, skip both.
See [Get S3 credentials and bearer tokens](../howto/s3-credentials-and-bearer-token.md).
