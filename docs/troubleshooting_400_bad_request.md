# Investigando Erros 400 ao Chamar a API GLPI

Este guia explica as causas mais comuns do retorno **HTTP 400: Bad Request** durante a inicialização do dashboard via Docker. O problema geralmente ocorre na etapa de `initSession` do GLPI e impede que o contêiner `dash` permaneça ativo.
Para entender em detalhes o funcionamento do endpoint, consulte também
[init_session_api.md](init_session_api.md).

## 1. Verifique as Credenciais

1. Crie o arquivo `.env` com `python scripts/setup_env.py` caso ainda não exista.
2. Preencha `GLPI_BASE_URL`, `GLPI_APP_TOKEN` e `GLPI_USER_TOKEN` (ou `GLPI_USERNAME`/`GLPI_PASSWORD`).
3. Execute um teste fora do Docker para confirmar a validade dos tokens:

```powershell
$headers = @{"Content-Type"="application/json"; "App-Token"="$Env:GLPI_APP_TOKEN"; "Authorization"="user_token $Env:GLPI_USER_TOKEN"}
Invoke-WebRequest -Uri "$Env:GLPI_BASE_URL/initSession" -Headers $headers -Method Get
```

Se a chamada retornar `200 OK` com um `session_token`, as credenciais estão corretas.

## 2. Teste a Conectividade a Partir do Contêiner

1. Altere temporariamente o arquivo `docker-compose.yml` para manter o contêiner ativo:

   ```yaml
   services:
     dash:
       command: tail -f /dev/null
   ```

2. Recrie os serviços (`docker compose up -d --build`).
3. Acesse o shell do contêiner e teste DNS e HTTP:

   ```bash
   docker compose exec dash bash
   apt-get update && apt-get install -y curl dnsutils iputils-ping
   ping -c 3 cau.ppiratini.intra.rs.gov.br
   curl -v http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/initSession
   ```

   Se a sua rede intercepta HTTPS com certificados internos,
   defina `VERIFY_SSL=false` no `.env` para que o worker ignore erros de TLS.

Se o `curl` retornar o mesmo erro 400, a conexão está ocorrendo e o problema é realmente na autenticação ou formatação dos headers.

## 3. Ajuste do Código e Logs

Caso esteja utilizando a versão padrão do projeto, verifique `src/glpi_dashboard/services/glpi_session.py`. A partir da versão atual, erros de inicialização registram o corpo da resposta para facilitar o diagnóstico. Veja o log com `docker compose logs dash`.

## 4. Otimize o Build do Docker

Um contexto de build grande (acima de 400 MB) pode indicar arquivos desnecessários. Confirme se `.dockerignore` contém entradas como:

```.ignore
.venv/
*.md
docs/
tests/
```

Isso reduz o tempo de build e evita vazamento de arquivos locais no contêiner.

Com as etapas acima é possível isolar problemas de autenticação, resolver falhas de DNS e reduzir o tempo de construção da imagem Docker.

## 5. Erro `ERROR_WRONG_APP_TOKEN_PARAMETER`

Caso os logs mostrem **`ERROR_WRONG_APP_TOKEN_PARAMETER`** após a chamada a `initSession`, verifique:

1. **Valor do app-token** – copie o token exibido em `Configuração > Geral > API` no GLPI e compare com `GLPI_APP_TOKEN` definido no `.env`. Qualquer caractere incorreto resulta em `400 Bad Request`.
2. **Intervalo de IP** – o app-token pode restringir endereços autorizados. Certifique-se de que o IP do contêiner esteja incluso. Para testes, permita `0.0.0.0/0` e ajuste depois.
3. **Recriação do cliente** – se houver dúvidas sobre tokens antigos persistentes, exclua o cliente de API e crie um novo, mantendo apenas o token necessário.

Seguindo esses passos, a autenticação deve ser aceita e o dashboard continuará a inicialização normalmente.

## 6. SSL Handshake Errors

Ambientes corporativos podem realizar inspe\u00e7\u00e3o de pacotes TLS, gerando falhas de handshake ao chamar o GLPI via HTTPS. Nesse caso:

1. Abra o arquivo `.env` e defina `VERIFY_SSL=false`.
2. Recrie o cont\u00eainer do backend para aplicar a vari\u00e1vel:

   ```bash
   docker compose up -d --build
   ```

Para testes pontuais utilize `curl` com o par\u00e2metro `-k` (insecure), compat\u00edvel com a op\u00e7\u00e3o acima:

```bash
curl -vk https://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php/initSession
```

Se o comando responder com `200 OK`, o certificado foi ignorado corretamente e o problema est\u00e1 limitado \u00e0 verifica\u00e7\u00e3o SSL.
