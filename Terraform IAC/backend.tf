terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-backend"
    storage_account_name = "statestoragetf"                      
    container_name       = "terraform-state-storage"                       
    key = "terraform.tfstate"        
  }
}