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
  force_destroy = true
}

resource "databricks_schema" "raw_sales_schema" {
  catalog_name = databricks_catalog.raw_catalog.id
  name         = "sales"
  comment      = "Contains raw data ingested directly from the sales department."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "ingestion"
      "kind" : "raw data"
    }
  )
  force_destroy = true
}

resource "databricks_catalog" "stg_catalog" {
  name    = "${var.dev_name}_stg"
  owner   = var.catalog_owner
  comment = "Home for transformed and cleansed data, ready for analysis."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "staging"
      "kind" : "processed data"
    }
  )
  force_destroy = true
}

resource "databricks_schema" "stg_sales_schema" {
  catalog_name = databricks_catalog.stg_catalog.id
  name         = "sales"
  comment      = "Holds curated data refined of the sales department."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "staging"
      "kind" : "processed data"
    }
  )
  force_destroy = true
}
