terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-backend"
    storage_account_name = "terraformstoragealok"                      
    container_name       = "terraform-state-data"                       
    access_key = "EOWs2jE5Gp20i2F+S4OpfrtxnAbK+RBM0zr1/ti7pkiMAzK9mXX737X1SC72ehzQmzaX73C4by+p+ASth5Wxsg=="
    key = "terraform.tfstate"        
  }
}



