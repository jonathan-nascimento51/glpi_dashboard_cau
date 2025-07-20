# Knowledge Base: Erros Comuns

Aplique todos os conceitos aprendidos durante o desenvolvimento em nossa base de dados para evitar repetir erros nas próximas melhorias e correções, liberando mais processamento para outras frentes do projeto.

## 400 Bad Request
- **Causa**: headers ausentes ou formato de payload invalido.
- **Correção**: valide os tokens e compare o corpo enviado com a documentação da API.

## 401 Unauthorized
- **Causa**: credenciais incorretas ou token expirado.
- **Correção**: gere novo token no GLPI e confirme usuario/senha.

## 403 Forbidden
- **Causa**: o token da API (`app_token` ou `user_token`) é válido, mas não possui as permissões necessárias para acessar o recurso solicitado. Por exemplo, tentar ler chamados sem ter a permissão de leitura no perfil associado.
- **Correção**: no GLPI, verifique o perfil de permissões associado ao usuário ou cliente de API e conceda o acesso necessário (leitura, escrita, etc.) para os `itemtypes` desejados.

## 404 Not Found
- **Causa**: URL incorreta ou endpoint desabilitado.
- **Correção**: verifique o caminho usado e habilite o modulo correspondente.

## 408 Request Timeout
- **Causa**: latência de rede ou servidor indisponivel.
- **Correção**: aumente o timeout ou teste a conectividade antes de reenviar.

## 500 Internal Server Error
- **Causa**: falha inesperada no GLPI ou parametros fora do esperado.
- **Correção**: repita a operacao e verifique
