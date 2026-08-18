# How the bucket registry is built

`earthaccess_auth.daac.BUCKET_ENDPOINTS` maps a bare S3 bucket name (e.g.
`podaac-ops-cumulus-protected`) to the `s3credentials` endpoint that issues
temporary AWS credentials scoped to it. It's what lets `earthaccess` resolve
a plain `s3://some-bucket/...` URL to the right DAAC without the caller
having to pass `provider=` or `credentials_endpoint=` themselves.

## Where the data comes from

Every cloud-hosted CMR collection that supports direct S3 access carries a
`DirectDistributionInformation` block in its UMM-C metadata:

```json
"DirectDistributionInformation": {
  "Region": "us-west-2",
  "S3BucketAndObjectPrefixNames": [
    "podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/",
    "podaac-ops-cumulus-public/MUR-JPL-L4-GLOB-v4.1/"
  ],
  "S3CredentialsAPIEndpoint": "https://archive.podaac.earthdata.nasa.gov/s3credentials",
  "S3CredentialsAPIDocumentationURL": "https://archive.podaac.earthdata.nasa.gov/s3credentialsREADME"
}
```

The bucket names and the credentials endpoint sit side by side in the same
block, so sweeping this field across every collection in CMR gives a bucket
-> endpoint mapping straight from the source of truth, rather than guessing
a DAAC (and therefore an endpoint) from the bucket name — the approach
`earthaccess` used previously (a bare `"cumulus" in url` check), which
missed buckets like `lp-prod-protected`, `asdc-prod-protected`,
`prod-lads`, and all of ASF's per-mission buckets.

This also resolves buckets that have no corresponding entry in the
[`DAACS`][earthaccess_auth.daac.DAACS] registry at all — for example CSDA
(`csda-cumulus-prod-protected-5047`), which isn't one of NASA's EOSDIS DAACs
and so was never in the hand-maintained DAAC table, and ASF's per-mission
buckets, where the endpoint varies by mission rather than being one fixed
`s3credentials` URL per DAAC.

`S3BucketAndObjectPrefixNames` entries also carry an object prefix after the
bucket name (`bucket/prefix/`); the prefix is discarded — the registry only
needs to resolve bucket names, not sub-paths within them, since a single set
of EDL-derived STS credentials is valid for the whole bucket regardless of
prefix.

## Running the sweep

```console
$ python earthaccess-auth/scripts/sync_bucket_registry.py --output bucket_registry.json
Swept 8214 cloud-hosted collections -> 47 buckets.
Wrote bucket_registry.json
```

The script pages through `cmr.earthdata.nasa.gov/search/collections.umm_json`
with `cloud_hosted=true` using the `CMR-Search-After` header (CMR's
recommended pagination mechanism for result sets that don't fit in one
page), and reduces every collection's `DirectDistributionInformation` down
to one row per unique bucket.

`--check` diffs the sweep against the mapping currently vendored in
[`BUCKET_ENDPOINTS`][earthaccess_auth.daac.BUCKET_ENDPOINTS] and exits
non-zero if there's drift — new buckets (new missions, new DAACs), buckets
that dropped out of CMR, or a bucket whose credentials endpoint changed.
This is meant to run on a schedule in CI so registry drift shows up as a PR
rather than as a runtime failure for users.

## Cleaning the raw data

A few things need handling before the swept data is usable:

- **Missing separators.** Some `S3BucketAndObjectPrefixNames` entries are
  missing the `/` between the bucket name and the object prefix, e.g.
  `gesdisc-cumulus-prod-protectedAqua_AIRS_Level2` (the real bucket is
  `gesdisc-cumulus-prod-protected`). NASA Cumulus bucket names consistently
  end in `-protected` or `-public` (optionally with a numeric suffix, e.g.
  CSDA's `-5047`), so the script recovers the split by locating that suffix
  rather than the (missing) separator.
- **Placeholder buckets.** A small number of collections (QA/test
  collections) list a literal `TestBucket` value that isn't a real S3
  bucket. These are dropped.
- **Endpoint conflicts.** If the same bucket name shows up with two
  different `S3CredentialsAPIEndpoint` values across collections, the
  script keeps the first one seen and prints a warning — this hasn't been
  observed in practice, but would indicate either a CMR metadata error or a
  bucket rename in progress, and is worth a manual look either way.

## Feeding the mapping into `daac.py`

The sweep's output isn't consumed automatically — merge new/changed rows
from `bucket_registry.json` into
[`BUCKET_ENDPOINTS`][earthaccess_auth.daac.BUCKET_ENDPOINTS] by hand (or
via the `--check` CI job's diff) so the vendored table stays a reviewed,
human-legible artifact rather than a black box regenerated on every run.
