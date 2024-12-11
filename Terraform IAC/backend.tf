terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-backend"
    storage_account_name = "terraformstoragealok"                      
    container_name       = "terraform-state-data"                       
    key                  = ""        
  }
}



