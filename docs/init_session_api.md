# Endpoint `initSession` da API GLPI (v10.x)

Este documento resume como autenticar-se corretamente no GLPI usando o endpoint
`initSession`. A maioria dos erros `400 Bad Request` ocorre quando os cabeçalhos
não seguem o formato exigido pela API.

## Requisição
- **URL**: `[GLPI_URL]/apirest.php/initSession`
- **Método**: `GET`
- **Cabeçalhos obrigatórios**:
  - `App-Token`: token da aplicação registrado no GLPI.
  - `Content-Type: application/json`
  - `Authorization`: escolha **uma** forma de autenticação:
    - `user_token <TOKEN_PESSOAL>` – token pessoal do usuário (recomendado).
    - `Basic <login:senha em Base64>` – caso utilize login/senha.
- **Corpo**: não deve haver corpo na requisição.
- **Parâmetros opcionais**:
  - `get_full_session`: se `true`, o GLPI retorna também dados da sessão.

Exemplo usando `curl` com `user_token`:
```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: user_token SEU_USER_TOKEN" \
  -H "App-Token: SEU_APP_TOKEN" \
  "https://seu-dominio/glpi/apirest.php/initSession"
```

Em caso de sucesso, o retorno será `200 OK` com JSON contendo o `session_token`.
Se algum cabeçalho estiver incorreto ou faltar, o servidor responderá `400 Bad Request`.

Para exemplos em Python e mais detalhes, consulte
`docs/troubleshooting_400_bad_request.md`.

