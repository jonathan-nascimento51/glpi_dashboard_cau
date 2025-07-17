# Configuração de Desenvolvimento no Windows

Este guia explica como configurar um fluxo de trabalho semiautônomo no Windows 10
utilizando VS Code, WSL e GitHub Actions. As etapas abaixo seguem a mesma lógica
da configuração Unix descrita nos demais documentos, destacando apenas os pontos
específicos do Windows.

## 1. Editor e ambiente

- **Visual Studio Code** é a opção recomendada para Python e JavaScript/TypeScript.
  Instale as extensões oficiais e utilize o terminal integrado para o Git.
- **WSL (Windows Subsystem for Linux)** fornece um shell Unix‑like totalmente
  integrado ao VS Code. Ele permite alternar interpretadores Python e criar
  ambientes virtuais da mesma forma que no Linux.
- Instale a versão **Node.js LTS** mais recente e habilite `pip`/`venv` para
  Python. Esses recursos são necessários tanto para o front-end quanto para o
  back-end.

## 2. Fluxo de Git

1. Inicie um repositório Git local ou clone o existente.
2. Trabalhe em branches de recurso para mudanças grandes e mantenha os Pull
   Requests pequenos e focados.
3. Descreva cada PR de forma clara para facilitar a revisão.

## 3. Integração Contínua

O projeto utiliza GitHub Actions para rodar lint e testes tanto no front-end
Node.js quanto no back-end em Python. Abaixo segue um exemplo simplificado do
workflow:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '20.19.0'
  - run: cd frontend && npm ci
  - run: cd frontend && npm run lint
  - run: cd frontend && npm run build --if-present
  - run: cd frontend && npm test
  - uses: actions/setup-python@v5
    with:
      python-version: '3.10'
  - run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt -r requirements-dev.txt
      pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
  - run: flake8 .
  - run: pytest
```

Use o trecho acima como ponto de partida ao customizar seus arquivos em
`.github/workflows/` para o ambiente Windows. Essa mesma configuração funciona no
Linux via WSL ou nos servidores de CI.

## 4. Otimização opcional do Windows

Alguns serviços e apps padrão podem ser desativados para reduzir o consumo de memória durante o desenvolvimento. O script `scripts/windows/optimize-windows-dev.ps1` aplica essas otimizações de forma automática. Para restaurar as configurações originais use `scripts/windows/restore-defaults.ps1`.

Execute-os a partir de um PowerShell com privilégios de administrador:

```powershell
# Desativa serviços e remove apps desnecessários
scripts/windows/optimize-windows-dev.ps1

# (Quando precisar reverter)
scripts/windows/restore-defaults.ps1
```
