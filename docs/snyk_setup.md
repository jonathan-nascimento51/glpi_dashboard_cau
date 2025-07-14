# Configurando acesso ao Snyk

O pipeline de CI executa uma varredura de vulnerabilidades com o Snyk após os testes.
Esse passo requer conexão de saída para `https://snyk.io`. Caso sua infraestrutura
utilize proxy ou lista de domínios permitidos, certifique-se de liberar o acesso a
esse host.

1. **Permissão de rede**
   - Adicione `snyk.io` à sua regra de _allowlist_ ou configure o proxy corporativo
     para encaminhar requisições HTTPS para esse domínio.
   - Valide a conectividade executando:

     ```bash
     ./scripts/check_snyk_access.sh
     ```

     O script retornará erro caso não consiga estabelecer a conexão.

2. **Token de autenticação**
   - Gere um token em <https://app.snyk.io/account> e salve-o como `SNYK_TOKEN`
     nos _Secrets_ do repositório ou como variável de ambiente local.

3. **Execução manual**
   - É possível rodar a análise localmente com:

     ```bash
     snyk test --severity-threshold=high --json-file-output=snyk.json
     ```

   - Certifique-se de que o token e a conectividade estejam configurados antes de executar.
