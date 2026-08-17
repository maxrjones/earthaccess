# Get S3 credentials and bearer tokens

`earthaccess-auth` gives you three things once you're logged in: a bearer
token, temporary AWS S3 credentials, and (via the `obstore` extra) a
credential *provider* that fetches and refreshes those credentials for you.
Which one you want depends on what you're handing it to.

## The raw bearer token

The minimal case: no fsspec, no obstore, just the token string — inject it
into a header somewhere yourself. This is the pattern a Lambda-deployed
consumer with a tight dependency budget (no fsspec, no obstore) would use.

```python
import earthaccess_auth

auth = earthaccess_auth.login(strategy="environment")
token = auth.token["access_token"]
```

## Header dict for HTTP-based stores

For anything that accepts a plain `headers` dict — obstore HTTP stores,
icechunk's `http_store(headers=...)` for virtual chunk containers — use
`http_client_options`:

```python
from earthaccess_auth.adapters.obstore import http_client_options

options = http_client_options(auth)
# {"default_headers": {"authorization": "Bearer <token>"}}
```

## Temporary AWS S3 credentials

For anything that wants `key`/`secret`/`token` (or `aws_access_key_id`
/`aws_secret_access_key`/`aws_session_token`) directly — `boto3`, `s3fs`,
`awscli`:

```python
creds = auth.get_s3_credentials(daac="NSIDC")
# {"accessKeyId": "...", "secretAccessKey": "...", "sessionToken": "...", "expiration": "..."}
```

You can look credentials up by DAAC short name (`daac="NSIDC"`), by cloud
provider code (`provider="NSIDC_CPRD"`, from
[`find_provider`](../reference/api.md)), or by a raw `s3credentials`
endpoint URL (`endpoint=...`) if you already have one. These credentials
are scoped to that DAAC's cloud bucket(s) and expire in about an hour —
don't cache them longer than that.

## An obstore credential *provider*

If you're handing credentials to an `obstore.store.S3Store` (or the
`obstore.fsspec.FsspecStore` wrapper — see
[Read a dataset with xarray](read-a-dataset.md)), pass a *provider*, not a
one-shot credentials dict. The provider re-calls `get_s3_credentials()`
automatically once the current credentials near expiry, so a long-running
job doesn't need its own refresh loop:

```python
from earthaccess_auth.adapters.obstore import s3_credential_provider

credential_provider = s3_credential_provider(
    auth,
    credentials_endpoint="https://data.nsidc.earthdatacloud.nasa.gov/s3credentials",
)
```

`credentials_endpoint` is a DAAC's `s3credentials` URL — see the
`"s3-credentials"` field on each entry in
[`DAACS`](../reference/api.md#earthaccess_auth.daac.DAACS).
