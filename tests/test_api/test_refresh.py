import pytest

from openedu.auth import OpenEduAuth
from tests.fake_api_session import FakeApiSession


@pytest.mark.parametrize("logged_in", [True, False])
def test_login_refresh(logged_in):
    auth = OpenEduAuth()
    auth.session = FakeApiSession()
    FakeApiSession.logged_in = logged_in
    if logged_in:
        assert auth.login_refresh().status_code == 200
    else:
        assert auth.login_refresh().status_code == 401


def test_keycloack():
    auth = OpenEduAuth()
    auth.session = FakeApiSession()
    assert auth.login_keycloak()

def test_login():
    auth = OpenEduAuth()
    auth.session = FakeApiSession()
    auth.login('admin', 'admin')
    assert FakeApiSession.logged_in