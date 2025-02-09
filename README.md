
---

# Migração Databricks

O objetivo deste projeto é implementar o processo de extração de dados de um banco de dados Microsoft SQLServer usando Databricks disponbilizando tabelas staging. O projeto está dividido em duas pastas: infra e pipeline_elt. A pasta infra contém arquivos terraform para criação de catologs e schemas necessários para a ingestão dos dados no Databricks utilizando Terraform. A pasta pipeline_elt contém o bundle do Databricks com a criação do scripts e workflow para automatizar o processo. Este projeto foi desenvolvido para extrair todas as tabelas do departamente de `sales` do banco de dados da `AdventureWorks`. 

## Estrutura do Projeto

- `infra/`: Contém arquivos Terraform para criação de catálogos e esquemas necessários.
- `pipeline_elt/`: Contém o bundle Databricks com scripts e workflows para automação do processo.

## Clonando o Repositório

Para clonar o repositório localmente, execute o seguinte comando:
```sh
git clone https://github.com/duartejr/desafio_final_lh_de.git
cd desafio_final_lh_de
```

## Instalação

### Instalação do Databricks CLI

1. Instale o Databricks CLI: https://docs.databricks.com/dev-tools/cli/databricks-cli.html
2. Autentique-se no seu workspace Databricks [https://learn.microsoft.com/pt-pt/azure/databricks/dev-tools/cli/authentication]:
  
    2.1 Use a CLI do Databricks para executar o seguinte comando:
    ```sh
    $ databricks configure
    ```
    2.2 Para o prompt Databricks Host, insira o URL da instância do seu workspace do Databricks, por exemplo https://dbc-a1b2345c-d6e7.cloud.databricks.com.

    2.3 Para o prompt Access token pessoal, insira o access token pessoal do Databricks para seu workspace.

    Se preferir também pode configurar a autenticação do Databricks utilizando a autenticação OAuth machine-to-machine (M2M). Para mais detalhes consulte a seção conrrespondente no seguinte endereço: https://learn.microsoft.com/pt-pt/azure/databricks/dev-tools/cli/authentication 
  
  Adicionalmente você também pode instalar a extensão do Databricks para o Visual Studio Code: https://learn.microsoft.com/pt-pt/azure/databricks/dev-tools/vscode-ext/ . Esta extensão trás ferramentas que facilitam as estapas de CI/CD dos bundles no Databricks. Com ela você poderá executar arquivos de código Python locais diretamente em clusters do Databricks em seus espaços de trabalho remoto. Ela também permite sincronizar seus códigos locais com o código em seus espaços de trabalho remotos.


### Instalação do Terraform

1. Instale o Terraform: https://learn.hashicorp.com/tutorials/terraform/install-cli

    O link acima te levará a documentação oficial do Terraform com o passo a passo para sua instalação de acordo com o seu ambiente de desenvolvimento.

### Criação de um Ambiente Virtual Python

Após a conclusão dos passos anteriores é necessário criar um ambiente virtual (venv) do Python. Seu objetivo é criar um ambiente controlado, com todas os pacotes e biliotecas necessárias para a execução de todos os scripts criados para o projeto.

#### Linux

1. Crie um ambiente virtual:
    ```sh
    python3 -m venv venv
    ```
2. Ative o ambiente virtual:
    ```sh
    source venv/bin/activate
    ```

#### Windows

1. Crie um ambiente virtual:
    ```sh
    python -m venv venv
    ```
2. Ative o ambiente virtual:
    ```sh
    .\venv\Scripts\activate
    ```

####

Com o ambiente virtual ativo instale os pacotes e bibliotecas necessários. Os mesmos podem ser instalados instalados através do arquivo `requirements.txt` da seguinte forma:
```sh
pip install -r requirements.txt
```

## Variáveis de Ambiente

Para exportar variáveis de ambiente a partir de um arquivo `.env`, inclua as variáveis no arquivo `.env` no seguinte formato:
```
export VARIAVEL_EXEMPLO=valor_exemplo
export OUTRA_VARIAVEL=outro_valor
```

Utilize o arquivo `.env.example` como base para a declaração das variáveis de ambiente. Ele contém a lista de todas as variáveis necessárias. Preencha os valores corretamente, renomeio para `.env` e siga para o próximo passo.

Utilize o comando abaixo para carregá-las no seu shell:

#### Bash (Linux e macOS)
```sh
source .env
```

#### PowerShell (Windows)
```powershell
Get-Content .env | ForEach-Object { if ($_ -match "^(.*?)=(.*)$") { Set-Item -Path env:$($matches[1]) -Value $matches[2] } }
```

## Workflows

Este repositório utiliza workflows para automatizar processos de deploy da infraestrura e do bundle do Databricks. Confira os arquivos na pasta `.github/workflows` para mais detalhes sobre os workflows configurados, ou acesse aqui o [README](https://github.com/duartejr/deafio_final_lh_de/blob/a4da62bf31d571edc9243562d8f321bd7dd392ec/.github/workflows/README.md) dos workflows disponíveis. Assim, o deploy pode ser feito de forma automática, utilizando os workflows, ou manualmente como descrito a seguir.

## Deploy do Terraform

Para fazer o deploy do Terraform que está na pasta `infra`, siga os passos abaixo:

1. Navegue até a pasta `infra`:
    ```sh
    cd infra
    ```
2. Inicialize o Terraform:
    ```sh
    terraform init
    ```
3. Planeje a execução do Terraform:
    ```sh
    terraform plan
    ```
4. Aplique as mudanças com o Terraform:
    ```sh
    terraform apply
    ```
OBS: As etapas anteriores funcionarão adequadamente no caso de os recursos (`catalog` e `schemas`) ainda não exisitirem no Databricks. Portanto são etapadas para a inicialização da infraestrutura necessária apenas. Para alteração em uma infraestrutura já existente será necessário realizar a persistência do `tfstate` em um backend remoto. O `tfstate` é o arquivo de estado do Terraform que armazena informações sobre os recursos provisionados para rastrear mudanças e gerenciar a infraestrutura. Caso algum recursos tente ser criado e o Terraform não tenha acesso a informação do state ele para o processo a fim de evitar mudanças que comprometam a infraestrutura existente. Essa persistência pode ser feita em uma próxima fase do projeto com a disponibilização de um bucket s3 ou Azure Blob Storage para realizar a persistência do `tfstate` remotamente.

### Recursos criados

Uma vez realizado o deploy da infraestrura serão criados os seguintes recursos:

- nome_desenvolvedor_raw : Catalog para armazenar os dados extraídos diretamente do banco de dados sem tratamento.
    - dev_raw_sales : Schema para armazenar os dados raw de sales a serem utilizados em ambiente de desenvolvimento.
    - prod_raw_sales : Schema para armazenar os dados raw de sales a serem utilizados em ambiente de produção.
- nome_desenvolvedor_stg : Catalog para armazenar os dados tratados em tabelas staging.
    - dev_stg_sales : Schema para armazenar os dados staging de sales a serem utilizados em ambiente de desenvolvimento.
    - prod_stg_sales : Schema para armzenar os dados staging de sales a serem utilizados em ambiente de produção.

## Deploy do Databricks

Antes de realizar o primeiro deploy no Databricks é necessários configurar as secrets necessárias para acessar o banco de dados.

### Criar um Secret Scope

Primeio você deve criar um Secret Scope, que é um espaço seguro, dentor do Databricks, para armazenar e gerenciar secrets (credenciais, senhas, chaves de API) de forma criptografada. Portanto, garatem maior segurança do que apenas deixá-las como variáveis de ambiente.

Execute o seguinte comando para criar um scope:
```sh
databricks bundle create-scope --scope nome_desenvolvedor_adw
``` 

É esperado que o scope criado tenha o nome do desenvolvedor seguido de _adw.

### Configuração de Secrets

Após o scope criado deve-se configurar as secrets necessárias.

Para configurar secrets no Databricks, utilize o comando abaixo:
```sh
databricks secrets put-secret --json '{
  "scope": "<scope-name>",
  "key": "<key-name>",
  "string_value": "<secret>"
}'
```

`key` é o nome da secret e `string_value` é o valor da mesma. Para executar esse projeto as secrets necessárias são: 
- pswd_mssql : Senha de acesso ao banco de dados
- ip_mssql : IP de acesso ao banco de dados
- port_mssql : Porta do banco de dados
- user_mssql : Usuário do banco de dados

OBS: Se for contribuir com o projeto diretamente no repositório atual, e realizar o deploy apenas através dos workflows axistentes, a declaração dessas variáveis não é necessárias por já estarem declaradas dentro do repositório. Mas, no caso de criar um fork do mesmo será necessário declarar as mesmas no ambiente do Github como descrito no [README](https://github.com/duartejr/deafio_final_lh_de/blob/a4da62bf31d571edc9243562d8f321bd7dd392ec/.github/workflows/README.md) correspondente aos workflows.

### Deploy no Databricks

3. Para deploy de uma cópia de desenvolvimento do projeto, execute:
    ```sh
    $ databricks bundle deploy --target dev
    ```
4. Para deploy de uma cópia de produção, execute:
    ```sh
    $ databricks bundle deploy --target prod
    ```

### Uso

1. Para rodar um job ou pipeline, use o comando:
    ```sh
    $ databricks bundle run
    ```

Jobs e pipelines quando feito deploy no ambiente de `dev` ficam com o status de PAUSED por padrão. Ou seja, esses jobs só serão disparados manualmente. Já quando feito o deploy em `prod` os mesmos ficaram ativos e seguiram as regras manualmente, o usuário deverá pausar os mesmos manualmente caso deseje.

### Jobs utilizados na pipeline

A pipeline criada utiliza duas tasks.
- extract_raw_data_task : Realiza a extração dos dados diretamente do banco de dados e armazena no catalog de dados raw. 
- load_stage_data_task : Lê os dados salvos no schema de raw, aplica as transformações necessárias e salva no schema de staging correspondente para cada tabela.

A extraçãoé feita de forma incremental e pode ser configurada através do arquivo `resources.yml` que é o responsável por configurar os workflows do Databricks. O segmento de código a seguir apresenta um exemplo de como realizar a extração de dados com data de atualização entre 01/01/2007 e o dia de hoje.

```yml
- task_key: extract_raw_data_task
    spark_python_task:
        python_file: ../src/extract_raw.py
        parameters: ["-o", "${var.pipeline_owner}", "-e", "${bundle.environment}", "-d", "2007-01-01 00:00:00"]
```
O script `extract_raw.py` aceita os seguintes parâmetros:
- -o | --owner : Nome do responsável pela pipeline, já extraído das variáveis de ambiente do Databricks
- -e | --environment : O nome do ambiente em que o script está sendo executado: dev ou prod. Já extraído automaticamente das variáveis de ambiente do Databricks.
- -d | --first_modified_date : A data mais antiga de atualização dos dados. Quando definida ele vai extrair os dados com data de atualialização entre o valor definido e o dia atual. Se não for definido valor vai considerar apenas o lag definido.
- -l | --lag : Tamanho da janela de atualização em dias. Quando não definido, e -d também é deixado vazio, vai utilizar o padrão que é de 7 dias. Ou seja, irá realizar a extração com data de atualização entre os últimos 7 dias. 

Para verificar a data de atualização dos dados é utilizada a coluna ModifiedDate.

A carga dos dados de staging é realizada pelo script: `load_stage.py`. Esse script verifica a existência de dados nos schemas raw, caso exista realiza as transformações necessárias e salva os dados nas tabelas de staging correspondentes. A ingestão é feita de forma incremental utilizando o merge. Desta forma garante-se a atualização de dados, inserção de novos e a preservação de dados antigos. O merge é feito utilizando as `primary keys` definidas nos arquivo de configuração `tables_mapping.yaml`.

O trecho de código a seguir mostra a chamada desse script dentro do workflow do Databricks:
```yaml
- task_key: load_stage_data_task
    spark_python_task:
        python_file: ../src/load_stage.py
        parameters: ["-o", "${var.pipeline_owner}", "-e", "${bundle.environment}"]
    depends_on: 
        - task_key: extract_raw_data_task
```

O script `load_stage.py` aceita os seguintes parâmetros:
- -o | --owner : Nome do responsável pela pipeline, já extraído das variáveis de ambiente do Databricks
- -e | --environment : O nome do ambiente em que o script está sendo executado: dev ou prod. Já extraído automaticamente das variáveis de ambiente do Databricks.

### Arquivo de configuração `tables_mapping.yaml`

Esse arquivo contém o mapeamento de todas as tabelas que deverão ser extraídas, primary keys e colunas a serem mantidas na ingestão das tabelas staging. Para cada tabela deve ser criada uma estrutura como no exemplo a seguir:
```yaml
CountryRegionCurrency:
    primary_key:
      - country_region_code
      - currency_code
    stg_name: country_region_currency
    stg_columns:
      CountryRegionCode: country_region_code
      CurrencyCode: currency_code
      ModifiedDate: modified_date
      extract_date: extract_date
```
A primeira linha é o nome da tabela que será extraída do banco de dados, deve ser o mesmo nome utilizado no banco de dados.

`primary_key`- É o nome da coluna, ou conjunto de colunas, utilizada para identificar registros únicos nas tabelas, é o prâmetro utilizado no merge durante o carrregamento das tabelas staging. Portanto deve ser o nome que será utilizado nas colunas das tabelas staging.

`stg_name` - É o nome que será utilizado para a tabela de staging.

`stg_columns` - Mapeia as colunas raw `chaves` e seu respectivo nome das tabelas `staging`.

As transformações aplicadas para as tabela stagins são: padronização dos nomes de colunas, remoção de dados duplicados. O tipos de dados das colunas são mantidos os mesmos do banco de dados original.

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/new_feature`)
3. Faça commit das suas mudanças (`git commit -m 'Add some new feature'`)
4. Faça push para a branch (`git push origin feature/new_feature`)
5. Abra um Pull Request

---

