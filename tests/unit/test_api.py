from unittest.mock import MagicMock

import earthaccess


def test_download_passes_through_none_provider(monkeypatch):
    """`provider=None` must stay `None` all the way to `Store.get`, not become
    the string `"NONE"` (which used to defeat the `provider is None` checks
    downstream in `Store`, leading to a bare `KeyError: 'accessKeyId'`).
    """
    mock_store = MagicMock()
    mock_store.get.return_value = []
    monkeypatch.setattr(earthaccess, "_store", mock_store)

    earthaccess.download(["s3://some-bucket/file.nc"])

    args, _kwargs = mock_store.get.call_args
    assert args[2] is None


def test_download_normalizes_provider_case(monkeypatch):
    mock_store = MagicMock()
    mock_store.get.return_value = []
    monkeypatch.setattr(earthaccess, "_store", mock_store)

    earthaccess.download(["s3://some-bucket/file.nc"], provider="pocloud")

    args, _kwargs = mock_store.get.call_args
    assert args[2] == "POCLOUD"
