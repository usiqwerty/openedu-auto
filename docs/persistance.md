Весь процесс состоит из пяти 302-редиректов

### 1. Начало. login-refresh
POST https://courses.openedu.ru/login_refresh

#### 401
Если получаем код 401, значит нужно обновить авторизацию, делаем первый запрос на keycloak.
Может отправить `sessionid`, но это неважно
#### 200
Если код 200, то получаем json
```json
{
  "success": true,
  "user_id": ...,
  "response_epoch_seconds": 1741604226.0589693,
  "response_http_date": "Mon, 10 Mar 2025 10:57:06 GMT",
  "expires": "Mon, 10 Mar 2025 11:00:05 GMT",
  "expires_epoch_seconds": 1741604405
}
```
Устанавливает

`edx-jwt-cookie-header-payload`

`edx-jwt-cookie-signature`

`openedx-language-preference`
### 2. keycloak
GET https://courses.openedu.ru/auth/login/keycloak/

Query-параметры
```json
{
  "auth_entry":"login",
  "next":"https://apps.openedu.ru/learning/course/course-v1:.../block-v1:...+type@sequential+block@.../block-v1:...+type@vertical+block@..."
}
```
Возвращает редирект на auth.
### 3. auth
Устанавливает куки
`KC_RESTART`

`KEYCLOAK_IDENTITY`

`KEYCLOAK_LOCALE`

`KEYCLOAK_REMEMBER_ME`

`KEYCLOAK_SESSION`

`KEYCLOAK_SESSION_LEGACY`

Далее пересылает на keycloak

### 4. keycloak
GET https://courses.openedu.ru/auth/complete/keycloak/
```json
{
  "state": "46DgsDNllo4TNSRPfwyioiMrpRPXE8c2",
  "session_state": "6b8697dc-36da-495a-8613-6c4ecf98486f&code=e1f90d30-188a-4672-b6ab-a1754b38239a.6b8697dc-36da-495a-8613-6c4ecf98486f.8eb81aea-4e43-4084-966d-229ad667af15"
}
```
Устанавливает куки

`edx-jwt-cookie-header-payload`

`edx-jwt-cookie-signature`

`edx-user-info`

`edxloggedin`

`openedx-language-preference`

`sessionid`

Пересылает на keycloak без параметров

### 5. keycloak
GET https://courses.openedu.ru/auth/complete/keycloak/

Устанавливает куку `csrftoken`

Пересылает на `next` из login-action'а