from requests import Response, Request

from tests.fake_api_session import FakeApiSession


@FakeApiSession.register("https://courses.openedu.ru/login_refresh")
def login_refresh(req: Request):
    resp = Response()
    if FakeApiSession.logged_in:
        resp.status_code = 200
        return resp

    resp.status_code = 401
    resp.cookies["sessionid"] = "blablabla"
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['vary'] = 'Accept-Language, Origin, Cookie'
    resp.headers['x-frame-options'] = "ALLOW"
    resp.headers['Keep-Alive'] = 'timeout=15'
    resp.headers['access-control-allow-origin'] = 'https://apps.openedu.ru'
    resp.headers['access-control-allow-credentials'] = 'true'
    resp._content = b'"Unauthorized"'
    return resp


@FakeApiSession.register('https://courses.openedu.ru/auth/login/keycloak/')
def keycloak(req: Request):
    resp = Response()
    resp.status_code = 302




    state = '46DgsDNllo4TNSRPfwyioiMrpRPXE8c2'
    nonce = 'vo1BYCPLcRQsiaISeZ0hiSxSibUmq5CIJpWewBgL11FykQmjQ0CoJqH7RiCcCQ97'
    uri = 'https://courses.openedu.ru/auth/complete/keycloak/'
    resp.headers['location'] = (f'https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth?client_id=edx&'
                                f'redirect_uri={uri}&state={state}&response_type=code&nonce={nonce}&scope=openid+profile+email')
    resp.cookies['sessionid'] = 'blablabla'
    return resp


@FakeApiSession.register('https://courses.openedu.ru/auth/complete/keycloak/')
def keycloak(req: Request):
    resp = Response()
    resp.status_code = 302
    if req.params.get('state') and req.params.get('session_state'):
        resp.headers['Location'] = "https://courses.openedu.ru/auth/complete/keycloak/"
    else:
        pass
    return resp
