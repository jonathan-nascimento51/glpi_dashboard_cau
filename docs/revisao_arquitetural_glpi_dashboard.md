# Revisão Arquitetural e Guia de Integração para a API REST do GLPI

Revisão Arquitetural e Guia de Integração para a API REST do GLPI: Uma Análise Diagnóstica da Aplicação glpi_dashboard_cau
Seção 1: Sumário Executivo e Análise Diagnóstica
Este relatório apresenta uma análise técnica aprofundada da aplicação glpi_dashboard_cau e da sua interação com a API REST do GLPI. A investigação foi motivada pela observação de que os dados exibidos no painel de controlo não correspondiam aos dados esperados, apesar de os registos da aplicação indicarem que as requisições à API estavam a ser executadas com sucesso. A análise conclui que o problema não reside em falhas de comunicação ou erros na API, mas sim em deficiências na implementação do cliente da API dentro da aplicação. Especificamente, a aplicação não gere a paginação dos resultados e não realiza o tratamento necessário dos dados relacionais retornados pela API. Este documento fornece um diagnóstico preciso, recomendações de remediação imediata e um guia estratégico completo para o desenvolvimento de integrações robustas e resilientes com o GLPI.
1.1. Identificação do Problema Central
A discrepância entre os dados obtidos e os dados exibidos na aplicação glpi_dashboard_cau tem origem em duas falhas fundamentais na lógica do cliente da API:
Recuperação Incompleta de Dados: A aplicação está a solicitar e a processar apenas o primeiro conjunto de resultados devolvido pela API do GLPI. As APIs RESTful que lidam com grandes volumes de dados, como listas de chamados, implementam a paginação como um mecanismo padrão para garantir o desempenho e a estabilidade. A ausência de um ciclo de paginação na lógica de busca de dados resulta na exibição de apenas um subconjunto dos chamados totais, levando à perceção de que os dados estão "errados" ou em falta.
Manuseamento Incorreto de Dados Brutos: A aplicação exibe identificadores numéricos (IDs) para campos relacionais, como status, prioridade e utilizadores, em vez dos seus valores textuais correspondentes. A API do GLPI, seguindo um modelo de dados normalizado, devolve IDs que funcionam como chaves estrangeiras para outras tabelas na base de dados.1 Sem uma camada de transformação ou enriquecimento de dados, a aplicação apresenta ao utilizador final dados brutos (ex: status: 1 em vez de "Novo"), que são tecnicamente corretos, mas semanticamente inúteis e interpretados como incorretos.
1.2. Análise dos Registos da Aplicação
Uma análise detalhada dos registos do Docker Compose fornecidos confirma que a infraestrutura da aplicação e o ciclo de vida da comunicação com a API estão a funcionar corretamente, reforçando que o problema é de natureza lógica e não técnica.
Inicialização dos Contentores: As linhas [+] Correndo 5/5 e os subsequentes estados em execução e recriado para os contentores redis-1, postgres-1, dash-1 e worker-1 indicam que o ambiente Docker foi iniciado com sucesso. A mensagem do PostgreSQL informando que o banco foi inicializado confirma que a base de dados subjacente está preparada corretamente. O PostgreSQL executa os scripts de `docker/db-init/` apenas na primeira inicialização; para aplicar mudanças posteriores nesses arquivos, execute `docker compose down -v` e suba novamente.
Início do Processo de Busca de Dados: A linha traço-1 | 2025-07-01 04:22:02.031 - raiz - INFO - Buscando dados de tíquete da API GLPI marca o início do processo de obtenção de dados pelo serviço dash.
Autenticação e Gestão de Sessão: A sequência de registos que se segue é crucial para o diagnóstico:
traço-1 |... AVISO - Tanto user_token quanto o nome de usuário/senha fornecidos. Priorizando user_token para initSession. Este aviso é um ponto de observação importante. A aplicação está a fornecer múltiplos métodos de credenciais. A API do GLPI, conforme documentado, prioriza o user_token quando ambos são fornecidos.3 Embora isto não seja um erro que interrompa a execução, indica uma configuração redundante que deve ser simplificada para fornecer apenas o método de autenticação pretendido.
traço-1 |... Sessão GLPI iniciada com êxito. Esta mensagem confirma que a autenticação foi bem-sucedida e que um session-token válido foi obtido.
traço-1 |... Sessão GLPI encerrada com êxito. Esta mensagem, que ocorre após a inicialização do servidor Dash, confirma que o ciclo de vida da sessão foi concluído corretamente com uma chamada a killSession. Este padrão de initSession -> ação -> killSession é o fluxo de trabalho esperado e documentado para interações com a API do GLPI.4
Execução do Servidor e Callbacks: As linhas traço-1 |... O Dash está sendo executado no <http://0.0.0.0:8050/> e as subsequentes requisições GET e POST com código de estado 200 (ex: POST /_dash-update-component HTTP/1.1" 200 -) demonstram que o servidor web da aplicação está a funcionar e que os callbacks do Dash (que provavelmente contêm a lógica de busca de dados) estão a ser executados sem falhas ou exceções que causem um crash.
A ausência de códigos de erro 4xx ou 5xx nos registos de interação com a API, combinada com a confirmação de um ciclo de sessão bem-sucedido, permite concluir que a aplicação está a comunicar com sucesso com o GLPI. O problema não está na obtenção dos dados, mas sim na lógica que processa a resposta recebida.
1.3. Passos de Remediação Imediata
Para corrigir as falhas identificadas, as seguintes ações devem ser implementadas no código da aplicação:
Implementar um Ciclo de Paginação: A lógica de busca de dados deve ser modificada para inspecionar o cabeçalho de resposta Content-Range após cada requisição. Este cabeçalho contém o total de itens disponíveis (ex: 0-19/46). Se o número de itens retornados for menor que o total, a aplicação deve realizar requisições subsequentes, ajustando o parâmetro de consulta range (ex: range=20-39), até que todos os dados tenham sido recuperados.
Implementar a Transformação de Dados: É necessário criar uma camada de mapeamento de dados. Para campos com valores codificados, como status, priority e urgency, deve ser implementada uma lógica que traduza os IDs numéricos para as suas representações textuais correspondentes, conforme detalhado na Tabela 2 deste relatório. Para campos relacionais como users_id_requester, deve-se utilizar o parâmetro expand_dropdowns=1 na requisição para que a API retorne os nomes em vez dos IDs, ou, como alternativa, realizar chamadas adicionais à API para buscar os detalhes desses objetos relacionados (ex: /apirest.php/User/{id}).
Refinar a Configuração de Autenticação: O ficheiro de configuração ou as variáveis de ambiente da aplicação devem ser ajustados para fornecer apenas um método de autenticação (preferencialmente user_token e app_token), eliminando assim a mensagem de aviso e tornando a intenção da configuração explícita.
A implementação destes três passos resolverá diretamente a perceção de que os dados estão "incorretos", garantindo que o conjunto completo de chamados seja recuperado e que os dados sejam apresentados de forma legível e compreensível para o utilizador final. A "próxima melhoria" mais impactante para a aplicação não é a adição de uma nova funcionalidade, mas sim a refatoração da sua camada de interação com a API para incorporar estas práticas fundamentais, tornando-a verdadeiramente robusta.
Seção 2: Um Guia Abrangente para a API REST do GLPI
Para construir integrações duradouras e de alta qualidade, é imperativo um conhecimento profundo da arquitetura, capacidades e idiossincrasias da API do GLPI. Esta seção serve como um guia de referência técnica para esse fim.
2.1. Arquitetura da API: Endpoints e Versões
O ecossistema do GLPI apresenta duas versões principais da sua API, com filosofias de design distintas. A aplicação glpi_dashboard_cau utiliza atualmente a versão mais antiga.
A API REST Legada (/apirest.php): Este é o endpoint que a aplicação utiliza, conforme inferido pelo fluxo de trabalho de sessão e pela documentação histórica. É descrito pela comunidade de desenvolvimento como sendo extremamente poderoso, mas também de baixo nível e, por vezes, confuso.7 A sua estrutura está intimamente ligada ao modelo de dados da base de dados do GLPI. Esta ligação direta explica por que razão certas operações, como a construção de parâmetros de busca, podem parecer pouco intuitivas e por que razão a API devolve IDs em vez de valores textuais, refletindo diretamente as chaves estrangeiras da base de dados.9
A API Moderna de Alto Nível (/api.php): Introduzida em versões mais recentes do GLPI (a partir da 10.1), esta nova API foi projetada com um foco na facilidade de utilização e na adesão a padrões de desenvolvimento modernos.7 A sua vantagem mais significativa é a inclusão de suporte para a Swagger UI (também conhecida como OpenAPI Specification).10 A Swagger UI é uma ferramenta interativa que permite aos desenvolvedores explorar os endpoints da API, visualizar os modelos de dados, e até mesmo executar chamadas de teste diretamente a partir do navegador.11 Esta funcionalidade reduz drasticamente a curva de aprendizagem e a necessidade de recorrer a fóruns ou engenharia reversa para compreender a API.
Acesso à Documentação da API: Independentemente da versão, o GLPI fornece acesso à documentação da API diretamente a partir da sua interface web. Navegando para Configuração > Geral > API, um administrador pode ativar a API e encontrar um link para a documentação interativa.3 Este deve ser sempre o primeiro ponto de referência ao trabalhar com a API.
2.2. Aprofundamento na Autenticação e Gestão de Sessão
A autenticação na API do GLPI é um processo multifacetado que é fundamental para a segurança e o funcionamento de qualquer integração. O modelo de sessão da API legada é notavelmente stateful, o que representa um desvio dos princípios puramente RESTful e exige uma gestão cuidadosa por parte do cliente.
Métodos de Autenticação: Existem três mecanismos principais para se autenticar na API legada:
Login e Senha: A forma mais básica, utilizando as credenciais de um utilizador GLPI. Estas são enviadas codificadas em Base64 no cabeçalho Authorization (Basic Auth). Devido à sua natureza, este método só deve ser utilizado sobre uma conexão HTTPS segura.14 É ativado na configuração da API através da opção "Ativar login com credenciais".15
Token de Utilizador (user_token): Uma chave de acesso pessoal e de longa duração que pode ser gerada no perfil de cada utilizador.3 Este token é enviado no cabeçalho Authorization com o prefixo user_token.6 Este é o método que a aplicação glpi_dashboard_cau está a utilizar, conforme indicado pelos registos.
Token de Aplicação (app_token): Um token que representa a aplicação cliente em si. É configurado pelo administrador em Configuração > Geral > API > Clientes da API.3 Este token não autentica um utilizador, mas sim autoriza a aplicação a comunicar com a API. É enviado num cabeçalho HTTP separado, App-Token.6 Na maioria dos cenários de produção, tanto um app_token como um método de autenticação de utilizador (user_token ou login/senha) são necessários.
O Ciclo de Vida da Sessão (Stateful): Ao contrário das APIs RESTful stateless, onde cada pedido contém toda a informação necessária para ser processado, a API legada do GLPI requer um processo de estabelecimento de sessão:
initSession: A primeira chamada que uma aplicação deve fazer. Envia-se as credenciais do utilizador (via user_token ou Basic Auth) e o app_token. Em troca, a API devolve um Session-Token temporário.6
Session-Token: Este token de sessão temporário deve ser incluído no cabeçalho Session-Token em todas as requisições subsequentes dentro da mesma sessão.6 É este token que mantém o estado da sessão no servidor.
killSession: A última chamada que a aplicação deve fazer ao concluir as suas operações. Esta chamada invalida o Session-Token no servidor, terminando a sessão de forma segura. Este passo é crucial para a segurança e para evitar o acúmulo de sessões órfãs no servidor GLPI.4
A natureza stateful deste fluxo de trabalho implica que a aplicação cliente deve ser projetada para gerir este ciclo de vida de forma robusta. Deve ser capaz de iniciar uma sessão, armazenar o Session-Token de forma segura, utilizá-lo em todos os pedidos e, crucialmente, garantir que killSession seja chamado no final, mesmo em caso de erro. Uma abordagem arquitetural recomendada para isto é o uso de um gestor de contexto (como o with do Python), que pode automatizar as chamadas initSession e killSession no início e no fim de um bloco de código, respetivamente.4
OAuth2 (Nova API): É importante notar que a nova API de alto nível está a mover-se em direção a um fluxo de autenticação mais padrão da indústria, o OAuth2. Esta versão suportará os tipos de concessão password e authorization_code, que envolvem um client_id e um client_secret, alinhando o GLPI com as melhores práticas modernas de autenticação de APIs.10
Método de Autenticação
Como Obter
Perfil de Segurança
Caso de Uso Recomendado
Fontes Chave
Login e Senha
Credenciais de um utilizador GLPI existente.
Baixo. Transmite credenciais diretamente. Requer HTTPS obrigatório.
Ambientes de desenvolvimento ou scripts rápidos onde a segurança não é a principal preocupação.3
Token de Utilizador (user_token)
Gerado no perfil do utilizador (Chaves de acesso remoto).
Médio. O token é de longa duração. Se comprometido, dá acesso como o utilizador.
Scripts de backend ou serviços que precisam de agir em nome de um utilizador de serviço específico.3
Token de Aplicação (app_token)
Gerado em Config. > Geral > API > Clientes da API.
N/A (Autorização). Não autentica, mas autoriza a aplicação. Pode restringir o acesso por IP.
Usado em conjunto com um método de autenticação de utilizador. Obrigatório na maioria das configurações de produção.3
user_token + app_token
Combinação dos dois métodos acima.
Alto (Recomendado). Fornece autenticação de utilizador e autorização de aplicação. Permite um controlo de acesso mais granular.
Todas as integrações de produção, incluindo dashboards, automações e aplicações de terceiros.6
OAuth2 (Nova API)
Registar um cliente OAuth na interface do GLPI para obter client_id e client_secret.
Muito Alto. Padrão da indústria para delegação de autorização segura.
Aplicações web e móveis modernas que interagem com a nova API (/api.php).10
Tabela 1: Métodos de Autenticação da API do GLPI: Casos de Uso e Melhores Práticas
Seção 3: Dominar a Recuperação e a Estrutura de Dados
Esta seção aborda os mecanismos práticos para obter os dados corretos da API, com um foco particular na resolução dos problemas centrais de paginação e estrutura de dados identificados na aplicação glpi_dashboard_cau.
3.1. O Endpoint search: A Chave para a Filtragem
Enquanto a obtenção de um item por ID (/apirest.php/{itemtype}/{id}) é direta, a maioria das necessidades de uma aplicação de dashboard envolve a busca de múltiplos itens com base em condições específicas. Para isso, o endpoint /search/{itemtype} é a ferramenta principal e mais flexível.4
O Parâmetro criteria: O coração da filtragem é o parâmetro criteria. Não é um parâmetro simples, mas sim uma estrutura de array complexa passada como parâmetros de consulta na URL.19 Cada condição no array é composta por:
field: O ID numérico do campo sobre o qual se quer pesquisar.
searchtype: O operador de comparação a ser usado, como equals, contains, notequals, lessthan, morethan.21
value: O valor a ser procurado.
link: O operador lógico (AND ou OR) para concatenar múltiplas condições.19
Por exemplo, para procurar chamados não eliminados com urgência igual a 5, a URL seria semelhante a:
apirest.php/search/Ticket?is_deleted=0&criteria[field]=12&criteria[searchtype]=equals&criteria[value]=notold&criteria[link]=AND&criteria[field]=10&criteria[searchtype]=equals&criteria[value]=5.19
O Desafio de Encontrar IDs de Campo: Uma das maiores dificuldades ao usar o endpoint search é determinar o field ID correto para cada atributo. Existem duas abordagens principais para descobrir estes IDs:
Programaticamente: Utilizar o endpoint /listSearchOptions/{itemtype}. Este endpoint devolve uma lista de todas as opções de busca disponíveis para um determinado tipo de item, incluindo os seus nomes, tabelas e, mais importante, os seus IDs numéricos.4 Esta é a abordagem mais robusta para uma aplicação.
Manualmente (Engenharia Reversa): Realizar uma busca na interface web do GLPI com os filtros desejados e, em seguida, inspecionar a URL da página de resultados. A URL conterá os parâmetros criteria com os IDs de campo corretos, que podem ser copiados e adaptados para uso na API.19
3.2. Paginação Robusta: O Parâmetro range
Este é o conceito mais crítico para resolver o problema de "dados em falta" na aplicação. A API do GLPI não devolve todos os resultados de uma só vez; ela pagina-os.
O Parâmetro range: Para controlar a paginação, o cliente deve usar o parâmetro range na string de consulta, especificado como range=start-end (ex: range=0-49).22 O valor padrão pode variar entre as versões do GLPI, sendo por vezes 20 ou 50 itens por página.22 Confiar no valor padrão é uma má prática; o cliente deve sempre especificar explicitamente o range desejado.
Cabeçalhos de Resposta de Paginação: A API fornece metadados essenciais nos cabeçalhos de resposta HTTP para permitir que o cliente gira a paginação de forma inteligente:
Content-Range: Este é o cabeçalho mais importante. Ele informa o intervalo de itens que está a ser retornado e o número total de itens que correspondem à consulta. O formato é offset-limit/count, por exemplo, 0-19/46 significa que estão a ser retornados os itens 0 a 19 de um total de 46.6
Accept-Range: Este cabeçalho informa o número máximo de itens que o servidor está configurado para retornar numa única requisição.6
Estratégia de Implementação de Paginação: Uma implementação de cliente robusta deve seguir este algoritmo:
Fazer a requisição inicial com um range definido (ex: range=0-99).
Após receber a resposta, analisar o cabeçalho Content-Range.
Extrair o limite (limit) e o total (count) do cabeçalho.
Se limit + 1 < count, significa que existem mais páginas de resultados.
Calcular o próximo range (ex: range=100-199) e fazer uma nova requisição.
Repetir os passos 2-5 até que todos os itens tenham sido recuperados.
A falha na implementação deste ciclo é a causa mais provável para a aplicação glpi_dashboard_cau estar a exibir apenas um subconjunto dos dados.
3.3. O Tipo de Item 'Ticket' em Profundidade
Compreender a estrutura do objeto Ticket é fundamental para resolver o problema de "dados incorretos".
Esquema do Objeto Ticket Padrão: Com base em exemplos de chamadas à API, um objeto Ticket típico inclui os seguintes campos-chave: id, name (título), content (descrição), status, urgency, impact, priority, itilcategories_id, type,_users_id_requester (ID do solicitante), _users_id_assign (ID do técnico atribuído),_groups_id_requester (ID do grupo solicitante), date_creation e date_mod.16
Mapeamento de IDs para Texto: Conforme mencionado, muitos destes campos são IDs numéricos. A Tabela 2 abaixo fornece um mapeamento direto para os valores mais comuns, com base na documentação e em discussões da comunidade.
Campo
ID
Valor Textual
Fonte
Status
1
Novo
2
Em atendimento (atribuído)
3
Em atendimento (planejado)
4
Pendente
5
Solucionado
6
Fechado
Prioridade / Urgência / Impacto
1
Muito Baixa
2
Baixa
3
Média
4
Alta
5
Muito Alta
6
Maior (Apenas Prioridade/Urgência)
Tipo
1
Incidente
2
Requisição
Tabela 2: Mapeamento de IDs para Valores Textuais em Chamados GLPI
Expansão de Dados com expand_dropdowns: Para evitar múltiplas chamadas à API, o parâmetro expand_dropdowns=1 pode ser adicionado à string de consulta. Este parâmetro instrui a API a substituir os IDs de campos de dropdown (como itilcategories_id) pelos seus nomes legíveis por humanos diretamente na resposta.2 Esta é uma ferramenta de otimização extremamente útil.
Interação com Objetos Relacionados: Um chamado possui vários sub-objetos, como acompanhamentos (TicketFollowup), utilizadores associados (Ticket_User) e grupos (Group_Ticket). Estes são acedidos através de sub-coleções na URL, por exemplo: /apirest.php/Ticket/{id}/TicketFollowup.16
Manuseamento de Campos Personalizados: A adição de campos personalizados a chamados é possível através do plugin fields.28 No entanto, a interação com estes campos via API pode ser complexa. Por vezes, o campo personalizado não aparece no objeto Ticket principal. Nesses casos, pode ser necessário fazer uma chamada a um endpoint separado e dinamicamente nomeado que corresponde ao "contentor" do campo personalizado para ler ou escrever o seu valor.30
Templates de Chamados: A aplicação de templates de chamados durante a criação via API tem limitações. Embora seja possível atribuir uma itilcategories_id que tenha um template associado, os elementos predefinidos do template (como tarefas, campos pré-preenchidos, etc.) não são automaticamente aplicados ao chamado criado via API.27 Este comportamento deve ser tido em conta ao projetar automações de criação de chamados.
A combinação de uma estrutura de dados normalizada e uma API de baixo nível significa que o cliente é responsável por grande parte do trabalho de enriquecimento e transformação de dados. Uma aplicação que simplesmente obtém o objeto Ticket e o exibe diretamente receberá um conjunto de dados que é, para todos os efeitos, inutilizável. A construção de uma camada de "Enriquecimento de Dados" no cliente, que utiliza expand_dropdowns e realiza mapeamentos de IDs, é um passo arquitetural essencial para garantir que os dados apresentados ao utilizador sejam "corretos" e significativos.
Seção 4: Construir um Cliente GLPI Resiliente: Melhores Práticas
Para evoluir a aplicação glpi_dashboard_cau de um script funcional para uma solução de software robusta e de fácil manutenção, é crucial adotar práticas de desenvolvimento que promovam a resiliência e a separação de preocupações.
4.1. Gestão Avançada de Erros e Validação de Respostas
Uma implementação robusta não pode assumir que todas as chamadas à API serão bem-sucedidas. É necessário antecipar e gerir uma variedade de cenários de falha.
Tratamento de Códigos de Status HTTP: O tratamento adequado dos códigos de status HTTP é a primeira linha de defesa. A aplicação deve distinguir claramente entre:
2xx (Sucesso): Respostas como 200 OK, 201 Created ou 206 Partial Content indicam que a requisição foi bem-sucedida.24
4xx (Erro do Cliente): Respostas como 400 Bad Request (parâmetros inválidos), 401 Unauthorized (credenciais inválidas ou em falta) ou 404 Not Found (item não encontrado) indicam um problema com a requisição enviada pelo cliente. Estes erros geralmente não devem ser tentados novamente sem modificação.6
5xx (Erro do Servidor): Respostas como 500 Internal Server Error indicam um problema no lado do servidor GLPI. Estes podem ser erros transitórios, e uma estratégia de nova tentativa com exponential backoff pode ser apropriada.31
Análise do Payload de Erro do GLPI: Quando o GLPI devolve um erro 4xx, ele geralmente inclui um corpo de resposta JSON que fornece mais detalhes. O formato típico é um array contendo uma string de código de erro e uma mensagem legível por humanos, por exemplo: ``.4 A aplicação cliente deve analisar este payload para:
Registar o código de erro específico (ex: ERROR_SESSION_TOKEN_INVALID) para uma depuração mais eficaz.
Implementar lógicas de recuperação específicas. Por exemplo, ao receber um ERROR_SESSION_TOKEN_INVALID, o cliente deve descartar o token de sessão atual e tentar iniciar uma nova sessão.
Código de Erro GLPI
Mensagem de Exemplo
Causa Provável
Ação Recomendada no Cliente
Fontes
ERROR_SESSION_TOKEN_INVALID
session_token semble incorrect
O token de sessão expirou, foi invalidado (killSession) ou está incorreto.
Descartar o token de sessão atual. Tentar re-iniciar a sessão com initSession e obter um novo token. Tentar novamente a requisição original com o novo token.4
ERROR_APP_TOKEN_PARAMETERS_MISSING
missing parameter app_token
O cabeçalho App-Token não foi incluído na requisição e é exigido pela configuração do GLPI.
Garantir que o app_token está a ser enviado em todas as requisições à API.32
ERROR_GLPI_LOGIN
Incorrect username or password
As credenciais de login/senha ou o user_token fornecidos em initSession estão incorretos.
Falhar a operação e registar um erro de configuração. Notificar o administrador. Não tentar novamente com as mesmas credenciais.32
ERROR_ITEM_NOT_FOUND
Élément introuvable
Foi feita uma tentativa de aceder a um item (ex: Ticket/9999) que não existe.
Tratar como um resultado esperado (ex: devolver None ou uma lista vazia). Não é um erro fatal do sistema.4
ERROR_JSON_PAYLOAD_FORBIDDEN
GET Request should not have json payload
Foi enviado um corpo de requisição (payload) numa chamada GET, o que não é permitido.
Refatorar a requisição para passar todos os parâmetros como uma string de consulta na URL, em vez de no corpo da requisição.9
Tabela 3: Códigos de Erro Comuns da API do GLPI e Estratégias de Tratamento
4.2. Arquitetura Recomendada para o Cliente: A Camada Anti-Corrupção
A API do GLPI, especialmente a versão legada, possui um conjunto de regras e comportamentos específicos que a tornam um parceiro de integração complexo. Acoplar a lógica de negócio do dashboard (ex: a geração de gráficos) diretamente a esta API cria uma aplicação frágil e difícil de manter.
A solução arquitetural para este problema é a implementação de uma Camada Anti-Corrupção (Anti-Corruption Layer - ACL). Na prática, isto traduz-se na criação de uma classe ou módulo Python dedicado (ex: GlpiApiClient) que se torna o único componente da aplicação responsável por comunicar diretamente com a API do GLPI. O resto da aplicação comunica apenas com esta camada, que expõe métodos simples e limpos e devolve objetos de dados consistentes e específicos do domínio da aplicação.
As responsabilidades desta camada GlpiApiClient seriam:
Gestão de Autenticação e Sessão: Encapsular toda a lógica de initSession, armazenamento do Session-Token e killSession. O resto da aplicação não precisa de saber que existe um token de sessão.
Construção de Requisições: Expor métodos de alto nível como search_tickets(status="New", assigned_to="John Doe") que, internamente, constroem os complexos parâmetros criteria e range.
Gestão de Paginação: O método de busca deve conter, de forma transparente, o ciclo que recupera todas as páginas de resultados, devolvendo uma lista completa ao chamador.
Transformação de Dados: Receber a resposta bruta da API (com IDs) e transformá-la em modelos de dados limpos e validados (usar bibliotecas como Pydantic é ideal para isto), que são então usados pelo resto da aplicação.
Tratamento de Erros: Capturar os erros da API e os códigos de status HTTP e traduzi-los em exceções específicas da aplicação (ex: GlpiConnectionError, TicketNotFoundError), permitindo um tratamento de erros mais limpo no resto do código.
A adoção deste padrão arquitetural oferece enormes benefícios. Torna o código do dashboard muito mais limpo e focado na sua responsabilidade principal: a visualização de dados. Isola toda a complexidade da API do GLPI num único local, tornando-a mais fácil de testar, depurar e manter. Mais importante ainda, prepara a aplicação para o futuro. Quando a nova API do GLPI (/api.php) se tornar estável e preferível, apenas a implementação interna da camada GlpiApiClient precisará de ser atualizada; o resto da aplicação glpi_dashboard_cau poderá permanecer inalterado, garantindo uma transição suave e de baixo risco.

