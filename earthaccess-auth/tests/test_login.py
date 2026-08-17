import contextlib
from unittest import mock

import earthaccess_auth
from earthaccess_auth import Auth
from earthaccess_auth.exceptions import LoginStrategyUnavailable


def test_login_all_falls_through_to_first_success(monkeypatch):
    calls = []

    def fake_login(self, strategy="netrc", **_kwargs):
        calls.append(strategy)
        if strategy == "environment":
            msg = "no environment variables set"
            raise LoginStrategyUnavailable(msg)
        self.authenticated = True
        return self

    monkeypatch.setattr(Auth, "login", fake_login)
    auth = earthaccess_auth.login(strategy="all")
    assert calls == ["environment", "netrc"]
    assert auth.authenticated


def test_login_single_strategy_does_not_fall_through(monkeypatch):
    calls = []

    def fake_login(_self, strategy="netrc", **_kwargs):
        calls.append(strategy)
        msg = "unavailable"
        raise LoginStrategyUnavailable(msg)

    monkeypatch.setattr(Auth, "login", fake_login)
    with contextlib.suppress(LoginStrategyUnavailable):
        earthaccess_auth.login(strategy="netrc")
    assert calls == ["netrc"]


def test_login_all_falls_through_to_interactive(monkeypatch):
    calls = []

    def fake_login(self, strategy="netrc", **_kwargs):
        calls.append(strategy)
        if strategy in ("environment", "netrc"):
            msg = f"{strategy} unavailable"
            raise LoginStrategyUnavailable(msg)
        self.authenticated = True
        return self

    monkeypatch.setattr(Auth, "login", fake_login)
    auth = earthaccess_auth.login(strategy="all")
    assert calls == ["environment", "netrc", "interactive"]
    assert auth.authenticated


def test_login_all_exhausted_returns_unauthenticated(monkeypatch):
    def fake_login(_self, strategy="netrc", **_kwargs):
        msg = f"{strategy} unavailable"
        raise LoginStrategyUnavailable(msg)

    monkeypatch.setattr(Auth, "login", fake_login)
    auth = earthaccess_auth.login(strategy="all")
    assert not auth.authenticated


def test_login_all_uses_environment_token(monkeypatch):
    monkeypatch.setenv("EARTHDATA_TOKEN", "token-123")
    with mock.patch.object(
        Auth, "_netrc", side_effect=AssertionError("should not reach netrc")
    ):
        auth = earthaccess_auth.login(strategy="all")
    assert auth.authenticated
    assert auth.token == {"access_token": "token-123"}
