terraform {
  required_version = "1.10.5"
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.62.1"

    }
  }
}