4.3. Apresentando Dados com Clareza
O último passo para uma UI de qualidade é a formatação dos dados para apresentação. Dados brutos da API, mesmo que já traduzidos pela ACL, podem não ser ideais para o usuário final. O exemplo mais comum é o formato de data. A API retornará datas no formato ISO 8601 (ex: 2023-10-27T10:00:00Z). Apresentar isso diretamente na UI é tecnicamente correto, mas pouco amigável.

Boas práticas de formatação no cliente incluem:

- **Formatação de Datas**: Usar bibliotecas como `date-fns` ou a API nativa do navegador `Intl.DateTimeFormat` para formatar datas e horas de acordo com o local (locale) do usuário. Por exemplo, converter `2023-10-27T10:00:00Z` para "27/10/2023 07:00" para um usuário no Brasil (considerando o fuso horário) ou "10/27/2023 10:00 AM" para um usuário em outro local.
- **Capitalização e Estilização**: Aplicar estilos CSS com base nos valores dos dados. Por exemplo, a coluna "Prioridade" pode ter cores diferentes para "Alta" (vermelho), "Média" (amarelo) e "Baixa" (verde) para melhorar a legibilidade visual da tabela.
- **Truncamento de Texto**: Para campos de texto longos como o título (`title`), truncar o texto com "..." e exibir o texto completo em um tooltip ao passar o mouse, evitando quebras de layout na tabela.

