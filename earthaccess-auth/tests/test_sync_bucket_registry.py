"""Tests for scripts/sync_bucket_registry.py.

The script lives outside the installed package (it's a maintainer tool, not
runtime code), so it's loaded directly from its file path.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "sync_bucket_registry.py"

spec = importlib.util.spec_from_file_location("sync_bucket_registry", SCRIPT_PATH)
sync_bucket_registry = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sync_bucket_registry
spec.loader.exec_module(sync_bucket_registry)

build_bucket_registry = sync_bucket_registry.build_bucket_registry
split_bucket_and_prefix = sync_bucket_registry.split_bucket_and_prefix


def _collection(provider, endpoint, region, prefixes):
    return {
        "meta": {"provider-id": provider},
        "umm": {
            "DirectDistributionInformation": {
                "Region": region,
                "S3BucketAndObjectPrefixNames": prefixes,
                "S3CredentialsAPIEndpoint": endpoint,
            },
        },
    }


def test_split_bucket_and_prefix_with_separator():
    assert split_bucket_and_prefix("podaac-ops-cumulus-protected/MUR-JPL/") == (
        "podaac-ops-cumulus-protected",
        "MUR-JPL/",
    )


def test_split_bucket_and_prefix_recovers_missing_separator():
    # The real, observed malformed entry: no "/" between bucket and prefix.
    assert split_bucket_and_prefix(
        "gesdisc-cumulus-prod-protectedAqua_AIRS_Level2",
    ) == ("gesdisc-cumulus-prod-protected", "Aqua_AIRS_Level2")


def test_split_bucket_and_prefix_recovers_missing_separator_with_numeric_suffix():
    assert split_bucket_and_prefix(
        "csda-cumulus-prod-protected-5047SomeShortName",
    ) == ("csda-cumulus-prod-protected-5047", "SomeShortName")


def test_build_bucket_registry_extracts_bucket_endpoint_region():
    collections = [
        _collection(
            "POCLOUD",
            "https://archive.podaac.earthdata.nasa.gov/s3credentials",
            "us-west-2",
            ["podaac-ops-cumulus-protected/COLL/"],
        ),
    ]

    registry = build_bucket_registry(collections)

    assert set(registry) == {"podaac-ops-cumulus-protected"}
    entry = registry["podaac-ops-cumulus-protected"]
    assert entry.endpoint == "https://archive.podaac.earthdata.nasa.gov/s3credentials"
    assert entry.region == "us-west-2"
    assert entry.providers == {"POCLOUD"}


def test_build_bucket_registry_drops_test_bucket():
    collections = [
        _collection(
            "SOME_QA_PROVIDER",
            "https://example.com/s3credentials",
            "us-west-2",
            ["TestBucket/COLL/"],
        ),
    ]

    registry = build_bucket_registry(collections)

    assert registry == {}


def test_build_bucket_registry_normalizes_malformed_entry():
    collections = [
        _collection(
            "GES_DISC",
            "https://data.gesdisc.earthdata.nasa.gov/s3credentials",
            "us-west-2",
            ["gesdisc-cumulus-prod-protectedAqua_AIRS_Level2"],
        ),
    ]

    registry = build_bucket_registry(collections)

    assert set(registry) == {"gesdisc-cumulus-prod-protected"}


def test_build_bucket_registry_skips_collections_without_direct_distribution():
    collections = [{"meta": {"provider-id": "SOME_PROVIDER"}, "umm": {}}]

    assert build_bucket_registry(collections) == {}
