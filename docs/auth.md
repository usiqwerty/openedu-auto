# Авторизация

## С нуля

## Из состояния
В url передаётся параметр state

### 1. auth

GET https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth

Параметры

```json
{
  "client_id": "plp",
  "redirect_uri": "https://openedu.ru/complete/npoedsso/",
  "state": "4K654wELRojV2zpLfMNXMtB2thD26Ore",
  "response_type": "code",
  "nonce": "GMR1vYcHbezS6rMCCQI2G4umQuVhbonlEl62R0adUcPvxdT5Z71LSHOrhk1vof4R",
  "scope": "openid+profile+email"
}
```

### 2. Login action

POST https://sso.openedu.ru/realms/openedu/login-actions/authenticate

Query-параметры

```json
{
  "session_code": "hdiTZEanxUElUiLEKA5HcMtqjSf05kjrqWoCAarS-mk",
  "execution": "268f8c1b-34e5-4303-9ca7-f655361ae590",
  "client_id": "plp",
  "tab_id": "-l9ZLj7asLI"
}
```

Body-параметры

username, password, rememberMe (on, off)

### 3. npoed sso

GET https://openedu.ru/complete/npoedsso/

Query-парметры
```json
{
  "state": "4K654wELRojV2zpLfMNXMtB2thD26Ore",
  "session_state": "6b8697dc-36da-495a-8613-6c4ecf98486f",
  "code": "736a037b-9406-42a8-8173-3e38116790ee.6b8697dc-36da-495a-8613-6c4ecf98486f.a8bac7c8-08f0-4ab2-b194-a6f565c61399"
}
```
`state` - тот самый параметр из начала