Esses refinamentos finais, embora pequenos, são o que separam uma aplicação funcional de uma aplicação profissional e agradável de usar.
Seção 5: Conclusão e Roteiro Estratégico
5.1. Sumário das Conclusões
A análise detalhada da aplicação glpi_dashboard_cau e da API REST do GLPI revela que a discrepância de dados observada não é o resultado de uma falha técnica, mas sim de uma implementação de cliente de API incompleta. Os registos mostram um ciclo de comunicação bem-sucedido, mas a lógica da aplicação falha em dois aspetos críticos: não gere a paginação dos resultados da API, levando à obtenção de um conjunto de dados parcial, e não transforma os identificadores relacionais retornados pela API nos seus valores textuais correspondentes, resultando numa exibição de dados brutos e incompreensíveis.
A solução para estes problemas imediatos envolve a implementação de um ciclo de paginação robusto, que utilize o cabeçalho Content-Range, e a criação de uma camada de mapeamento de dados para traduzir os IDs. No entanto, uma solução estratégica e de longo prazo exige uma refatoração arquitetural. A introdução de uma Camada Anti-Corrupção, na forma de um cliente de API dedicado, irá isolar a complexidade da API do GLPI, resultando numa aplicação mais resiliente, de fácil manutenção e preparada para futuras evoluções da API.
5.2. Roteiro Prioritizado para glpi_dashboard_cau
Para guiar a evolução da aplicação de forma estruturada, recomenda-se o seguinte roteiro de desenvolvimento, dividido em fases:
Fase 1 (Remediação Imediata):
Objetivo: Corrigir o problema de exatidão dos dados com o mínimo de refatoração.
Ações:
Implementar um ciclo de paginação na função de busca de dados existente para garantir que todos os chamados sejam recuperados.
Implementar um mapeamento de IDs para texto (conforme Tabela 2) para os campos status, priority, urgency e type antes de os dados serem enviados para o frontend.
Adicionar o parâmetro expand_dropdowns=1 às requisições para resolver automaticamente os nomes de categorias e outros campos de dropdown.
Ajustar a configuração de autenticação para eliminar a mensagem de aviso.
Fase 2 (Refatoração para Robustez):
Objetivo: Isolar a lógica de interação com a API e melhorar a manutenibilidade do código.
Ações:
Criar uma nova classe ou módulo Python, GlpiApiClient.
Mover toda a lógica de interação com a API (autenticação, gestão de sessão, construção de criteria, paginação, transformação de dados e tratamento de erros) para esta nova classe.
Refatorar os callbacks do Dash para utilizarem esta nova classe GlpiApiClient, que deverá devolver objetos de dados limpos e prontos a usar.
Fase 3 (Melhoria Contínua):
Objetivo: Adicionar novas funcionalidades ao dashboard sobre uma base de dados estável e confiável.
Ações:
Com a camada de cliente da API robusta implementada, começar a desenvolver novos gráficos, tabelas e visualizações.
Expandir o GlpiApiClient para interagir com outros tipos de itens do GLPI (ex: Computer, User, Problem) conforme necessário.
Fase 4 (Preparação para o Futuro):
Objetivo: Garantir a longevidade e a compatibilidade da aplicação.
Ações:
Monitorizar o desenvolvimento e a estabilização da nova API de alto nível do GLPI (/api.php).
Avaliar a migração para a nova API quando esta oferecer vantagens claras (ex: melhor desempenho, funcionalidades GraphQL, documentação Swagger superior).
Quando a decisão de migrar for tomada, a atualização será contida dentro da classe GlpiApiClient, minimizando o impacto no resto da aplicação.
Seguir este roteiro transformará a aplicação glpi_dashboard_cau de uma ferramenta funcional, mas frágil, numa solução de business intelligence robusta, confiável e preparada para acompanhar a evolução do ecossistema GLPI.
