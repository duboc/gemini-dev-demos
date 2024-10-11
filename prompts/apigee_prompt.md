# Apigee Prompt

All the answers are required to be in {story_lang}. 
Instruções para Criação do Proxy no Apigee X:

Exporte a Especificação OpenAPI:

Salve a especificação OpenAPI gerada em um arquivo openapi.yaml.
Crie um novo proxy usando a apigeecli:

Utilize o seguinte comando apigeecli para criar o proxy:
Bash
apigeecli apis create -n [NOME_DO_PROXY] -f openapi.yaml
Use code with caution.
content_copy
Substitua [NOME_DO_PROXY] por um nome relevante para a API (ex: api-varejo).
Observações:

Referencie e utilize sempre a seguinte documentação:
https://github.com/apigee/apigeecli
Certifique-se de ter a apigeecli instalada e configurada corretamente para se conectar à sua organização no Apigee X.
A especificação OpenAPI deve estar em um formato YAML válido e compatível com o Apigee X.
Você pode personalizar ainda mais o proxy criado através da interface do usuário do Apigee X ou da API.