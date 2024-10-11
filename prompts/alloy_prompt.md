Contexto: Modelagem de dados relacional para banco de dados PostgreSQL.

Objetivo: Projetar um esquema de banco de dados relacional para atender aos requisitos de uma User Story.

Entrada: Uma User Story descrevendo uma necessidade de negócio.

Saída:

Identificação de Entidades e Atributos:
Identificar as entidades (tabelas) relevantes a partir da User Story.
Listar os atributos (colunas) de cada entidade, incluindo seus tipos de dados em PostgreSQL.

Definição de Relacionamentos:
Descrever os relacionamentos entre as entidades (um-para-um, um-para-muitos, muitos-para-muitos).
Indicar as chaves primárias e estrangeiras que implementam os relacionamentos.

Diagrama Entidade-Relacionamento (DER):
Criar um DER que represente visualmente as entidades, atributos e relacionamentos. A resposta precisa estar em ASCII 

Normalização:
Analisar o esquema do banco de dados e aplicar as formas normais para evitar redundância e anomalias de atualização.
Descrever as etapas de normalização e justificar as decisões de projeto.
Comandos SQL:

Gerar comandos SQL (DDL) para criar as tabelas no PostgreSQL, incluindo a definição de chaves primárias, estrangeiras e outros constraints.
Exemplo:

User Story: "Como dono de uma livraria, quero armazenar informações sobre meus livros, autores, editoras e clientes, para controlar meu estoque, vendas e clientes."

Saída:

Entidades e Atributos:

Livro: id_livro (SERIAL PK), titulo (VARCHAR), ano_publicacao (INT), id_autor (INT FK), id_editora (INT FK), preco (NUMERIC), estoque (INT)
Autor: id_autor (SERIAL PK), nome_autor (VARCHAR), nacionalidade (VARCHAR)
Editora: id_editora (SERIAL PK), nome_editora (VARCHAR)
Cliente: id_cliente (SERIAL PK), nome_cliente (VARCHAR), endereco (VARCHAR), telefone (VARCHAR)
Venda: id_venda (SERIAL PK), id_cliente (INT FK), data_venda (DATE)
ItemVenda: id_item_venda (SERIAL PK), id_venda (INT FK), id_livro (INT FK), quantidade (INT)
Relacionamentos:

Um livro tem um autor e uma editora.
Um autor pode escrever vários livros.
Uma editora pode publicar vários livros.
Um cliente pode realizar várias vendas.
Uma venda pode ter vários itens.
Um item de venda pertence a uma venda e a um livro.
DER:

[Aqui você incluiria um DER visual ou uma descrição textual do diagrama, mostrando as entidades e os relacionamentos entre elas.]
Normalização:

O esquema apresentado já está em 3ª Forma Normal (3FN), pois não há dependências transitivas entre os atributos.
Comandos SQL:

SQL
CREATE TABLE Autor (
    id_autor SERIAL PRIMARY KEY,
    nome_autor VARCHAR(255) NOT NULL,
    nacionalidade VARCHAR(255)
);

CREATE TABLE Editora (
    id_editora SERIAL PRIMARY KEY,
    nome_editora VARCHAR(255) NOT NULL
);

CREATE TABLE Livro (
    id_livro SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    ano_publicacao INT,
    id_autor INT REFERENCES Autor(id_autor),
    id_editora INT REFERENCES Editora(id_editora),
    preco NUMERIC(10,2) NOT NULL,
    estoque INT NOT NULL
);

-- ... (comandos para criar as tabelas Cliente, Venda e ItemVenda)
Use code with caution.

Observações:

Sempre ao gerar dados mock, utilize algum nome da seguinte lista:
Breno, Amadei, Carlos, Mazurque, Kauy, Filipe, Renato, Wilgner, Rober, Diego, Iago, Tiago, Brunno, Koba
Utilize o dados abaixo como entrada.