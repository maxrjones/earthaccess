# List the contents of an S3 bucket

Useful for exploring what a DAAC's cloud bucket actually contains before you
build a granule URL by hand, or for a quick sanity check that your S3
credentials work at all.

```python
--8<-- "examples/list_bucket_contents.py"
```

`obstore.list()` returns a lazily-paginated stream of `ObjectMeta` dicts
(`path`, `size`, `last_modified`, `e_tag`). Iterating it fetches pages as
needed instead of loading the whole prefix into memory up front.

Already on `s3fs`? `auth.get_s3_credentials(daac=...)` returns a plain
temporary AWS credential dict that `s3fs.S3FileSystem` (like anything else
`boto3`-shaped) accepts directly — no separate adapter needed. See
[Get S3 credentials and bearer tokens](s3-credentials-and-bearer-token.md).

This script is [`examples/list_bucket_contents.py`](https://github.com/earthaccess-dev/earthaccess/tree/main/earthaccess-auth/examples/list_bucket_contents.py),
and declares its own dependencies ([PEP 723](https://peps.python.org/pep-0723/)),
so `uv run examples/list_bucket_contents.py` works standalone.
