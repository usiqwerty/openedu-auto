import os

from requests import Request, Response

from tests.fake_api_session import FakeApiSession


@FakeApiSession.register("https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth")
def auth_page(req: Request):
    truthful = True
    resp = Response()
    if req.headers["Accept"] == "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" and \
        req.headers["Accept-Encoding"] == "gzip, deflate, br, zstd" and \
        req.headers["Accept-Language"] == "en-US,en;q=0.5" and \
        req.headers["Connection"] == "keep-alive" and \
        req.headers["Cookie"] == "AUTH_SESSION_ID=7a4bf64f-2c33-46ad-a11b-2f4abb93fe21.keycloak-kc-1-2899; AUTH_SESSION_ID_LEGACY=7a4bf64f-2c33-46ad-a11b-2f4abb93fe21.keycloak-kc-1-2899; KEYCLOAK_LOCALE=ru; KEYCLOAK_IDENTITY=eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhYzNiZGU2OC05OWI5LTRjMzctOTllOC00ZDMwNTBhYzBkZTcifQ.eyJleHAiOjE3NDIxNjMwNDksImlhdCI6MTc0MTY4Nzg0OSwianRpIjoiMGM2NGY0N2EtODIyYS00MzU3LWE1YWYtYjcyNTc4ZmE5Zjg5IiwiaXNzIjoiaHR0cHM6Ly9zc28ub3BlbmVkdS5ydS9yZWFsbXMvb3BlbmVkdSIsInN1YiI6IjVhMDgxNTcyLWQzMWYtNDc3Ni05YTgxLTc1ZGUwM2NmNzI5YSIsInR5cCI6IlNlcmlhbGl6ZWQtSUQiLCJzZXNzaW9uX3N0YXRlIjoiN2E0YmY2NGYtMmMzMy00NmFkLWExMWItMmY0YWJiOTNmZTIxIiwic2lkIjoiN2E0YmY2NGYtMmMzMy00NmFkLWExMWItMmY0YWJiOTNmZTIxIiwic3RhdGVfY2hlY2tlciI6IlpZX3NBdnBKbzhJUm92Y1pydFBRNWt5cXVTeFhNdnl0ODdRd1BHbmViLW8ifQ.7U6BxybOhTXo--Nfthvw7oux47Zj8SyrZ1cY77UeFMI; KEYCLOAK_IDENTITY_LEGACY=eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhYzNiZGU2OC05OWI5LTRjMzctOTllOC00ZDMwNTBhYzBkZTcifQ.eyJleHAiOjE3NDIxNjMwNDksImlhdCI6MTc0MTY4Nzg0OSwianRpIjoiMGM2NGY0N2EtODIyYS00MzU3LWE1YWYtYjcyNTc4ZmE5Zjg5IiwiaXNzIjoiaHR0cHM6Ly9zc28ub3BlbmVkdS5ydS9yZWFsbXMvb3BlbmVkdSIsInN1YiI6IjVhMDgxNTcyLWQzMWYtNDc3Ni05YTgxLTc1ZGUwM2NmNzI5YSIsInR5cCI6IlNlcmlhbGl6ZWQtSUQiLCJzZXNzaW9uX3N0YXRlIjoiN2E0YmY2NGYtMmMzMy00NmFkLWExMWItMmY0YWJiOTNmZTIxIiwic2lkIjoiN2E0YmY2NGYtMmMzMy00NmFkLWExMWItMmY0YWJiOTNmZTIxIiwic3RhdGVfY2hlY2tlciI6IlpZX3NBdnBKbzhJUm92Y1pydFBRNWt5cXVTeFhNdnl0ODdRd1BHbmViLW8ifQ.7U6BxybOhTXo--Nfthvw7oux47Zj8SyrZ1cY77UeFMI; KEYCLOAK_SESSION=openedu/5a081572-d31f-4776-9a81-75de03cf729a/7a4bf64f-2c33-46ad-a11b-2f4abb93fe21; KEYCLOAK_SESSION_LEGACY=openedu/5a081572-d31f-4776-9a81-75de03cf729a/7a4bf64f-2c33-46ad-a11b-2f4abb93fe21; KEYCLOAK_REMEMBER_ME=username:kirillkizilov; openedx-language-preference=ru; sessionid=1|6id2qsl0dcb7xznrn50x9y55928o2q2m|GVL8Kjwfz5Dx|IjBhOGNhMjAzODU0MjEyY2UyZjhkNDMzNDg2NDNiY2U5OWQ0OTI2MjBkYjEzNWUwMTZiZDZiMmFiYTZiMjc1ZGQi:1trwZl:H_MdLxu2avCCLr-zc_C9z_AXpKU" and \
        req.headers["Host"] == "sso.openedu.ru" and \
        req.headers["Priority"] == "u=0, i" and \
        req.headers["Referer"] == "https://apps.openedu.ru/" and \
        req.headers["Sec-Fetch-Dest"] == "document" and \
        req.headers["Sec-Fetch-Mode"] == "navigate" and \
        req.headers["Sec-Fetch-Site"] =="same-site" and \
        req.headers["Upgrade-Insecure-Requests"] == "1" and \
        req.headers["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0":
        pass
    else:
        truthful = False

    if not truthful:
        with open(os.path.join("tests", "data", 'auth.html'), 'rb') as f:
            html = f.read()
        resp.status_code = 200
        resp._content = html
    else:
        resp.status_code = 302
        state = "ah"
        session_state = "ashhhh"
        resp.headers['location'] = (f"https://courses.openedu.ru/auth/complete/keycloak/"
                                    f"?state={state}&session_state={session_state}")
    return resp


@FakeApiSession.register('https://sso.openedu.ru/realms/openedu/login-actions/authenticate')
def authenticate(req: Request):
    resp = Response()
    resp.status_code = 302
    FakeApiSession.logged_in = True
    resp.headers = {'cache-control': 'no-store, must-revalidate, max-age=0', 'Connection': 'keep-alive',
                    'Content-Length': '0',
                    'content-security-policy': "frame-ancestors 'self' https://*.examus.net https://*.student.examus.net https://*.openedu.ru https://*.hse.ru/ always",
                    'Date': 'Mon, 10 Mar 2025 17:47:01 GMT', 'Keep-Alive': 'timeout=15',
                    'Location': 'https://openedu.ru?session_state=2f49a663-f52d-4ec2-86ef-24615c745259&code=19847c59-ef59-4aa9-b02c-93bf33c9510a.2f49a663-f52d-4ec2-86ef-24615c745259.a8bac7c8-08f0-4ab2-b194-a6f565c61399',
                    'p3p': 'CP="This is not a P3P policy!"', 'referrer-policy': 'no-referrer', 'Server': 'QRATOR',
                    'set-cookie': 'KEYCLOAK_REMEMBER_ME=username:admin; Version=1; Expires=Tue, 10-Mar-2026 17:47:01 GMT; Max-Age=31536000; Path=/realms/openedu/; Secure; HttpOnly',
                    'strict-transport-security': 'max-age=31536000; includeSubDomains',
                    'x-content-type-options': 'nosniff', 'x-frame-options': 'ALLOW', 'x-robots-tag': 'none',
                    'x-xss-protection': '1; mode=block'}

    return resp


@FakeApiSession.register("https://openedu.ru/login/npoedsso/")
def npoed_sso(req: Request):
    resp = Response()
    uri = 'https://openedu.ru/complete/npoedsso/'
    state = '7FDprBaPdw4RHeb18uXdF4RYqyWrWtLO'
    nonce = 'TANsrVxnjJuOqmq25oOH2tkfCJfLKlGYdhDYO13Qll3S9xINfe4Ep5zYXOcVSQgg'
    url = f"https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth?client_id=plp&redirect_uri={uri}&state={state}&response_type=code&nonce={nonce}&scope=openid+profile+email"

    resp.headers['Location'] = url
    resp.cookies['plpsessionid'] = 'vr1yxjnaacdggtht672eti79mbihnqjx'
    resp.status_code = 302
    return resp
