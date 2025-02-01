
resource "databricks_catalog" "raw_catalog" {
  name    = "${var.dev_name}_raw"
  owner   = var.catalog_owner
  comment = "Landing zone for raw, unprocessed data."

  properties = merge(
    local.common_tags,
    {
      "purpose" : "ingestion"
      "kind" : "raw data"
    }
  )

  lifecycle {
    prevent_destroy = true
  }
}

resource "databricks_schema" "raw_dev_sales_schema" {
  catalog_name = databricks_catalog.raw_catalog.name
  name         = "dev_raw_sales"
  comment      = "Contains raw data ingested directly from the sales department. For development pourposes."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "ingestion"
      "kind" : "raw data"
      "environment" : "dev"
    }
  )
  lifecycle {
    prevent_destroy = true
  }
}

resource "databricks_schema" "raw_prod_sales_schema" {
  catalog_name = databricks_catalog.raw_catalog.name
  name         = "prod_raw_sales"
  comment      = "Contains raw data ingested directly from the sales department. To be used in production."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "ingestion"
      "kind" : "raw data"
      "environment" : "prod"
    }
  )
  lifecycle {
    prevent_destroy = true
  }
}