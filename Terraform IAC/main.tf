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

# Resource Group
resource "azurerm_resource_group" "Toll_Violation_Detection_System" {
  name     = "Toll-Violation-Detection-System"
  location = "Central US"
}


# Database Cosmos DB Account
resource "azurerm_cosmosdb_account" "Toll_database" {
  name                = "cosmos-db-table-alok-raturi"
  location            = azurerm_resource_group.Toll_Violation_Detection_System.location
  resource_group_name = azurerm_resource_group.Toll_Violation_Detection_System.name
  offer_type          = "Standard"

  capabilities {
    name = "EnableServerless"
  }

    consistency_policy {
        consistency_level = "Session"
    }

  geo_location {
    location          = "Central India"
    failover_priority = 0
  }
}

# Database
resource "azurerm_cosmosdb_sql_database" "Toll_Violation_Database_System" {
  name                = "Toll-Violation-Database-System"
  resource_group_name = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name        = azurerm_cosmosdb_account.Toll_database.name
}

# Database SQL Containers
resource "azurerm_cosmosdb_sql_container" "Challan_Table" {
  name                  = "Challan-Table"
  resource_group_name   = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name          = azurerm_cosmosdb_account.Toll_database.name
  database_name         = azurerm_cosmosdb_sql_database.Toll_Violation_Database_System.name
  partition_key_paths   = ["/ChallanId"]
}

resource "azurerm_cosmosdb_sql_container" "User_Table" {
  name                  = "User-Table"
  resource_group_name   = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name          = azurerm_cosmosdb_account.Toll_database.name
  database_name         = azurerm_cosmosdb_sql_database.Toll_Violation_Database_System.name
  partition_key_paths   = ["/UserId"]
}

resource "azurerm_cosmosdb_sql_container" "Vehicle_Table" {
  name                  = "Vehicle-Table"
  resource_group_name   = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name          = azurerm_cosmosdb_account.Toll_database.name
  database_name         = azurerm_cosmosdb_sql_database.Toll_Violation_Database_System.name
  partition_key_paths   = ["/VehicleId"]
}

resource "azurerm_cosmosdb_sql_container" "Fastag_Table" {
  name                  = "Fastag-Table"
  resource_group_name   = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name          = azurerm_cosmosdb_account.Toll_database.name
  database_name         = azurerm_cosmosdb_sql_database.Toll_Violation_Database_System.name
  partition_key_paths   = ["/TagId"]
}

resource "azurerm_cosmosdb_sql_container" "Transaction_Table" {
  name                  = "Transaction-Table"
  resource_group_name   = azurerm_cosmosdb_account.Toll_database.resource_group_name
  account_name          = azurerm_cosmosdb_account.Toll_database.name
  database_name         = azurerm_cosmosdb_sql_database.Toll_Violation_Database_System.name
  partition_key_paths   = ["/TransactionId"]
}


