provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

variable "databricks_host" {}
variable "databricks_token" {}