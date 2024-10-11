# OpenAPI Prompt

All the answers are required to be in {story_lang}.

Instruções para o Modelo:

Recebimento da Sugestão de Tabela DW (Varejo):

Utilize a sugestão da tabela DW gerada anteriormente para o contexto de varejo, incluindo:
Nome da tabela (ex: Fato_Vendas)
Dimensões (com seus atributos e tipos de dados)
Fatos (com suas métricas e tipos de dados)
Geração da Especificação OpenAPI (YAML):

Gere uma especificação OpenAPI (Swagger) versão 3.0 em formato YAML que defina uma API RESTful para consulta dos dados da tabela DW.
Inclua os seguintes elementos na especificação:
Informações: Título da API, descrição, versão, termos de uso, contato.
Servidores: URL base da API no Apigee X.
Caminhos (Paths):
/vendas: Retorna uma lista de vendas com paginação e filtros opcionais (por cliente, produto, loja, data, etc.).
/vendas/id: Retorna detalhes de uma venda específica pelo ID.
/clientes: Retorna uma lista de clientes com paginação e filtros opcionais.
/produtos: Retorna uma lista de produtos com paginação e filtros opcionais.
/lojas: Retorna uma lista de lojas com paginação e filtros opcionais.
/relatorios: Retorna relatórios agregados (ex: vendas por mês, vendas por categoria de produto).
Definições (Schemas):
Defina os schemas (modelos de dados) para cada dimensão e fato da tabela DW.
Inclua exemplos de dados para cada schema.
Segurança: Defina o esquema de autenticação da API (ex: OAuth2, API Key).


Sugestão de Tabela DW:

Nome da Tabela: Fato_Vendas

Dimensões:
- Cliente (ID_Cliente INTEGER, Nome STRING, Sexo STRING, Faixa_Etaria STRING)
- Produto (ID_Produto INTEGER, Nome STRING, Categoria STRING, Subcategoria STRING)
- Loja (ID_Loja INTEGER, Nome STRING, Cidade STRING, Estado STRING)
- Tempo (ID_Tempo DATE, Ano INTEGER, Trimestre INTEGER, Mês INTEGER, Dia INTEGER)

Fatos:
- Data_Venda DATE
- Quantidade_Vendida INTEGER
- Valor_Total FLOAT
- Forma_Pagamento STRING

Gere uma especificação OpenAPI 3.0 em formato YAML para uma API de consulta de dados de vendas no varejo