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
  lifecycle {
    prevent_destroy = true
  }
}

resource "databricks_schema" "stg_dev_sales_schema" {
  catalog_name = databricks_catalog.stg_catalog.name
  name         = "dev_stg_sales"
  comment      = "Holds curated data refined of the sales department. For development pourposes."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "staging"
      "kind" : "processed data"
      "environment" : "dev"
    }
  )

  lifecycle {
    prevent_destroy = true
  }

}

resource "databricks_schema" "stg_prod_sales_schema" {
  catalog_name = databricks_catalog.stg_catalog.name
  name         = "prod_stg_sales"
  comment      = "Holds curated data refined of the sales department. To be used in production."
  properties = merge(
    local.common_tags,
    {
      "purpose" : "staging"
      "kind" : "processed data"
      "environment" : "prod"
    }
  )

  lifecycle {
    prevent_destroy = true
  }
  
}
