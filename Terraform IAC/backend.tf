terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-backend"
    storage_account_name = "statestorageterraform"                      
    container_name       = "state-storage-terraform"                       
    access_key = ""
    key = "terraform.tfstate"        
  }
}