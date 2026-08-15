"""The auth implementation moved to earthaccess-auth (see earthaccess-auth/tests/).

These tests pin the re-export shims: same class objects, so isinstance
checks and except clauses written against either package keep working.
"""

import earthaccess
import earthaccess.auth
import earthaccess.daac
import earthaccess.exceptions
import earthaccess.system
import earthaccess_auth
import earthaccess_auth.exceptions


def test_shims_reexport_identical_objects():
    assert earthaccess.Auth is earthaccess_auth.Auth
    assert (
        earthaccess.auth.SessionWithHeaderRedirection
        is earthaccess_auth.SessionWithHeaderRedirection
    )
    assert earthaccess.auth.netrc_path is earthaccess_auth.netrc_path
    assert earthaccess.daac.DAACS is earthaccess_auth.daac.DAACS
    assert earthaccess.system.PROD is earthaccess_auth.system.PROD
    assert earthaccess.system.UAT is earthaccess_auth.system.UAT
    assert (
        earthaccess.exceptions.LoginAttemptFailure
        is earthaccess_auth.exceptions.LoginAttemptFailure
    )
    assert (
        earthaccess.exceptions.LoginStrategyUnavailable
        is earthaccess_auth.exceptions.LoginStrategyUnavailable
    )


def test_singleton_reports_earthaccess_user_agent():
    session = earthaccess.__auth__.get_session()
    assert session.headers["User-Agent"] == f"earthaccess v{earthaccess.__version__}"
