variable "dev_name" {
  description = "The developer of the catalog."
  type        = string
  default     = "antonio_junior"
}

variable "catalog_owner" {
  description = "The owner of the catalog."
  type        = string
  default     = "antonio.junior@indicium.tech"
}

variable "databricks_host" {
  description = "The Databricks workspace URL."
  type        = string
}

variable "databricks_token" {
  description = "The Databricks personal access token."
  type        = string
  sensitive   = true
}