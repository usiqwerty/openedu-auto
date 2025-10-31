import re

from bs4 import BeautifulSoup
from requests import Session


def login_urfu(session: Session, username: str, password: str):
    oed_login_r = session.get("https://openedu.ru/auth/login/npoedsso/", allow_redirects=True)
    assert len(oed_login_r.history) > 0

    # extract urfu social login button
    urfu_button_re_r = re.search(r'"loginUrl": "\\(/realms/openedu/broker/urfu/login[\w\W]+?)",', oed_login_r.text)
    urfu_button_url = f"https://sso.openedu.ru{urfu_button_re_r.group(1)}"
    urfu_login_r = session.get(urfu_button_url)

    urfu_login_soup = BeautifulSoup(urfu_login_r.text, 'html.parser')
    urfu_login_form = urfu_login_soup.find("form")
    urfu_auth_url = urfu_login_form['action']
    r = session.post(urfu_auth_url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data={
        "username": username,
        "password": password,
        "credentialId": ""
    })

    # very cool success check
    assert len(r.history) > 1
    assert r.url.startswith("https://openedu.ru")
