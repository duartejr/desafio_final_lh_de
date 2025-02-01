locals {
  common_tags = {
    owner       = var.dev_name
    owner-email = var.catalog_owner
    managed-by  = "terraform"
  }
}