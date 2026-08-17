# Choosing a backend

`earthaccess-auth` doesn't pick a data-access backend for you. It hands you
a token, a session, or a credential provider, and you decide what to do
with it. This is how the three options in this documentation compare:

| | obstore (S3) | fsspec (HTTPS) | fsspec (S3, via `s3fs`) |
| --- | --- | --- | --- |
| Extra required | `earthaccess-auth[obstore]` | `earthaccess-auth[fsspec]` | `earthaccess-auth[fsspec]` + `s3fs` |
| Works outside `us-west-2` | Yes, but pays cross-region egress | Yes, that's its purpose | Yes, but pays cross-region egress |
| Works for on-prem (non-cloud) DAAC archives | No, on-prem archives aren't in S3 | Yes | No |
| Credential refresh on long-running jobs | Automatic (`s3_credential_provider`) | Doesn't apply; it's a bearer token, not S3 creds | Manual; re-call `get_s3_credentials()` yourself |
| Typical throughput for large binary reads | Fastest (Rust client, no GIL) | Good | Good |
| Adapter shipped by `earthaccess-auth` | Yes (`adapters.obstore`) | Yes (`adapters.fsspec`) | No, `get_s3_credentials()` is generic enough that `s3fs` needs no adapter |

## Rules of thumb

If you're running in AWS `us-west-2` and the data is cloud-hosted, go
straight to S3: `obstore` for the fastest reads and automatic credential
refresh, or `s3fs` if you're already deep in the `fsspec` ecosystem (an
existing `xarray` + `fsspec` pipeline, say) and don't want a second
dependency.

If you're running anywhere else, or the collection is on-prem only, use
the fsspec HTTPS session (`get_fsspec_https_session`). Cross-region S3
reads are billed to the requester and slower than same-region reads.

If you just need a token or headers and no file access at all, skip both.
See [Get S3 credentials and bearer tokens](../howto/s3-credentials-and-bearer-token.md).
