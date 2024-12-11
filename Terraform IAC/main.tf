terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "8a228cff-023f-42af-818d-51a84a828d46"
}

resource "azurerm_resource_group" "terraform_backend" {
  name     = "terraform-backend"
  location = "Central India"
}