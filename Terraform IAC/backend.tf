terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-backend"
    storage_account_name = "tfstateaccount12"                      
    container_name       = "terraform-state-container"                       
    key = "terraform.tfstate"        
  }
}