output "raw_catalog_name" {
  value = databricks_catalog.raw_catalog.name
}

output "stg_catalog_name" {
  value = databricks_catalog.stg_catalog.name
}
