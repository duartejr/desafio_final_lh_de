resource "databricks_catalog" "raw_catalog" {
  name  = "${var.dev_name}_raw"
  owner = var.catalog_owner
}

resource "databricks_catalog" "stg_catalog" {
  name  = "${var.dev_name}_stg"
  owner = var.catalog_owner
}
