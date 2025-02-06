# Workflows

## Create infrastructure into Databricks

**Arquivo:** [deploy_infra.yml](https://github.com/duartejr/deafio_final_lh_de/blob/a4da62bf31d571edc9243562d8f321bd7dd392ec/.github/workflows/deploy_infra.yml)

Este workflow cria a infraestrutura no Databricks usando Terraform.

### Gatilhos
- `push` no branch `main` e no caminho `infra/**`

### Jobs
- **deploy**
  - **runs-on:** ubuntu-latest
  - **steps:**
    - Checkout do repositório
    - Configuração do Terraform
    - Inicialização do Terraform
    - Aplicação do Terraform com as variáveis de ambiente `DATABRICKS_HOST` e `DATABRICKS_TOKEN`

---

## Deploy Databricks bundle

**Arquivo:** [deploy_bundle.yml](https://github.com/duartejr/deafio_final_lh_de/blob/a4da62bf31d571edc9243562d8f321bd7dd392ec/.github/workflows/deploy_bundle.yml)

Este workflow faz o deploy de um bundle no Databricks.

### Gatilhos
- `push` nos branches `main` e `dev` e nos caminhos `pipeline_elt/**` e `.github/workflows/**`

### Variáveis de Ambiente
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`

### Jobs
- **build**
  - **runs-on:** ubuntu-latest
  - **steps:**
    - Checkout do repositório
    - Instalação do Databricks CLI
    - Autenticação no Databricks
    - Deploy para Databricks (produção se no branch `main`, desenvolvimento se no branch `dev`)

---

## Como criar as variáveis de ambiente

1. Vá para a página do repositório no GitHub.
2. Clique na aba "Settings".
3. No menu lateral, clique em "Secrets and variables" e depois em "Actions".
4. Clique no botão "New repository secret".
5. Adicione as seguintes variáveis de ambiente:
   - `DATABRICKS_HOST`: URL do host do Databricks.
   - `DATABRICKS_TOKEN`: Token de acesso ao Databricks.
