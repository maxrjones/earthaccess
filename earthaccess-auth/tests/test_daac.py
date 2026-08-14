from earthaccess_auth.daac import DAACS, find_provider


def test_daacs_registry_is_populated() -> None:
    short_names = {d["short-name"] for d in DAACS}
    assert {"NSIDC", "PODAAC", "LPDAAC"} <= short_names


def test_nsidc_s3_credentials_endpoint() -> None:
    nsidc = next(d for d in DAACS if d["short-name"] == "NSIDC")
    assert (
        nsidc["s3-credentials"]
        == "https://data.nsidc.earthdatacloud.nasa.gov/s3credentials"
    )


def test_find_provider_cloud_hosted() -> None:
    assert find_provider("NSIDC", cloud_hosted=True) == "NSIDC_CPRD"
